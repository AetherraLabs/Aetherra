"""Windows CLI signal intent must not turn unrelated cancellation into a save."""

# Standard library imports
import asyncio
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
import aetherra_os_launcher as launcher_module
from tests.unit import test_consciousness_observer_continuity as continuity_tests

observer_profile = continuity_tests.observer_profile


@pytest.fixture
def cli_operation(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["aetherra_os_launcher.py", "--no-gui"])
    # Exercise the Windows branch with the real Runner on every CI platform.
    # Keep the interpreter/event-loop platform untouched for embedded callers.
    monkeypatch.setattr(launcher_module, "sys", SimpleNamespace(platform="win32"))

    async def nothing(*args):
        pass

    for name in (
        "_refresh_owned_engine_heartbeat",
        "_refresh_observation_service_heartbeats",
        "_write_os_status",
        "_cleanup_os_status",
    ):
        monkeypatch.setattr(launcher_module.AetherraOSLauncher, name, nothing)
    previous = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, previous)


@pytest.mark.parametrize(
    ("trigger", "expected"),
    [
        ("sigint", True),
        ("cancel", False),
        ("custom_then_cancel", False),
        ("cancel_then_sigint", False),
        ("sigint_then_cancel", False),
    ],
)
def test_only_first_cli_sigint_cancellation_is_orderly(
    monkeypatch, cli_operation, trigger, expected
):
    exits = []
    if trigger == "custom_then_cancel":
        signal.signal(signal.SIGINT, lambda signum, frame: None)
    previous = signal.getsignal(signal.SIGINT)

    async def operation(launcher, config):
        task = asyncio.current_task()
        launcher.running = True

        def interrupt():
            if trigger in {"cancel", "cancel_then_sigint"}:
                task.cancel()
            if trigger != "cancel":
                signal.raise_signal(signal.SIGINT)
            if trigger in {"custom_then_cancel", "sigint_then_cancel"}:
                task.cancel()

        asyncio.get_running_loop().call_soon(interrupt)
        exits.append(await launcher._main_operation_loop())

    monkeypatch.setattr(launcher_module.AetherraOSLauncher, "launch_full_os", operation)
    assert asyncio.run(launcher_module.main()) == 0
    assert exits == [expected]
    assert signal.getsignal(signal.SIGINT) is previous


def test_second_sigint_abandons_inflight_checkpoint(
    monkeypatch, cli_operation, observer_profile
):
    store = continuity_tests.CheckpointStore(pending_save=True)
    owned = continuity_tests.observer(store)
    statuses = []
    loop_exits = []

    async def operation(launcher, config):
        owned.start()
        await continuity_tests.until(owned, lambda s: s["ticks_completed"] == 1)
        launcher.running = True
        asyncio.get_running_loop().call_soon(signal.raise_signal, signal.SIGINT)
        orderly = await launcher._main_operation_loop()
        loop_exits.append(orderly)
        if not orderly:
            await owned.stop()
            return

        async def second_interrupt():
            await continuity_tests.until(owned, lambda s: store.entered.is_set())
            signal.raise_signal(signal.SIGINT)

        interrupter = asyncio.create_task(second_interrupt())
        try:
            await owned.stop(save_checkpoint=True)
        finally:
            # A late successful I/O result must never become an acknowledged save.
            if store.rows and not store.save.done():
                store.save.set_result(
                    SimpleNamespace(
                        record_id="late",
                        checkpoint_id=store.rows[0]["checkpoint_id"],
                        payload=store.rows[0],
                    )
                )
            await owned.stop()
            statuses.append(owned.get_runtime_status())
            if interrupter.done():
                interrupter.exception()

    monkeypatch.setattr(launcher_module.AetherraOSLauncher, "launch_full_os", operation)
    with pytest.raises(KeyboardInterrupt):
        asyncio.run(launcher_module.main())
    assert loop_exits == [True]
    assert statuses[0]["continuity"]["saved_record_id"] is None
    assert statuses[0]["continuity"]["state"] == "uncertain"
    assert statuses[0]["thread_alive"] is False
    assert store.controls[0].cancelled.is_set()
    assert signal.getsignal(signal.SIGINT) is signal.default_int_handler


def test_embedded_main_in_worker_thread_preserves_signal_owner(
    monkeypatch, cli_operation
):
    exits = []
    previous = signal.getsignal(signal.SIGINT)

    async def operation(launcher, config):
        exits.append(await launcher._main_operation_loop())

    monkeypatch.setattr(launcher_module.AetherraOSLauncher, "launch_full_os", operation)
    with ThreadPoolExecutor(max_workers=1) as executor:
        result = executor.submit(lambda: asyncio.run(launcher_module.main())).result(5)
    assert result == 0
    assert exits == [True]
    assert signal.getsignal(signal.SIGINT) is previous


@pytest.mark.parametrize("disposition", [signal.SIG_DFL, signal.SIG_IGN])
def test_embedded_noncallable_signal_disposition_is_preserved(
    monkeypatch, cli_operation, disposition
):
    signal.signal(signal.SIGINT, disposition)
    active_handlers = []

    async def operation(launcher, config):
        active_handlers.append(signal.getsignal(signal.SIGINT))
        assert await launcher._main_operation_loop() is True

    monkeypatch.setattr(launcher_module.AetherraOSLauncher, "launch_full_os", operation)
    assert asyncio.run(launcher_module.main()) == 0
    # Do not deliver SIG_DFL: its process-termination policy must stay intact.
    assert active_handlers == [disposition]
    assert signal.getsignal(signal.SIGINT) is disposition


memory = continuity_tests.memory
policy = continuity_tests.policy
governed = continuity_tests.governed
database = continuity_tests.database


def test_second_sigint_cancels_periodic_work_inside_orderly_stop(
    monkeypatch, cli_operation, database, policy
):
    owned = continuity_tests.due_on_first_tick(database, monkeypatch, policy)
    entered, release = continuity_tests.hold_periodic_boundary(
        monkeypatch, "after_policy"
    )
    observed = []

    async def operation(launcher, config):
        owned.start()
        try:
            assert await asyncio.to_thread(entered.wait, 1.5)
            launcher.running = True
            asyncio.get_running_loop().call_soon(signal.raise_signal, signal.SIGINT)
            assert await launcher._main_operation_loop()
            asyncio.get_running_loop().call_later(
                0.05, signal.raise_signal, signal.SIGINT
            )
            await owned.stop(save_checkpoint=True)
        finally:
            release.set()
            await owned.stop()
            await continuity_tests.until(owned, lambda s: not s["thread_alive"])
            observed.append(owned.get_runtime_status()["continuity"])

    monkeypatch.setattr(launcher_module.AetherraOSLauncher, "launch_full_os", operation)
    with pytest.raises(KeyboardInterrupt):
        asyncio.run(launcher_module.main())
    assert observed[0]["last_save_acceptance"] == "unacknowledged"
    assert observed[0]["saved_record_id"] is None
    assert len(continuity_tests.recovery.stream.legacy.rows(database)) == 1


writing = continuity_tests.recovery.writing


@pytest.mark.asyncio
@pytest.mark.parametrize("pending", [False, True])
async def test_delayed_launcher_stop_propagates_absolute_cutoff(
    writing, database, monkeypatch, pending
):
    # Aetherra imports
    from Aetherra.aetherra_core.memory import lifecycle_checkpoint
    from Aetherra.consciousness import runtime_observer as runtime

    session, clock, tick = writing
    launcher = launcher_module.AetherraOSLauncher()
    owned = continuity_tests.observer(
        database, automatic=dict(continuity_tests.recovery.AUTO, start_mode="create")
    )
    owned._session = session
    launcher.systems["consciousness_core"] = owned
    clock[0] = session.started_monotonic + 28.75
    cutoff = clock[0] + 2
    real_time = runtime.time.time
    simulated = SimpleNamespace(monotonic=lambda: clock[0], time=real_time)
    monkeypatch.setattr(launcher_module, "time", simulated)
    monkeypatch.setattr(runtime, "time", simulated)
    monkeypatch.setattr(lifecycle_checkpoint, "time", simulated)
    stop = owned.stop
    observed = []

    async def delayed_stop(**kwargs):
        if observed:
            await stop(**kwargs)
            return
        # Event-loop delivery is delayed after the launcher records its deadline.
        # Memory can seal a periodic receipt during this part of the original budget.
        tick(30)
        if pending:
            session.poll(local_owned=True)
            continuity_tests.recovery.stream.wait_for_worker(session._write_job)
        tick(30.25)
        await stop(**kwargs)
        clock[0] = cutoff
        open_at_cutoff = session._write_control.active() if pending else None
        session.poll(local_owned=True)
        if session._write_job is not None:
            continuity_tests.recovery.stream.wait_for_worker(session._write_job)
            session.poll(local_owned=True)
        observed.append(
            (owned._save_deadline, open_at_cutoff, session.get_cached_status())
        )
        assert database.drain_lifecycle_checkpoints(0.5)

    monkeypatch.setattr(owned, "stop", delayed_stop)
    await launcher._stop_consciousness_observer(save_checkpoint=True)
    await launcher._stop_consciousness_observer()
    deadline, open_at_cutoff, status = observed[0]
    assert deadline == cutoff
    assert session._stop_deadline == cutoff
    if pending:
        assert open_at_cutoff is False
        assert status["last_save_acceptance"] == "unacknowledged"
    else:
        assert status["last_save_acceptance"] == "none"
    assert status["saved_record_id"] is None
    assert not status["stop_save_submitted"]
    assert len(continuity_tests.recovery.stream.legacy.rows(database)) == int(pending)

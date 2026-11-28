"""Pending operation cancellation must reach the launcher's owned cleanup."""

# Standard library imports
import asyncio
import contextlib

# Third party imports
import pytest

# Aetherra imports
from tests.unit import test_launcher_startup_cancellation as startup

isolated_launcher = startup.isolated_launcher


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "boundary",
    [
        "_refresh_owned_engine_heartbeat",
        "_refresh_observation_service_heartbeats",
        "_write_os_status",
    ],
)
@pytest.mark.parametrize("delivery", ["consumed", "wait_for_completion"])
@pytest.mark.parametrize(
    ("marked_sigint", "cancellations"), [(False, 1), (True, 1), (True, 2)]
)
async def test_operation_cancellation_stops_before_further_work(
    monkeypatch, isolated_launcher, boundary, delivery, marked_sigint, cancellations
):
    case = isolated_launcher
    launcher = case.launcher
    waiting = asyncio.Event()
    reply = asyncio.get_running_loop().create_future()
    calls = []
    operations = (
        "_refresh_owned_engine_heartbeat",
        "_refresh_observation_service_heartbeats",
        "_write_os_status",
    )

    def operation(name):
        async def run():
            calls.append(name)
            if name != boundary:
                return
            waiting.set()
            if delivery == "wait_for_completion":
                await asyncio.wait_for(reply, timeout=60)
            else:
                with contextlib.suppress(asyncio.CancelledError):
                    await asyncio.Future()

        return run

    for name in operations:
        monkeypatch.setattr(launcher, name, operation(name))
    task = asyncio.create_task(launcher.launch_full_os({"quiet": True, "mode": "test"}))
    try:
        await asyncio.wait_for(waiting.wait(), timeout=2)
        assert case.operation.is_set()
        assert launcher.running
        if delivery == "wait_for_completion":
            reply.set_result(None)
        task.cancel()
        if marked_sigint:
            launcher._orderly_cli_sigint_task = task
        if cancellations == 2:
            task.cancel()
        await asyncio.wait((task,), timeout=0.5)
        state = {
            "boundary": boundary,
            "delivery": delivery,
            "marked_sigint": marked_sigint,
            "task_done": task.done(),
            "cancelling": task.cancelling(),
            "running": launcher.running,
            "owned_system_stopped": case.stopped.is_set(),
            "checkpoint_intents": case.saves,
            "operation_calls": calls,
        }
        assert task.done(), state
        await task
        assert case.stopped.is_set(), state
        assert not launcher.running, state
        assert case.saves == (
            [True, False] if marked_sigint and cancellations == 1 else [False]
        ), state
        assert calls == list(operations[: operations.index(boundary) + 1]), state
    finally:
        await startup.cleanup(task)


@pytest.mark.asyncio
async def test_pending_cancellation_at_operation_entry_skips_all_work(
    monkeypatch, isolated_launcher
):
    case = isolated_launcher
    launcher = case.launcher
    waiting = asyncio.Event()
    calls = []

    async def heartbeat():
        calls.append("heartbeat")

    monkeypatch.setattr(launcher, "_refresh_owned_engine_heartbeat", heartbeat)

    async def enter_with_pending_cancel():
        waiting.set()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.Future()
        launcher.running = True
        return await launcher._main_operation_loop()

    task = asyncio.create_task(enter_with_pending_cancel())
    try:
        await asyncio.wait_for(waiting.wait(), timeout=2)
        task.cancel()
        await asyncio.wait((task,), timeout=0.5)
        assert task.done(), "Pending operation cancellation entered its long sleep"
        assert await task is False
        assert calls == []
    finally:
        await startup.cleanup(task)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "boundary",
    [
        "_load_core_systems",
        "_announce_os_online",
        "_main_operation_loop",
        "_refresh_owned_engine_heartbeat",
        "_refresh_observation_service_heartbeats",
        "_write_os_status",
    ],
)
@pytest.mark.parametrize(
    ("marked_sigint", "cancellations"), [(False, 1), (True, 1), (True, 2)]
)
async def test_inline_cancellation_does_not_escape_into_owned_cleanup(
    monkeypatch, isolated_launcher, boundary, marked_sigint, cancellations
):
    """A signal between suspensions must settle before asynchronous teardown."""
    case = isolated_launcher
    launcher = case.launcher
    heartbeat_started = asyncio.Event()
    heartbeat_stopped = asyncio.Event()

    async def heartbeat():
        heartbeat_started.set()
        try:
            await asyncio.Future()
        finally:
            await asyncio.sleep(0)
            heartbeat_stopped.set()

    heartbeat_task = asyncio.create_task(heartbeat())
    await heartbeat_started.wait()
    launcher._daemon_heartbeat_tasks.append(heartbeat_task)
    original = getattr(launcher, boundary)

    def cancel_inline():
        current = asyncio.current_task()
        for _ in range(cancellations):
            current.cancel()
        if marked_sigint:
            launcher._orderly_cli_sigint_task = current

    async def boundary_with_signal(*args, **kwargs):
        if boundary == "_main_operation_loop":
            cancel_inline()
            return await original(*args, **kwargs)
        result = await original(*args, **kwargs)
        # Models Windows SIGINT arriving inside a synchronous part of an
        # awaited method: cancel() is requested, but has not been delivered.
        cancel_inline()
        return result

    monkeypatch.setattr(launcher, boundary, boundary_with_signal)
    task = asyncio.create_task(launcher.launch_full_os({"quiet": True, "mode": "test"}))
    try:
        _, pending = await asyncio.wait((task,), timeout=2)
        assert not pending, "Launch did not settle after inline cancellation"
        assert case.stopped.is_set(), "Cancellation escaped into owned cleanup"
        assert heartbeat_stopped.is_set(), "Owned heartbeat teardown was interrupted"
        startup_cancel = boundary in {"_load_core_systems", "_announce_os_online"}
        orderly = not startup_cancel and marked_sigint and cancellations == 1
        assert case.saves == ([True, False] if orderly else [False])
        if startup_cancel:
            assert task.cancelled()
        else:
            await task
        assert not launcher.running
    finally:
        await startup.cleanup(task)
        await startup.cleanup(heartbeat_task)

"""Startup cancellation must survive an awaited dependency consuming the signal."""

# Standard library imports
import asyncio
import contextlib
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from aetherra_os_launcher import AetherraOSLauncher


@pytest.fixture
def isolated_launcher(monkeypatch):
    launcher = AetherraOSLauncher()
    stopped = asyncio.Event()
    operation = asyncio.Event()
    saves = []

    async def nothing(*args, **kwargs):
        return None

    async def shutdown():
        stopped.set()

    async def load(*args):
        launcher.systems["owned-system"] = SimpleNamespace(shutdown=shutdown)

    real_stop = launcher._stop_consciousness_observer
    real_operation = launcher._main_operation_loop

    async def stop(*, save_checkpoint=False):
        saves.append(save_checkpoint)
        await real_stop(save_checkpoint=save_checkpoint)

    async def main_operation():
        operation.set()
        return await real_operation()

    for name in (
        "_emit_boot_presence",
        "_initialize_service_registry",
        "_start_kernel_loop",
        "_activate_systems",
        "_validate_system_health",
        "_run_startup_readiness_scan",
        "_refresh_owned_engine_heartbeat",
        "_refresh_observation_service_heartbeats",
        "_write_os_status",
        "_cleanup_os_status",
    ):
        monkeypatch.setattr(launcher, name, nothing)
    monkeypatch.setattr(launcher, "_update_boot_phase", lambda **kwargs: None)
    monkeypatch.setattr(launcher, "_log_readiness_summary", lambda report: None)
    monkeypatch.setattr(launcher, "_load_core_systems", load)
    monkeypatch.setattr(launcher, "_main_operation_loop", main_operation)
    monkeypatch.setattr(launcher, "_stop_consciousness_observer", stop)
    monkeypatch.setenv("AETHERRA_NO_FAKE_DATA", "0")
    monkeypatch.setenv("AETHERRA_DISCLOSURE_TIER", "integration")
    monkeypatch.setenv("AETHERRA_KEEP_MONITOR", "0")
    return SimpleNamespace(
        launcher=launcher,
        stopped=stopped,
        operation=operation,
        saves=saves,
        load=load,
        nothing=nothing,
    )


async def cleanup(task):
    if not task.done():
        task.cancel()
    _, pending = await asyncio.wait((task,), timeout=2)
    assert not pending, "Controlled launch task survived test cleanup"
    with contextlib.suppress(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
@pytest.mark.parametrize("boundary", ["load", "announce"])
@pytest.mark.parametrize(
    ("delivery", "marked_sigint"),
    [
        ("propagated", False),
        ("consumed", False),
        ("consumed", True),
        ("wait_for_completion", False),
    ],
)
async def test_startup_cancellation_reaches_owned_cleanup(
    monkeypatch, isolated_launcher, boundary, delivery, marked_sigint
):
    case = isolated_launcher
    launcher = case.launcher
    waiting = asyncio.Event()
    reply = asyncio.get_running_loop().create_future()

    async def controlled_await(*args, **kwargs):
        waiting.set()
        if delivery == "wait_for_completion":
            # 3.11 can return a completed result instead of pending cancellation.
            await asyncio.wait_for(reply, timeout=60)
        else:
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                if delivery == "propagated":
                    raise

    if boundary == "load":

        async def load(*args):
            await case.load()
            await controlled_await()

        monkeypatch.setattr(launcher, "_load_core_systems", load)
    else:
        # Keep the actual announcement, including its awaited kernel enqueue.
        launcher.kernel_loop = SimpleNamespace(
            get_status=lambda: {"cycle_count": 0},
            add_task=controlled_await,
            shutdown=case.nothing,
        )

    task = asyncio.create_task(launcher.launch_full_os({"quiet": True, "mode": "test"}))
    try:
        await asyncio.wait_for(waiting.wait(), timeout=2)
        if delivery == "wait_for_completion":
            reply.set_result(None)
        task.cancel()
        if marked_sigint:
            launcher._orderly_cli_sigint_task = task
        await asyncio.wait((task,), timeout=0.5)
        state = {
            "boundary": boundary,
            "delivery": delivery,
            "task_done": task.done(),
            "cancelling": task.cancelling(),
            "operation_entered": case.operation.is_set(),
            "running": launcher.running,
            "owned_system_stopped": case.stopped.is_set(),
            "checkpoint_intents": case.saves,
        }
        assert task.done(), state
        assert task.cancelled(), state
        assert case.stopped.is_set(), state
        assert not case.operation.is_set(), state
        assert not launcher.running, state
        assert case.saves == [False], state
    finally:
        await cleanup(task)


@pytest.mark.asyncio
async def test_normal_boot_keeps_orderly_sigint_checkpoint_intent(isolated_launcher):
    case = isolated_launcher
    launcher = case.launcher
    task = asyncio.create_task(launcher.launch_full_os({"quiet": True, "mode": "test"}))
    try:
        await asyncio.wait_for(case.operation.wait(), timeout=2)
        assert launcher.running
        assert not case.stopped.is_set()
        task.cancel()
        launcher._orderly_cli_sigint_task = task
        await asyncio.wait((task,), timeout=2)
        assert task.done()
        await task
        assert case.stopped.is_set()
        assert not launcher.running
        assert case.saves == [True, False]
    finally:
        await cleanup(task)

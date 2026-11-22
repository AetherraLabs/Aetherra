"""Startup interruption must release the launcher's owned resources."""

# Standard library imports
import asyncio
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from Aetherra.homeostasis.homeostasis_integration import HomeostasisWatchdog
from aetherra_os_launcher import AetherraOSLauncher


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [False, True], ids=["cancelled", "failed"])
async def test_interrupted_boot_closes_started_system(monkeypatch, failure):
    started = asyncio.Event()
    server = await asyncio.start_server(lambda r, w: w.close(), "127.0.0.1", 0)

    class DormantOrchestrator:
        running = False

    orchestrator = DormantOrchestrator()
    watchdog = HomeostasisWatchdog(orchestrator)
    watchdog.start()
    for _ in range(100):
        if watchdog.loop is not None and watchdog.loop.is_running():
            break
        await asyncio.sleep(0.01)

    async def shutdown():
        watchdog.stop()
        server.close()
        await server.wait_closed()

    async def nothing(*args):
        pass

    launcher = AetherraOSLauncher()

    async def load(*args):
        launcher.systems["started-system"] = SimpleNamespace(shutdown=shutdown)
        started.set()
        if failure:
            raise RuntimeError("startup interrupted")
        await asyncio.Future()

    # Isolate external boot setup; keep the real launch/cancellation/shutdown path.
    monkeypatch.setattr(launcher, "_emit_boot_presence", nothing)
    monkeypatch.setattr(launcher, "_initialize_service_registry", nothing)
    monkeypatch.setattr(launcher, "_update_boot_phase", lambda **kwargs: None)
    monkeypatch.setattr(launcher, "_load_core_systems", load)
    task = asyncio.create_task(launcher.launch_full_os({"quiet": True}))
    try:
        await asyncio.wait_for(started.wait(), 2)
        if not failure:
            task.cancel()
        with pytest.raises(RuntimeError if failure else asyncio.CancelledError):
            await task
        assert not server.is_serving(), "interrupted boot left a started system alive"
        assert not watchdog.thread.is_alive(), "startup left watchdog alive"
    finally:
        await shutdown()
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

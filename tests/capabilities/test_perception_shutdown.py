"""Log followers must release their child process even when no new log arrives."""

# Standard library imports
import asyncio
import platform
import subprocess
import sys
import threading
import time

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness.core.think_stream import ThinkStream
from Aetherra.perception_bus.adapters import linux
from Aetherra.perception_bus.adapters.linux import LinuxJournalAdapter
from Aetherra.perception_bus.bus import PerceptionBus
from aetherra_os_launcher import AetherraOSLauncher
from aetherra_service_registry import shutdown_service_registry


@pytest.mark.parametrize(
    ("stubborn", "journal_fails"),
    [(False, False), (True, False), (False, True)],
    ids=["quiet", "ignores-terminate", "journal-fallback"],
)
def test_journal_stop_reaps_idle_follower(monkeypatch, stubborn, journal_fails):
    if stubborn and sys.platform == "win32":
        pytest.skip("Windows terminate does not deliver SIGTERM")
    real_popen = subprocess.Popen
    children = []
    monkeypatch.setattr(linux.shutil, "which", lambda name: "/usr/bin/journalctl")
    ready = threading.Event()
    bus = PerceptionBus()

    def record(event):
        if event.payload.get("line") == "ready":
            ready.set()

    bus.subscribe(record)

    def spawn(_command, **kwargs):
        # Replace only the host telemetry source; use a real idle child and pipe.
        code = (
            "import signal,time; "
            + ("signal.signal(signal.SIGTERM, signal.SIG_IGN); " if stubborn else "")
            + "print('ready', flush=True); time.sleep(60)"
        )
        if journal_fails and _command[0] == "journalctl":
            code = "raise SystemExit(1)"
        child = real_popen([sys.executable, "-c", code], **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(subprocess, "Popen", spawn)
    adapter = LinuxJournalAdapter(bus)
    before = set(threading.enumerate())
    try:
        adapter.start()
        assert ready.wait(5), "follower did not deliver its initial log"
        started = time.monotonic()
        adapter.stop()
        assert time.monotonic() - started < 6
        assert children[-1].poll() is not None, "stop left the idle follower alive"
        assert not [
            t
            for t in threading.enumerate()
            if t not in before and t.name == adapter.name
        ], "stop left the pipe reader alive"
        adapter.stop()  # Repeated teardown must be safe.
    finally:
        adapter.is_running = False
        for child in children:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=5)
        for thread in set(threading.enumerate()) - before:
            if thread.name == adapter.name:
                thread.join(timeout=5)


@pytest.mark.asyncio
async def test_launcher_stops_its_perception_follower(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    # Keep the journal follower real; other host sensors and HTTP are external.
    for sensor in (
        linux.LinuxProcAdapter,
        linux.LinuxDiskAdapter,
        linux.LinuxFSAdapter,
        linux.LinuxServiceAdapter,
    ):
        monkeypatch.setattr(sensor, "start", lambda self: None)
    monkeypatch.setattr(ThinkStream, "register_hub_api", lambda *args: None)
    real_popen = subprocess.Popen
    children = []

    def spawn(_command, **kwargs):
        child = real_popen(
            [sys.executable, "-c", "import time; time.sleep(60)"], **kwargs
        )
        children.append(child)
        return child

    monkeypatch.setattr(subprocess, "Popen", spawn)
    launcher = AetherraOSLauncher()
    try:
        await launcher._start_consciousness_core()
        for _ in range(100):
            if children:
                break
            await asyncio.sleep(0.01)
        assert children
        assert children[0].poll() is None
        await launcher._graceful_shutdown()
        assert children[0].poll() is not None, "launcher lost ownership of its follower"
        assert not [
            t
            for t in asyncio.all_tasks()
            if t.get_coro().__name__ == "_consciousness_tick_loop"
        ]
    finally:
        await launcher._graceful_shutdown()
        await shutdown_service_registry()
        for child in children:
            if child.poll() is None:
                child.kill()
            child.wait(timeout=5)

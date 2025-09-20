def test_pytest_discovery_sanity():
    assert 1 + 1 == 2


# Standard library imports
import asyncio
import time

# Third party imports
import pytest

# Aetherra imports
from aetherra_kernel_loop import AetherraKernelLoop


@pytest.mark.asyncio
async def test_passive_heartbeat_interval_respect(monkeypatch):
    """
    Verifies that passive heartbeat loop triggers expected heartbeat count with short interval.
    """
    # Setup kernel loop with short interval
    kernel = AetherraKernelLoop()
    kernel.running = True
    interval = 0.2  # 200ms interval for fast test
    heartbeats = []

    # Mock service registry
    class DummyRegistry:
        def __init__(self):
            self.services = ["memory_system", "plugin_manager"]
            self.meta = {svc: {"last_heartbeat": 0} for svc in self.services}

        def list_services(self):
            return self.meta

        def is_self_heartbeating(self, svc):
            return False

        async def update_heartbeat(self, svc):
            heartbeats.append((svc, time.time()))
            self.meta[svc]["last_heartbeat"] = time.time()

    kernel.service_registry = DummyRegistry()

    # Patch interval via environment and passive_services
    monkeypatch.setenv("AETHERRA_PASSIVE_HEARTBEAT_SEC", str(interval))
    monkeypatch.setenv("AETHERRA_PASSIVE_HEARTBEAT_ALLOW_FLOOR", "1")
    monkeypatch.setattr(
        kernel, "_get_passive_services", lambda: ["memory_system", "plugin_manager"]
    )

    # Run loop for a short duration
    async def run_loop():
        await asyncio.wait_for(kernel._passive_services_heartbeat_loop(), timeout=1.0)

    # Stop after 1 second
    async def stopper():
        await asyncio.sleep(1)
        kernel.running = False

    await asyncio.gather(run_loop(), stopper())

    # Expect at least 4 heartbeats per service (1s / 0.2s)
    counts = dict.fromkeys(["memory_system", "plugin_manager"], 0)
    for svc, _ in heartbeats:
        counts[svc] += 1
    for svc in counts:
        assert counts[svc] >= 4, f"Service {svc} heartbeat count too low: {counts[svc]}"

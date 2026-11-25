"""Homeostasis sampling must leave governed lifecycle updates responsive."""

# Standard library imports
import asyncio
import json
import threading
from types import SimpleNamespace

# Third party imports
import psutil
import pytest

# Aetherra imports
from Aetherra.homeostasis.homeostasis_integration import (
    ContinuousValidator,
    SystemFeedback,
)
from aetherra_service_registry import AetherraServiceRegistry, ServiceStatus


@pytest.mark.parametrize("collector", ["feedback", "validation"])
def test_cpu_sampling_does_not_block_governed_status(monkeypatch, tmp_path, collector):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    entered = threading.Event()
    release = threading.Event()

    def sample_cpu(*, interval):
        assert interval == 1  # Preserve the existing measurement window.
        entered.set()
        release.wait(5)  # Bounded safety net for the old blocking implementation.
        return 42.25

    monkeypatch.setattr(psutil, "cpu_percent", sample_cpu)
    monkeypatch.setattr(
        psutil, "virtual_memory", lambda: SimpleNamespace(percent=30, available=1024)
    )
    monkeypatch.setattr(psutil, "disk_usage", lambda _: SimpleNamespace(percent=20))
    orchestrator = SimpleNamespace(
        supervisor=None, metrics=None, controller=None, feedback_system=None
    )
    source = (
        SystemFeedback(orchestrator)._collect_os_feedback
        if collector == "feedback"
        else ContinuousValidator(orchestrator)._collect_validation_metrics
    )

    async def exercise():
        registry = AetherraServiceRegistry()
        owner = object()
        assert await registry.register_service("consciousness_core", owner)
        collecting = asyncio.create_task(source())
        try:
            assert await asyncio.to_thread(entered.wait, 2)
            applied = await registry.update_service_status(
                "consciousness_core",
                ServiceStatus.HEALTHY,
                expected_instance=owner,
                nonblocking_preflight=True,
                preflight_timeout=1,
            )
            assert applied is True
            assert not collecting.done(), "CPU sampler blocked the event loop"
        finally:
            release.set()
            result = await collecting
        metrics = result["metrics"] if collector == "feedback" else result["os_metrics"]
        key = "cpu_usage" if collector == "feedback" else "cpu_percent"
        assert metrics[key] == 42.25

    asyncio.run(exercise())
    entries = [
        json.loads(line)
        for line in (tmp_path / ".aetherra/security/audit.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert any(
        entry.get("details", {}).get("intent", {}).get("action")
        == "service_registry.status_update"
        and entry["details"]["decision"]["status"] == "allow"
        for entry in entries
    )

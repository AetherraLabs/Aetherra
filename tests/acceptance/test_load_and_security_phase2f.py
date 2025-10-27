import time

import pytest

from Aetherra.homeostasis.homeostasis_integration import DLQMonitor
from Aetherra.homeostasis.self_incorporation_security import (
    SelfIncorporationSecurity,
)
from Aetherra.security import capabilities as caps

# ---- DLQ behavior under load ----


class _DummyKernel:
    def __init__(self, items: list[dict]):
        self._items = list(items)

    async def get_dlq_items(self, limit: int = 100) -> list[dict]:
        return self._items[:limit]


class _DummyActuators:
    def __init__(self):
        self.disabled: list[str] = []

    async def disable_actuator(self, action_type: str):
        self.disabled.append(action_type)


@pytest.mark.asyncio
async def test_dlq_monitor_quarantines_actuator_on_high_failure_rate():
    # Simulate many failures of the same actuator type in DLQ with proper shape
    now = time.time()
    items = []
    for _ in range(7):
        items.append(
            {
                "type": "actuator_action",
                "ts": now,
                "reason": "timeout",
                "trace_id": "t-123",
                "data": {
                    "action_type": "restart_component",
                    "target_service": "X",
                },
            }
        )

    kernel = _DummyKernel(items)
    actuators = _DummyActuators()

    mon = DLQMonitor(kernel_loop=kernel, actuators=actuators, poll_interval=1)

    # Run a single poll+analyze cycle
    await mon._poll_and_analyze_dlq()  # private but acceptable for acceptance test

    # Expect the actuator to be quarantined/disabled due to high failure rate
    assert "restart_component" in actuators.disabled

    metrics = mon.get_metrics()
    assert metrics["dlq_count"] == len(items)
    assert any("timeout" in r for r in metrics.get("top_failure_reasons", {}))


# ---- Security acceptance: strict mode & capability grants ----


@pytest.mark.asyncio
async def test_security_capability_grant_required_strict_mode(monkeypatch):
    # Enable strict mode
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")

    # Force capability check to deny
    monkeypatch.setattr(caps, "has_capability", lambda requester, cap: False)

    sec = SelfIncorporationSecurity(trust_mode="strict")
    ok = await sec.check_capabilities("plugin:demo", ["network:webhook"])

    assert ok is False, "Missing capability should be denied in strict mode"

    # Clean up env
    monkeypatch.delenv("AETHERRA_PROFILE", raising=False)


@pytest.mark.asyncio
async def test_security_policy_drift_detection_critical(tmp_path):
    sec = SelfIncorporationSecurity(trust_mode="standard")

    # Create a dummy file path to anchor the drift cache key
    test_file = tmp_path / "demo_module.py"
    test_file.write_text("print('hi')", encoding="utf-8")

    # First record: baseline risk 0.1
    first = await sec.detect_policy_drift(test_file, 0.1)
    assert first.approved is True
    assert first.reason in ("no_drift", "drift_check_failed")

    # Second with large drift: from 0.1 to 0.9 (delta 0.8 > 0.3 threshold)
    second = await sec.detect_policy_drift(test_file, 0.9)
    assert second.approved is False
    assert second.reason == "critical_policy_drift"

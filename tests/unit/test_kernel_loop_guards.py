# Standard library imports
import importlib
from typing import Any


def test_backpressure_guard_detects_violations(monkeypatch: Any) -> None:
    # Force production profile for guard evaluation
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # Re-import to ensure env picked up only via instance methods
    kl = importlib.import_module("aetherra_kernel_loop").AetherraKernelLoop()
    # Configure unsafe values
    kl.queue_limits = {"high_priority": 0, "normal_priority": 0, "background": 0}
    kl.dlq_enabled = False
    kl.plugin_invoke_timeout_sec = 61.0
    kl.plugin_cb_threshold = 6
    kl.plugin_max_concurrency = 0

    passed, violations = kl._evaluate_backpressure_guard()
    assert passed is False
    # Verify key violations are present
    assert any(v.startswith("unbounded_queue_") for v in violations)
    assert "dlq_disabled" in violations
    assert "plugin_timeout_high" in violations
    assert "plugin_cb_threshold_high" in violations
    assert "plugin_max_concurrency_unbounded" in violations


def test_ensure_task_envelope_sets_defaults(monkeypatch: Any) -> None:
    kl = importlib.import_module("aetherra_kernel_loop").AetherraKernelLoop()
    # Set a low default TTL to exercise deadline path
    kl.default_task_ttl_sec = 5
    env = kl._ensure_task_envelope({"type": "demo", "data": {}})
    assert isinstance(env, dict)
    assert env.get("trace_id")
    assert env.get("enqueued_ts")
    assert env.get("deadline_ts") == env["enqueued_ts"] + 5

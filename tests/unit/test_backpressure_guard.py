import pytest  # noqa: F401  (kept for potential future extension)

from aetherra_kernel_loop import AetherraKernelLoop


def test_backpressure_guard_fails_with_unbounded_in_prod(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # Ensure queues unbounded and dlq disabled
    monkeypatch.delenv("AETHERRA_KERNEL_QSIZE_HIGH", raising=False)
    monkeypatch.delenv("AETHERRA_KERNEL_QSIZE_NORMAL", raising=False)
    monkeypatch.delenv("AETHERRA_KERNEL_QSIZE_BACKGROUND", raising=False)
    monkeypatch.setenv("AETHERRA_KERNEL_DLQ", "0")
    # Force plugin timeout high and concurrency unlimited
    monkeypatch.setenv("AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC", "90")
    monkeypatch.setenv("AETHERRA_PLUGIN_MAX_CONCURRENCY", "0")
    kl = AetherraKernelLoop()
    # Production defaults will have applied bounded queues; force them unbounded manually to simulate misconfiguration
    kl.queue_limits["high_priority"] = 0
    kl.queue_limits["normal_priority"] = 0
    kl.queue_limits["background"] = 0
    passed, violations = kl._evaluate_backpressure_guard()  # noqa: SLF001
    assert not passed
    assert any(v.startswith("unbounded_queue") for v in violations)


def test_backpressure_guard_passes_with_defaults(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_KERNEL_QSIZE_HIGH", "100")
    monkeypatch.setenv("AETHERRA_KERNEL_QSIZE_NORMAL", "500")
    monkeypatch.setenv("AETHERRA_KERNEL_QSIZE_BACKGROUND", "1000")
    monkeypatch.setenv("AETHERRA_KERNEL_DLQ", "1")
    monkeypatch.setenv("AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC", "20")
    monkeypatch.setenv("AETHERRA_PLUGIN_CB_THRESHOLD", "3")
    monkeypatch.setenv("AETHERRA_PLUGIN_MAX_CONCURRENCY", "1")
    kl = AetherraKernelLoop()
    passed, violations = kl._evaluate_backpressure_guard()  # noqa: SLF001
    assert passed
    assert violations == []

import asyncio
import json

import pytest

from aetherra_kernel_loop import AetherraKernelLoop


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def _audit_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_direct_kernel_pause_writes_guardian_audit(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    kernel = AetherraKernelLoop()

    kernel.pause()

    assert kernel.paused is True
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "kernel.pause"
    assert entry["details"]["intent"]["metadata"] == {"operation": "pause"}


def test_direct_kernel_resume_denial_preserves_pause_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-kernel-client",
        strict=True,
    )
    kernel = AetherraKernelLoop()
    kernel.paused = True

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        kernel.resume()

    assert kernel.paused is True
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "kernel.resume"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_direct_kernel_drain_denial_preserves_queue(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-kernel-client",
        strict=True,
    )
    kernel = AetherraKernelLoop()
    kernel.normal_priority_queue.put_nowait({"type": "work", "trace_id": "T-1"})

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(kernel.drain_queue("normal_priority", mode="drop"))

    assert kernel.normal_priority_queue.qsize() == 1
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "kernel.drain_queue"
    assert entry["details"]["intent"]["metadata"] == {
        "queue": "normal_priority",
        "mode": "drop",
    }


def test_direct_kernel_queue_limit_denial_preserves_limits(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-kernel-client",
        strict=True,
    )
    kernel = AetherraKernelLoop()
    before = dict(kernel.queue_limits)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        kernel.set_queue_limits({"normal_priority": 5})

    assert kernel.queue_limits == before
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "kernel.set_queue_limits"
    assert entry["details"]["intent"]["metadata"]["limit_keys"] == "***REDACTED***"


def test_direct_kernel_shutdown_denial_preserves_running_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-kernel-client",
        strict=True,
    )
    kernel = AetherraKernelLoop()
    kernel.running = True

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(kernel.shutdown())

    assert kernel.running is True
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "kernel.shutdown"
    assert entry["details"]["decision"]["reason"] == "missing_capability"

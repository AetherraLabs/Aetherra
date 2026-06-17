import asyncio
import json

import pytest

from Aetherra.homeostasis.homeostasis_core import ControllerMode
from Aetherra.homeostasis.homeostasis_integration import HomeostasisOrchestrator


class _Controller:
    def __init__(self):
        self.mode = ControllerMode.OBSERVE_ONLY
        self.emergency_stopped = False
        self.reset_count = 0

    def set_mode(self, mode):
        self.mode = mode

    def emergency_stop(self):
        self.emergency_stopped = True

    def reset_emergency_stop(self):
        self.emergency_stopped = False
        self.reset_count += 1


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


def _orchestrator_with_controller():
    orchestrator = HomeostasisOrchestrator()
    orchestrator.controller = _Controller()
    return orchestrator


def test_direct_controller_mode_change_is_guardian_audited(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    orchestrator = _orchestrator_with_controller()

    asyncio.run(
        orchestrator.set_controller_mode(
            ControllerMode.ACTIVE_LIMITED,
            "operator requested limited active mode",
        )
    )

    assert orchestrator.controller.mode is ControllerMode.ACTIVE_LIMITED
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "homeostasis.set_mode"
    assert entry["details"]["intent"]["metadata"] == {
        "mode": "active_limited",
        "reason_present": True,
    }


def test_direct_controller_mode_denial_preserves_mode(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-homeostasis-client",
        strict=True,
    )
    orchestrator = _orchestrator_with_controller()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            orchestrator.set_controller_mode(
                ControllerMode.ACTIVE,
                "attempt direct mode escalation",
            )
        )

    assert orchestrator.controller.mode is ControllerMode.OBSERVE_ONLY
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "homeostasis.set_mode"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_direct_emergency_denial_preserves_controller_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-homeostasis-client",
        strict=True,
    )
    orchestrator = _orchestrator_with_controller()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(orchestrator.emergency_stop("attempt direct emergency stop"))

    assert orchestrator.controller.emergency_stopped is False
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "homeostasis.emergency_stop"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_direct_reset_emergency_requires_guardian(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-homeostasis-client",
        strict=True,
    )
    orchestrator = _orchestrator_with_controller()
    orchestrator.controller.emergency_stopped = True

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(orchestrator.reset_emergency_stop())

    assert orchestrator.controller.emergency_stopped is True
    assert orchestrator.controller.reset_count == 0
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "homeostasis.reset_emergency"
    assert entry["details"]["decision"]["reason"] == "missing_capability"

import json
import time

import pytest

from Aetherra.homeostasis.homeostasis_core import (
    ActionPriority,
    ControlAction,
    ControllerMode,
    HomeostasisController,
)


@pytest.fixture
def guardian_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    return tmp_path


def _audit_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _controller():
    controller = HomeostasisController()
    controller.mode = ControllerMode.ACTIVE
    return controller


def _action(**overrides):
    data = {
        "action_type": "increase_plugin_timeouts",
        "target_service": "plugin_system",
        "parameters": {"token": "do-not-audit-this-value"},
        "priority": ActionPriority.MEDIUM,
        "timestamp": time.time(),
        "controller_name": "plugin_success_control",
        "reason": "plugin success below target",
    }
    data.update(overrides)
    return ControlAction(**data)


def test_controller_policy_gate_audits_autonomous_action_without_parameter_values(
    guardian_env,
):
    controller = _controller()
    action = _action()

    allowed = controller._apply_policy_constraints([action])
    entries = _audit_entries(guardian_env)

    assert allowed == [action]
    assert entries[-1]["details"]["intent"]["action"] == "homeostasis.plan_action"
    assert "homeostasis_actuation" in entries[-1]["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])


def test_controller_policy_gate_blocks_explicit_requester_without_capability(
    monkeypatch, guardian_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    controller = _controller()
    action = _action()
    action.requester = "untrusted_controller"

    allowed = controller._apply_policy_constraints([action])
    entries = _audit_entries(guardian_env)

    assert allowed == []
    assert controller.stats["actions_blocked"] == 1
    assert controller.policy_violations[-1]["type"] == "guardian_denied"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_controller_policy_gate_contains_security_policy_action(guardian_env):
    controller = _controller()
    action = _action(
        action_type="relax_policy",
        target_service="security_policy",
        parameters={"mode": "permissive"},
    )

    allowed = controller._apply_policy_constraints([action])
    entries = _audit_entries(guardian_env)

    assert allowed == []
    assert controller.policy_violations[-1]["type"] == "guardian_denied"
    assert entries[-1]["details"]["decision"]["status"] == "contain"

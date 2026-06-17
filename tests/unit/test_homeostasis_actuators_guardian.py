import asyncio
import json
import time

import pytest

from Aetherra.homeostasis.homeostasis_actuators import (
    ActuatorResult,
    HomeostasisActuators,
)
from Aetherra.homeostasis.homeostasis_core import ActionPriority, ControlAction


class _AuditLayer:
    def __init__(self):
        self.started = 0
        self.completed = 0

    async def start_action_trace(self, **kwargs):
        self.started += 1
        return "trace-1"

    async def complete_action_trace(self, **kwargs):
        self.completed += 1


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


def _action(**overrides):
    data = {
        "action_type": "increase_plugin_timeouts",
        "target_service": "plugin_service",
        "parameters": {"multiplier": 1.5},
        "priority": ActionPriority.MEDIUM,
        "timestamp": time.time(),
        "controller_name": "latency_controller",
        "reason": "reduce task latency",
    }
    data.update(overrides)
    return ControlAction(**data)


def test_direct_actuator_execution_writes_guardian_audit_without_parameter_values(
    monkeypatch, guardian_env
):
    audit_layer = _AuditLayer()
    actuators = HomeostasisActuators()
    action = _action(parameters={"token": "do-not-audit-this-value"})

    async def adjust_plugin_timeouts(target, parameters):
        return ActuatorResult(
            success=True,
            message="timeouts adjusted",
            rollback_data={"original_timeouts": {"plugin_service": 30.0}},
        )

    monkeypatch.setattr(
        "Aetherra.homeostasis.homeostasis_actuators.get_audit_layer",
        lambda: audit_layer,
    )
    monkeypatch.setattr(actuators, "adjust_plugin_timeouts", adjust_plugin_timeouts)

    result = asyncio.run(actuators.execute_action(action))
    entries = _audit_entries(guardian_env)

    assert result is True
    assert audit_layer.started == 1
    assert audit_layer.completed == 1
    assert len(actuators.action_history) == 1
    assert len(actuators.rollback_stack) == 1
    assert entries[-1]["details"]["intent"]["action"] == "homeostasis.actuate"
    assert "homeostasis_actuation" in entries[-1]["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])


def test_direct_actuator_execution_blocks_explicit_requester_without_capability(
    monkeypatch, guardian_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    audit_layer = _AuditLayer()
    actuators = HomeostasisActuators()
    action = _action()
    action.requester = "untrusted_controller"

    monkeypatch.setattr(
        "Aetherra.homeostasis.homeostasis_actuators.get_audit_layer",
        lambda: audit_layer,
    )

    with pytest.raises(PermissionError, match="missing_capability"):
        asyncio.run(actuators.execute_action(action))

    assert audit_layer.started == 0
    assert actuators.action_history == []
    assert actuators.rollback_stack == []


def test_direct_actuator_rollback_writes_guardian_audit(guardian_env):
    actuators = HomeostasisActuators()
    actuators.rollback_stack.append(
        {
            "action_type": "increase_plugin_timeouts",
            "target": "plugin_service",
            "parameters": {},
            "rollback_data": {"original_timeouts": {"plugin_service": 30.0}},
        }
    )

    async def rollback_plugin_timeouts(rollback_data):
        return ActuatorResult(success=True, message="timeouts restored")

    actuators._rollback_plugin_timeouts = rollback_plugin_timeouts

    result = asyncio.run(actuators.rollback_last_action())
    entries = _audit_entries(guardian_env)

    assert result.success is True
    assert actuators.rollback_stack == []
    assert entries[-1]["details"]["intent"]["action"] == "homeostasis.rollback"


def test_direct_actuator_rollback_denial_keeps_stack(monkeypatch, guardian_env):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    actuators = HomeostasisActuators()
    actuators.rollback_stack.append(
        {
            "action_type": "increase_plugin_timeouts",
            "target": "plugin_service",
            "parameters": {},
            "rollback_data": {"original_timeouts": {"plugin_service": 30.0}},
        }
    )

    with pytest.raises(PermissionError, match="missing_capability"):
        actuators._guardian_preflight_rollback("untrusted_controller")

    assert len(actuators.rollback_stack) == 1

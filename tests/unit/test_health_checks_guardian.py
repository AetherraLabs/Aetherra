import json

import pytest

from Aetherra.consciousness.core.types import LedgerEntry
from Aetherra.consciousness.health_checks import HealthCheck, HealthCheckEngine
from Aetherra.consciousness.self_trust import SelfTrust
from Aetherra.safety_envelope.policy_engine import PolicyEngine


class FakeActuator:
    def __init__(self):
        self.executed_plans = []

    def execute(self, plan):
        self.executed_plans.append(plan)
        return LedgerEntry(
            intent=plan.intent,
            plan=plan,
            policy_decision="allowed",
            actions=[{"step": step.id} for step in plan.steps],
            success=True,
        )


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


def _write_policy(tmp_path, requester, capabilities):
    policy_dir = tmp_path / "policy"
    policy_dir.mkdir(parents=True, exist_ok=True)
    (policy_dir / "capabilities.json").write_text(
        json.dumps({"allow": {requester: list(capabilities)}}),
        encoding="utf-8",
    )


def _audit_text(root):
    return (root / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _audit_entries(root):
    return [
        json.loads(line)
        for line in _audit_text(root).splitlines()
        if line.strip()
    ]


def _remediation_check(*, name="private_chat_system", verified=True):
    calls = {"probe": 0}

    def probe():
        calls["probe"] += 1
        return {"ok": calls["probe"] > 1 and verified}

    return HealthCheck(
        name=name,
        question="Should private chat recover?",
        probe=probe,
        pass_if=lambda data: bool(data.get("ok")),
        remediate=[("system.rotate_logs", {"path": "private.log"})],
        verify=lambda data: bool(data.get("ok")),
        rollback=[],
        risk="low",
    )


def test_health_check_remediation_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    fake_actuator = FakeActuator()
    engine = HealthCheckEngine(PolicyEngine("autopilot"))
    engine.actuator = fake_actuator

    result = engine.run_check(_remediation_check())

    assert result["status"] == "repaired"
    assert len(fake_actuator.executed_plans) == 1
    ledger_text = _audit_text(tmp_path)
    assert "private_chat_system" not in ledger_text
    assert "private.log" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.health_check_remediate"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "run_check.remediate"
    assert metadata["step_count"] == 1
    assert metadata["step_capabilities"] == ["system.rotate_logs"]


def test_health_check_remediation_denial_skips_actuator_and_result_mutation(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-health-client",
        strict=True,
    )
    fake_actuator = FakeActuator()
    engine = HealthCheckEngine(PolicyEngine("autopilot"))
    engine.actuator = fake_actuator

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        engine.run_check(_remediation_check())

    assert fake_actuator.executed_plans == []
    assert engine.last_results == {}
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.health_check_remediate"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_health_check_self_trust_denial_skips_trust_observation(
    monkeypatch, tmp_path
):
    requester = "external-health-remediator"
    _guardian_env(monkeypatch, tmp_path, requester=requester, strict=True)
    _write_policy(
        tmp_path,
        requester,
        {
            "autonomy:execute",
            "consciousness:act",
            "system.rotate_logs",
        },
    )
    fake_actuator = FakeActuator()
    self_trust = SelfTrust()
    engine = HealthCheckEngine(
        PolicyEngine("autopilot"),
        self_trust=self_trust,
    )
    engine.actuator = fake_actuator

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        engine.run_check(_remediation_check(name="chat_system"))

    assert len(fake_actuator.executed_plans) == 1
    assert self_trust.subsystems == {}
    assert engine.last_results == {}
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.health_check_self_trust_update"
    )
    assert entry["details"]["intent"]["metadata"]["operation"] == (
        "run_check.self_trust_update"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"

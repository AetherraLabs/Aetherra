import json

import pytest

from Aetherra.consciousness.core import config as core_config
from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
from Aetherra.consciousness.core.types import Event, Focus, Intent, LedgerEntry


class StubBus:
    def drain(self, max_items=256):
        return []


class FakeSafetyEnvelope:
    def __init__(self):
        self.executed_plans = []
        self.policy = None

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


def _intent():
    return Intent(
        why="private service instability reason",
        goal="Stabilize private-service-name",
        expected_gain=0.7,
        risk="medium",
        cost_estimate="3m",
        plan=["restart_service"],
        rollback=["restore_config"],
        deadline_s=300,
        priority=0.8,
    )


def test_consciousness_autonomy_plan_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    safety = FakeSafetyEnvelope()
    core = ConsciousnessCore(StubBus(), safety_envelope=safety, memory_engine=None)
    intent = _intent()
    core.active_intents.append(intent)

    core._maybe_act()

    assert len(safety.executed_plans) == 1
    assert core.active_intents == []
    ledger_text = _audit_text(tmp_path)
    assert "private service instability reason" not in ledger_text
    assert "private-service-name" not in ledger_text
    entries = _audit_entries(tmp_path)
    entry = next(
        item
        for item in entries
        if item["details"]["intent"]["action"]
        == "consciousness.autonomy_plan_execute"
    )
    assert entry["details"]["intent"]["action"] == "consciousness.autonomy_plan_execute"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["intent_risk"] == "medium"
    assert metadata["plan_step_count"] == 1
    assert metadata["rollback_step_count"] == 1


def test_consciousness_autonomy_plan_denial_skips_execution_and_intent_removal(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-autonomy-client",
        strict=True,
    )
    safety = FakeSafetyEnvelope()
    core = ConsciousnessCore(StubBus(), safety_envelope=safety, memory_engine=None)
    intent = _intent()
    core.active_intents.append(intent)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        core._maybe_act()

    assert safety.executed_plans == []
    assert core.active_intents == [intent]
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.autonomy_plan_execute"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_consciousness_micro_reflection_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setattr(core_config, "ENABLE_QFAC_PERSISTENCE", False)
    core = ConsciousnessCore(StubBus(), safety_envelope=None, memory_engine=None)
    focus = Focus(
        event=Event(
            type="private.focus.event",
            payload={"secret": "private-payload"},
            source="private-source",
        ),
        resonance=0.9,
        reason="private reason",
    )
    intent = _intent()

    moment = core._reflect_micro([focus], [intent])

    assert core.narrative_thread == [moment]
    ledger_text = _audit_text(tmp_path)
    assert "private.focus.event" not in ledger_text
    assert "Stabilize private-service-name" not in ledger_text
    assert "private service instability reason" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.micro_reflection_update"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["reflection_kind"] == "micro"
    assert metadata["focus_count"] == 1
    assert metadata["intent_count"] == 1


def test_consciousness_micro_reflection_denial_skips_narrative_append(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-reflection-client",
        strict=True,
    )
    monkeypatch.setattr(core_config, "ENABLE_QFAC_PERSISTENCE", False)
    core = ConsciousnessCore(StubBus(), safety_envelope=None, memory_engine=None)
    focus = Focus(event=Event(type="svc.health", payload={}), resonance=0.9)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        core._reflect_micro([focus], [_intent()])

    assert core.narrative_thread == []
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.micro_reflection_update"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_consciousness_reflection_qfac_persistence_uses_guarded_memory_path(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setattr(core_config, "ENABLE_QFAC_PERSISTENCE", True)
    core = ConsciousnessCore(StubBus(), safety_envelope=None, memory_engine=None)
    focus = Focus(
        event=Event(
            type="private.qfac.focus",
            payload={"secret": "do-not-audit-this-payload"},
            source="private-source",
        ),
        resonance=0.9,
        reason="private reason",
    )

    core._reflect_micro([focus], [_intent()])

    ledger_text = _audit_text(tmp_path)
    actions = [
        entry["details"]["intent"]["action"]
        for entry in _audit_entries(tmp_path)
    ]
    assert "consciousness.micro_reflection_update" in actions
    assert "memory.qfac_store" in actions
    assert "private.qfac.focus" not in ledger_text
    assert "do-not-audit-this-payload" not in ledger_text
    assert "Stabilize private-service-name" not in ledger_text


def test_consciousness_macro_reflection_denial_skips_learning_decay_and_qfac(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-reflection-client",
        strict=True,
    )
    monkeypatch.setattr(core_config, "ENABLE_QFAC_PERSISTENCE", True)
    qfac_calls = []
    monkeypatch.setattr(
        "Aetherra.consciousness.core.consciousness_core.qfac_store",
        lambda **kwargs: qfac_calls.append(kwargs),
    )
    core = ConsciousnessCore(StubBus(), safety_envelope=None, memory_engine=None)
    core.ql.p.curiosity_gain = 0.08
    before_curiosity = core.ql.p.curiosity_gain

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        core._reflect_macro()

    assert core.ql.p.curiosity_gain == before_curiosity
    assert qfac_calls == []
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.macro_reflection_update"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"

import json

import pytest

from Aetherra.guardian import (
    GuardianMode,
    GuardianStatus,
    IntentDeclaration,
    classify_decision_tier,
    create_preauthorization,
    evaluate_intent,
    list_preauthorization_events,
)
from Aetherra.guardian.risk import assess_risk


def _routine_intent(**overrides):
    values = {
        "requester": "lyrixa",
        "subsystem": "status",
        "action": "status.message_publish",
        "target": "local_status_channel",
        "purpose": "Publish bounded local status update",
        "reversible": True,
        "rollback_plan": "publish a corrected status message",
        "evidence": ("status_window:startup",),
    }
    values.update(overrides)
    return IntentDeclaration(**values)


def test_preauthorization_allows_exact_low_risk_routine_intent(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    intent = _routine_intent()
    risk = assess_risk(intent)
    tier = classify_decision_tier(intent, risk)
    grant = create_preauthorization(
        intent,
        risk,
        decision_tier=tier,
        guardian_mode=GuardianMode.ENFORCING,
        max_uses=1,
    )

    decision = evaluate_intent(
        intent,
        preauthorization_id=grant.grant_id,
        capability_checker=lambda requester, capability: False,
    )

    assert decision.status == GuardianStatus.ALLOW_LIMITED
    assert decision.reason == "preauthorized_guardian_grant"
    events = list_preauthorization_events()
    assert [event["event"] for event in events] == ["created", "used"]


def test_preauthorization_does_not_bypass_declared_capabilities(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _routine_intent(capabilities=("event:publish",))
    risk = assess_risk(intent)
    tier = classify_decision_tier(intent, risk)
    grant = create_preauthorization(
        intent,
        risk,
        decision_tier=tier,
        guardian_mode=GuardianMode.ENFORCING,
    )

    decision = evaluate_intent(
        intent,
        preauthorization_id=grant.grant_id,
        capability_checker=lambda requester, capability: False,
    )

    assert decision.status == GuardianStatus.DENY
    assert decision.reason == "missing_capability"


def test_preauthorization_is_single_scope_and_single_use(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _routine_intent()
    risk = assess_risk(intent)
    tier = classify_decision_tier(intent, risk)
    grant = create_preauthorization(
        intent,
        risk,
        decision_tier=tier,
        guardian_mode=GuardianMode.ENFORCING,
        max_uses=1,
    )

    first = evaluate_intent(intent, preauthorization_id=grant.grant_id)
    replay = evaluate_intent(intent, preauthorization_id=grant.grant_id)
    changed_scope = evaluate_intent(
        _routine_intent(target="other_channel"),
        preauthorization_id=grant.grant_id,
    )

    assert first.status == GuardianStatus.ALLOW_LIMITED
    assert replay.reason != "preauthorized_guardian_grant"
    assert changed_scope.reason != "preauthorized_guardian_grant"


def test_preauthorization_rejects_privileged_or_non_reversible_intents(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    privileged = _routine_intent(
        action="plugin.execute",
        subsystem="plugin_manager",
        target="demo",
        capabilities=("plugin:execute",),
    )
    privileged_risk = assess_risk(privileged)

    with pytest.raises(ValueError):
        create_preauthorization(
            privileged,
            privileged_risk,
            decision_tier=classify_decision_tier(privileged, privileged_risk),
            guardian_mode=GuardianMode.ENFORCING,
        )

    non_reversible = _routine_intent(reversible=False, rollback_plan=None)
    non_reversible_risk = assess_risk(non_reversible)
    with pytest.raises(ValueError):
        create_preauthorization(
            non_reversible,
            non_reversible_risk,
            decision_tier=classify_decision_tier(non_reversible, non_reversible_risk),
            guardian_mode=GuardianMode.ENFORCING,
        )


def test_preauthorization_invalidates_on_policy_change(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    policy_path = tmp_path / ".aetherra" / "guardian" / "policy.json"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(json.dumps({"version": 1, "default": "allow"}), encoding="utf-8")
    intent = _routine_intent()
    risk = assess_risk(intent)
    tier = classify_decision_tier(intent, risk)
    grant = create_preauthorization(
        intent,
        risk,
        decision_tier=tier,
        guardian_mode=GuardianMode.ENFORCING,
    )
    policy_path.write_text(json.dumps({"version": 2, "default": "allow"}), encoding="utf-8")

    decision = evaluate_intent(intent, preauthorization_id=grant.grant_id)

    assert decision.reason != "preauthorized_guardian_grant"

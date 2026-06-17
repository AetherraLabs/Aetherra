import json

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent
from Aetherra.guardian.approval import (
    consume_approval,
    create_approval_request,
    list_approval_events,
    list_approval_statuses,
    resolve_approval,
    validate_approval,
)
from Aetherra.guardian.risk import assess_risk


def _intent(**overrides):
    values = {
        "requester": "self_improvement_engine",
        "subsystem": "self_improvement",
        "action": "self.apply_proposal",
        "target": "kernel",
        "purpose": "Apply proposal",
        "capabilities": ("self:modify", "code:modify", "system:reload"),
        "evidence": ("proposal:SI-APPROVAL",),
    }
    values.update(overrides)
    return IntentDeclaration(**values)


def test_approval_must_be_resolved_before_consumption(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent()
    approval = create_approval_request(intent, assess_risk(intent))

    result = validate_approval(approval.request_id, intent)

    assert result.valid is False
    assert result.reason == "approval_pending"


def test_approved_intent_can_be_consumed_once(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent()
    approval = create_approval_request(intent, assess_risk(intent))
    resolve_approval(approval.request_id, approved=True, approver="user")

    first = consume_approval(approval.request_id, intent)
    second = consume_approval(approval.request_id, intent)

    assert first.valid is True
    assert second.valid is False
    assert second.reason == "approval_already_consumed"
    assert list_approval_events()[-1]["event"] == "consumed"


def test_approval_is_bound_to_original_intent(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent(target="kernel")
    approval = create_approval_request(intent, assess_risk(intent))
    resolve_approval(approval.request_id, approved=True, approver="user")

    changed_intent = _intent(target="other-kernel")
    result = consume_approval(approval.request_id, changed_intent)

    assert result.valid is False
    assert result.reason == "approval_intent_mismatch"


def test_evaluate_intent_consumes_valid_approval(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    intent = _intent()
    first_decision = evaluate_intent(
        intent,
        capability_checker=lambda requester, capability: True,
    )
    approval_id = first_decision.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="user")

    approved_decision = evaluate_intent(
        intent,
        approval_id=approval_id,
        capability_checker=lambda requester, capability: True,
    )
    replay_decision = evaluate_intent(
        intent,
        approval_id=approval_id,
        capability_checker=lambda requester, capability: True,
    )

    assert approved_decision.status == GuardianStatus.ALLOW_LIMITED
    assert approved_decision.reason == "approved_with_guardian_approval"
    assert replay_decision.status == GuardianStatus.REQUIRE_APPROVAL


def test_approval_expiration_blocks_resolution_and_consumption(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_TIMEOUT_SEC", "1")
    intent = _intent()
    approval = create_approval_request(intent, assess_risk(intent))

    created = list_approval_events()[0]
    created["expires_at"] = "2000-01-01T00:00:00Z"
    log_path = tmp_path / ".aetherra" / "guardian" / "approvals.jsonl"
    log_path.write_text(json.dumps(created) + "\n", encoding="utf-8")

    resolution = resolve_approval(approval.request_id, approved=True, approver="user")
    validation = validate_approval(approval.request_id, intent)
    statuses = list_approval_statuses()

    assert resolution["state"] == "expired"
    assert validation.valid is False
    assert validation.reason == "approval_expired"
    assert statuses[0]["state"] == "expired"

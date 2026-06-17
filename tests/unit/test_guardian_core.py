import json

from Aetherra.guardian import (
    GuardianDecisionTier,
    GuardianStatus,
    IntentDeclaration,
    RiskLevel,
    classify_decision_tier,
    evaluate_intent,
)
from Aetherra.guardian.approval import list_approval_events
from Aetherra.guardian.containment import list_containment_events
from Aetherra.guardian.risk import assess_risk


def _plugin_intent(**overrides):
    values = {
        "requester": "plugin:demo",
        "subsystem": "plugin_manager",
        "action": "plugin.execute",
        "target": "demo",
        "purpose": "Execute plugin",
        "capabilities": ("execute",),
        "evidence": ("plugin:demo",),
    }
    values.update(overrides)
    return IntentDeclaration(**values)


def test_guardian_allows_safe_plugin_execution_and_audits(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")

    decision = evaluate_intent(
        _plugin_intent(),
        capability_checker=lambda requester, capability: True,
    )

    assert decision.status == GuardianStatus.ALLOW_LIMITED
    assert decision.risk_level == RiskLevel.MEDIUM
    assert decision.audit_id is not None

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert entries[-1]["event_type"] == "guardian_decision"
    assert entries[-1]["details"]["decision"]["status"] == "allow_limited"
    assert entries[-1]["details"]["decision"]["details"]["decision_tier"] == "privileged"


def test_guardian_denies_missing_capability(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")

    decision = evaluate_intent(
        _plugin_intent(),
        capability_checker=lambda requester, capability: False,
    )

    assert decision.status == GuardianStatus.DENY
    assert decision.reason == "missing_capability"


def test_guardian_emergency_mode_contains_non_recovery_action(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "emergency")

    decision = evaluate_intent(
        _plugin_intent(),
        capability_checker=lambda requester, capability: True,
    )

    assert decision.status == GuardianStatus.CONTAIN
    assert decision.reason == "guardian_emergency_mode"
    events = list_containment_events()
    assert events[-1]["reason"] == "guardian_emergency_mode"


def test_guardian_high_risk_action_creates_approval_request(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")

    intent = IntentDeclaration(
        requester="lyrixa",
        subsystem="file_system",
        action="delete",
        target="workspace/old-plan.md",
        purpose="Remove obsolete plan",
        capabilities=("fs:delete",),
        reversible=False,
        evidence=("user_request",),
    )

    decision = evaluate_intent(
        intent,
        capability_checker=lambda requester, capability: True,
    )

    assert decision.status == GuardianStatus.REQUIRE_APPROVAL
    assert decision.details["approval_request_id"].startswith("apr_")
    events = list_approval_events()
    assert events[-1]["request_id"] == decision.details["approval_request_id"]


def test_guardian_high_risk_action_with_rollback_uses_risk_approval_reason(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")

    intent = IntentDeclaration(
        requester="self_improvement_engine",
        subsystem="self_improvement",
        action="self.apply_proposal",
        target="Aetherra/core/runtime.py",
        purpose="Apply reviewed self-improvement proposal",
        capabilities=("self:modify",),
        reversible=True,
        rollback_plan="git restore Aetherra/core/runtime.py",
        evidence=("proposal:SI-1",),
    )

    decision = evaluate_intent(
        intent,
        capability_checker=lambda requester, capability: True,
    )

    assert decision.status == GuardianStatus.REQUIRE_APPROVAL
    assert decision.reason == "risk_requires_approval"
    assert decision.rollback_required is False


def test_guardian_classifies_decision_tiers():
    critical = IntentDeclaration(
        requester="security_admin",
        subsystem="security",
        action="security.policy_update",
        target="Aetherra/security/policy.json",
        purpose="Update Security policy",
        capabilities=("security:modify",),
        reversible=True,
        rollback_plan="restore previous policy",
    )
    privileged = IntentDeclaration(
        requester="network_client",
        subsystem="network",
        action="network.request",
        target="https://example.invalid",
        purpose="Fetch remote metadata",
        capabilities=("network:outbound",),
        reversible=True,
        rollback_plan="discard response",
    )
    routine = IntentDeclaration(
        requester="lyrixa",
        subsystem="consciousness",
        action="consciousness.status_message",
        target="message:broadcast",
        purpose="Publish bounded status message",
        capabilities=("event:publish",),
        reversible=True,
        rollback_plan="publish compensating status",
    )
    observational = IntentDeclaration(
        requester="operator",
        subsystem="guardian",
        action="status",
        target="guardian",
        purpose="Read Guardian status",
    )
    telemetry = IntentDeclaration(
        requester="monitor",
        subsystem="metrics",
        action="metrics.heartbeat",
        target="local_metrics",
        purpose="Update heartbeat counter",
    )

    assert classify_decision_tier(critical, assess_risk(critical)) == GuardianDecisionTier.CRITICAL
    assert (
        classify_decision_tier(privileged, assess_risk(privileged))
        == GuardianDecisionTier.PRIVILEGED
    )
    assert (
        classify_decision_tier(routine, assess_risk(routine))
        == GuardianDecisionTier.ROUTINE_GUARDED
    )
    assert (
        classify_decision_tier(observational, assess_risk(observational))
        == GuardianDecisionTier.OBSERVATIONAL
    )
    assert (
        classify_decision_tier(telemetry, assess_risk(telemetry))
        == GuardianDecisionTier.TELEMETRY_INTERNAL
    )

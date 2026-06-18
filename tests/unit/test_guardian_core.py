import json

from Aetherra.guardian import (
    GuardianDecisionTier,
    GuardianMode,
    GuardianStatus,
    IntentDeclaration,
    RiskLevel,
    classify_decision_tier,
    evaluate_intent,
    guardian_mode,
    guardian_mode_events,
    guardian_mode_status,
    record_outcome,
    set_guardian_mode,
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
    assert decision.audit_id == entries[-1]["hash"]


def test_guardian_records_bounded_outcome_without_raw_payload(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")

    decision = evaluate_intent(
        _plugin_intent(),
        capability_checker=lambda requester, capability: True,
    )

    outcome_id = record_outcome(
        decision.audit_id,
        {
            "status": "completed",
            "summary": "Plugin finished without side effects",
            "duration_ms": 42.5,
            "metrics": {
                "files_changed": 0,
                "result_label": "sensitive internal label",
            },
            "raw_payload": "private execution payload",
        },
    )

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    outcome_entry = entries[-1]
    outcome = outcome_entry["details"]["outcome"]

    assert outcome_id == outcome_entry["hash"]
    assert outcome_entry["event_type"] == "guardian_outcome"
    assert outcome_entry["details"]["decision_audit_id"] == decision.audit_id
    assert outcome["status"] == "completed"
    assert outcome["duration_ms"] == 42.5
    assert outcome["metrics"]["files_changed"] == 0
    assert outcome["metrics"]["result_label"]["sha256"]
    assert "raw_payload" in outcome["omitted_fields"]
    assert "private execution payload" not in audit_path.read_text(encoding="utf-8")


def test_guardian_denies_missing_capability(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")

    decision = evaluate_intent(
        _plugin_intent(),
        capability_checker=lambda requester, capability: False,
    )

    assert decision.status == GuardianStatus.DENY
    assert decision.reason == "missing_capability"


def test_guardian_mode_changes_are_persisted_and_audited(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.delenv("AETHERRA_GUARDIAN_MODE", raising=False)

    result = set_guardian_mode(
        "strict",
        reason="production_hardening",
        changed_by="guardian-admin",
    )

    assert result["mode"] == "strict"
    assert result["previous_mode"] == "enforcing"
    assert result["audit_id"]
    assert guardian_mode() == GuardianMode.STRICT
    assert guardian_mode_status()["state"] == "persisted"

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert entries[-1]["event_type"] == "guardian_mode_changed"
    assert entries[-1]["details"]["mode"] == "strict"


def test_guardian_mode_environment_override_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "emergency")

    result = set_guardian_mode(
        GuardianMode.STRICT,
        reason="persisted fallback",
        changed_by="guardian-admin",
    )

    assert result["mode"] == "strict"
    assert result["env_override_active"] is True
    assert guardian_mode() == GuardianMode.EMERGENCY
    assert guardian_mode_status()["state"] == "env_override"


def test_guardian_mode_metadata_is_sanitized(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.delenv("AETHERRA_GUARDIAN_MODE", raising=False)

    set_guardian_mode(
        "strict",
        reason="operator_requested",
        changed_by="guardian-admin",
        metadata={
            "ticket": "SEC-1234",
            "raw_context": {"private": "value"},
        },
    )

    event = guardian_mode_events()[-1]

    assert event["metadata"]["ticket"]["sha256"]
    assert event["metadata"]["ticket"]["length"] == 8
    assert event["metadata"]["raw_context"] == {"type": "dict"}
    assert "SEC-1234" not in (tmp_path / ".aetherra" / "guardian" / "mode.jsonl").read_text(
        encoding="utf-8"
    )


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

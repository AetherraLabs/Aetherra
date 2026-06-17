import asyncio
import json

import pytest

from Aetherra.homeostasis.alert_intelligence import (
    AlertSeverity,
    AlertStatus,
    IntelligentAlert,
)
from Aetherra.homeostasis.intelligent_alert_manager import (
    AlertEscalationRule,
    AlertNotificationChannel,
    IntelligentAlertManager,
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


def _manager(tmp_path):
    manager = IntelligentAlertManager(db_path=str(tmp_path / "alerts.db"))
    manager.notification_channels = []
    return manager


def _alert(**overrides):
    data = {
        "alert_id": "alert-001",
        "detection_id": "detection-001",
        "title": "Latency alert",
        "description": "do-not-audit-this-value",
        "severity": AlertSeverity.MEDIUM,
        "category": "Performance",
        "explanation": "do-not-audit-this-value",
        "root_cause_hypothesis": "do-not-audit-this-value",
        "remediation_suggestions": ["do-not-audit-this-value"],
        "impact_assessment": "do-not-audit-this-value",
        "triggered_at": "2026-06-15T10:00:00",
        "expires_at": None,
        "context_data": {},
        "status": AlertStatus.ACTIVE,
        "assignee": None,
        "escalation_level": 0,
        "reflection_analysis": None,
        "explanation_confidence": 0.8,
    }
    data.update(overrides)
    return IntelligentAlert(**data)


def test_alert_escalation_writes_guardian_audit_without_alert_text(
    guardian_env,
):
    manager = _manager(guardian_env)
    alert = _alert()
    rule = AlertEscalationRule(
        "medium_test",
        "severity == 'medium' and age > 0",
        AlertSeverity.HIGH,
        0.0,
    )

    asyncio.run(manager._escalate_alert(alert, rule))
    entries = _audit_entries(guardian_env)

    assert alert.severity == AlertSeverity.HIGH
    assert alert.escalation_level == 1
    assert manager.alerts_escalated == 1
    assert entries[-1]["details"]["intent"]["action"] == "homeostasis.alert_escalate"
    assert "homeostasis_actuation" in entries[-1]["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])


def test_alert_escalation_blocks_explicit_requester_without_capability(
    monkeypatch, guardian_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    manager = _manager(guardian_env)
    alert = _alert(context_data={"guardian_requester": "untrusted_notifier"})
    rule = AlertEscalationRule(
        "medium_test",
        "severity == 'medium' and age > 0",
        AlertSeverity.HIGH,
        0.0,
    )

    asyncio.run(manager._escalate_alert(alert, rule))
    entries = _audit_entries(guardian_env)

    assert alert.severity == AlertSeverity.MEDIUM
    assert alert.escalation_level == 0
    assert manager.alerts_escalated == 0
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_alert_escalation_audit_records_bounded_metadata(guardian_env):
    manager = _manager(guardian_env)
    alert = _alert(alert_id="alert-002", category="SecurityPolicy")
    rule = AlertEscalationRule(
        "security_test",
        "severity == 'medium' and age > 0",
        AlertSeverity.HIGH,
        0.0,
    )

    asyncio.run(manager._escalate_alert(alert, rule))
    entries = _audit_entries(guardian_env)
    metadata = entries[-1]["details"]["intent"]["metadata"]

    assert metadata["alert_id"] == "alert-002"
    assert metadata["category"] == "SecurityPolicy"
    assert metadata["old_severity"] == "medium"
    assert metadata["new_severity"] == "high"
    assert metadata["rule_name"] == "security_test"


def test_alert_notification_writes_guardian_audit_without_endpoint_or_text(
    monkeypatch,
    guardian_env,
):
    manager = _manager(guardian_env)
    manager.notification_channels = [
        AlertNotificationChannel(
            "homeostasis_feedback",
            "homeostasis",
            "internal://do-not-audit-this-value",
            {AlertSeverity.HIGH},
        )
    ]
    alert = _alert(severity=AlertSeverity.HIGH)
    sent = []

    async def fake_send(channel, alert):
        sent.append((channel.name, alert.alert_id))

    monkeypatch.setattr(manager, "_send_notification", fake_send)

    asyncio.run(manager._send_notifications(alert))
    entries = _audit_entries(guardian_env)

    assert sent == [("homeostasis_feedback", "alert-001")]
    assert manager.notifications_sent == 1
    assert entries[-1]["details"]["intent"]["action"] == "homeostasis.alert_notify"
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])


def test_external_alert_notification_requires_network_capability_in_strict_mode(
    monkeypatch,
    guardian_env,
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    manager = _manager(guardian_env)
    manager.notification_channels = [
        AlertNotificationChannel(
            "ops_webhook",
            "webhook",
            "https://example.invalid/do-not-audit-this-value",
            {AlertSeverity.HIGH},
        )
    ]
    alert = _alert(severity=AlertSeverity.HIGH)
    sent = []

    async def fake_send(channel, alert):
        sent.append((channel.name, alert.alert_id))

    monkeypatch.setattr(manager, "_send_notification", fake_send)

    asyncio.run(manager._send_notifications(alert))
    entries = _audit_entries(guardian_env)

    assert sent == []
    assert manager.notifications_sent == 0
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])

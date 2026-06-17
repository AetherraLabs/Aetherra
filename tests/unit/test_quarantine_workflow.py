# Standard library imports
import json
from unittest.mock import MagicMock

import pytest

# Aetherra imports
from aetherra_self_incorporation import QuarantineManager


def _configure_guardian(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_APPROVAL_ID", raising=False)
    return tmp_path


def _guardian_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_quarantine_manager_basic():
    audit = MagicMock()
    qm = QuarantineManager(audit_ledger=audit)
    file_id = "test_file.py"
    reason = "test reason"
    context = {"foo": "bar"}
    qm.quarantine(file_id, reason, context)
    status = qm.get_status(file_id)
    assert status["status"] == "quarantined"
    assert status["reason"] == reason
    assert status["context"] == context
    assert "timestamp" in status
    audit.append.assert_called_once()

    # Escalate
    qm.escalate(file_id, new_level=1, approval="test_approval")
    status = qm.get_status(file_id)
    assert status["status"] == "escalated"
    assert status["escalation_level"] == 1
    assert status["approval"] == "test_approval"
    assert audit.append.call_count == 2

    # Release
    qm.release(file_id, approved=True)
    assert qm.get_status(file_id) == {}
    assert audit.append.call_count == 3


def test_quarantine_manager_list():
    qm = QuarantineManager()
    qm.quarantine("f1", "r1")
    qm.quarantine("f2", "r2")
    assert len(qm.list_quarantined()) == 2
    qm.escalate("f1", 1)
    assert len(qm.list_quarantined()) == 1
    qm.release("f2", approved=False)
    assert len(qm.list_quarantined()) == 0


def test_quarantine_release_writes_guardian_audit_without_raw_file_id(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    qm = QuarantineManager()
    qm.quarantine(
        "sensitive-plugin-do-not-audit.py",
        "contains sensitive issue text",
        {"path": "private/path/sensitive-plugin-do-not-audit.py"},
    )

    qm.release("sensitive-plugin-do-not-audit.py", approved=True)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert qm.get_status("sensitive-plugin-do-not-audit.py") == {}
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.quarantine_release"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "sensitive-plugin-do-not-audit" not in ledger_text
    assert "contains sensitive issue text" not in ledger_text


def test_quarantine_escalate_denies_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    qm = QuarantineManager()
    qm.quarantine("blocked.py", "blocked reason")

    with pytest.raises(PermissionError) as exc_info:
        qm.escalate("blocked.py", 2, requester="untrusted_operator")

    status = qm.get_status("blocked.py")
    entries = _guardian_entries(audit_root)

    assert str(exc_info.value).startswith("guardian_denied:missing_capability")
    assert status["status"] == "quarantined"
    assert status["escalation_level"] == 0
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.quarantine_escalate"

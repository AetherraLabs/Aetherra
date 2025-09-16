from unittest.mock import MagicMock

from aetherra_self_incorporation import QuarantineManager


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

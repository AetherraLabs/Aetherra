import json

import pytest

from Aetherra.aetherra_core.memory import qfac


def _configure_guardian(monkeypatch, tmp_path):
    audit_root = tmp_path / "audit"
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(audit_root))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_APPROVAL_ID", raising=False)
    return audit_root


def _guardian_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    if not audit_path.exists():
        return []
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_qfac_store_uses_guardian_and_sanitizes_audit(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)

    record = qfac.qfac_store(
        "secret memory content",
        embedding=[1.0, 0.0],
        observer_state={"agent": "lyrixa"},
    )
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert record.content == "secret memory content"
    assert entries[-1]["details"]["intent"]["action"] == "memory.qfac_store"
    assert entries[-1]["details"]["decision"]["status"] in {"allow", "allow_limited"}
    assert entries[-1]["details"]["intent"]["metadata"]["embedding_dimension"] == 2
    assert "secret memory content" not in ledger_text
    assert "lyrixa" not in ledger_text


def test_qfac_rewrite_uses_guardian(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)

    result = qfac.qfac_rewrite_budgeted(budget_tokens=10)
    entries = _guardian_entries(audit_root)

    assert result >= 0
    assert entries[-1]["details"]["intent"]["action"] == "memory.qfac_rewrite"
    assert entries[-1]["details"]["decision"]["status"] in {"allow", "allow_limited"}
    assert entries[-1]["details"]["intent"]["metadata"]["mode"] == "simple"


def test_qfac_store_denies_external_requester_before_mutation(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    called = False

    def _blocked_store(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("QFAC store should not be called after Guardian denial")

    monkeypatch.setattr(qfac._simple_api, "qfac_store", _blocked_store)

    with pytest.raises(PermissionError):
        qfac.qfac_store("should not persist")

    entries = _guardian_entries(audit_root)
    assert called is False
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_qfac_rewrite_denies_external_requester_before_mutation(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    called = False

    def _blocked_rewrite(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("QFAC rewrite should not be called after Guardian denial")

    monkeypatch.setattr(qfac._simple_api, "qfac_rewrite_budgeted", _blocked_rewrite)

    with pytest.raises(PermissionError):
        qfac.qfac_rewrite_budgeted(budget_tokens=10)

    entries = _guardian_entries(audit_root)
    assert called is False
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

import json

import pytest

from Aetherra.consciousness.episodic_store import EpisodicStore


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    audit_root = tmp_path / "audit"
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(audit_root))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    return audit_root


def _audit_text(audit_root):
    return (audit_root / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _last_audit_entry(audit_root):
    entries = [
        json.loads(line)
        for line in _audit_text(audit_root).splitlines()
        if line.strip()
    ]
    return entries[-1]


def test_episodic_append_is_guardian_audited_without_content(monkeypatch, tmp_path):
    audit_root = _guardian_env(monkeypatch, tmp_path)
    path = tmp_path / "events.jsonl"
    store = EpisodicStore(str(path))

    store.new_event(
        type="reflection",
        content="do-not-audit-this-private-reflection",
        source="private-source",
        importance=0.6,
    )

    assert path.exists()
    ledger_text = _audit_text(audit_root)
    assert "do-not-audit-this-private-reflection" not in ledger_text
    assert "private-source" not in ledger_text
    assert str(path) not in ledger_text
    assert _last_audit_entry(audit_root)["details"]["intent"]["action"] == (
        "consciousness.episodic_event_append"
    )


def test_episodic_append_guardian_denial_leaves_store_empty(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-consciousness-client",
        strict=True,
    )
    path = tmp_path / "events.jsonl"
    store = EpisodicStore(str(path))

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        store.new_event(
            type="reflection",
            content="blocked-private-reflection",
            source="private-source",
            importance=0.6,
        )

    assert path.exists() is False
    assert store.list_recent() == []

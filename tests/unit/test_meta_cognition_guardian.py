import json
import sqlite3

import pytest

from Aetherra.consciousness.intelligence.meta_cognition import (
    MetaCognitionSystem,
    SelfKnowledgeDomain,
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


def _row_count(db_path, table):
    with sqlite3.connect(db_path) as conn:
        if table == "meta_memory_nodes":
            return conn.execute("SELECT COUNT(*) FROM meta_memory_nodes").fetchone()[0]
        if table == "self_reflections":
            return conn.execute("SELECT COUNT(*) FROM self_reflections").fetchone()[0]
    raise ValueError(f"unsupported table: {table}")


def test_meta_memory_node_persist_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    db_path = tmp_path / "meta_cognition.db"
    system = MetaCognitionSystem(db_path=str(db_path))

    node_id = system.enhance_self_knowledge(
        SelfKnowledgeDomain.COGNITIVE_PATTERNS,
        {"private_pattern": "private_value"},
        confidence=0.8,
        source="private_source",
    )

    assert node_id in system.meta_memory_nodes
    assert _row_count(db_path, "meta_memory_nodes") == 1
    ledger_text = _audit_text(tmp_path)
    assert str(db_path) not in ledger_text
    assert node_id not in ledger_text
    assert "private_pattern" not in ledger_text
    assert "private_value" not in ledger_text
    assert "private_source" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.meta_memory_node_persist"
    assert entry["details"]["intent"]["metadata"]["domain"] == "cognitive_patterns"
    assert entry["details"]["intent"]["metadata"]["content_field_count"] == 1


def test_meta_memory_node_denial_skips_memory_and_database_mutation(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-client",
        strict=True,
    )
    db_path = tmp_path / "meta_cognition.db"
    system = MetaCognitionSystem(db_path=str(db_path))

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        system.enhance_self_knowledge(
            SelfKnowledgeDomain.COGNITIVE_PATTERNS,
            {"private_pattern": "private_value"},
            confidence=0.8,
            source="private_source",
        )

    assert system.meta_memory_nodes == {}
    assert _row_count(db_path, "meta_memory_nodes") == 0
    assert system.self_knowledge_coverage["cognitive_patterns"]["knowledge_nodes"] == []
    assert system.cognitive_state.get("meta_reflection_events") is None
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.meta_memory_node_persist"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_self_reflection_denial_restores_memory_and_skips_database_mutation(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-client",
        strict=True,
    )
    db_path = tmp_path / "meta_cognition.db"
    system = MetaCognitionSystem(db_path=str(db_path))
    before_coverage = json.loads(json.dumps(system.self_knowledge_coverage))
    before_state = json.loads(json.dumps(system.cognitive_state))

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        system.conduct_self_reflection(
            trigger_event="private_trigger",
            reflection_type="private_reflection",
            meta_level=2,
        )

    assert system.reflection_history == []
    assert system.meta_memory_nodes == {}
    assert system.self_knowledge_coverage == before_coverage
    assert system.cognitive_state == before_state
    assert _row_count(db_path, "self_reflections") == 0
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.self_reflection_persist"
    assert entry["details"]["decision"]["reason"] == "missing_capability"
    assert "private_trigger" not in _audit_text(tmp_path)

import asyncio
import json
from datetime import datetime, timedelta

from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem


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


def _seed_memory(system, *, memory_id="m1", content="secret memory"):
    cursor = system.ensure_connection().cursor()
    now = datetime.now()
    cursor.execute(
        """
        INSERT OR REPLACE INTO memories
        (id, content, context, tags, importance, created_at, last_accessed, access_count, memory_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            memory_id,
            json.dumps({"text": content}),
            json.dumps({"source": "test"}),
            json.dumps(["private"]),
            0.1,
            (now - timedelta(days=45)).isoformat(),
            now.isoformat(),
            0,
            "conversation",
        ),
    )
    system.ensure_connection().commit()


def test_memory_export_import_and_consolidate_use_guardian(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    db_path = tmp_path / "memory.db"
    export_path = tmp_path / "memory_export.json"
    with LyrixaMemorySystem(str(db_path)) as system:
        _seed_memory(system)

        assert system.export_memory(str(export_path)) is True
        assert export_path.exists()

        assert system.import_memory(str(export_path)) is True
        assert asyncio.run(system.consolidate_memories()) is True

    entries = _guardian_entries(audit_root)
    actions = [entry["details"]["intent"]["action"] for entry in entries[-3:]]
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert actions == ["memory.export", "memory.import", "memory.consolidate"]
    assert "secret memory" not in ledger_text
    assert "memory_export.json" not in ledger_text
    assert "private" not in ledger_text


def test_memory_export_denies_external_requester_before_file_write(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    export_path = tmp_path / "memory_export.json"
    with LyrixaMemorySystem(str(tmp_path / "memory.db")) as system:
        _seed_memory(system)

        assert system.export_memory(str(export_path)) is False

    entries = _guardian_entries(audit_root)
    assert not export_path.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_memory_import_denies_external_requester_before_database_mutation(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    import_path = tmp_path / "memory_import.json"
    import_path.write_text(
        json.dumps(
            [
                [
                    "m1",
                    json.dumps({"text": "secret memory"}),
                    "{}",
                    "[]",
                    0.5,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    0,
                    "conversation",
                ]
            ]
        ),
        encoding="utf-8",
    )
    with LyrixaMemorySystem(str(tmp_path / "memory.db")) as system:
        assert system.import_memory(str(import_path)) is False
        cursor = system.ensure_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]

    entries = _guardian_entries(audit_root)
    assert count == 0
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_memory_consolidation_denies_external_requester_before_mutation(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    with LyrixaMemorySystem(str(tmp_path / "memory.db")) as system:
        _seed_memory(system)

        assert asyncio.run(system.consolidate_memories()) is False
        cursor = system.ensure_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]

    entries = _guardian_entries(audit_root)
    assert count == 1
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_memory_delete_uses_guardian_and_sanitizes_audit(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    with LyrixaMemorySystem(str(tmp_path / "memory.db")) as system:
        _seed_memory(system, memory_id="memory-secret-id")

        assert system.delete_memory("memory-secret-id") is True
        cursor = system.ensure_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]

    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert count == 0
    assert entries[-1]["details"]["intent"]["action"] == "memory.delete"
    assert entries[-1]["details"]["decision"]["status"] in {"allow", "allow_limited"}
    assert "memory-secret-id" not in ledger_text
    assert "secret memory" not in ledger_text


def test_memory_delete_denies_external_requester_before_database_mutation(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    with LyrixaMemorySystem(str(tmp_path / "memory.db")) as system:
        _seed_memory(system, memory_id="memory-secret-id")

        assert system.delete_memory("memory-secret-id") is False
        cursor = system.ensure_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]

    entries = _guardian_entries(audit_root)
    assert count == 1
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

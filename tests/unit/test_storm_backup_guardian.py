import json
import sqlite3

import pytest

from Aetherra.guardian.approval import resolve_approval
from tools import storm_backup


def _configure_guardian(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path / "audit"))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_APPROVAL_ID", raising=False)
    return tmp_path / "audit"


def _guardian_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _create_storm_db(path, meta_value="old"):
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE storm_cells (id TEXT PRIMARY KEY, content TEXT);
            CREATE TABLE storm_overlaps (id TEXT PRIMARY KEY, source TEXT);
            CREATE TABLE storm_meta (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE storm_schema_version (version INTEGER PRIMARY KEY);
            """
        )
        conn.execute(
            "INSERT INTO storm_meta (key, value) VALUES (?, ?)",
            ("status", meta_value),
        )
        conn.execute("INSERT INTO storm_schema_version (version) VALUES (?)", (1,))
        conn.commit()
    finally:
        conn.close()


def _meta_value(path):
    conn = sqlite3.connect(path)
    try:
        return conn.execute(
            "SELECT value FROM storm_meta WHERE key = ?",
            ("status",),
        ).fetchone()[0]
    finally:
        conn.close()


def _write_backup_file(path, meta_value="new"):
    path.write_text(
        json.dumps(
            {
                "_meta": {"generated_at": "2026-06-15T00:00:00Z"},
                "storm_cells": [],
                "storm_overlaps": [],
                "storm_meta": [{"key": "status", "value": meta_value}],
                "storm_schema_version": [{"version": 2}],
            }
        ),
        encoding="utf-8",
    )


def test_storm_backup_writes_guardian_audit_without_raw_paths(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    db_path = tmp_path / "private-storm.db"
    out_path = tmp_path / "private-backup.json"
    _create_storm_db(db_path)

    storm_backup.backup(str(db_path), str(out_path))
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert out_path.exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.storm_backup"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "private-storm.db" not in ledger_text
    assert "private-backup.json" not in ledger_text


def test_storm_forced_restore_consumes_guardian_approval(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    db_path = tmp_path / "storm.db"
    backup_path = tmp_path / "restore.json"
    _create_storm_db(db_path, meta_value="old")
    _write_backup_file(backup_path, meta_value="new")
    pending = storm_backup._guardian_preflight_restore(
        str(db_path),
        str(backup_path),
        True,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    storm_backup.restore(str(db_path), str(backup_path), force=True)
    entries = _guardian_entries(audit_root)

    assert _meta_value(db_path) == "new"
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.storm_restore"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"


def test_storm_restore_denies_external_requester_before_database_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    db_path = tmp_path / "storm.db"
    backup_path = tmp_path / "restore.json"
    _create_storm_db(db_path, meta_value="old")
    _write_backup_file(backup_path, meta_value="new")

    with pytest.raises(PermissionError) as exc_info:
        storm_backup.restore(str(db_path), str(backup_path), force=True)
    entries = _guardian_entries(audit_root)

    assert str(exc_info.value).startswith("guardian_denied:missing_capability")
    assert _meta_value(db_path) == "old"
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.storm_restore"

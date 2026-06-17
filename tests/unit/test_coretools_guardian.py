import json
import zipfile

import pytest

from Aetherra.aetherra_core.system.coretools import CoreToolsPlugin


def _plugin(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "coretools-test")
    return CoreToolsPlugin()


def _guardian_entries(tmp_path):
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_coretools_write_file_passes_through_guardian(monkeypatch, tmp_path):
    plugin = _plugin(monkeypatch, tmp_path)
    target = tmp_path / "notes" / "safe.txt"

    result = plugin.write_file(str(target), "do-not-audit-this-content")
    entries = _guardian_entries(tmp_path)
    guardian_entry = next(
        entry
        for entry in entries
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "filesystem.write"
    )
    ledger_text = (
        tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result.startswith("Successfully wrote")
    assert target.read_text(encoding="utf-8") == "do-not-audit-this-content"
    assert guardian_entry["details"]["intent"]["capabilities"] == ["fs:write"]
    assert guardian_entry["details"]["decision"]["status"] == "allow_limited"
    assert "do-not-audit-this-content" not in ledger_text


def test_coretools_write_file_denied_before_mutation_when_capability_missing(
    monkeypatch, tmp_path
):
    plugin = _plugin(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    target = tmp_path / "blocked.txt"

    with pytest.raises(Exception, match="Guardian denied"):
        plugin.write_file(str(target), "should not be written")

    entries = _guardian_entries(tmp_path)
    guardian_entry = next(
        entry
        for entry in entries
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "filesystem.write"
    )

    assert target.exists() is False
    assert guardian_entry["details"]["decision"]["status"] == "deny"
    assert guardian_entry["details"]["decision"]["reason"] == "missing_capability"


def test_coretools_delete_requires_guardian_approval_before_delete(
    monkeypatch, tmp_path
):
    plugin = _plugin(monkeypatch, tmp_path)
    target = tmp_path / "important.txt"
    target.write_text("keep me", encoding="utf-8")

    with pytest.raises(Exception, match="Guardian denied"):
        plugin.delete_file(str(target))

    entries = _guardian_entries(tmp_path)
    guardian_entry = next(
        entry
        for entry in entries
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "filesystem.delete"
    )

    assert target.read_text(encoding="utf-8") == "keep me"
    assert guardian_entry["details"]["decision"]["status"] == "require_approval"


def test_coretools_extract_archive_blocks_zip_slip(monkeypatch, tmp_path):
    plugin = _plugin(monkeypatch, tmp_path)
    archive_path = tmp_path / "malicious.zip"
    extract_to = tmp_path / "extract"
    escaped = tmp_path / "escaped.txt"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../escaped.txt", "bad")

    with pytest.raises(Exception, match="escapes extraction directory"):
        plugin.extract_archive(str(archive_path), str(extract_to))

    assert escaped.exists() is False

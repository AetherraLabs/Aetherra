import json
from pathlib import Path

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import focused_cleanup


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
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _create_core_tree(tmp_path):
    base = tmp_path / "Aetherra" / "aetherra_core"
    keep_file = base / "agents" / "conversation_manager.py"
    remove_file = base / "engine" / "conversation_manager.py"
    move_source = base / "personality" / "personality_engine.py"
    move_destination = base / "engine" / "personality_engine.py"

    keep_file.parent.mkdir(parents=True)
    remove_file.parent.mkdir(parents=True)
    move_source.parent.mkdir(parents=True)
    keep_file.write_text("KEEP = True\n", encoding="utf-8")
    remove_file.write_text("REMOVE = True\n", encoding="utf-8")
    move_source.write_text("MOVE = True\n", encoding="utf-8")
    return keep_file, remove_file, move_source, move_destination


def test_focused_cleanup_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    keep_file, remove_file, move_source, move_destination = _create_core_tree(tmp_path)
    pending = focused_cleanup._guardian_preflight_cleanup(
        base_path=Path("Aetherra/aetherra_core"),
        backup_dir=Path("focused_cleanup_backup"),
        duplicate_count=5,
        move_count=4,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = focused_cleanup.focused_cleanup()
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert keep_file.exists()
    assert not remove_file.exists()
    assert not move_source.exists()
    assert move_destination.exists()
    assert (tmp_path / "focused_cleanup_backup" / "engine" / "conversation_manager.py").exists()
    assert (
        tmp_path / "focused_cleanup_backup" / "personality" / "personality_engine.py"
    ).exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.focused_cleanup"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "conversation_manager.py" not in ledger_text
    assert "personality_engine.py" not in ledger_text


def test_focused_cleanup_denies_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    keep_file, remove_file, move_source, move_destination = _create_core_tree(tmp_path)

    result = focused_cleanup.focused_cleanup()
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert keep_file.exists()
    assert remove_file.exists()
    assert move_source.exists()
    assert not move_destination.exists()
    assert not (tmp_path / "focused_cleanup_backup").exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

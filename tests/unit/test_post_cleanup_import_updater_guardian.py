import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.post_cleanup_import_updater import PostCleanupImportUpdater


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


def _create_import_target(tmp_path):
    source = tmp_path / "pkg" / "uses_old_import.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        "from Aetherra.plugins.agent_adapters.agent_base import AgentBase\n",
        encoding="utf-8",
    )
    return source


def test_post_cleanup_import_update_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    source = _create_import_target(tmp_path)
    updater = PostCleanupImportUpdater(base_path=tmp_path)
    plans = [updater._plan_file_imports(source)]
    pending = updater._guardian_preflight_update(
        total_files=1,
        planned_updates=plans,
        report_path=tmp_path / "POST_CLEANUP_IMPORT_UPDATE_REPORT.md",
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = PostCleanupImportUpdater(base_path=tmp_path).scan_and_update_imports()
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert "from Aetherra.plugins.core.agent_base" in source.read_text(
        encoding="utf-8"
    )
    assert (tmp_path / "POST_CLEANUP_IMPORT_UPDATE_REPORT.md").exists()
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.post_cleanup_import_update"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "uses_old_import.py" not in ledger_text


def test_post_cleanup_import_update_denies_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    source = _create_import_target(tmp_path)

    result = PostCleanupImportUpdater(base_path=tmp_path).scan_and_update_imports()
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert "agent_adapters.agent_base" in source.read_text(encoding="utf-8")
    assert not (tmp_path / "POST_CLEANUP_IMPORT_UPDATE_REPORT.md").exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

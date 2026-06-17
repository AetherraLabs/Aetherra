import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.fix_architecture import ArchitecturalFixer


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


def test_architecture_fixer_dry_run_does_not_require_guardian(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    fixer = ArchitecturalFixer(str(tmp_path / "project"), dry_run=True)
    monkeypatch.setattr(fixer, "_guardian_preflight_apply", None)

    result = fixer.apply_fixes()

    assert result == {"import_fixes": [], "gui_moves": [], "engine_analysis": []}
    assert not (tmp_path / "project" / "ARCHITECTURAL_FIX_REPORT.md").exists()
    assert _guardian_entries(audit_root) == []


def test_architecture_fixer_live_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    fixer = ArchitecturalFixer(str(project), dry_run=False)
    pending = fixer._guardian_preflight_apply()
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)
    monkeypatch.setattr(
        fixer,
        "fix_import_violations",
        lambda: ["private_architecture_path.py"],
    )
    monkeypatch.setattr(fixer, "move_gui_to_lyrixa", lambda: [])
    monkeypatch.setattr(fixer, "fix_engine_locations", lambda: [])

    result = fixer.apply_fixes()
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result["import_fixes"] == ["private_architecture_path.py"]
    assert (project / "architecture_guard.py").exists()
    assert (project / "ARCHITECTURAL_FIX_REPORT.md").exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.architecture_fix"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "private_architecture_path.py" not in ledger_text
    assert str(project) not in ledger_text


def test_architecture_fixer_live_denies_external_requester_before_side_effects(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    project = tmp_path / "project"
    project.mkdir()
    fixer = ArchitecturalFixer(str(project), dry_run=False)

    def fail_if_called():
        raise AssertionError("fixes should not run after Guardian denial")

    monkeypatch.setattr(fixer, "fix_import_violations", fail_if_called)
    monkeypatch.setattr(fixer, "move_gui_to_lyrixa", fail_if_called)
    monkeypatch.setattr(fixer, "fix_engine_locations", fail_if_called)

    result = fixer.apply_fixes()
    entries = _guardian_entries(audit_root)

    assert result == {"import_fixes": [], "gui_moves": [], "engine_analysis": []}
    assert not (project / "architecture_guard.py").exists()
    assert not (project / "ARCHITECTURAL_FIX_REPORT.md").exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.fix_architecture_simple import ArchitecturalFixer


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


def _create_violation_file(project):
    target = project / "Aetherra" / "plugins" / "core" / "plugin_system.py"
    target.parent.mkdir(parents=True)
    target.write_text("from lyrixa.core import Thing\n", encoding="utf-8")
    return target


def test_simple_architecture_fixer_dry_run_does_not_require_guardian(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    project = tmp_path / "project"
    target = _create_violation_file(project)
    fixer = ArchitecturalFixer(str(project), dry_run=True)
    monkeypatch.setattr(fixer, "_guardian_preflight_apply", None)

    result = fixer.apply_fixes()

    assert result["import_fixes"] == [str(target)]
    assert target.read_text(encoding="utf-8") == "from lyrixa.core import Thing\n"
    assert _guardian_entries(audit_root) == []


def test_simple_architecture_fixer_live_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    project = tmp_path / "project"
    target = _create_violation_file(project)
    fixer = ArchitecturalFixer(str(project), dry_run=False)
    pending = fixer._guardian_preflight_apply()
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = fixer.apply_fixes()
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result["import_fixes"] == [str(target)]
    assert target.read_text(encoding="utf-8").startswith(
        "# ARCHITECTURAL FIX: Removed Lyrixa import"
    )
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.architecture_import_fix"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert str(project) not in ledger_text
    assert "plugin_system.py" not in ledger_text


def test_simple_architecture_fixer_live_denies_external_requester_before_rewrite(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    project = tmp_path / "project"
    target = _create_violation_file(project)
    fixer = ArchitecturalFixer(str(project), dry_run=False)

    def fail_if_called():
        raise AssertionError("fixes should not run after Guardian denial")

    monkeypatch.setattr(fixer, "fix_import_violations", fail_if_called)

    result = fixer.apply_fixes()
    entries = _guardian_entries(audit_root)

    assert result == {"import_fixes": []}
    assert target.read_text(encoding="utf-8") == "from lyrixa.core import Thing\n"
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

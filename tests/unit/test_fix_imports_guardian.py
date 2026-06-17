import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.fix_imports import AetherraImportFixer


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


def _create_import_tree(tmp_path):
    package_dir = tmp_path / "Aetherra" / "aetherra_core" / "engine"
    package_dir.mkdir(parents=True)
    return package_dir


def _make_deterministic(fixer, monkeypatch):
    deps_status = {"flask": True, "requests": True}
    import_results = {"aetherra_core": False}
    monkeypatch.setattr(fixer, "check_dependencies", lambda: deps_status)
    monkeypatch.setattr(fixer, "test_imports", lambda: import_results)
    return deps_status, import_results


def test_import_fixer_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    package_dir = _create_import_tree(tmp_path)
    fixer = AetherraImportFixer(project_root=tmp_path)
    deps_status, import_results = _make_deterministic(fixer, monkeypatch)
    init_plans = fixer.plan_missing_init_files()
    report_plan = fixer.plan_report(deps_status, import_results)
    pending = fixer._guardian_preflight_file_writes(init_plans, report_plan)
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = fixer.fix_all_issues()
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result is True
    assert (package_dir / "__init__.py").exists()
    assert (tmp_path / "import_fix_report.md").exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.import_fix"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "aetherra_core" not in ledger_text
    assert "import_fix_report.md" not in ledger_text


def test_import_fixer_denies_external_requester_before_file_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    package_dir = _create_import_tree(tmp_path)
    fixer = AetherraImportFixer(project_root=tmp_path)
    _make_deterministic(fixer, monkeypatch)

    result = fixer.fix_all_issues()
    entries = _guardian_entries(audit_root)

    assert result is False
    assert not (package_dir / "__init__.py").exists()
    assert not (tmp_path / "import_fix_report.md").exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_import_fixer_denies_dependency_install_before_pip(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    monkeypatch.setattr(
        "tools.maintenance.fix_imports.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("pip ran")),
    )
    fixer = AetherraImportFixer(project_root=tmp_path)

    result = fixer.install_missing_dependencies(["example-package>=1.0"])
    entries = _guardian_entries(audit_root)

    assert result is False
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.import_dependency_install"
    )
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import quick_fix_imports


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


def _create_package_dir(tmp_path):
    package_dir = tmp_path / "Aetherra" / "aetherra_core" / "engine"
    package_dir.mkdir(parents=True)
    return package_dir


def test_quick_import_fix_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    package_dir = _create_package_dir(tmp_path)
    plans = quick_fix_imports.plan_missing_inits(tmp_path)
    pending = quick_fix_imports._guardian_preflight_init_creation(
        project_root=tmp_path,
        plans=plans,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = quick_fix_imports.fix_missing_inits(tmp_path)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result is True
    assert (package_dir / "__init__.py").exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.quick_import_init_fix"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "aetherra_core" not in ledger_text
    assert "__init__.py" not in ledger_text


def test_quick_import_fix_denies_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    package_dir = _create_package_dir(tmp_path)

    result = quick_fix_imports.fix_missing_inits(tmp_path)
    entries = _guardian_entries(audit_root)

    assert result is False
    assert not (package_dir / "__init__.py").exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_quick_import_fix_noop_does_not_require_guardian(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    package_dir = _create_package_dir(tmp_path)
    (tmp_path / "Aetherra" / "aetherra_core" / "__init__.py").write_text(
        "# existing\n",
        encoding="utf-8",
    )
    (package_dir / "__init__.py").write_text("# existing\n", encoding="utf-8")

    result = quick_fix_imports.fix_missing_inits(tmp_path)

    assert result is True
    assert _guardian_entries(audit_root) == []

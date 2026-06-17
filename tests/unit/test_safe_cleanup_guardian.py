import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import safe_cleanup


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


def _create_analysis(tmp_path):
    empty_file = tmp_path / "private-empty-marker.py"
    empty_file.write_text("", encoding="utf-8")
    keep_init = tmp_path / "pkg" / "__init__.py"
    remove_init = tmp_path / "pkg" / "nested" / "__init__.py"
    remove_init.parent.mkdir(parents=True)
    keep_init.write_text("# keep\n", encoding="utf-8")
    remove_init.write_text("# duplicate\n", encoding="utf-8")
    analysis = {
        "duplicates": [
            {
                "hash": "e3b0c44298fc1c149afbf4c8996fb924",
                "files": [str(empty_file)],
            },
            {
                "hash": "init-duplicate",
                "files": [str(keep_init), str(remove_init)],
            },
        ]
    }
    (tmp_path / "aetherra_project_analysis.json").write_text(
        json.dumps(analysis),
        encoding="utf-8",
    )
    return analysis, empty_file, keep_init, remove_init


def test_safe_cleanup_uses_guardian_approval_and_sanitized_audit(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    analysis, empty_file, keep_init, remove_init = _create_analysis(tmp_path)
    empty_files = safe_cleanup.find_empty_files(analysis)
    duplicate_init_files = safe_cleanup._duplicate_init_files_to_remove(analysis)
    pending = safe_cleanup._guardian_preflight_cleanup(empty_files, duplicate_init_files)
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = safe_cleanup.main()
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert not empty_file.exists()
    assert keep_init.exists()
    assert not remove_init.exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.safe_file_cleanup"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "private-empty-marker.py" not in ledger_text
    assert str(remove_init) not in ledger_text


def test_safe_cleanup_denies_external_requester_before_delete(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    _analysis, empty_file, keep_init, remove_init = _create_analysis(tmp_path)

    result = safe_cleanup.main()
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert empty_file.exists()
    assert keep_init.exists()
    assert remove_init.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

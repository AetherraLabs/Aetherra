import json

from tools import root_cleanup


def _configure_cleanup(monkeypatch, tmp_path):
    audit_root = tmp_path / "audit"
    workspace = tmp_path / "secret-root-cleanup"
    workspace.mkdir()
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(audit_root))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_APPROVAL_ID", raising=False)
    monkeypatch.setattr(root_cleanup, "ROOT", workspace)
    monkeypatch.setattr(
        root_cleanup,
        "PLANS",
        [
            {
                "name": "backups",
                "paths": ["source_backup"],
                "dest": "archive/backups",
            }
        ],
    )
    (workspace / "source_backup").mkdir()
    (workspace / "source_backup" / "data.txt").write_text(
        "cleanup payload\n",
        encoding="utf-8",
    )
    return audit_root, workspace


def _guardian_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_root_cleanup_plan_does_not_create_destination(monkeypatch, tmp_path):
    _audit_root, workspace = _configure_cleanup(monkeypatch, tmp_path)

    ops = root_cleanup.build_operations()

    assert len(ops) == 1
    assert not (workspace / "archive").exists()


def test_root_cleanup_apply_writes_guardian_audit_without_raw_paths(
    monkeypatch, tmp_path
):
    audit_root, workspace = _configure_cleanup(monkeypatch, tmp_path)
    ops = root_cleanup.build_operations()

    failures, results = root_cleanup.apply_operations(ops, prune=False)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert failures == 0
    assert results[0]["status"] == "copied"
    assert (workspace / "archive" / "backups" / "source_backup").exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.root_cleanup"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "secret-root-cleanup" not in ledger_text
    assert str(workspace) not in ledger_text


def test_root_cleanup_blocks_external_requester_before_copy(monkeypatch, tmp_path):
    audit_root, workspace = _configure_cleanup(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    ops = root_cleanup.build_operations()

    failures, results = root_cleanup.apply_operations(ops, prune=False)

    assert failures == 1
    assert results[0]["status"].startswith("guardian_denied:missing_capability")
    assert not (workspace / "archive").exists()
    assert (workspace / "source_backup").exists()


def test_root_cleanup_prune_requires_guardian_approval_before_delete(
    monkeypatch, tmp_path
):
    _audit_root, workspace = _configure_cleanup(monkeypatch, tmp_path)
    ops = root_cleanup.build_operations()

    failures, results = root_cleanup.apply_operations(ops, prune=True)

    assert failures == 1
    assert results[0]["status"].startswith("guardian_denied:rollback_required")
    assert not (workspace / "archive").exists()
    assert (workspace / "source_backup").exists()

import json

from Aetherra.aetherra_core.system.optimization_executor import (
    CodeChange,
    OptimizationExecutor,
    OptimizationProposal,
)


def _executor(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "optimizer-test")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "Aetherra").mkdir()
    (workspace / "tests").mkdir()
    return OptimizationExecutor(workspace=str(workspace), enable_dry_run=False), workspace


def _guardian_entries(tmp_path):
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_optimization_execute_passes_through_guardian(monkeypatch, tmp_path):
    executor, workspace = _executor(monkeypatch, tmp_path)
    target = workspace / "Aetherra" / "target.py"
    target.write_text("import os\nprint('hello')\n", encoding="utf-8")
    proposal = OptimizationProposal(
        proposal_id="opt_guardian_001",
        title="Remove unused import",
        description="Remove an unused import",
        optimization_type="code_refactoring",
        code_changes=[
            CodeChange(
                file_path=str(target),
                change_type="remove_import",
                old_code="import os\n",
                new_code="",
                reason="Unused import",
            )
        ],
    )

    result = executor.execute(proposal, run_tests=False)
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "optimization.apply"
    )

    assert result.success is True
    assert "Guardian preflight passed" in "\n".join(result.audit_trail)
    assert target.read_text(encoding="utf-8") == "print('hello')\n"
    assert guardian_entry["details"]["intent"]["capabilities"] == [
        "fs:write",
        "code:modify",
    ]
    assert "optimization_application" in guardian_entry["details"]["risk"]["factors"]


def test_optimization_denied_before_backup_or_write_when_capability_missing(
    monkeypatch, tmp_path
):
    executor, workspace = _executor(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    target = workspace / "Aetherra" / "target.py"
    target.write_text("print('before')\n", encoding="utf-8")
    proposal = OptimizationProposal(
        proposal_id="opt_guardian_blocked",
        title="Blocked optimization",
        description="Should not modify file",
        optimization_type="code_refactoring",
        code_changes=[
            CodeChange(
                file_path=str(target),
                change_type="replace_algorithm",
                old_code="before",
                new_code="after",
            )
        ],
    )

    result = executor.execute(proposal, run_tests=False)
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "optimization.apply"
    )

    assert result.success is False
    assert "Guardian denied" in result.message
    assert target.read_text(encoding="utf-8") == "print('before')\n"
    assert list(executor.backup_dir.iterdir()) == []
    assert guardian_entry["details"]["decision"]["status"] == "deny"
    assert guardian_entry["details"]["decision"]["reason"] == "missing_capability"


def test_optimization_guardian_audit_omits_code_snippets(monkeypatch, tmp_path):
    executor, workspace = _executor(monkeypatch, tmp_path)
    target = workspace / "Aetherra" / "secret_target.py"
    target.write_text("SECRET_SNIPPET = 'do-not-audit-this-code'\n", encoding="utf-8")
    proposal = OptimizationProposal(
        proposal_id="opt_guardian_redaction",
        title="Redaction test",
        description="Do not audit code snippets",
        optimization_type="code_refactoring",
        code_changes=[
            CodeChange(
                file_path=str(target),
                change_type="replace_algorithm",
                old_code="SECRET_SNIPPET = 'do-not-audit-this-code'\n",
                new_code="SECRET_SNIPPET = 'also-do-not-audit-this-code'\n",
            )
        ],
    )

    result = executor.execute(proposal, run_tests=False)
    ledger_text = (
        tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result.success is True
    assert "do-not-audit-this-code" not in ledger_text
    assert "also-do-not-audit-this-code" not in ledger_text
    assert "secret_target.py" in ledger_text


def test_manual_backup_restore_passes_through_guardian_without_raw_backup_id(
    monkeypatch, tmp_path
):
    executor, workspace = _executor(monkeypatch, tmp_path)
    target = workspace / "Aetherra" / "target.py"
    target.write_text("original\n", encoding="utf-8")
    backup_id = executor._create_backup("backup-do-not-audit-this-value")
    target.write_text("modified\n", encoding="utf-8")

    ok, message = executor.restore_backup(backup_id)
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "maintenance.restore_backup"
    )
    ledger_text = (
        tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert ok is True
    assert "Restored from backup" in message
    assert target.read_text(encoding="utf-8") == "original\n"
    assert guardian_entry["details"]["intent"]["subsystem"] == "maintenance"
    assert "maintenance_operation" in guardian_entry["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in ledger_text
    assert backup_id not in ledger_text


def test_manual_backup_restore_denied_before_workspace_mutation(monkeypatch, tmp_path):
    executor, workspace = _executor(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    target = workspace / "Aetherra" / "target.py"
    target.write_text("original\n", encoding="utf-8")
    backup_id = executor._create_backup("backup_guardian_blocked")
    target.write_text("modified\n", encoding="utf-8")

    ok, message = executor.restore_backup(backup_id)
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "maintenance.restore_backup"
    )

    assert ok is False
    assert "Guardian denied" in message
    assert target.read_text(encoding="utf-8") == "modified\n"
    assert guardian_entry["details"]["decision"]["status"] == "deny"
    assert guardian_entry["details"]["decision"]["reason"] == "missing_capability"

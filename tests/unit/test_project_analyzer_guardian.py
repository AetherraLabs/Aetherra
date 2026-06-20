import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.project_analyzer import (
    AetherraProjectAnalyzer,
    _guardian_preflight_analysis_write,
)


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


def _analyzer(project_root):
    analyzer = AetherraProjectAnalyzer(project_root)
    analyzer.directory_analysis = {
        "src": {
            "total_files": 2,
            "file_counts": {"python_module": 2},
            "files": [],
            "subdirectories": [],
        }
    }
    analyzer.duplicate_groups = [
        {
            "hash": "abc1234567890def",
            "files": ["src/a.py", "copy/a.py"],
            "count": 2,
        }
    ]
    return analyzer


def test_project_analysis_write_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    analyzer = _analyzer(tmp_path)
    output_file = tmp_path / "artifacts" / "maintenance" / "project_analysis.json"
    plan = analyzer.plan_analysis_write(output_file)
    pending = _guardian_preflight_analysis_write(
        project_root=tmp_path,
        plan=plan,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = analyzer.save_analysis(plan=plan)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result is True
    assert output_file.exists()
    assert json.loads(output_file.read_text(encoding="utf-8"))["summary"][
        "total_files"
    ] == 2
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.project_analysis_write"
    )
    assert entries[-1]["details"]["decision"]["reason"] == (
        "approved_with_guardian_approval"
    )
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "project_analysis.json" not in ledger_text
    assert "src/a.py" not in ledger_text


def test_project_analysis_write_denies_external_requester_before_write(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    analyzer = _analyzer(tmp_path)
    output_file = tmp_path / "artifacts" / "maintenance" / "project_analysis.json"
    plan = analyzer.plan_analysis_write(output_file)

    result = analyzer.save_analysis(plan=plan)
    entries = _guardian_entries(audit_root)

    assert result is False
    assert not output_file.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_project_analysis_write_blocks_unapproved_report_destination(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    analyzer = _analyzer(tmp_path)
    output_file = tmp_path / "project_analysis.json"
    plan = analyzer.plan_analysis_write(output_file)

    result = analyzer.save_analysis(plan=plan)

    assert result is False
    assert not output_file.exists()
    assert _guardian_entries(audit_root) == []

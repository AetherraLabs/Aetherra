import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import generate_reports


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


def _analysis():
    return {
        "duplicates": [
            {
                "hash": "abc1234567890def",
                "files": ["src/a.py", "copy/a.py"],
                "count": 2,
            }
        ],
        "directories": {
            "src": {
                "total_files": 1,
                "purpose": "source",
                "file_counts": {"python_module": 1},
                "subdirectories": [],
                "files": [{"name": "a.py", "category": "python_module"}],
            }
        },
        "summary": {
            "total_files": 2,
            "total_directories": 1,
            "duplicate_files": 1,
            "file_categories": {"python_module": 2},
        },
    }


def test_generate_reports_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    output_dir = tmp_path / "reports" / "maintenance"
    plans = generate_reports.plan_analysis_reports(_analysis(), output_dir)
    pending = generate_reports._guardian_preflight_report_generation(
        output_dir=output_dir,
        plans=plans,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = generate_reports.write_analysis_reports(
        plans,
        output_dir=output_dir,
        project_root=tmp_path,
    )
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert (output_dir / "DUPLICATE_FILES_REPORT.md").exists()
    assert (output_dir / "CONSOLIDATION_PLAN.md").exists()
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.analysis_report_generation"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "DUPLICATE_FILES_REPORT.md" not in ledger_text
    assert "src/a.py" not in ledger_text


def test_generate_reports_denies_external_requester_before_write(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    output_dir = tmp_path / "reports" / "maintenance"
    plans = generate_reports.plan_analysis_reports(_analysis(), output_dir)

    result = generate_reports.write_analysis_reports(
        plans,
        output_dir=output_dir,
        project_root=tmp_path,
    )
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert not output_dir.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_generate_reports_blocks_unapproved_report_destination(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    output_dir = tmp_path / "manual_reports"
    plans = generate_reports.plan_analysis_reports(_analysis(), output_dir)

    result = generate_reports.write_analysis_reports(
        plans,
        output_dir=output_dir,
        project_root=tmp_path,
    )

    assert result == 1
    assert not output_dir.exists()
    assert _guardian_entries(audit_root) == []

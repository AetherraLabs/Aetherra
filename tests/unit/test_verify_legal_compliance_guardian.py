import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.verify_legal_compliance import (
    LegalComplianceReportPlan,
    _guardian_preflight_legal_compliance_report,
    write_legal_compliance_report,
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


def _plan(tmp_path):
    return LegalComplianceReportPlan(
        file_path=tmp_path / "LEGAL_COMPLIANCE_REPORT.txt",
        content="# Legal Compliance\npackage-name 1.0\n",
        license_ok=True,
        files_ok=False,
    )


def test_legal_compliance_report_requires_approval_and_sanitizes_audit(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    plan = _plan(tmp_path)
    pending = _guardian_preflight_legal_compliance_report(
        project_root=tmp_path,
        plan=plan,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = write_legal_compliance_report(project_root=tmp_path, plan=plan)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result is True
    assert plan.file_path.exists()
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.legal_compliance_report"
    )
    assert entries[-1]["details"]["decision"]["reason"] == (
        "approved_with_guardian_approval"
    )
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "LEGAL_COMPLIANCE_REPORT.txt" not in ledger_text
    assert "package-name" not in ledger_text


def test_legal_compliance_report_denies_external_requester_before_write(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    plan = _plan(tmp_path)

    result = write_legal_compliance_report(project_root=tmp_path, plan=plan)
    entries = _guardian_entries(audit_root)

    assert result is False
    assert not plan.file_path.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

import importlib
import json

import pytest

from Aetherra.guardian.approval import resolve_approval

ANALYZER_MODULES = (
    "tools.maintenance.advanced_analyzer",
    "tools.maintenance.advanced_analyzer_fixed",
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


def _analyzer(module, project_root):
    analyzer = module.AdvancedProjectAnalyzer(project_root)
    analyzer.file_intelligence = {
        "src/a.py": {
            "language": "Python",
            "purpose": "Application logic",
            "complexity_score": 3,
            "size": 128,
        }
    }
    analyzer.directory_intelligence = {
        "src": {
            "file_count": 1,
            "subdirectory_count": 0,
        }
    }
    return analyzer


@pytest.mark.parametrize("module_name", ANALYZER_MODULES)
def test_advanced_intelligence_report_requires_approval_and_sanitizes_audit(
    monkeypatch,
    tmp_path,
    module_name,
):
    module = importlib.import_module(module_name)
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    analyzer = _analyzer(module, tmp_path)
    output_file = tmp_path / "advanced_project_intelligence.json"
    plan = analyzer.plan_intelligence_report(output_file)
    pending = module._guardian_preflight_intelligence_report(
        project_root=tmp_path,
        plan=plan,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = analyzer.save_intelligence_report(plan=plan)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == str(output_file)
    assert output_file.exists()
    assert json.loads(output_file.read_text(encoding="utf-8"))["summary"][
        "total_files"
    ] == 1
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.advanced_intelligence_report"
    )
    assert entries[-1]["details"]["decision"]["reason"] == (
        "approved_with_guardian_approval"
    )
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "advanced_project_intelligence.json" not in ledger_text
    assert "src/a.py" not in ledger_text


@pytest.mark.parametrize("module_name", ANALYZER_MODULES)
def test_advanced_intelligence_report_denies_external_requester_before_write(
    monkeypatch,
    tmp_path,
    module_name,
):
    module = importlib.import_module(module_name)
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    analyzer = _analyzer(module, tmp_path)
    output_file = tmp_path / "advanced_project_intelligence.json"
    plan = analyzer.plan_intelligence_report(output_file)

    result = analyzer.save_intelligence_report(plan=plan)
    entries = _guardian_entries(audit_root)

    assert result is None
    assert not output_file.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

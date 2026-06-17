import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.create_documentation import (
    DocumentationWritePlan,
    _guardian_preflight_documentation_write,
    write_documentation_plans,
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


def _plans(tmp_path):
    return [
        DocumentationWritePlan(
            file_path=tmp_path / "src" / "README.md",
            content="# Source\nAetherra/core/example.py\n",
            kind="directory_readme",
        ),
        DocumentationWritePlan(
            file_path=tmp_path / "PROJECT_BREAKDOWN.md",
            content="# Breakdown\nsrc/README.md\n",
            kind="project_breakdown",
        ),
    ]


def test_documentation_generation_requires_approval_and_sanitizes_audit(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    plans = _plans(tmp_path)
    pending = _guardian_preflight_documentation_write(
        project_root=tmp_path,
        plans=plans,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = write_documentation_plans(project_root=tmp_path, plans=plans)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert (tmp_path / "src" / "README.md").exists()
    assert (tmp_path / "PROJECT_BREAKDOWN.md").exists()
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.documentation_generation"
    )
    assert entries[-1]["details"]["decision"]["reason"] == (
        "approved_with_guardian_approval"
    )
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "PROJECT_BREAKDOWN.md" not in ledger_text
    assert "Aetherra/core/example.py" not in ledger_text


def test_documentation_generation_denies_external_requester_before_write(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    plans = _plans(tmp_path)

    result = write_documentation_plans(project_root=tmp_path, plans=plans)
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert not (tmp_path / "src" / "README.md").exists()
    assert not (tmp_path / "PROJECT_BREAKDOWN.md").exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

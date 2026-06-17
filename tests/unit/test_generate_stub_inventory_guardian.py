import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.generate_stub_inventory import (
    StubInventoryWritePlan,
    _guardian_preflight_stub_inventory,
    write_stub_inventory,
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


def _plan(output_file):
    return StubInventoryWritePlan(
        file_path=output_file,
        data={
            "summary": {
                "total_stubs": 1,
                "by_severity": {"critical": 0, "high": 1, "medium": 0, "low": 0},
                "by_module": {"Aetherra.core.example": 1},
            },
            "stubs": [
                {
                    "id": "STUB_0001",
                    "file": "Aetherra/core/example.py",
                    "function": "run",
                    "severity": "high",
                    "reason": "TODO marker",
                    "lines": "10-10",
                    "blocking_count": 0,
                }
            ],
            "generated_at": "2026-06-16T00:00:00+00:00",
            "generator": "tools/maintenance/generate_stub_inventory.py",
        },
    )


def test_stub_inventory_write_requires_approval_and_sanitizes_audit(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    output_file = tmp_path / "docs" / "STUB_INVENTORY.json"
    plan = _plan(output_file)
    pending = _guardian_preflight_stub_inventory(project_root=tmp_path, plan=plan)
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = write_stub_inventory(project_root=tmp_path, plan=plan)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result is True
    assert output_file.exists()
    assert json.loads(output_file.read_text(encoding="utf-8"))["summary"][
        "total_stubs"
    ] == 1
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.stub_inventory_write"
    )
    assert entries[-1]["details"]["decision"]["reason"] == (
        "approved_with_guardian_approval"
    )
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "STUB_INVENTORY.json" not in ledger_text
    assert "Aetherra/core/example.py" not in ledger_text


def test_stub_inventory_write_denies_external_requester_before_write(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    output_file = tmp_path / "docs" / "STUB_INVENTORY.json"
    plan = _plan(output_file)

    result = write_stub_inventory(project_root=tmp_path, plan=plan)
    entries = _guardian_entries(audit_root)

    assert result is False
    assert not output_file.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

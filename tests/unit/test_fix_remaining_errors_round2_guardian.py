import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import fix_remaining_errors_round2


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


def _create_round2_tree(tmp_path):
    generator = tmp_path / "Aetherra" / "lyrixa" / "gui" / "phase3_auto_generator.py"
    generator.parent.mkdir(parents=True)
    generator.write_text(
        'class Phase3Generator:\n'
        '    """Generator."""\n'
        "    def _generate_plugin_panel(self, component: ComponentState, template: str) -> str:\n"
        "        return component.name\n",
        encoding="utf-8",
    )
    return generator


def test_round2_fixes_use_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    generator = _create_round2_tree(tmp_path)
    plans = fix_remaining_errors_round2.plan_round2_fixes(tmp_path)
    pending = fix_remaining_errors_round2._guardian_preflight_round2_fixes(
        project_root=tmp_path,
        plans=plans,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = fix_remaining_errors_round2.apply_round2_fixes(tmp_path)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert "_safe_get_attr" in generator.read_text(encoding="utf-8")
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.round_two_error_fix"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "phase3_auto_generator.py" not in ledger_text


def test_round2_fixes_deny_external_requester_before_mutation(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    generator = _create_round2_tree(tmp_path)
    original_generator = generator.read_text(encoding="utf-8")

    result = fix_remaining_errors_round2.apply_round2_fixes(tmp_path)
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert generator.read_text(encoding="utf-8") == original_generator
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_round2_fixes_noop_does_not_require_guardian(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)

    result = fix_remaining_errors_round2.apply_round2_fixes(tmp_path)

    assert result == 0
    assert _guardian_entries(audit_root) == []

import importlib
import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import fix_unicode_service_registry


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


def _create_registry(tmp_path):
    registry = tmp_path / "aetherra_service_registry.py"
    registry.write_text("PLUGIN = 'ðŸ”Œ'\nVOICE = 'ðŸŽ™ï¸'\n", encoding="utf-8")
    return registry


def test_importing_service_registry_fixer_has_no_side_effects(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    registry = _create_registry(tmp_path)
    original = registry.read_text(encoding="utf-8")

    importlib.reload(fix_unicode_service_registry)

    assert registry.read_text(encoding="utf-8") == original
    assert _guardian_entries(audit_root) == []


def test_service_registry_unicode_fix_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    registry = _create_registry(tmp_path)
    plan = fix_unicode_service_registry.plan_unicode_service_registry_fix(registry)
    pending = fix_unicode_service_registry._guardian_preflight_fix(plan)
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = fix_unicode_service_registry.fix_unicode_service_registry(registry)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert "[PLUGIN]" in registry.read_text(encoding="utf-8")
    assert "[VOICE]" in registry.read_text(encoding="utf-8")
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.service_registry_unicode_fix"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "aetherra_service_registry.py" not in ledger_text


def test_service_registry_unicode_fix_denies_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    registry = _create_registry(tmp_path)
    original = registry.read_text(encoding="utf-8")

    result = fix_unicode_service_registry.fix_unicode_service_registry(registry)
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert registry.read_text(encoding="utf-8") == original
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

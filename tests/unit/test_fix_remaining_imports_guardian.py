import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import fix_remaining_imports


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
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _create_target_file(tmp_path):
    target = tmp_path / "Aetherra" / "consciousness" / "consciousness_orchestrator.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "from lyrixa.memory import MemoryThing\n"
        "import lyrixa.tools\n"
        "result = lyrixa.tools.run()\n",
        encoding="utf-8",
    )
    return target


def test_remaining_import_fix_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    target = _create_target_file(tmp_path)
    plans = fix_remaining_imports.plan_remaining_lyrixa_import_fixes(tmp_path)
    pending = fix_remaining_imports._guardian_preflight_fix(
        project_root=tmp_path,
        planned_updates=plans,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = fix_remaining_imports.fix_all_lyrixa_imports(tmp_path)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")
    rewritten = target.read_text(encoding="utf-8")

    assert result == 1
    assert "ARCHITECTURAL FIX: Removed Lyrixa import" in rewritten
    assert "ARCHITECTURAL FIX: Removed Lyrixa function call" in rewritten
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.remaining_import_fix"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "consciousness_orchestrator.py" not in ledger_text


def test_remaining_import_fix_denies_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    target = _create_target_file(tmp_path)
    original = target.read_text(encoding="utf-8")

    result = fix_remaining_imports.fix_all_lyrixa_imports(tmp_path)
    entries = _guardian_entries(audit_root)

    assert result == -1
    assert target.read_text(encoding="utf-8") == original
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import fix_phase7_errors


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


def _create_phase_repair_tree(tmp_path):
    plugins_dir = tmp_path / "Aetherra" / "plugins"
    plugins_dir.mkdir(parents=True)
    conversation = (
        tmp_path / "Aetherra" / "aetherra_core" / "agents" / "conversation_manager.py"
    )
    generator = tmp_path / "Aetherra" / "lyrixa" / "gui" / "phase3_auto_generator.py"
    styled = tmp_path / "Aetherra" / "lyrixa" / "gui" / "styled_panel.py"
    conversation.parent.mkdir(parents=True)
    generator.parent.mkdir(parents=True)
    conversation.write_text(
        "from Aetherra.core.ai.multi_llm_manager import MultiLLMManager\n"
        "class LyrixaConversationManager:\n"
        "    pass\n",
        encoding="utf-8",
    )
    generator.write_text(
        "def generate_panels_from_services(service_data):\n"
        "    return service_data.type\n",
        encoding="utf-8",
    )
    styled.write_text('STYLE = "box-shadow: 0 0 2px #000;"\n', encoding="utf-8")
    return plugins_dir, conversation, generator, styled


def test_phase_error_fixes_use_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    plugins_dir, conversation, generator, styled = _create_phase_repair_tree(tmp_path)
    plans, directories = fix_phase7_errors.plan_phase_error_fixes(tmp_path)
    pending = fix_phase7_errors._guardian_preflight_phase_error_fixes(
        project_root=tmp_path,
        plans=plans,
        directories_to_create=directories,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = fix_phase7_errors.apply_phase_error_fixes(tmp_path)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert (plugins_dir / "core").exists()
    assert (plugins_dir / "core" / "agent_base.py").exists()
    assert "Aetherra.core.multi_llm_manager" in conversation.read_text(encoding="utf-8")
    assert "defensive_service_data" in generator.read_text(encoding="utf-8")
    assert "box-shadow removed" in styled.read_text(encoding="utf-8")
    assert (
        tmp_path / "tools" / "maintenance" / "PHASE_7_1_ERROR_FIXES_SUMMARY.md"
    ).exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.error_repair_batch"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "conversation_manager.py" not in ledger_text
    assert "agent_base.py" not in ledger_text


def test_phase_error_fixes_deny_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    plugins_dir, conversation, generator, styled = _create_phase_repair_tree(tmp_path)
    originals = {
        "conversation": conversation.read_text(encoding="utf-8"),
        "generator": generator.read_text(encoding="utf-8"),
        "styled": styled.read_text(encoding="utf-8"),
    }

    result = fix_phase7_errors.apply_phase_error_fixes(tmp_path)
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert not (plugins_dir / "core").exists()
    assert conversation.read_text(encoding="utf-8") == originals["conversation"]
    assert generator.read_text(encoding="utf-8") == originals["generator"]
    assert styled.read_text(encoding="utf-8") == originals["styled"]
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"

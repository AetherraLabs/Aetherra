import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import fix_plugin_imports


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


def _create_plugin_tree(tmp_path):
    plugins_dir = tmp_path / "Aetherra" / "plugins"
    plugin_file = plugins_dir / "agent_adapters" / "plugin_agent.py"
    plugin_file.parent.mkdir(parents=True)
    (plugins_dir / "core").mkdir(parents=True)
    plugin_file.write_text(
        "from .agent_base import AgentBase\n"
        "from ..core.enhanced_memory import LyrixaEnhancedMemorySystem\n",
        encoding="utf-8",
    )
    return plugins_dir, plugin_file


def test_plugin_import_fix_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    plugins_dir, plugin_file = _create_plugin_tree(tmp_path)
    rewrite_plans, init_plans = fix_plugin_imports.plan_plugin_import_fixes(tmp_path)
    pending = fix_plugin_imports._guardian_preflight_plugin_import_fix(
        project_root=tmp_path,
        rewrite_plans=rewrite_plans,
        init_plans=init_plans,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = fix_plugin_imports.fix_plugin_imports(tmp_path)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")
    rewritten = plugin_file.read_text(encoding="utf-8")

    assert result == 0
    assert "from Aetherra.plugins.agent_adapters.agent_base import" in rewritten
    assert (
        "from Aetherra.aetherra_core.memory.enhanced_memory import" in rewritten
    )
    assert (plugins_dir / "__init__.py").exists()
    assert (plugins_dir / "agent_adapters" / "__init__.py").exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.plugin_import_fix"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "plugin_agent.py" not in ledger_text
    assert "agent_adapters" not in ledger_text


def test_plugin_import_fix_denies_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    plugins_dir, plugin_file = _create_plugin_tree(tmp_path)
    original = plugin_file.read_text(encoding="utf-8")

    result = fix_plugin_imports.fix_plugin_imports(tmp_path)
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert plugin_file.read_text(encoding="utf-8") == original
    assert not (plugins_dir / "__init__.py").exists()
    assert not (plugins_dir / "agent_adapters" / "__init__.py").exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_plugin_import_fix_noop_does_not_require_guardian(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    plugins_dir, plugin_file = _create_plugin_tree(tmp_path)
    plugin_file.write_text("VALUE = 1\n", encoding="utf-8")
    for directory in (plugins_dir, plugins_dir / "agent_adapters", plugins_dir / "core"):
        (directory / "__init__.py").write_text("# existing\n", encoding="utf-8")

    result = fix_plugin_imports.fix_plugin_imports(tmp_path)

    assert result == 0
    assert _guardian_entries(audit_root) == []

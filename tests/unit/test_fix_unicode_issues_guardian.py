import json
import os

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance import fix_unicode_issues


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


def _create_unicode_tree(tmp_path):
    launcher = tmp_path / "aetherra_os_launcher.py"
    introspector = (
        tmp_path / "Aetherra" / "plugins" / "extra_plugins" / "introspector_plugin.py"
    )
    router = (
        tmp_path
        / "Aetherra"
        / "plugins"
        / "memory_hooks"
        / "memory_aware_plugin_router.py"
    )
    introspector.parent.mkdir(parents=True)
    router.parent.mkdir(parents=True)
    launcher.write_text("print('âœ… boot')\n", encoding="utf-8")
    introspector.write_text(
        "from ..memory.fractal_mesh.base import FractalMesh\n",
        encoding="utf-8",
    )
    router.write_text(
        "from ..memory.fractal_mesh.base import FractalMesh\n",
        encoding="utf-8",
    )
    quantum_dir = (
        tmp_path / "Aetherra" / "aetherra_core" / "memory" / "QuantumEnhancedMemoryEngine"
    )
    return launcher, introspector, router, quantum_dir


def test_unicode_compatibility_fixes_use_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    launcher, introspector, router, quantum_dir = _create_unicode_tree(tmp_path)
    plans, directories = fix_unicode_issues.plan_unicode_compatibility_fixes(tmp_path)
    pending = fix_unicode_issues._guardian_preflight_unicode_fixes(
        project_root=tmp_path,
        plans=plans,
        directories_to_create=directories,
    )
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = fix_unicode_issues.apply_unicode_compatibility_fixes(tmp_path)
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert "[OK]" in launcher.read_text(encoding="utf-8")
    assert "Aetherra.aetherra_core.memory.fractal_mesh.base" in introspector.read_text(
        encoding="utf-8"
    )
    assert "Aetherra.aetherra_core.memory.fractal_mesh.base" in router.read_text(
        encoding="utf-8"
    )
    assert (quantum_dir / "quantum_memory_engine.py").exists()
    assert (quantum_dir / "__init__.py").exists()
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.unicode_compatibility_fix"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "aetherra_os_launcher.py" not in ledger_text
    assert "quantum_memory_engine.py" not in ledger_text


def test_unicode_compatibility_fixes_deny_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    launcher, introspector, router, quantum_dir = _create_unicode_tree(tmp_path)
    originals = {
        "launcher": launcher.read_text(encoding="utf-8"),
        "introspector": introspector.read_text(encoding="utf-8"),
        "router": router.read_text(encoding="utf-8"),
    }

    result = fix_unicode_issues.apply_unicode_compatibility_fixes(tmp_path)
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert launcher.read_text(encoding="utf-8") == originals["launcher"]
    assert introspector.read_text(encoding="utf-8") == originals["introspector"]
    assert router.read_text(encoding="utf-8") == originals["router"]
    assert not quantum_dir.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"


def test_set_utf8_environment_only_changes_current_process(monkeypatch):
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)
    monkeypatch.delenv("PYTHONUTF8", raising=False)

    fix_unicode_issues.set_utf8_environment()

    assert os.environ["PYTHONIOENCODING"] == "utf-8"
    assert os.environ["PYTHONUTF8"] == "1"

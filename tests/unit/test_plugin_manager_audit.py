# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import importlib.util
import json
import time

import pytest

import Aetherra.aetherra_core.plugins.plugin_manager as plugin_manager_module
import Aetherra.homeostasis.homeostasis_core as homeostasis_core
import Aetherra.security.api_keys as api_keys
from Aetherra.guardian import ContainmentAction, IntentDeclaration
from Aetherra.guardian.containment import record_containment


def test_execute_plugin_writes_security_audit_entry(monkeypatch, tmp_path):
    audit_path = tmp_path / "plugin_audit.jsonl"
    monkeypatch.setenv("AETHERRA_SECURITY_AUDIT_PATH", str(audit_path))
    monkeypatch.setattr(
        plugin_manager_module, "has_capability", lambda requester, capability: False
    )

    manager = plugin_manager_module.PluginManager()
    manager.plugins["demo"] = object()
    manager._plugin_modules["demo"] = None

    assert manager.execute_plugin("demo") is None
    assert audit_path.exists()

    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["event_type"] == "plugin_denied"
    assert entry["plugin_name"] == "demo"
    assert entry["reason"] == "missing_capability"


def test_plugin_execution_passes_through_guardian(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setattr(plugin_manager_module, "has_capability", lambda *_args: True)

    class DemoPlugin:
        def execute(self):
            return "ok"

    manager = plugin_manager_module.PluginManager()
    manager.plugins["demo"] = DemoPlugin()
    manager._plugin_modules["demo"] = None

    assert manager.execute_plugin("demo") == "ok"

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    guardian_entry = next(
        entry for entry in entries if entry.get("event_type") == "guardian_decision"
    )
    assert guardian_entry["details"]["intent"]["action"] == "plugin.execute"
    assert guardian_entry["details"]["decision"]["status"] == "allow_limited"


def test_plugin_load_passes_through_guardian(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setattr(plugin_manager_module, "has_capability", lambda *_args: True)

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    (plugins_dir / "loadable.py").write_text(
        '"""plugin source should not appear in guardian audit: TOP_SECRET_LOAD_TOKEN"""\n'
        "class LoadablePlugin:\n"
        "    def execute(self):\n"
        "        return 'loaded'\n",
        encoding="utf-8",
    )

    manager = plugin_manager_module.PluginManager(plugins_dir=str(plugins_dir))

    assert manager.load_plugin("loadable") is True
    assert manager.execute_plugin("loadable") == "loaded"

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    raw_audit = audit_path.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in raw_audit.splitlines() if line.strip()]
    load_entry = next(
        entry
        for entry in entries
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "plugin.load"
    )

    assert load_entry["details"]["intent"]["capabilities"] == ["plugin:load"]
    assert load_entry["details"]["risk"]["factors"] == ["plugin_loading"]
    assert load_entry["details"]["decision"]["status"] == "allow_limited"
    assert "TOP_SECRET_LOAD_TOKEN" not in raw_audit


def test_plugin_load_denied_before_import_when_capability_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setattr(plugin_manager_module, "has_capability", lambda *_args: False)

    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    marker_path = tmp_path / "import_marker.txt"
    (plugins_dir / "blocked.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(marker_path)!r}).write_text('imported', encoding='utf-8')\n"
        "class BlockedPlugin:\n"
        "    def execute(self):\n"
        "        return 'blocked'\n",
        encoding="utf-8",
    )

    manager = plugin_manager_module.PluginManager(plugins_dir=str(plugins_dir))

    assert manager.load_plugin("blocked") is False
    assert marker_path.exists() is False
    assert manager.plugin_states["blocked"] == plugin_manager_module.PluginState.DISABLED

    audit_path = tmp_path / ".aetherra" / "security" / "plugin_audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    denied_entry = next(entry for entry in entries if entry["event_type"] == "plugin_denied")

    assert denied_entry["plugin_name"] == "blocked"
    assert denied_entry["reason"] == "missing_capability"
    assert denied_entry["details"]["capability"] == "plugin:load"


def test_plugin_disable_containment_unloads_and_blocks_execution(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setattr(plugin_manager_module, "has_capability", lambda *_args: True)

    class DemoPlugin:
        def execute(self):
            return "ok"

    manager = plugin_manager_module.PluginManager()
    manager.plugins["demo"] = DemoPlugin()
    manager._plugin_modules["demo"] = object()
    intent = IntentDeclaration(
        requester="plugin:demo",
        subsystem="plugin_manager",
        action="plugin.execute",
        target="demo",
        purpose="Execute plugin through PluginManager",
        capabilities=("execute",),
        evidence=("plugin:demo",),
    )
    record_containment(
        intent,
        ContainmentAction.DISABLE_PLUGIN,
        reason="unsafe_plugin",
    )

    assert manager.execute_plugin("demo") is None
    assert "demo" not in manager.plugins
    assert "demo" not in manager._plugin_modules
    assert manager.plugin_states["demo"] == plugin_manager_module.PluginState.DISABLED


def test_plugin_block_containment_blocks_without_loading(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setattr(plugin_manager_module, "has_capability", lambda *_args: True)

    manager = plugin_manager_module.PluginManager()
    intent = IntentDeclaration(
        requester="plugin:demo",
        subsystem="plugin_manager",
        action="plugin.execute",
        target="demo",
        purpose="Execute plugin through PluginManager",
        capabilities=("execute",),
        evidence=("plugin:demo",),
    )
    record_containment(
        intent,
        ContainmentAction.BLOCK_ACTION,
        reason="unsafe_plugin",
    )

    assert manager.execute_plugin("demo") is None
    assert manager.plugin_states["demo"] == plugin_manager_module.PluginState.DISABLED


def test_default_audit_path_uses_workspace_security_dir(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.delenv("AETHERRA_SECURITY_AUDIT_PATH", raising=False)
    monkeypatch.setattr(
        plugin_manager_module, "has_capability", lambda requester, capability: False
    )

    manager = plugin_manager_module.PluginManager()
    manager.plugins["demo"] = object()
    manager._plugin_modules["demo"] = None

    assert manager.execute_plugin("demo") is None

    expected_path = workspace_root / ".aetherra" / "security" / "plugin_audit.jsonl"
    assert expected_path.exists()


def test_security_system_writes_central_audit_events(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.delenv("AETHERRA_SECURITY_AUDIT_PATH", raising=False)

    from Aetherra.aetherra_core.system import security_system

    security_system.append_security_audit_entry(
        "plugin",
        "plugin_denied",
        reason="missing_capability",
        details={"capability": "execute"},
    )

    expected_path = workspace_root / ".aetherra" / "security" / "audit.jsonl"
    assert expected_path.exists()
    lines = [
        json.loads(line)
        for line in expected_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert lines[0]["event_type"] == "plugin_denied"


def test_plugin_execution_is_blocked_in_safe_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_SAFE_MODE", "1")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))

    manager = plugin_manager_module.PluginManager()
    manager.plugins["demo"] = object()
    manager._plugin_modules["demo"] = None

    assert manager.execute_plugin("demo") is None

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    assert audit_path.exists()
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert entries[-1]["event_type"] == "plugin_denied"
    assert entries[-1]["reason"] == "safe_mode"


def test_api_keys_fail_closed_in_safe_mode(monkeypatch):
    monkeypatch.setenv("AETHERRA_SAFE_MODE", "1")
    monkeypatch.setattr(api_keys, "_cache", {})

    assert api_keys.get_key("demo_key") is None

    with pytest.raises(RuntimeError, match="safe mode"):
        api_keys.set_key("demo_key", "value")


def test_emergency_lockdown_enables_safe_mode(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.delenv("AETHERRA_SAFE_MODE", raising=False)

    from Aetherra.aetherra_core.system import security_system

    security_system.trigger_emergency_lockdown(
        "suspected_compromise",
        details={"source": "test"},
    )

    assert security_system.is_safe_mode_enabled() is True
    assert (workspace_root / ".aetherra" / "security" / "safe_mode.json").exists()

    manager = plugin_manager_module.PluginManager()
    manager.plugins["demo"] = object()
    manager._plugin_modules["demo"] = None

    assert manager.execute_plugin("demo") is None


def test_homeostasis_cannot_override_security_restrictions(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("AETHERRA_SAFE_MODE", "1")

    controller = homeostasis_core.HomeostasisController()
    controller.set_mode(homeostasis_core.ControllerMode.ACTIVE)

    assert controller.mode == homeostasis_core.ControllerMode.OBSERVE_ONLY

    controller.emergency_stop()
    assert controller._emergency_stop is False


def test_security_lockdown_recovery_requires_authorized_actor(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))

    from Aetherra.aetherra_core.system import security_system

    security_system.trigger_emergency_lockdown("test", actor="security")

    try:
        security_system.clear_security_lockdown(actor="homeostasis")
    except PermissionError:
        pass
    else:
        raise AssertionError("homeostasis should not clear security lockdown")

    result = security_system.clear_security_lockdown(
        actor="security",
        reason="manual_recovery",
        recovery_context={"approved_by": "security", "source": "test"},
    )
    assert result["cleared"] is True
    assert security_system.is_safe_mode_enabled() is False


def test_tampered_lockdown_state_is_treated_as_unsafe(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.delenv("AETHERRA_SAFE_MODE", raising=False)

    from Aetherra.aetherra_core.system import security_system

    security_system.trigger_emergency_lockdown("tamper_test", actor="security")
    state_path = workspace_root / ".aetherra" / "security" / "safe_mode.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["enabled"] = False
    state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert security_system.is_safe_mode_enabled() is False


def test_unauthorized_security_state_change_is_audited(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))

    from Aetherra.aetherra_core.system import security_system

    try:
        security_system.trigger_emergency_lockdown("blocked", actor="homeostasis")
    except PermissionError:
        pass
    else:
        raise AssertionError("unauthorized actor should be denied")

    audit_path = workspace_root / ".aetherra" / "security" / "audit.jsonl"
    assert audit_path.exists()
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    denied_entry = next(
        entry
        for entry in entries
        if entry.get("event_type") == "security_action_denied"
    )
    assert denied_entry["actor"] == "homeostasis"
    assert denied_entry["reason"] == "unauthorized_actor"


def test_plugin_execution_denies_when_capability_check_errors(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.delenv("AETHERRA_SAFE_MODE", raising=False)
    monkeypatch.setattr(
        plugin_manager_module,
        "has_capability",
        lambda requester, capability: (_ for _ in ()).throw(
            RuntimeError("capability service unavailable")
        ),
    )

    manager = plugin_manager_module.PluginManager()
    manager.plugins["demo"] = object()
    manager._plugin_modules["demo"] = None

    assert manager.execute_plugin("demo") is None

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    assert audit_path.exists()
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    entry = entries[-1]
    assert entry["event_type"] == "plugin_denied"
    assert entry["reason"] == "capability_check_failed"


def test_lockdown_recovery_requires_recovery_context(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))

    from Aetherra.aetherra_core.system import security_system

    security_system.trigger_emergency_lockdown("test", actor="security")

    try:
        security_system.clear_security_lockdown(actor="security")
    except ValueError:
        pass
    else:
        raise AssertionError("recovery should require a recovery context")

    audit_path = workspace_root / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(
        entry.get("event_type") == "security_recovery_denied" for entry in entries
    )


def test_lockdown_recovery_fails_closed_when_audit_is_tampered(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(workspace_root))

    from Aetherra.aetherra_core.system import security_system
    from Aetherra.security.audit_ledger import AuditLedgerError

    security_system.trigger_emergency_lockdown("test", actor="security")
    audit_path = workspace_root / ".aetherra" / "security" / "audit.jsonl"
    records = [json.loads(line) for line in audit_path.read_text("utf-8").splitlines()]
    records[0]["reason"] = "tampered"
    audit_path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )

    try:
        security_system.clear_security_lockdown(
            actor="security",
            reason="manual_recovery",
            recovery_context={"approved_by": "security"},
        )
    except AuditLedgerError:
        pass
    else:
        raise AssertionError("tampered audit ledger should block lockdown recovery")

    assert security_system.is_safe_mode_enabled() is True
    assert (workspace_root / ".aetherra" / "security" / "safe_mode.json").exists()


def _load_test_plugin(module_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_production_plugin_execution_uses_process_isolation(monkeypatch, tmp_path):
    module_path = tmp_path / "isolated_plugin.py"
    module_path.write_text(
        "class IsolatedPlugin:\n"
        "    def execute(self, value):\n"
        "        return {'result': value + 1}\n",
        encoding="utf-8",
    )
    module = _load_test_plugin(module_path, "isolated_plugin_success")
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_PLUGIN_ISOLATION", "process")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.delenv("AETHERRA_SAFE_MODE", raising=False)
    monkeypatch.setattr(plugin_manager_module, "has_capability", lambda *_args: True)

    manager = plugin_manager_module.PluginManager()
    manager.plugins["isolated"] = module.IsolatedPlugin()
    manager._plugin_modules["isolated"] = module

    assert manager.execute_plugin("isolated", 4) == {"result": 5}


def test_production_plugin_timeout_terminates_process(monkeypatch, tmp_path):
    module_path = tmp_path / "slow_isolated_plugin.py"
    marker_path = tmp_path / "late-side-effect.txt"
    module_path.write_text(
        "from pathlib import Path\n"
        "import time\n"
        "class SlowIsolatedPlugin:\n"
        "    def execute(self, marker):\n"
        "        time.sleep(0.5)\n"
        "        Path(marker).write_text('late', encoding='utf-8')\n",
        encoding="utf-8",
    )
    module = _load_test_plugin(module_path, "isolated_plugin_timeout")
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_PLUGIN_ISOLATION", "process")
    monkeypatch.setenv("AETHERRA_PLUGIN_MAX_RUNTIME_SEC", "0.1")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.delenv("AETHERRA_SAFE_MODE", raising=False)
    monkeypatch.setattr(plugin_manager_module, "has_capability", lambda *_args: True)

    manager = plugin_manager_module.PluginManager()
    manager.plugins["slow"] = module.SlowIsolatedPlugin()
    manager._plugin_modules["slow"] = module

    assert manager.execute_plugin("slow", str(marker_path)) is None
    time.sleep(0.6)
    assert not marker_path.exists()

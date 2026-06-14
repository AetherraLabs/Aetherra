# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import json

import Aetherra.aetherra_core.plugins.plugin_manager as plugin_manager_module
import Aetherra.homeostasis.homeostasis_core as homeostasis_core
import Aetherra.security.api_keys as api_keys


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

    try:
        api_keys.set_key("demo_key", "value")
    except RuntimeError as exc:
        assert "safe mode" in str(exc).lower()
    else:
        raise AssertionError("set_key should fail closed in safe mode")


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

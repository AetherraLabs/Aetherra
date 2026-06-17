import json

from Aetherra.aetherra_core.agents import base
from Aetherra.aetherra_core.agents.parser import AetherraCodeCompiler, PluginNode


class _MetaPlugins:
    def __init__(self):
        self.called = False

    def execute_meta_plugin(self, name, *args):
        self.called = True
        return f"meta:{name}:{len(args)}"


class _Stdlib:
    def __init__(self):
        self.called = False
        self.plugins = {"stdlib_demo": object()}

    def execute_plugin_action(self, plugin_name, action, memory_system=None):
        self.called = True
        return f"stdlib:{plugin_name}:{action}"


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def _interpreter(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    interpreter = base.AetherraInterpreter()
    interpreter.stdlib = None
    return interpreter


def test_legacy_plugin_dispatch_is_guardian_audited_without_args(
    monkeypatch, tmp_path
):
    called = False

    def _plugin(*args):
        nonlocal called
        called = True
        return f"ran:{len(args)}"

    monkeypatch.setattr(base, "PLUGIN_REGISTRY", {"demo": _plugin})
    interpreter = _interpreter(monkeypatch, tmp_path)

    result = interpreter._handle_plugin("plugin: demo do-not-audit-this-arg")
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in ledger_text.splitlines() if line.strip()]

    assert called is True
    assert result == "[Plugin:demo] ran:1"
    assert "do-not-audit-this-arg" not in ledger_text
    assert entries[-1]["details"]["intent"]["action"] == "agent.legacy_plugin_execute"


def test_legacy_plugin_denial_blocks_dispatch(monkeypatch, tmp_path):
    called = False

    def _plugin(*args):
        nonlocal called
        called = True
        return "should-not-run"

    monkeypatch.setattr(base, "PLUGIN_REGISTRY", {"demo": _plugin})
    interpreter = _interpreter(monkeypatch, tmp_path)
    _guardian_env(monkeypatch, tmp_path, requester="external-agent", strict=True)

    result = interpreter._handle_plugin("plugin: demo blocked")

    assert result.startswith("[Guardian] Plugin execution denied:")
    assert called is False


def test_stdlib_plugin_denial_blocks_dispatch(monkeypatch, tmp_path):
    interpreter = _interpreter(monkeypatch, tmp_path)
    stdlib = _Stdlib()
    interpreter.stdlib = stdlib
    _guardian_env(monkeypatch, tmp_path, requester="external-agent", strict=True)

    result = interpreter._handle_plugin("plugin: stdlib_demo blocked-action")

    assert result.startswith("[Guardian] Plugin execution denied:")
    assert stdlib.called is False


def test_meta_plugin_denial_blocks_dispatch(monkeypatch, tmp_path):
    interpreter = _interpreter(monkeypatch, tmp_path)
    meta_plugins = _MetaPlugins()
    interpreter.meta_plugins = meta_plugins
    _guardian_env(monkeypatch, tmp_path, requester="external-agent", strict=True)

    result = interpreter._handle_meta_plugin("meta: demo blocked")

    assert result.startswith("[Guardian] Meta-plugin execution denied:")
    assert meta_plugins.called is False


def test_enhanced_plugin_dispatch_audits_parameter_keys_not_values(
    monkeypatch, tmp_path
):
    called = False

    def _plugin(**kwargs):
        nonlocal called
        called = True
        return f"ran:{sorted(kwargs)}"

    monkeypatch.setattr(base, "PLUGIN_REGISTRY", {"demo": _plugin})
    interpreter = _interpreter(monkeypatch, tmp_path)

    result = interpreter._parse_enhanced_plugin(
        'plugin: demo(secret="do-not-audit-this-value")'
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")

    assert called is True
    assert "Enhanced Plugin Execution" in result
    assert "do-not-audit-this-value" not in ledger_text
    assert "agent.legacy_plugin_execute" in ledger_text


def test_compiled_plugin_load_denial_blocks_dispatch(monkeypatch, tmp_path):
    called = False

    def _plugin(*args):
        nonlocal called
        called = True
        return "should-not-run"

    monkeypatch.setattr(base, "PLUGIN_REGISTRY", {"demo": _plugin})
    interpreter = _interpreter(monkeypatch, tmp_path)
    _guardian_env(monkeypatch, tmp_path, requester="external-agent", strict=True)

    result = interpreter.load_plugin("demo", "do-not-audit-this-action")

    assert result.startswith("[Guardian] Plugin load denied:")
    assert called is False


def test_compiled_plugin_load_audits_without_action_payload(monkeypatch, tmp_path):
    monkeypatch.setattr(base, "PLUGIN_REGISTRY", {})
    interpreter = _interpreter(monkeypatch, tmp_path)

    result = interpreter.load_plugin("demo", "do-not-audit-this-action")
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")

    assert "Guarded compiled plugin block accepted" in result
    assert "do-not-audit-this-action" not in ledger_text
    assert "agent.compiled_plugin_load" in ledger_text


def test_plugin_compiler_escapes_generated_load_literals():
    compiler = AetherraCodeCompiler()
    node = PluginNode(
        type="plugin",
        line=1,
        plugin_name="demo'plugin",
        actions=[],
    )

    generated = compiler.compile_plugin(node)

    assert generated == 'interpreter.load_plugin("demo\'plugin", \'\')'

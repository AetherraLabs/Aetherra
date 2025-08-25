import os


def _make_plugin(tmp_path, name, manifest_overrides=None, main_py_body=None):
    pdir = tmp_path / "lyrixa_plugins" / name
    pdir.mkdir(parents=True)
    manifest = {
        "name": name,
        "version": "1.0.0",
        "entry_point": "main.py",
        "timeout_ms": 500,
    }
    if manifest_overrides:
        manifest.update(manifest_overrides)
    (pdir / "manifest.json").write_text(__import__("json").dumps(manifest))
    (pdir / "main.py").write_text(
        main_py_body
        or (
            """
def execute(command, **kwargs):
    return {"ok": True, "kwargs": kwargs}
"""
        ).strip()
    )
    return pdir


def _new_system(tmp_path):
    import Aetherra.plugins.core.plugin_system as ps

    # Monkeypatch Path used in ctor to point to tmp_path
    ps.Path = lambda p="": tmp_path / (p or "")
    return ps.LyrixaPluginSystem()


def test_policy_allow_untrusted_secret_override(tmp_path, monkeypatch):
    _make_plugin(
        tmp_path,
        "secret_plugin",
        manifest_overrides={"data_classification": "secret"},
    )

    system = _new_system(tmp_path)
    system._discover_plugins()
    system.activate_plugin("secret_plugin")

    # Without override/env, should block
    if "AETHERRA_ALLOW_UNTRUSTED_SECRET" in os.environ:
        monkeypatch.delenv("AETHERRA_ALLOW_UNTRUSTED_SECRET", raising=False)
    out = system.execute_plugin("secret_plugin", "any")
    assert out.get("success") is False
    assert out.get("error") == "classification_violation"

    # With policy override, should pass
    system.set_policy({"allow_untrusted_secret": True})
    out2 = system.execute_plugin("secret_plugin", "any")
    assert out2.get("success") is True


def test_policy_max_executions_budget(tmp_path):
    _make_plugin(tmp_path, "budget_plugin")
    system = _new_system(tmp_path)
    system._discover_plugins()
    system.activate_plugin("budget_plugin")

    system.set_policy({"max_executions": 1})

    ok1 = system.execute_plugin("budget_plugin", "ping")
    assert ok1.get("success") is True

    # Second call should be rejected by budget
    ok2 = system.execute_plugin("budget_plugin", "ping")
    assert ok2.get("success") is False
    assert ok2.get("error") == "policy_exhausted"

import pytest

from aetherra_script_service import AetherScriptService


class FakePlugin:
    def __init__(self, version: str):
        class Manifest:
            def __init__(self, v: str):
                self.version = v

        self.manifest = Manifest(version)


class FakePluginManager:
    def __init__(self, mapping):
        # dict name -> FakePlugin
        self.installed_plugins = dict(mapping)


@pytest.mark.asyncio
async def test_require_plugin_semver_satisfied():
    svc = AetherScriptService()
    await svc.initialize()
    plugins = FakePluginManager({"demo": FakePlugin("1.2.3")})

    script = 'require plugin demo version="^1.2"\ngoal "x"\n'
    result = await svc.execute_script_content(
        script, filename="<test>", context={"plugins": plugins}
    )
    assert result["success"] is True
    payload = result["result"]
    req = payload["results"][0]
    assert req["type"] == "require" and req["kind"] == "plugin"
    assert req["ok"] is True
    # exposed in payload
    assert any(r.get("name") == "demo" for r in payload.get("requires", []))


@pytest.mark.asyncio
async def test_require_plugin_semver_unsatisfied_strict(monkeypatch):
    svc = AetherScriptService()
    await svc.initialize()
    plugins = FakePluginManager({"demo": FakePlugin("1.2.3")})

    # ~1.3 requires >=1.3.0 <1.4.0, but we have 1.2.3, so fail. Strict should error.
    script = 'require plugin demo version="~1.3"\n'
    monkeypatch.setenv("AETHERRA_REQUIRE_STRICT", "1")
    result = await svc.execute_script_content(
        script, filename="<test>", context={"plugins": plugins}
    )
    assert result["success"] is False
    assert "require plugin failed" in result.get("error", "")
    monkeypatch.delenv("AETHERRA_REQUIRE_STRICT", raising=False)


@pytest.mark.asyncio
async def test_require_module_present():
    svc = AetherScriptService()
    await svc.initialize()
    # pip should exist in most Python environments
    script = 'require module pip\ngoal "x"\n'
    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    req = result["result"]["results"][0]
    assert req["type"] == "require" and req["kind"] == "module"
    assert req["ok"] is True


@pytest.mark.asyncio
async def test_require_module_version_unsatisfied_non_strict():
    svc = AetherScriptService()
    await svc.initialize()
    # Ask for an absurd version so it fails, but without strict it should not error overall
    script = 'require module pip version="9999.0.0"\n'
    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    req = result["result"]["results"][0]
    assert req["ok"] is False


@pytest.mark.asyncio
async def test_payload_exposes_policy_and_requires():
    svc = AetherScriptService()
    await svc.initialize()
    script = "policy max_executions=2 allow_untrusted_secret=true\nrequire module pip\n"
    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]
    assert payload.get("policy", {}).get("max_executions") == 2
    assert payload.get("policy", {}).get("allow_untrusted_secret") is True
    assert any(r.get("kind") == "module" for r in payload.get("requires", []))

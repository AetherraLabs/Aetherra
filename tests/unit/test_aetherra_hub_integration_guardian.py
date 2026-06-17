import json

import pytest

from Aetherra.aetherra_hub_integration import AetherraHubIntegration


class _FakeHubClient:
    def __init__(self, details, content):
        self.details = details
        self.content = content

    async def get_plugin_details(self, plugin_id):
        return dict(self.details, id=plugin_id)

    async def download_plugin(self, plugin_id, version="latest"):
        return self.content


def _integration(monkeypatch, tmp_path, *, details=None, content=None):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "hub-integration-test")
    integration = AetherraHubIntegration(project_root=str(tmp_path))
    integration.client = _FakeHubClient(
        details
        or {
            "name": "Hub Plugin",
            "version": "1.0.0",
            "type": "bundle",
            "description": "secret='do-not-audit-hub-description'",
        },
        content or b"do-not-audit-package-bytes",
    )
    return integration


def _ledger_text(tmp_path):
    return (tmp_path / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _guardian_entries(tmp_path):
    return [
        json.loads(line)
        for line in _ledger_text(tmp_path).splitlines()
        if line.strip()
    ]


@pytest.mark.asyncio
async def test_hub_integration_install_passes_through_guardian(monkeypatch, tmp_path):
    integration = _integration(monkeypatch, tmp_path)

    result = await integration.install_plugin_from_hub("hub_guarded_plugin", "1.0.0")
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "hub.plugin_install"
    )
    ledger_text = _ledger_text(tmp_path)

    assert result["success"] is True
    assert (tmp_path / "plugins" / "hub_guarded_plugin" / "package.zip").exists()
    assert guardian_entry["details"]["intent"]["capabilities"] == [
        "plugin:install",
        "fs:write",
    ]
    assert "plugin_installation" in guardian_entry["details"]["risk"]["factors"]
    assert "do-not-audit-hub-description" not in ledger_text
    assert "do-not-audit-package-bytes" not in ledger_text


@pytest.mark.asyncio
async def test_hub_integration_install_denied_before_write_when_capability_missing(
    monkeypatch, tmp_path
):
    integration = _integration(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")

    result = await integration.install_plugin_from_hub("blocked_hub_plugin", "1.0.0")
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "hub.plugin_install"
    )

    assert result["success"] is False
    assert "Guardian denied" in result["error"]
    assert (tmp_path / "plugins" / "blocked_hub_plugin" / "package.zip").exists() is False
    assert guardian_entry["details"]["decision"]["status"] == "deny"
    assert guardian_entry["details"]["decision"]["reason"] == "missing_capability"


@pytest.mark.asyncio
async def test_hub_integration_uninstall_requires_guardian_approval_before_delete(
    monkeypatch, tmp_path
):
    integration = _integration(monkeypatch, tmp_path)
    plugin_dir = tmp_path / "plugins" / "installed_hub_plugin"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "manifest.json").write_text("{}", encoding="utf-8")
    integration.local_plugins["installed_hub_plugin"] = {
        "path": str(plugin_dir),
        "installed_from_hub": True,
    }

    result = await integration.uninstall_plugin("installed_hub_plugin")
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "hub.plugin_uninstall"
    )

    assert result["success"] is False
    assert "Guardian denied" in result["error"]
    assert plugin_dir.exists()
    assert guardian_entry["details"]["decision"]["status"] == "require_approval"

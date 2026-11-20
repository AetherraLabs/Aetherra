from types import SimpleNamespace

import pytest

from aetherra_os_launcher import AetherraOSLauncher


@pytest.mark.asyncio
async def test_normal_launcher_requests_loopback_binding(monkeypatch, tmp_path):
    from aetherra_hub import compat

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_SKIP_LAUNCHER_AI_DEFAULTS", "1")
    monkeypatch.setenv("AETHERRA_HUB_URL", "http://localhost:43210")
    calls = []

    def start(port, **kwargs):
        calls.append((port, kwargs))
        return SimpleNamespace(is_running=lambda: False)

    monkeypatch.setattr(compat, "start_hub_server", start)
    launcher = AetherraOSLauncher()
    await launcher._load_aetherra_hub({"hub_enabled": True, "presence_enabled": True})
    assert calls == [(43210, {"host": "127.0.0.1"})]

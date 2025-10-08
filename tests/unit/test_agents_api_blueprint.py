import os
import socket

import requests

from aetherra_hub.compat import AetherraHubServer


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_agents_api_disabled_then_enabled(monkeypatch):
    port = _free_port()
    base = f"http://localhost:{port}"
    srv = AetherraHubServer(port)
    srv.start_server()

    # Disabled path -> 501
    r = requests.get(f"{base}/api/agents", timeout=3)
    assert r.status_code in (403, 501)

    # Enable + token required
    monkeypatch.setenv("AETHERRA_AGENTS_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AGENTS_API_TOKEN", "tok")

    # Minimal orchestrator status via registry mock
    from aetherra_service_registry import get_service_registry

    class _MockEng:
        def get_system_status(self):
            return {"agent_orchestrator": {"total_agents": 0, "pending_tasks": 0}}

    import asyncio

    async def _register():
        reg = await get_service_registry()
        await reg.register_service("aetherra_engine", _MockEng())

    asyncio.run(_register())

    r2 = requests.get(
        f"{base}/api/agents", headers={"X-Aetherra-Token": "tok"}, timeout=3
    )
    assert r2.status_code == 200
    data = r2.json()
    assert data.get("ok") is True
    assert "orchestrator" in data

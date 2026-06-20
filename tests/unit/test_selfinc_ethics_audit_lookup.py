# Standard library imports
import asyncio
import socket

# Third party imports
import pytest
import requests

# Aetherra imports
from aetherra_hub.compat import start_hub_server
from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)
from aetherra_service_registry import get_service_registry, register_service


def _free_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture
def selfinc_base_url(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path / "state"))
    service = SelfIncorporationService(SelfIncorporationConfig())
    asyncio.run(register_service("self_incorporation", service))
    port = _free_tcp_port()
    server = start_hub_server(port=port)
    try:
        yield f"http://localhost:{port}/api/selfinc"
    finally:
        server.stop_server()
        registry = asyncio.run(get_service_registry())
        asyncio.run(registry.unregister_service("self_incorporation"))


def test_ethics_audit_lookup(selfinc_base_url):
    # Evaluate and get trace_id
    resp = requests.post(
        f"{selfinc_base_url}/ethics/evaluate",
        json={
            "action": "register_plugin",
            "target": {
                "file_id": "private-plugin-id",
                "declared_capabilities": ["private-network-capability"],
            },
        },
        timeout=10,
    )
    assert resp.status_code == 200
    trace_id = resp.json()["trace_id"]
    # Lookup audit
    audit = requests.get(f"{selfinc_base_url}/ethics/audit/{trace_id}", timeout=10)
    assert audit.status_code == 200
    data = audit.json()
    assert data["trace_id"] == trace_id
    assert "ethics_overall" in data
    assert "risk_level" in data
    assert "result" in data
    assert "private-plugin-id" not in audit.text
    assert "private-network-capability" not in audit.text

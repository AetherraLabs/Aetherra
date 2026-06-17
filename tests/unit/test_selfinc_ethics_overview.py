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


def post_evaluate(base_url, action, target):
    resp = requests.post(
        f"{base_url}/ethics/evaluate",
        json={"action": action, "target": target},
        timeout=10,
    )
    assert resp.status_code == 200
    return resp.json()


def get_overview(base_url):
    resp = requests.get(f"{base_url}/ethics/overview", timeout=10)
    assert resp.status_code == 200
    return resp.json()


def test_ethics_overview_counts(selfinc_base_url):
    # High risk
    post_evaluate(
        selfinc_base_url,
        "register_plugin",
        {
            "file_id": "plugin1",
            "declared_capabilities": ["network", "exec", "filesystem"],
        },
    )
    # Medium risk
    post_evaluate(
        selfinc_base_url,
        "register_plugin",
        {
            "file_id": "plugin2",
            "declared_capabilities": ["ui"],
            "complexity_score": 0.6,
        },
    )
    overview = get_overview(selfinc_base_url)
    stats = overview["stats"]
    assert stats["total_decisions"] >= 2
    assert stats["avg_score"] > 0
    assert overview["risk_assessment"]["high_risk_actions"] >= 1
    assert overview["risk_assessment"]["medium_risk_actions"] >= 1

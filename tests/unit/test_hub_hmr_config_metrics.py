# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import socket

import pytest

requests = pytest.importorskip("requests")

import aetherra_hub.compat as hub_mod

FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class MockKernel:
    def get_status(self):
        return {"running": True}


class MockHMR:
    def get_config_metrics(self):
        return {
            "enabled": True,
            "strict": True,
            "allowed_sources_count": 2,
            "audit_max_bytes": 5242880,
            "audit_max_backups": 3,
        }


async def _register_mock_services(kernel, hmr):
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    await reg.register_service("kernel_loop", kernel)
    await reg.register_service("hmr_controller", hmr)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_prometheus_and_json_expose_hmr_config_metrics():
    asyncio.run(_register_mock_services(MockKernel(), MockHMR()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"

    # Prometheus text should include HMR config gauges
    r = requests.get(f"{base}/metrics", timeout=3)
    assert r.status_code == 200
    body = r.text
    assert "aetherra_hmr_enabled" in body
    assert "aetherra_hmr_strict" in body
    assert "aetherra_hmr_allowed_sources_count" in body
    assert "aetherra_hmr_audit_max_bytes" in body
    assert "aetherra_hmr_audit_max_backups" in body

    # JSON kernel metrics should include an 'hmr' object
    rj = requests.get(f"{base}/api/kernel/metrics", timeout=3)
    assert rj.status_code == 200
    data = rj.json()
    assert isinstance(data, dict)
    hmr = data.get("hmr", {})
    assert isinstance(hmr, dict)
    # Spot-check a couple values
    assert hmr.get("enabled") is True
    assert hmr.get("strict") is True

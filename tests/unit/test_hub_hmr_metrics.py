# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio
import socket

# Third party imports
import pytest

# Aetherra imports
import aetherra_hub.compat as hub_mod

requests = pytest.importorskip("requests")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class MockKernel:
    def get_status(self):
        # Minimal kernel status including inflight map
        return {
            "running": True,
            "inflight": {
                "engine": 0,
                "adapter:plugin": 3,
            },
            "queue_sizes": {"high_priority": 0, "normal_priority": 0, "background": 0},
        }


class MockHMR:
    def get_audit_counters(self):
        # Minimal audit counters map for Prometheus emission
        return {"swapped": 2, "gated": 1}


async def _register_mock_services(kernel, hmr):
    # Aetherra imports
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
def test_prometheus_exposes_inflight_and_hmr_audit_counters():
    # Register mock kernel + HMR controller
    asyncio.run(_register_mock_services(MockKernel(), MockHMR()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    r = requests.get(f"{base}/metrics", timeout=3)
    assert r.status_code == 200
    body = r.text

    # In-flight gauges per target
    assert 'aetherra_kernel_inflight_current{target="engine"}' in body
    assert 'aetherra_kernel_inflight_current{target="adapter:plugin"}' in body

    # HMR audit counters
    assert 'aetherra_hmr_audit_total{event="swapped"}' in body
    assert 'aetherra_hmr_audit_total{event="gated"}' in body

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class MockKLM:
    def get_metrics(self):
        return {
            "loads_total": 3,
            "reloads_total": 2,
            "rollbacks_total": 1,
            "active_modules": 2,
            "per_module_active": {"modA": 1, "modB": 1},
        }


class MockKEB:
    def get_metrics(self):
        return {
            "events_published_total": 10,
            "events_delivered_total": 8,
            "events_dropped_burst": 2,
            "topic_backlog": {"topicX": 0, "topicY": 1},
        }


async def _register_mock_services():
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    # Register mock Module Manager and Event Bus services
    await reg.register_service("module_manager", MockKLM())
    await reg.register_service("event_bus", MockKEB())


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_prometheus_exposes_klm_and_keb_metrics():
    import asyncio

    # Register mock services
    asyncio.run(_register_mock_services())

    # Start hub server on a free port
    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    r = requests.get(f"{base}/metrics", timeout=3)
    assert r.status_code == 200
    body = r.text

    # KLM metrics
    assert "aetherra_klm_loads_total" in body
    assert "aetherra_klm_reloads_total" in body
    assert "aetherra_klm_rollbacks_total" in body
    assert "aetherra_klm_active_modules" in body
    assert 'aetherra_klm_active_module{module="modA"}' in body

    # KEB metrics
    assert "aetherra_keb_events_published_total" in body
    assert "aetherra_keb_events_delivered_total" in body
    assert "aetherra_keb_events_dropped_burst" in body
    assert 'aetherra_keb_topic_backlog{topic="topicX"}' in body

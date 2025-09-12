# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import socket

import pytest

import aetherra_hub.compat as hub_mod
from aetherra_event_bus import EventBus
from aetherra_module_manager import ModuleManager
from aetherra_service_registry import get_service_registry

requests = pytest.importorskip("requests")

FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _ensure_services_registered():
    reg = await get_service_registry()
    mm = ModuleManager(reg)
    eb = EventBus(reg)
    await reg.register_service("module_manager", mm)
    await reg.register_service("event_bus", eb)
    # Prime minimal metrics for non-empty responses
    await mm.load_module("m1", {"version": "1.0"})
    await eb.subscribe("topicK", "svc1")
    await eb.publish("topicK", {"hello": "world"})


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_klm_keb_status_and_metrics_endpoints():
    # Ensure services exist in the registry before starting the hub
    asyncio.run(_ensure_services_registered())

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"

    # KLM status
    r = requests.get(f"{base}/api/klm/status", timeout=3)
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, dict)
    assert isinstance(js.get("metrics"), dict)
    # KLM metrics
    r = requests.get(f"{base}/api/klm/metrics", timeout=3)
    assert r.status_code == 200
    jm = r.json()
    assert isinstance(jm, dict)
    assert "loads_total" in jm

    # KEB status
    r = requests.get(f"{base}/api/keb/status", timeout=3)
    assert r.status_code == 200
    es = r.json()
    assert isinstance(es, dict)
    assert isinstance(es.get("metrics"), dict)
    # KEB metrics
    r = requests.get(f"{base}/api/keb/metrics", timeout=3)
    assert r.status_code == 200
    em = r.json()
    assert isinstance(em, dict)
    assert "events_published_total" in em

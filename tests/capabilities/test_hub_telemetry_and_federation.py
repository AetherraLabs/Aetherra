# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Third party imports
import requests


def test_telemetry_and_federation_endpoints(signing_hub, monkeypatch):
    # Aetherra imports
    from aetherra_hub.blueprints import telemetry

    base, _ = signing_hub
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "synthetic-control-test")
    monkeypatch.setenv("AETHERRA_FEDERATION_ENABLED", "0")
    monkeypatch.setattr(telemetry, "_state", {"telemetry_received": 0})
    headers = {"X-Aetherra-Control-Token": "synthetic-control-test"}

    denied = requests.post(
        f"{base}/api/telemetry",
        json={"event": "ping"},
        timeout=5,
        allow_redirects=False,
    )
    assert denied.status_code == 401
    assert telemetry._state["telemetry_received"] == 0
    response = requests.post(
        f"{base}/api/telemetry",
        headers=headers,
        json={"event": "ping"},
        timeout=5,
        allow_redirects=False,
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    stats = requests.get(f"{base}/api/stats", timeout=5, allow_redirects=False)
    assert stats.status_code == 200
    assert stats.json()["telemetry_received"] == 1

    for path in ("announce", "sync"):
        response = requests.post(
            f"{base}/api/peers/{path}",
            headers=headers,
            timeout=5,
            allow_redirects=False,
        )
        assert response.status_code == 501
        assert response.json()["status"] == "federation_disabled"
    graph = requests.get(f"{base}/api/memory/graph", timeout=5, allow_redirects=False)
    assert graph.status_code == 501
    assert graph.json()["status"] == "memory_graph_disabled"

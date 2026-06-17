# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import socket

# Third party imports
import pytest

requests = pytest.importorskip("requests")

# Aetherra imports
import aetherra_hub.compat as hub_mod

FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_hub_runs_in_thread_and_handles_federation_and_telemetry(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.delenv("AETHERRA_NET_STRICT", raising=False)
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    # Find a free port for the hub
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()

    server = hub_mod.AetherraHubServer(port)
    ok = server.start_server()
    assert ok and server.is_running()

    base = f"http://localhost:{port}"

    # Health
    r = requests.get(f"{base}/health", timeout=3)
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"

    # Telemetry ingest
    r = requests.post(f"{base}/api/telemetry", json={"event": "unit_ping"}, timeout=3)
    assert r.status_code == 200

    # Stats should reflect telemetry
    r = requests.get(f"{base}/api/stats", timeout=3)
    assert r.status_code == 200
    stats = r.json()
    assert stats.get("telemetry_received", 0) >= 1

    # Federation: add a peer and announce/sync
    r = requests.post(f"{base}/api/peers", json={"url": f"{base}"}, timeout=3)
    assert r.status_code == 200

    r = requests.post(f"{base}/api/peers/announce", timeout=3)
    assert r.status_code in (200, 501)  # 501 if federation disabled

    r = requests.post(f"{base}/api/peers/sync", timeout=5)
    assert r.status_code in (200, 501)

    # Plugins listing includes federated view when enabled
    r = requests.get(f"{base}/api/plugins", timeout=3)
    assert r.status_code == 200

    # Memory graph optics may be disabled
    r = requests.get(f"{base}/api/memory/graph", timeout=3)
    assert r.status_code in (200, 501)

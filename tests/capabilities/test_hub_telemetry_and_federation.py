# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Third party imports
import pytest
import requests

# Aetherra imports
from aetherra_hub.compat import start_hub_server

HAS_FLASK = True
try:
    # Third party imports
    import flask  # noqa: F401
except Exception:
    HAS_FLASK = False


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_telemetry_and_federation_endpoints():
    # Start hub server on a test port
    server = start_hub_server(port=3011)
    assert server.is_running()

    # Telemetry ingest
    r = requests.post("http://localhost:3011/api/telemetry", json={"event": "ping"})
    assert r.status_code == 200

    # Stats reflect telemetry
    s = requests.get("http://localhost:3011/api/stats").json()
    assert s.get("telemetry_received", 0) >= 1

    # Federation endpoints should respond (even if disabled)
    a = requests.post("http://localhost:3011/api/peers/announce")
    assert a.status_code in (200, 501)
    y = requests.post("http://localhost:3011/api/peers/sync")
    assert y.status_code in (200, 501)

    # Memory graph optics responds (may be disabled)
    g = requests.get("http://localhost:3011/api/memory/graph")
    assert g.status_code in (200, 501)

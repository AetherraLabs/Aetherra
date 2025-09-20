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
def test_quantum_status_endpoint_basic():
    # Start hub server on a test port
    server = start_hub_server(port=3012)
    assert server.is_running()

    r = requests.get("http://localhost:3012/api/quantum/status", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # Best-effort keys
    assert "available" in data
    assert "backend" in data

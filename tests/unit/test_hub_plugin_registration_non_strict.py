# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_register_allows_unsigned_when_non_strict(monkeypatch):
    # Ensure strict signing mode is off
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "0")

    # Find a free port for the hub
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()

    server = hub_mod.AetherraHubServer(port)
    ok = server.start_server()
    assert ok and server.is_running()

    base = f"http://localhost:{port}"

    # Attempt to register without signature/pubkey should be allowed in non-strict mode
    payload = {
        "name": "unsigned_non_strict_test_plugin",
        "version": "0.1.0",
        "description": "Unsigned plugin allowed in non-strict mode",
    }
    r = requests.post(f"{base}/api/plugins/register", json=payload, timeout=3)
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "success"

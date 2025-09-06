# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_register_rejects_invalid_manifest_schema(monkeypatch):
    # Non-strict signing here; schema should still be enforced
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "0")

    # Free port
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()

    server = hub_mod.AetherraHubServer(port)
    ok = server.start_server()
    assert ok and server.is_running()

    base = f"http://localhost:{port}"

    # Invalid permission value should fail schema validation
    payload = {
        "name": "bad_manifest_plugin",
        "version": "0.1.0",
        "entry_point": "main.py",
        "permissions": ["not-a-permission"],
    }
    r = requests.post(f"{base}/api/plugins/register", json=payload, timeout=3)
    assert r.status_code == 400
    data = r.json()
    assert data.get("error") == "manifest_invalid"

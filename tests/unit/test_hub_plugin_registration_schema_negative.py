# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import socket

# Third party imports
import pytest

# Aetherra imports
import aetherra_hub.compat as hub_mod

requests = pytest.importorskip("requests")
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

    try:
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
    finally:
        server.stop_server()

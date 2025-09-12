# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import socket

import pytest

import aetherra_hub.compat as hub_mod

requests = pytest.importorskip("requests")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_register_rejects_invalid_signature_when_strict(monkeypatch):
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")

    # Free port
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()

    server = hub_mod.AetherraHubServer(port)
    ok = server.start_server()
    assert ok and server.is_running()

    base = f"http://localhost:{port}"

    # Provide bogus signature/pubkey; hub should attempt verify and reject
    payload = {
        "name": "bogus_sig_plugin",
        "version": "0.1.0",
        "entry_point": "main.py",
        "signature": "ed25519:deadbeef",
        "pubkey": "ed25519:cafebabe",
    }
    r = requests.post(f"{base}/api/plugins/register", json=payload, timeout=3)
    # If signature verification library is unavailable, hub returns error accordingly
    assert r.status_code in (400, 500)
    data = r.json()
    assert any(k in data for k in ("error", "status"))

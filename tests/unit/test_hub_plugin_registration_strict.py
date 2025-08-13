import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_register_requires_signature_when_strict(monkeypatch):
    # Enable strict signing mode via env
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")

    # Find a free port for the hub
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()

    server = hub_mod.AetherraHubServer(port)
    ok = server.start_server()
    assert ok and server.is_running()

    base = f"http://localhost:{port}"

    # Attempt to register without signature/pubkey should be rejected with 400
    payload = {
        "name": "unsigned_test_plugin",
        "version": "0.1.0",
        "description": "Unsigned plugin used for strict-mode test",
    }
    r = requests.post(f"{base}/api/plugins/register", json=payload, timeout=3)
    assert r.status_code == 400

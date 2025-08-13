import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)

ps_mod = __import__(
    "Aetherra.security.plugin_signing",
    fromlist=["NACL", "generate_keypair", "sign_manifest"],
)  # type: ignore
NACL = getattr(ps_mod, "NACL", False)

generate_keypair = getattr(ps_mod, "generate_keypair", None)
sign_manifest = getattr(ps_mod, "sign_manifest", None)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
@pytest.mark.skipif(not NACL, reason="PyNaCl not available for signing")
def test_register_accepts_signed_manifest_when_strict(monkeypatch):
    # Enable strict signing mode via env
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")

    # Generate keys and sign manifest
    pub_b64, secret_b64 = generate_keypair()  # type: ignore[misc]
    base_manifest = {
        "name": "signed_strict_test_plugin",
        "version": "0.1.0",
        "description": "Signed plugin for strict-mode test",
    }
    signed = sign_manifest(base_manifest, secret_b64)  # type: ignore[misc]

    # Ensure signature fields exist
    assert signed.get("signature") and signed.get("pubkey")

    # Find a free port for the hub
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()

    server = hub_mod.AetherraHubServer(port)
    ok = server.start_server()
    assert ok and server.is_running()

    base = f"http://localhost:{port}"

    r = requests.post(f"{base}/api/plugins/register", json=signed, timeout=3)
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "success"

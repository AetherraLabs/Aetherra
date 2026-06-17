# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import importlib.util
import time

# Third party imports
import pytest

# Aetherra imports
from aetherra_hub.compat import AetherraHubServer

HAS_FLASK = importlib.util.find_spec("flask") is not None
HAS_NACL = importlib.util.find_spec("nacl") is not None


def _start_server(port=3011):
    server = AetherraHubServer(port)
    ok = server.start_server()
    assert ok
    # wait briefly for thread to start
    time.sleep(0.3)
    return server


def _post_json(url, payload):
    # Third party imports
    import requests

    return requests.post(url, json=payload, timeout=5)


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_register_unsigned_non_strict(monkeypatch):
    monkeypatch.delenv("AETHERRA_SIGNING_STRICT", raising=False)
    srv = _start_server(3012)
    try:
        resp = _post_json(
            "http://localhost:3012/api/plugins/register",
            {
                "name": "unsigned_plugin",
                "version": "1.0.0",
                "description": "Unsigned plugin for non-strict registration test",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
    finally:
        srv.stop_server()


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_register_unsigned_strict(monkeypatch):
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    srv = _start_server(3013)
    try:
        resp = _post_json(
            "http://localhost:3013/api/plugins/register",
            {
                "name": "unsigned_plugin",
                "version": "1.0.0",
                "description": "Unsigned plugin for strict registration test",
            },
        )
        assert resp.status_code == 400
    finally:
        srv.stop_server()


@pytest.mark.skipif(
    not HAS_FLASK or not HAS_NACL, reason="Flask or PyNaCl not installed"
)
def test_register_signed_valid(monkeypatch):
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    # Generate key and sign
    # Aetherra imports
    from Aetherra.security.plugin_signing import generate_keypair, sign_manifest

    pub, secret = generate_keypair()
    manifest = {
        "name": "signed_plugin",
        "version": "1.0.0",
        "description": "Signed plugin registration test",
    }
    signed = sign_manifest(manifest, secret)

    srv = _start_server(3014)
    try:
        resp = _post_json("http://localhost:3014/api/plugins/register", signed)
        assert resp.status_code == 200
        # Fetch back
        # Third party imports
        import requests

        r2 = requests.get("http://localhost:3014/api/plugins/signed_plugin", timeout=5)
        assert r2.status_code == 200
        pdata = r2.json()
        assert pdata.get("signature_verified") is True
    finally:
        srv.stop_server()

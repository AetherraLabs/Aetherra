# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Signing enforcement through real loopback Hub requests and committed registry state."""

# Third party imports
import requests

# Aetherra imports
from Aetherra.security.plugin_signing import generate_keypair, sign_manifest


def test_register_unsigned_non_strict(monkeypatch, signing_hub):
    monkeypatch.delenv("AETHERRA_SIGNING_STRICT", raising=False)
    base, store = signing_hub
    response = requests.post(
        f"{base}/api/plugins/register",
        json={
            "name": "unsigned_plugin",
            "version": "1.0.0",
            "description": "Synthetic unsigned manifest",
        },
        timeout=5,
        allow_redirects=False,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    listing = requests.get(f"{base}/api/plugins", timeout=5, allow_redirects=False)
    assert listing.status_code == 200
    assert any(
        plugin["name"] == "unsigned_plugin" for plugin in listing.json()["plugins"]
    )


def test_register_unsigned_strict(monkeypatch, signing_hub):
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    base, store = signing_hub
    response = requests.post(
        f"{base}/api/plugins/register",
        json={
            "name": "unsigned_plugin",
            "version": "1.0.0",
            "description": "Synthetic unsigned manifest",
        },
        timeout=5,
        allow_redirects=False,
    )
    assert response.status_code == 400
    assert store.get("unsigned_plugin") is None
    listing = requests.get(f"{base}/api/plugins", timeout=5, allow_redirects=False)
    assert listing.status_code == 200
    assert all(
        plugin["name"] != "unsigned_plugin" for plugin in listing.json()["plugins"]
    )


def test_register_signed_valid(monkeypatch, signing_hub):
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    base, store = signing_hub
    public, secret = generate_keypair()
    signed = sign_manifest(
        {
            "name": "signed_plugin",
            "version": "1.0.0",
            "description": "Synthetic signed manifest",
        },
        secret,
    )
    response = requests.post(
        f"{base}/api/plugins/register", json=signed, timeout=5, allow_redirects=False
    )
    assert response.status_code == 200
    listing = requests.get(f"{base}/api/plugins", timeout=5, allow_redirects=False)
    assert listing.status_code == 200
    assert any(
        plugin["name"] == "signed_plugin" for plugin in listing.json()["plugins"]
    )
    stored = store.get("signed_plugin")
    assert stored is not None
    assert stored["signature_verified"] is True
    assert stored["pubkey"] == public
    assert stored["signature"] == signed["signature"]

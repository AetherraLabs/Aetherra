# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Discovery signs a synthetic manifest and registers it with the loopback Hub."""

# Standard library imports
import asyncio

# Third party imports
import requests

# Aetherra imports
from Aetherra.security.api_keys import get_keys_file, set_key
from Aetherra.security.plugin_signing import generate_keypair
from aetherra_plugin_discovery import AetherraPluginDiscovery, PluginMetadata


def test_discovery_registers_signed_manifest(monkeypatch, tmp_path, signing_hub):
    monkeypatch.setenv("AETHERRA_SIGN_PLUGINS", "1")
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    public, secret = generate_keypair()
    set_key("plugin_signing_secret", secret)
    assert get_keys_file().is_relative_to(tmp_path)
    base, store = signing_hub
    real_post = requests.post

    def owned_hub_post(url, **kwargs):
        assert url == f"{base}/api/plugins/register"
        kwargs["allow_redirects"] = False
        return real_post(url, **kwargs)

    monkeypatch.setattr(requests, "post", owned_hub_post)
    discovery = AetherraPluginDiscovery()
    discovery.hub_url = base
    metadata = PluginMetadata(
        name="disc_signed", version="1.0.0", description="", author=""
    )
    assert asyncio.run(discovery.register_with_hub(metadata)) is True
    listing = requests.get(f"{base}/api/plugins", timeout=5, allow_redirects=False)
    assert listing.status_code == 200
    assert any(plugin["name"] == "disc_signed" for plugin in listing.json()["plugins"])
    stored = store.get("disc_signed")
    assert stored is not None
    assert stored["signature_verified"] is True
    assert stored["signature"]
    assert stored["pubkey"] == public

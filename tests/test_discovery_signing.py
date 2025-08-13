import importlib.util
import time

import pytest

from aetherra_hub_server import AetherraHubServer
from aetherra_plugin_discovery import AetherraPluginDiscovery, PluginMetadata

HAS_FLASK = importlib.util.find_spec("flask") is not None
HAS_NACL = importlib.util.find_spec("nacl") is not None


def _start_server(port=3015):
    server = AetherraHubServer(port)
    ok = server.start_server()
    assert ok
    time.sleep(0.3)
    return server


@pytest.mark.skipif(
    not HAS_FLASK or not HAS_NACL, reason="Flask or PyNaCl not installed"
)
def test_discovery_registers_signed_manifest(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_SIGN_PLUGINS", "1")
    # Store a temp key for signing
    monkeypatch.setenv("AETHERRA_HOME", str(tmp_path))
    from Aetherra.security.api_keys import set_key

    set_key("plugin_signing_secret", "")  # ensure exists
    from Aetherra.security.plugin_signing import generate_keypair

    pub, secret = generate_keypair()
    set_key("plugin_signing_secret", secret)

    srv = _start_server(3016)
    try:
        disc = AetherraPluginDiscovery()
        disc.hub_url = "http://localhost:3016"
        meta = PluginMetadata(
            name="disc_signed",
            version="1.0.0",
            description="",
            author="",
        )
        # call register
        import asyncio

        asyncio.get_event_loop().run_until_complete(disc.register_with_hub(meta))
        # Fetch back
        import requests

        r2 = requests.get("http://localhost:3016/api/plugins/disc_signed", timeout=5)
        assert r2.status_code == 200
        pdata = r2.json()
        assert pdata.get("signature") or pdata.get("pubkey")
    finally:
        srv.stop_server()

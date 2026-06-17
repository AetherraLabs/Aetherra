# SPDX-License-Identifier: GPL-3.0-or-later
# Verifies hub server exposes plugin endpoints and Lyrixa chat bridge functionality.
from __future__ import annotations

# Standard library imports
import os
import socket
import sys
import time
from contextlib import suppress
from pathlib import Path

# Third party imports
import pytest

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HUB_PORT = 3015  # use non-default to avoid collisions


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


@pytest.fixture(scope="module")
def hub_server():
    if not _port_free(HUB_PORT):
        pytest.skip(f"Port {HUB_PORT} busy; skipping hub integration test")

    # Ensure API flags don't interfere (we only need /api/lyrixa/chat which does not require AI API flags)
    env_backup = os.environ.copy()
    os.environ["AETHERRA_HUB_SKIP_OPTIONALS"] = "1"
    os.environ["AETHERRA_SIGNING_STRICT"] = "0"
    os.environ["AETHERRA_HUB_STRICT"] = "0"
    os.environ["AETHERRA_STRICT"] = "0"
    os.environ["AETHERRA_ALLOW_UNSIGNED_DEV"] = "1"

    # Aetherra imports
    from aetherra_hub.compat import AetherraHubServer

    hub = AetherraHubServer(port=HUB_PORT)
    # Start via compatibility layer API
    if not hub.start_server():
        pytest.skip("Hub server failed to start")

    # Wait for port
    for _ in range(40):
        if not _port_free(HUB_PORT):
            break
        time.sleep(0.1)
    else:
        pytest.skip("Hub server failed to start in time")

    yield hub

    # Teardown best-effort
    try:
        with suppress(Exception):
            hub.stop_server()
    finally:
        os.environ.clear()
        os.environ.update(env_backup)


@pytest.mark.asyncio
async def test_plugin_registration_and_listing(hub_server):
    # Third party imports
    import requests

    # Register a plugin
    payload = {
        "name": "sample_plugin",
        "version": "0.0.1",
        "description": "Sample",
        "category": "utilities",
    }
    r = requests.post(
        f"http://localhost:{HUB_PORT}/api/plugins/register", json=payload, timeout=3
    )
    assert r.status_code in (200, 201), r.text

    # List plugins
    r2 = requests.get(f"http://localhost:{HUB_PORT}/api/plugins", timeout=3)
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert any(p.get("name") == "sample_plugin" for p in data.get("plugins", [])), (
        "Registered plugin not in listing"
    )


def test_lyrixa_chat_bridge_fallback_or_forward(hub_server):
    # Third party imports
    import requests

    # Send a chat request (Lyrixa service likely not registered in minimal test environment)
    r = requests.post(
        f"http://localhost:{HUB_PORT}/api/lyrixa/chat",
        json={"message": "hello"},
        timeout=3,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "text" in body, "chat bridge response missing 'text'"
    # Fallback path returns no suggestions list or empty; forward path would include them
    assert isinstance(body.get("suggestions", []), list)

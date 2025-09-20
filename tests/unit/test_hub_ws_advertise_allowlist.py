# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import socket

# Third party imports
import pytest

requests = pytest.importorskip("requests")


# Aetherra imports
import aetherra_hub.compat as hub_mod

FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ws_advertise_denied_for_disallowed_source_in_prod(monkeypatch):
    # Production profile -> deny-by-default when allowlist unset
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.delenv("AETHERRA_NETWORK_ALLOWLIST", raising=False)

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    # Simulate non-allowlisted client via X-Forwarded-For
    r = requests.get(
        f"{base}/api/ai/stream_ws",
        headers={"X-Forwarded-For": "10.1.2.3"},
        timeout=3,
    )
    assert r.status_code == 403
    js = r.json()
    assert js.get("error") == "forbidden"


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ws_advertise_allowed_localhost_in_prod(monkeypatch):
    # Production profile with default allowlist (localhost allowed)
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.delenv("AETHERRA_NETWORK_ALLOWLIST", raising=False)

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    r = requests.get(f"{base}/api/ai/stream_ws", timeout=3)
    # If WS isn't enabled or Sock not installed, endpoint returns 501 ws_disabled.
    # The allowlist should NOT block localhost access (i.e., not 403).
    assert r.status_code in (200, 501)
    if r.status_code == 501:
        assert r.json().get("error") == "ws_disabled"

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio
import socket

# Third party imports
import pytest

requests = pytest.importorskip("requests")

# Aetherra imports
import aetherra_hub.compat as hub_mod

FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class RateLimitedEngine:
    async def process_message(self, msg: str, ctx: dict | None = None):
        raise Exception("Rate limit: tokens exhausted")


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _register_engine(engine):
    # Aetherra imports
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", engine)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_stream_sse_retry_after_header_present(monkeypatch):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    # Configure explicit retry-after value
    monkeypatch.setenv("AETHERRA_RETRY_AFTER_SEC", "11")

    asyncio.run(_register_engine(RateLimitedEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"

    # POST streaming endpoint
    with requests.post(
        f"{base}/api/ai/stream",
        json={"message": "hi"},
        stream=True,
        timeout=10,
    ) as resp:
        assert resp.status_code == 200
        # New header hint should be present
        assert resp.headers.get("X-Aetherra-Retry-After") == "11"
        _ = b"".join(resp.iter_content(None))

    # GET streaming alias should also expose the header
    with requests.get(
        f"{base}/api/ai/stream?message=hi",
        stream=True,
        timeout=10,
    ) as resp:
        assert resp.status_code == 200
        assert resp.headers.get("X-Aetherra-Retry-After") == "11"
        _ = b"".join(resp.iter_content(None))

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import json
import socket

import pytest

requests = pytest.importorskip("requests")


hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class RateLimitedEngine:
    async def process_message(self, msg: str, ctx: dict | None = None):
        # Simulate upstream provider rate limit
        raise Exception("Rate limit: tokens exhausted")


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _register_engine(engine):
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", engine)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ai_ask_returns_429_with_retry_after(monkeypatch):
    # Enable API, no token required
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    # Configure retry-after seconds to a small test value
    monkeypatch.setenv("AETHERRA_RETRY_AFTER_SEC", "7")

    asyncio.run(_register_engine(RateLimitedEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    r = requests.post(f"{base}/api/ai/ask", json={"message": "hi"}, timeout=5)
    assert r.status_code == 429
    assert r.headers.get("Retry-After") == "7"
    body = r.json()
    assert body.get("error", {}).get("code") == "rate_limited"
    det = body.get("error", {}).get("details", {})
    assert det.get("retry_after_sec") == 7


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ai_stream_emits_rate_limited_error_with_retry_after(monkeypatch):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    monkeypatch.setenv("AETHERRA_RETRY_AFTER_SEC", "5")

    asyncio.run(_register_engine(RateLimitedEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    with requests.post(
        f"{base}/api/ai/stream",
        json={"message": "rate limit me"},
        stream=True,
        timeout=10,
    ) as resp:
        assert resp.status_code == 200
        text = "".join([chunk.decode("utf-8") for chunk in resp.iter_content(None)])
        assert "event: error" in text and "event: final" in text
        # Find the error data line and parse
        err_line = next(
            (
                ln
                for ln in text.splitlines()
                if ln.startswith("data: ") and '"type": "error"' in ln
            ),
            None,
        )
        assert err_line is not None
    payload = json.loads(err_line.split(": ", 1)[1])
    inner = payload.get("data", {})  # envelope's data field
    # Error object is directly under inner["error"]
    err_obj = inner.get("error", {})
    assert err_obj.get("code") == "rate_limited"
    det = err_obj.get("details", {})
    assert det.get("retry_after_sec") == 5

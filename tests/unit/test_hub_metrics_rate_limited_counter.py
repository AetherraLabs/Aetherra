# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
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
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", engine)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_rate_limited_counter_increments_on_429(monkeypatch):
    # Enable API
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")

    asyncio.run(_register_engine(RateLimitedEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    # Initial scrape
    r1 = requests.get(f"{base}/metrics", timeout=5)
    assert r1.status_code == 200
    body1 = r1.text
    # Parse current counter (default 0 if missing)
    import re

    def extract_rate_limited(text: str) -> int:
        m = re.search(
            r"^aetherra_chat_rate_limited_total\s+(\d+(?:\.\d+)?)$", text, re.M
        )
        if not m:
            return 0
        try:
            return int(float(m.group(1)))
        except Exception:
            return 0

    before = extract_rate_limited(body1)

    # Trigger rate limit via /api/ai/ask
    r2 = requests.post(f"{base}/api/ai/ask", json={"message": "hi"}, timeout=5)
    assert r2.status_code == 429

    # Scrape again; counter should increase by 1
    r3 = requests.get(f"{base}/metrics", timeout=5)
    assert r3.status_code == 200
    after = extract_rate_limited(r3.text)

    assert after >= before + 1


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_stream_rate_limited_counter_increments_on_error(monkeypatch):
    # Enable streaming API
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")

    asyncio.run(_register_engine(RateLimitedEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    # Initial scrape
    body1 = requests.get(f"{base}/metrics", timeout=5).text

    import re

    def extract_rate_limited(text: str) -> int:
        m = re.search(
            r"^aetherra_chat_rate_limited_total\s+(\d+(?:\.\d+)?)$", text, re.M
        )
        if not m:
            return 0
        try:
            return int(float(m.group(1)))
        except Exception:
            return 0

    before = extract_rate_limited(body1)

    # Trigger streaming call that will error with rate_limited
    with requests.post(
        f"{base}/api/ai/stream", json={"message": "rl"}, stream=True, timeout=10
    ) as resp:
        assert resp.status_code == 200
        # drain
        _ = b"".join(resp.iter_content(None))

    after_text = requests.get(f"{base}/metrics", timeout=5).text
    after = extract_rate_limited(after_text)

    assert after >= before + 1

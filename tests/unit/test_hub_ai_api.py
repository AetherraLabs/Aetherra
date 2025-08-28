import asyncio
import socket

import pytest

requests = pytest.importorskip("requests")


hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class MockEngine:
    async def process_message(self, msg: str, ctx: dict | None = None):
        # Deterministic, minimal response that looks like the engine output
        return {
            "text": f"echo: {msg}",
            "confidence": 0.5,
            "confidence_details": {"sources": [], "calibration": "mock"},
            "context_used": bool(ctx),
        }


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _register_mock_engine(engine: MockEngine):
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", engine)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ai_ask_disabled_returns_501(monkeypatch):
    # Ensure AI API is disabled
    for key in (
        "AETHERRA_AI_API_ENABLED",
        "AETHERRA_AI_API_REQUIRE_TOKEN",
        "AETHERRA_AI_API_TOKEN",
        "AETHERRA_HUB_CONTROL_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    r = requests.post(f"{base}/api/ai/ask", json={"message": "hi"}, timeout=3)
    assert r.status_code == 501
    js = r.json()
    assert js.get("error") == "disabled"


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ai_ask_requires_token_enforced_and_success(monkeypatch):
    # Enable and require token
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "sek")

    # Register mock engine so calls succeed
    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"

    # Missing token -> 403
    r = requests.post(f"{base}/api/ai/ask", json={"message": "hello"}, timeout=3)
    assert r.status_code == 403

    # Wrong token -> 403
    r = requests.post(
        f"{base}/api/ai/ask",
        json={"message": "hello"},
        headers={"X-Aetherra-Token": "nope"},
        timeout=3,
    )
    assert r.status_code == 403

    # Correct token -> 200 with ok True and result
    r = requests.post(
        f"{base}/api/ai/ask",
        json={"message": "hello", "context": {"x": 1}},
        headers={"X-Aetherra-Token": "sek"},
        timeout=3,
    )
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True
    assert isinstance(js.get("result"), dict)
    assert js["result"].get("text", "").startswith("echo: hello")


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ai_ask_no_token_required_success(monkeypatch):
    # Enabled but no token required
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    monkeypatch.delenv("AETHERRA_AI_API_TOKEN", raising=False)
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)

    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    r = requests.post(f"{base}/api/ai/ask", json={"message": "ping"}, timeout=3)
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True
    assert isinstance(js.get("result"), dict)
    assert js["result"].get("text", "").startswith("echo: ping")


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ai_stream_disabled_and_enabled_placeholder(monkeypatch):
    # Disabled entirely -> disabled from AI API gate
    for k in (
        "AETHERRA_AI_API_ENABLED",
        "AETHERRA_AI_API_REQUIRE_TOKEN",
        "AETHERRA_AI_API_TOKEN",
    ):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.delenv("AETHERRA_AI_API_STREAM", raising=False)

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    r = requests.post(f"{base}/api/ai/stream", json={"message": "x"}, timeout=3)
    assert r.status_code == 501
    assert r.json().get("error") == "disabled"

    # Enable API but keep stream disabled -> 501 disabled
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    r = requests.post(f"{base}/api/ai/stream", json={"message": "x"}, timeout=3)
    assert r.status_code == 501
    assert r.json().get("error") == "disabled"

    # Now enable streaming; require token and register engine
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "tok")
    asyncio.run(_register_mock_engine(MockEngine()))

    # Expect text/event-stream and a final event
    with requests.post(
        f"{base}/api/ai/stream",
        json={"message": "stream me"},
        headers={"X-Aetherra-Token": "tok"},
        timeout=5,
        stream=True,
    ) as resp:
        assert resp.status_code == 200
        assert resp.headers.get("Content-Type", "").startswith("text/event-stream")

        # Accumulate small chunked stream
        text = "".join(
            [chunk.decode("utf-8") for chunk in resp.iter_content(chunk_size=None)]
        )
        assert "event: status" in text
        assert "event: token" in text
        assert "event: final" in text
        assert '"ok": true' in text.lower()

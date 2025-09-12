# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import json
import socket
from typing import Any

import pytest

import aetherra_hub.compat as hub_mod

FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


websockets = pytest.importorskip("websockets")
flask_sock = pytest.importorskip("flask_sock")


class MockEngine:
    async def process_message(self, msg: str, ctx: dict | None = None):
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
def test_ws_stream_idempotency_duplicate_returns_error_with_echo(monkeypatch):
    # Enable AI API, streaming, WS, and idempotency enforcement
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_WS", "1")
    monkeypatch.setenv("AETHERRA_IDEMPOTENCY_ENFORCE", "1")
    # Do not require token for simplicity
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")

    # Register mock engine
    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base_ws = f"ws://localhost:{port}/ws/ai/stream"
    cmi = "ws-dup-123"

    async def _first_conn():
        async with websockets.connect(base_ws) as ws:
            await ws.send(
                json.dumps(
                    {
                        "message": "hello ws",
                        "client_message_id": cmi,
                        "context": {"principal": "tester"},
                    }
                )
            )
            # Receive a couple frames to ensure server processed start; then close
            try:
                await asyncio.wait_for(ws.recv(), timeout=1.0)
            except Exception:
                pass

    async def _second_conn_duplicate():
        async with websockets.connect(base_ws) as ws:
            await ws.send(
                json.dumps(
                    {
                        "message": "hello ws",
                        "client_message_id": cmi,
                        "context": {"principal": "tester"},
                    }
                )
            )
            # Expect immediate error JSON (not envelope), with code=duplicate and echo client_message_id
            raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            obj = json.loads(raw)
            assert obj.get("ok") is False
            assert obj.get("code") == "duplicate"
            assert obj.get("client_message_id") == cmi
            # Server should close soon after
            with pytest.raises(Exception):
                # Next recv should fail or timeout as server closes
                await asyncio.wait_for(ws.recv(), timeout=1.0)

    asyncio.run(_first_conn())
    asyncio.run(_second_conn_duplicate())


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_ws_resume_last_event_id_monotonic(monkeypatch):
    # Enable AI API, streaming, WS
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_WS", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")

    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base_ws = f"ws://localhost:{port}/ws/ai/stream"

    async def _connect_and_collect(start_id: int | None):
        msgs = []
        async with websockets.connect(base_ws) as ws:
            payload: dict[str, Any] = {"message": "resume test"}
            if start_id is not None:
                payload["last_event_id"] = start_id
            await ws.send(json.dumps(payload))
            # Read a few frames
            for _ in range(3):
                raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
                obj = json.loads(raw)
                msgs.append(obj)
            # Close client side
        return msgs

    first = asyncio.run(_connect_and_collect(None))
    assert first and isinstance(first[0].get("id"), int)
    base_id = first[0]["id"]

    second = asyncio.run(_connect_and_collect(base_id))
    assert second and second[0]["id"] == base_id + 1

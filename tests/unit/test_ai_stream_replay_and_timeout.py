# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import socket

# Third party imports
import pytest
import requests

# Aetherra imports
from aetherra_hub.compat import AetherraHubServer

HAS_FLASK = True
try:
    # Third party imports
    import flask  # noqa: F401
except Exception:  # pragma: no cover
    HAS_FLASK = False


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_ai_stream_replay_and_soft_timeout(monkeypatch):
    # Enable streaming + minimal engine disabled path to produce offline chunks quickly
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    # Activate replay buffer for a few frames
    monkeypatch.setenv("AETHERRA_SSE_REPLAY_MAX_EVENTS", "10")
    monkeypatch.setenv("AETHERRA_SSE_REPLAY_MAX_AGE_S", "30")

    port = _free_port()
    server = AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    # First request collects frames
    r1 = requests.post(
        f"{base}/api/ai/stream", json={"message": "hello"}, stream=True, timeout=5
    )
    assert r1.status_code == 200
    text1 = "".join(chunk.decode("utf-8") for chunk in r1.iter_content(chunk_size=None))
    assert "event: final" in text1

    # Extract last id (last 'id: ' before final)
    last_id = 0
    for line in text1.splitlines():
        if line.startswith("id: "):
            try:
                last_id = int(line.split(": ", 1)[1])
            except Exception:
                pass
    assert last_id > 0

    # Second request with Last-Event-ID header should replay nothing newer than first run (no new frames yet)
    r2 = requests.post(
        f"{base}/api/ai/stream",
        json={"message": "world"},
        headers={"Last-Event-ID": str(last_id)},
        stream=True,
        timeout=5,
    )
    assert r2.status_code == 200
    text2 = "".join(chunk.decode("utf-8") for chunk in r2.iter_content(chunk_size=None))
    # Should still produce a new stream with its own status + final events
    assert "event: status" in text2 and "event: final" in text2

    # Soft timeout path: set tight 1s soft timeout and simulate slow processing with engine_wait_ms
    monkeypatch.setenv("AETHERRA_STREAM_SOFT_TIMEOUT_S", "1")
    monkeypatch.setenv(
        "AETHERRA_ENGINE_WAIT_MS", "1500"
    )  # 1.5s -> triggers soft timeout

    port2 = _free_port()
    server2 = AetherraHubServer(port2)
    assert server2.start_server()
    base2 = f"http://localhost:{port2}"

    r3 = requests.post(
        f"{base2}/api/ai/stream", json={"message": "slow"}, stream=True, timeout=6
    )
    assert r3.status_code == 200
    text3 = "".join(chunk.decode("utf-8") for chunk in r3.iter_content(chunk_size=None))
    assert "soft_timeout" in text3.lower()

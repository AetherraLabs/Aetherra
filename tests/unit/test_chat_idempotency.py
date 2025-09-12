# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import os
import time

import pytest
import requests

from aetherra_hub.compat import start_hub_server

PORT = 3014
BASE = f"http://localhost:{PORT}"


def _ensure_env():
    os.environ["AETHERRA_AI_API_ENABLED"] = "1"
    os.environ["AETHERRA_AI_API_STREAM"] = "1"
    os.environ["AETHERRA_AI_API_REQUIRE_TOKEN"] = "0"
    os.environ["AETHERRA_IDEMPOTENCY_ENFORCE"] = "1"


def _start_hub():
    _ensure_env()
    start_hub_server(PORT)
    # Wait briefly for server readiness
    for _ in range(50):
        try:
            r = requests.get(f"{BASE}/health", timeout=0.2)
            if r.status_code in (200, 404, 405):
                return
        except Exception:
            time.sleep(0.05)
    for _ in range(50):
        try:
            r = requests.get(f"{BASE}/", timeout=0.2)
            if r.status_code == 200:
                return
        except Exception:
            time.sleep(0.05)


@pytest.mark.integration
def test_ask_idempotency_duplicate_echoes_client_message_id():
    _start_hub()
    cmi = "dup-ask-1"
    principal = "idem_user"
    # First OK
    r1 = requests.post(
        f"{BASE}/api/ai/ask",
        json={
            "message": "hello",
            "client_message_id": cmi,
            "context": {"principal": principal},
        },
        timeout=10,
    )
    assert r1.status_code == 200
    j1 = r1.json()
    assert j1.get("ok") is True
    # Second should be 409 duplicate and echo client_message_id
    r2 = requests.post(
        f"{BASE}/api/ai/ask",
        json={
            "message": "hello",
            "client_message_id": cmi,
            "context": {"principal": principal},
        },
        timeout=10,
    )
    assert r2.status_code == 409
    j2 = r2.json()
    assert j2.get("ok") is False
    assert j2.get("client_message_id") == cmi
    err = j2.get("error") or {}
    assert err.get("code") == "duplicate"


@pytest.mark.integration
def test_stream_post_idempotency_duplicate_returns_409_with_echo():
    _start_hub()
    cmi = "dup-stream-post-1"
    principal = "idem_stream_post"
    # First: should start SSE (200)
    r1 = requests.post(
        f"{BASE}/api/ai/stream",
        headers={"Accept": "text/event-stream"},
        json={
            "message": "stream it",
            "client_message_id": cmi,
            "context": {"principal": principal},
        },
        stream=True,
        timeout=10,
    )
    assert r1.status_code == 200
    # Close immediately; idempotency mark should be set
    try:
        r1.close()
    except Exception:
        pass
    # Second duplicate should be 409 JSON (not SSE)
    r2 = requests.post(
        f"{BASE}/api/ai/stream",
        headers={"Accept": "application/json"},
        json={
            "message": "stream it",
            "client_message_id": cmi,
            "context": {"principal": principal},
        },
        timeout=10,
    )
    assert r2.status_code == 409
    j2 = r2.json()
    assert j2.get("ok") is False
    assert j2.get("client_message_id") == cmi
    err = j2.get("error") or {}
    assert err.get("code") == "duplicate"


@pytest.mark.integration
def test_stream_get_idempotency_duplicate_returns_409_with_echo():
    _start_hub()
    cmi = "dup-stream-get-1"
    principal = "idem_stream_get"
    # First: SSE GET should start (200)
    r1 = requests.get(
        f"{BASE}/api/ai/stream",
        headers={"Accept": "text/event-stream", "X-Aetherra-Principal": principal},
        params={"message": "get streaming", "client_message_id": cmi},
        stream=True,
        timeout=10,
    )
    assert r1.status_code == 200
    try:
        r1.close()
    except Exception:
        pass
    # Second duplicate via GET should be 409 JSON
    r2 = requests.get(
        f"{BASE}/api/ai/stream",
        headers={"Accept": "application/json", "X-Aetherra-Principal": principal},
        params={"message": "get streaming", "client_message_id": cmi},
        timeout=10,
    )
    assert r2.status_code == 409
    j2 = r2.json()
    assert j2.get("ok") is False
    assert j2.get("client_message_id") == cmi
    err = j2.get("error") or {}
    assert err.get("code") == "duplicate"

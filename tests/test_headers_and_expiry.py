# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import json
import os
import time

# Third party imports
import pytest
import requests

# Aetherra imports
from aetherra_hub.compat import start_hub_server

PORT = 3012
BASE = f"http://localhost:{PORT}"
ASK_URL = f"{BASE}/api/ai/ask"
STREAM_URL = f"{BASE}/api/ai/stream"
LYRIXA_URL = f"{BASE}/api/lyrixa/chat"


def _ensure_env():
    os.environ["AETHERRA_AI_API_ENABLED"] = "1"
    os.environ["AETHERRA_AI_API_STREAM"] = "1"
    os.environ["AETHERRA_AI_API_REQUIRE_TOKEN"] = "0"


def _start_hub():
    _ensure_env()
    start_hub_server(PORT)
    # Wait for server
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


def _iter_sse(resp):
    buf = ""
    for chunk in resp.iter_lines(decode_unicode=True):
        if not chunk:
            if buf.strip():
                yield buf
            buf = ""
            continue
        buf += chunk + "\n"


def _parse_envelope(block):
    eid = None
    etype = None
    data = None
    for line in block.strip().splitlines():
        if line.startswith("id: "):
            try:
                eid = int(line.split(": ", 1)[1])
            except Exception:
                eid = None
        elif line.startswith("event: "):
            etype = line.split(": ", 1)[1]
        elif line.startswith("data: "):
            try:
                data = json.loads(line.split(": ", 1)[1])
            except Exception:
                data = None
    return eid, etype, data


@pytest.mark.integration
def test_headers_on_ask_and_stream_endpoints():
    _start_hub()

    # Ask (non-stream) should always include headers, even on engine failure
    trace = "test-trace-ask-123"
    r = requests.post(
        ASK_URL,
        json={"message": "hello"},
        headers={"X-Aetherra-Trace-Id": trace},
        timeout=5,
    )
    assert r.headers.get("X-Aetherra-Chat-Version") == "2"
    assert r.headers.get("X-Aetherra-Trace-Id")
    # If we supplied a trace id, it should propagate back
    assert r.headers.get("X-Aetherra-Trace-Id") == trace
    pol = r.headers.get("X-Aetherra-Policy")
    assert pol is not None
    pol_obj = json.loads(pol)
    for key in ("ai_enabled", "stream_enabled", "require_token"):
        assert key in pol_obj

    # Stream (POST) response should include the same headers
    trace2 = "test-trace-stream-456"
    with requests.post(
        STREAM_URL,
        json={"message": "stream please"},
        headers={"X-Aetherra-Trace-Id": trace2},
        stream=True,
        timeout=10,
    ) as s:
        assert s.headers.get("X-Aetherra-Chat-Version") == "2"
        assert s.headers.get("X-Aetherra-Trace-Id") == trace2
        pol2 = s.headers.get("X-Aetherra-Policy")
        assert pol2 and isinstance(json.loads(pol2), dict)


@pytest.mark.integration
def test_headers_on_stream_get_alias():
    _start_hub()
    trace = "test-trace-get-789"
    with requests.get(
        STREAM_URL,
        params={"message": "hi"},
        headers={"X-Aetherra-Trace-Id": trace},
        stream=True,
        timeout=10,
    ) as s:
        assert s.headers.get("X-Aetherra-Chat-Version") == "2"
        assert s.headers.get("X-Aetherra-Trace-Id") == trace
        pol = s.headers.get("X-Aetherra-Policy")
        assert pol and isinstance(json.loads(pol), dict)


@pytest.mark.integration
def test_expiry_nonstream_and_bridge_409():
    _start_hub()
    past = time.time() - 5
    r1 = requests.post(
        ASK_URL,
        json={"message": "expired", "deadline_ts": past},
        timeout=5,
    )
    assert r1.status_code == 409
    j1 = r1.json()
    err1 = j1.get("error") or {}
    assert err1.get("code") == "invalid_request"
    assert "expired" in (err1.get("message") or "").lower()
    assert r1.headers.get("X-Aetherra-Chat-Version") == "2"
    assert r1.headers.get("X-Aetherra-Trace-Id")

    r2 = requests.post(
        LYRIXA_URL,
        json={"message": "expired", "deadline_ts": past},
        timeout=5,
    )
    assert r2.status_code == 409
    j2 = r2.json()
    err2 = j2.get("error") or {}
    assert err2.get("code") == "invalid_request"
    assert "expired" in (err2.get("message") or "").lower()
    assert r2.headers.get("X-Aetherra-Chat-Version") == "2"
    assert r2.headers.get("X-Aetherra-Trace-Id")


@pytest.mark.integration
def test_expiry_stream_post_emits_error_and_final():
    _start_hub()
    past = time.time() - 1
    with requests.post(
        STREAM_URL,
        json={"message": "expired", "deadline_ts": past},
        stream=True,
        timeout=10,
    ) as s:
        events = []
        for block in _iter_sse(s):
            eid, etype, data = _parse_envelope(block)
            if etype and data:
                events.append((etype, data))
            if etype == "final":
                break
        types = [t for t, _ in events]
        assert "error" in types
        assert types[-1] == "final"
        # Ensure the error is due to expiry
    err_objs = [d["data"].get("error") for t, d in events if t == "error"]
    assert any((e or {}).get("code") == "invalid_request" for e in err_objs)
    assert any("expired" in ((e or {}).get("message") or "").lower() for e in err_objs)


@pytest.mark.integration
def test_expiry_stream_get_emits_error_and_final():
    _start_hub()
    past = time.time() - 1
    with requests.get(
        STREAM_URL,
        params={"message": "expired", "deadline_ts": str(past)},
        stream=True,
        timeout=10,
    ) as s:
        events = []
        for block in _iter_sse(s):
            eid, etype, data = _parse_envelope(block)
            if etype and data:
                events.append((etype, data))
            if etype == "final":
                break
        types = [t for t, _ in events]
        assert "error" in types
        assert types[-1] == "final"
    err_objs = [d["data"].get("error") for t, d in events if t == "error"]
    assert any((e or {}).get("code") == "invalid_request" for e in err_objs)
    assert any("expired" in ((e or {}).get("message") or "").lower() for e in err_objs)


@pytest.mark.integration
def test_expired_request_writes_fallback_dlq_file():
    _start_hub()
    # Standard library imports
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        # Point hub fallback DLQ to temp dir for isolation
        os.environ["AETHERRA_STATE_DIR"] = td
        past = time.time() - 2
        r = requests.post(
            ASK_URL,
            json={"message": "x", "deadline_ts": past},
            timeout=5,
        )
        assert r.status_code == 409
        p = Path(td) / "hub_chat_dlq.jsonl"
        # Wait briefly for file to be written
        for _ in range(20):
            if p.exists() and p.stat().st_size > 0:
                break
            time.sleep(0.05)
        assert p.exists() and p.stat().st_size > 0
        # Validate last line JSON has expected shape
        last = None
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last = line.strip()
        assert last is not None
        entry = json.loads(last)
        assert entry.get("reason") == "expired"
        assert entry.get("type") == "chat.request"
        data = entry.get("data") or {}
        assert data.get("endpoint") in {
            "/api/ai/ask",
            "/api/ai/stream",
            "/api/lyrixa/chat",
            "/api/ai/stream[GET]",
        }


@pytest.mark.integration
def test_headers_on_lyrixa_bridge_success():
    _start_hub()
    r = requests.post(LYRIXA_URL, json={"message": "ping"}, timeout=5)
    assert r.status_code == 200
    assert r.headers.get("X-Aetherra-Chat-Version") == "2"
    assert r.headers.get("X-Aetherra-Trace-Id")
    pol = r.headers.get("X-Aetherra-Policy")
    assert pol and isinstance(json.loads(pol), dict)

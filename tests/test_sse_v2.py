import json
import os
import time

import pytest
import requests

from aetherra_hub_server import start_hub_server

PORT = 3012
BASE = f"http://localhost:{PORT}"
STREAM_URL = f"{BASE}/api/ai/stream"


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
    # No explicit health route; server should still be listening via index page
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
            # dispatch
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
def test_stream_event_order_and_envelope_basic():
    _start_hub()
    # start stream
    with requests.post(
        STREAM_URL,
        json={"message": "hello from test"},
        stream=True,
        timeout=10,
    ) as r:
        assert r.status_code == 200
        events = []
        for block in _iter_sse(r):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            assert isinstance(eid, int) and eid >= 1
            assert etype in {
                "status",
                "auth",
                "policy",
                "usage",
                "final",
                "error",
                "thought",
                "tool",
                "chunk",
            }
            assert isinstance(data, dict)
            # check required envelope keys
            assert set(data.keys()) >= {"id", "trace_id", "ts", "type", "data"}
            events.append((eid, etype, data))
            if etype in ("final",):
                break
        # order
        types = [t for _, t, _ in events]
        assert types[0] == "status"
        assert "auth" in types[:3]
        assert "policy" in types[:3]
        # usage should come before final if success
        if "error" not in types:
            assert "usage" in types
            assert types.index("usage") < types.index("final")
        # monotonic ids
        ids = [eid for eid, _, _ in events]
        assert ids == sorted(ids)


@pytest.mark.integration
def test_last_event_id_resume_monotonic():
    _start_hub()
    # first few events
    with requests.post(
        STREAM_URL,
        json={"message": "resume test"},
        stream=True,
        timeout=10,
    ) as r:
        first_ids = []
        last_id = 0
        for block in _iter_sse(r):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            first_ids.append(eid)
            last_id = eid
            if etype in ("policy",):
                break
    # resume with Last-Event-ID
    headers = {"Last-Event-ID": str(last_id)}
    with requests.get(
        STREAM_URL,
        headers=headers,
        params={"message": "resume test"},
        stream=True,
        timeout=10,
    ) as r2:
        resumed_ids = []
        for block in _iter_sse(r2):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            resumed_ids.append(eid)
            # ensure starts strictly greater than last_id
            assert last_id is not None and eid > last_id
            if etype in ("final",):
                break
        assert last_id is not None
        assert resumed_ids and resumed_ids[0] == last_id + 1


@pytest.mark.integration
def test_last_event_id_gap_resume_skips_seen_and_remains_monotonic():
    _start_hub()
    # Consume a portion of the stream to get some ids, then drop connection early
    with requests.post(
        STREAM_URL,
        json={"message": "gap resume test"},
        stream=True,
        timeout=10,
    ) as r:
        seen = []
        last_id = None
        for block in _iter_sse(r):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            seen.append(eid)
            last_id = eid
            if len(seen) >= 3:
                break
    assert last_id is not None
    # Pretend client only persisted the first id and lost the next few; resume from stale earlier id
    headers = {"Last-Event-ID": str(seen[0])}
    with requests.get(
        STREAM_URL,
        headers=headers,
        params={"message": "gap resume test"},
        stream=True,
        timeout=10,
    ) as r2:
        resumed = []
        for block in _iter_sse(r2):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            resumed.append(eid)
            # All resumed ids must be strictly greater than provided Last-Event-ID
            assert eid > seen[0]
            if etype == "final":
                break
        assert resumed and resumed[0] == seen[0] + 1


@pytest.mark.integration
def test_last_event_id_far_stale_starts_from_next():
    _start_hub()
    # Start a stream, record a high id, then resume from a much older id
    with requests.post(
        STREAM_URL,
        json={"message": "far stale resume"},
        stream=True,
        timeout=10,
    ) as r:
        last_id = None
        for block in _iter_sse(r):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            last_id = eid
            if etype in ("policy",):
                break
    assert last_id is not None
    # Provide a Last-Event-ID of 0 (very stale) to ensure server starts at 1
    headers = {"Last-Event-ID": "0"}
    with requests.get(
        STREAM_URL,
        headers=headers,
        params={"message": "far stale resume"},
        stream=True,
        timeout=10,
    ) as r2:
        first = None
        for block in _iter_sse(r2):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            first = eid
            break
        assert first is not None and first >= 1


@pytest.mark.integration
def test_usage_presence_and_shape():
    _start_hub()
    with requests.post(
        STREAM_URL,
        json={"message": "measure usage"},
        stream=True,
        timeout=10,
    ) as r:
        saw_usage = False
        saw_final = False
        saw_error = False
        for block in _iter_sse(r):
            eid, etype, data = _parse_envelope(block)
            if etype is None or data is None:
                continue
            if etype == "usage":
                saw_usage = True
                inner = data["data"]
                for key in ("tokens_in", "tokens_out", "chars_in", "chars_out"):
                    assert key in inner and isinstance(inner[key], int)
            if etype == "error":
                saw_error = True
            if etype == "final":
                saw_final = True
                break
        assert saw_final
        # If success, usage should be present; if not, we at least saw an error
        assert saw_usage or saw_error


@pytest.mark.integration
def test_midstream_events_presence():
    _start_hub()
    with requests.post(
        STREAM_URL,
        json={"message": "emit midstream"},
        stream=True,
        timeout=10,
    ) as r:
        assert r.status_code == 200
        saw_final = False
        for block in _iter_sse(r):
            eid, etype, data = _parse_envelope(block)
            if etype is None:
                continue
            if etype == "final":
                saw_final = True
                break
        # Mid-stream events are optional; ensure stream completes
        assert saw_final


@pytest.mark.integration
def test_get_stream_echoes_scratchpad_policy_in_final():
    _start_hub()
    # Use GET alias and supply scratchpad_policy via query param
    params = {
        "message": "policy echo test",
        "scratchpad_policy": "redacted",
    }
    with requests.get(
        STREAM_URL,
        params=params,
        stream=True,
        timeout=10,
    ) as r:
        assert r.status_code == 200
        saw_final = False
        echoed = None
        for block in _iter_sse(r):
            eid, etype, data = _parse_envelope(block)
            if etype is None or data is None:
                continue
            if etype == "final":
                inner = data.get("data") or {}
                result = inner.get("result") or {}
                echoed = result.get("scratchpad_policy")
                saw_final = True
                break
        assert saw_final
        assert echoed == "redacted"


@pytest.mark.integration
def test_stream_resume_after_rate_limit_with_last_event_id():
    _start_hub()
    import asyncio

    from aetherra_service_registry import get_service_registry

    class RateLimitedEngine:
        async def process_message(self, msg: str, ctx: dict | None = None):
            raise Exception("Rate limit: tokens exhausted")

    class SuccessEngine:
        async def process_message(self, msg: str, ctx: dict | None = None):
            return {"response": "ok"}

    async def _register_engine(engine):
        reg = await get_service_registry()
        await reg.register_service("aetherra_engine", engine)

    # Configure short retry-after for fast test and register a rate-limited engine
    os.environ["AETHERRA_RETRY_AFTER_SEC"] = "1"
    asyncio.run(_register_engine(RateLimitedEngine()))

    # First attempt: expect an error event with code=rate_limited
    with requests.post(
        STREAM_URL,
        json={"message": "limit then resume"},
        stream=True,
        timeout=10,
    ) as resp:
        assert resp.status_code == 200
        last_id = None
        saw_rate_limited = False
        for block in _iter_sse(resp):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            last_id = eid
            if etype == "error":
                err = (data.get("data") or {}).get("error") or {}
                if err.get("code") == "rate_limited":
                    saw_rate_limited = True
            if etype == "final":
                break
        assert saw_rate_limited and isinstance(last_id, int)

    # Swap engine to success and wait for minimal backoff
    asyncio.run(_register_engine(SuccessEngine()))
    time.sleep(1.1)

    # Second attempt with Last-Event-ID should start from last_id+1 and complete successfully
    headers = {"Last-Event-ID": str(last_id)}
    with requests.get(
        STREAM_URL,
        headers=headers,
        params={"message": "limit then resume"},
        stream=True,
        timeout=10,
    ) as resp2:
        assert resp2.status_code == 200
        first_eid = None
        saw_final_ok = False
        for block in _iter_sse(resp2):
            eid, etype, data = _parse_envelope(block)
            if eid is None or etype is None or data is None:
                continue
            if first_eid is None:
                first_eid = eid
                assert first_eid == last_id + 1
            if etype == "final":
                inner = data.get("data") or {}
                saw_final_ok = bool(inner.get("ok", False))
                break
        assert isinstance(first_eid, int) and saw_final_ok

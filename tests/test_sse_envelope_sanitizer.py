import json
from datetime import datetime

import pytest

from aetherra_hub.services.ai_stream import StreamContext


def _extract_json_from_sse(frame: str) -> dict:
    # Find the 'data: ' line and parse the JSON after it
    for line in frame.splitlines():
        if line.startswith("data: "):
            payload = line[len("data: ") :]
            return json.loads(payload)
    raise AssertionError("No data line found in SSE frame")


def test_envelope_sanitizes_callables_and_strips_callbacks():
    ctx = StreamContext(trace_id="trace-test", start_event_id=1)

    # Include callables in both top-level data and inside result,
    # plus an internal _callbacks dict we don't want to leak.
    data = {
        "fn": (lambda x=1: x),
        "result": {
            "x": (lambda: None),
            "_callbacks": {
                "on_chunk": (lambda: None),
                "on_thought": (lambda: None),
            },
        },
    }

    frame = ctx.envelope("final", data)
    env = _extract_json_from_sse(frame)

    assert env["type"] == "final"
    assert isinstance(env["id"], int)

    # Top-level callable is stringified by the JSON-default
    assert "fn" in env["data"]
    assert isinstance(env["data"]["fn"], str)
    assert env["data"]["fn"].startswith("<callable:") or env["data"]["fn"].startswith(
        "<callable>"
    )

    # Result exists and has callables stringified
    result = env["data"].get("result")
    assert isinstance(result, dict)
    assert "_callbacks" not in result  # stripped defensively on final
    assert isinstance(result.get("x"), str)
    assert result["x"].startswith("<callable:") or result["x"].startswith("<callable>")


def test_envelope_sanitizes_datetime_and_bytes():
    ctx = StreamContext(trace_id="trace-dt-bytes", start_event_id=10)

    dt = datetime(2025, 10, 24, 12, 30, 45)
    raw_bytes = b"binary\xffdata"

    data = {
        "timestamp": dt,
        "blob": raw_bytes,
        "result": {
            "nested_dt": dt,
            "nested_bytes": bytearray(b"test\x00data"),
        },
    }

    frame = ctx.envelope("chunk", data)
    env = _extract_json_from_sse(frame)

    assert env["type"] == "chunk"
    assert env["id"] == 10

    # Datetime is ISO-formatted
    assert isinstance(env["data"]["timestamp"], str)
    assert env["data"]["timestamp"] == "2025-10-24T12:30:45"

    # Bytes are decoded to UTF-8 (with replacement for invalid chars)
    assert isinstance(env["data"]["blob"], str)
    # The \xff will be replaced with U+FFFD replacement character
    assert "binary" in env["data"]["blob"]

    # Nested items also sanitized
    result = env["data"]["result"]
    assert isinstance(result["nested_dt"], str)
    assert result["nested_dt"] == "2025-10-24T12:30:45"
    assert isinstance(result["nested_bytes"], str)
    assert "test" in result["nested_bytes"]


@pytest.mark.parametrize(
    "internal_key",
    ["_callbacks", "_metadata", "_trace", "_context", "_internal"],
)
def test_envelope_strips_internal_keys_from_final(internal_key):
    """Verify that all internal keys defined in _INTERNAL_KEYS are stripped from final results."""
    ctx = StreamContext(trace_id="trace-internal", start_event_id=20)

    # Include the internal key in the result payload
    data = {
        "ok": True,
        "result": {
            "answer": "test response",
            internal_key: {"should": "be stripped"},
        },
    }

    frame = ctx.envelope("final", data)
    env = _extract_json_from_sse(frame)

    assert env["type"] == "final"
    result = env["data"]["result"]

    # The internal key should be removed
    assert internal_key not in result
    # Normal keys should remain
    assert result["answer"] == "test response"


def test_envelope_strips_multiple_internal_keys():
    """Verify that multiple internal keys are all stripped in a single call."""
    ctx = StreamContext(trace_id="trace-multi", start_event_id=30)

    data = {
        "ok": True,
        "result": {
            "answer": "response",
            "_callbacks": {"fn": lambda: None},
            "_metadata": {"extra": "info"},
            "_trace": "trace-data",
            "_context": {"ctx": "value"},
            "safe_key": "preserved",
        },
    }

    frame = ctx.envelope("final", data)
    env = _extract_json_from_sse(frame)

    result = env["data"]["result"]

    # All internal keys stripped
    assert "_callbacks" not in result
    assert "_metadata" not in result
    assert "_trace" not in result
    assert "_context" not in result

    # Safe keys preserved
    assert result["answer"] == "response"
    assert result["safe_key"] == "preserved"

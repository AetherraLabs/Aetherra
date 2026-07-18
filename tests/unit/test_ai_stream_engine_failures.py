# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from __future__ import annotations

import json

from aetherra_hub.services import ai_stream


class FailingEngine:
    async def process_message(self, prompt, ctx):
        raise RuntimeError("sensitive path C:/Users/example/stream-secret.db")


class TimeoutEngine:
    async def process_message(self, prompt, ctx):
        raise TimeoutError("timeout path C:/Users/example/timeout-secret.db")


class RateLimitedEngine:
    async def process_message(self, prompt, ctx):
        raise RuntimeError("rate limit token=t-1 C:/Users/example/rate-secret.db")


def _events(frames: list[str]) -> list[dict]:
    events = []
    for frame in frames:
        data_line = next(
            line.removeprefix("data: ")
            for line in frame.splitlines()
            if line.startswith("data: ")
        )
        events.append(json.loads(data_line))
    return events


def _stream_with_engine(monkeypatch, engine):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setattr(ai_stream, "_get_engine", lambda: engine)
    return list(
        ai_stream.stream_sse(
            {"message": "hello"},
            {"trace_id": "trace-stream"},
        )
    )


def test_stream_sanitizes_engine_processing_exception(monkeypatch):
    frames = _stream_with_engine(monkeypatch, FailingEngine())
    text = "".join(frames)
    events = _events(frames)
    error_events = [event for event in events if event["type"] == "error"]

    assert error_events[-1]["data"]["error"] == {
        "code": "engine_error",
        "message": "AI engine stream failed",
        "details": {"trace_id": "trace-stream"},
    }
    assert "stream-secret.db" not in text
    assert "sensitive path" not in text


def test_stream_sanitizes_timeout_exception(monkeypatch):
    frames = _stream_with_engine(monkeypatch, TimeoutEngine())
    text = "".join(frames)
    events = _events(frames)
    error_events = [event for event in events if event["type"] == "error"]

    assert error_events[-1]["data"]["error"] == {
        "code": "timeout",
        "message": "AI engine request timed out",
        "details": {"trace_id": "trace-stream"},
    }
    assert "timeout-secret.db" not in text


def test_stream_sanitizes_rate_limit_exception(monkeypatch):
    frames = _stream_with_engine(monkeypatch, RateLimitedEngine())
    text = "".join(frames)
    events = _events(frames)
    error_events = [event for event in events if event["type"] == "error"]

    assert error_events[-1]["data"]["error"] == {
        "code": "rate_limited",
        "message": "AI service rate limit exceeded",
        "details": {"retry_after_sec": 2.0},
    }
    assert "rate-secret.db" not in text
    assert "t-1" not in text

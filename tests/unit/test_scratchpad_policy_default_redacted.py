# Standard library imports
import json

# Aetherra imports
from aetherra_hub.services import ai_stream


def _collect(stream_iter):
    return list(stream_iter)


def test_scratchpad_policy_defaults_redacted(monkeypatch):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")

    # Provide a fake engine with process_message returning a dict including scratchpad
    class FakeEngine:
        async def process_message(self, prompt, ctx):  # noqa: D401
            return {"response": "ok", "scratchpad": "internal notes"}

    async def _get_engine_async_mock():
        return FakeEngine()

    monkeypatch.setattr(ai_stream, "_get_engine_async", _get_engine_async_mock)
    # Force immediate _get_engine resolution
    monkeypatch.setattr(ai_stream, "_get_engine", lambda: FakeEngine())

    body = {"message": "hello"}
    headers = {}
    frames = _collect(ai_stream.stream_sse(body, headers))
    final = [f for f in frames if f.startswith("id:") and "final" in f][-1]
    data_line = [ln for ln in final.splitlines() if ln.startswith("data:")][0]
    payload = json.loads(data_line.split("data: ")[1])
    result = payload["data"]["result"]
    assert result.get("scratchpad_policy") == "redacted"
    # Under redacted policy scratchpad content should be masked
    assert result.get("scratchpad") == "[redacted]"


def test_scratchpad_policy_ephemeral_allowed(monkeypatch):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")

    class FakeEngine:
        async def process_message(self, prompt, ctx):
            return {"response": "ok", "scratchpad": "temp notes"}

    monkeypatch.setattr(ai_stream, "_get_engine", lambda: FakeEngine())
    body = {"message": "hello", "scratchpad_policy": "ephemeral"}
    frames = _collect(ai_stream.stream_sse(body, {}))
    final = [f for f in frames if f.startswith("id:") and "final" in f][-1]
    data_line = [ln for ln in final.splitlines() if ln.startswith("data:")][0]
    payload = json.loads(data_line.split("data: ")[1])
    result = payload["data"]["result"]
    assert result.get("scratchpad_policy") == "ephemeral"
    # Ephemeral can expose (not redacted)
    assert result.get("scratchpad") == "temp notes"

import json

from flask import Flask

from aetherra_hub.blueprints.ai_stream import bp as ai_stream_bp
from aetherra_hub.blueprints.metrics import bp as metrics_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(ai_stream_bp)
    app.register_blueprint(metrics_bp)
    return app


def _read_sse_events(body: str):
    events = []
    cur = {}
    for line in body.splitlines():
        if not line.strip():
            if cur:
                events.append(cur)
                cur = {}
            continue
        if line.startswith("id: "):
            cur["id"] = line[4:].strip()
        elif line.startswith("event: "):
            cur["event"] = line[7:].strip()
        elif line.startswith("data: "):
            cur.setdefault("data", [])
            cur["data"].append(line[6:])
    if cur:
        events.append(cur)
    for e in events:
        if "data" in e:
            try:
                e["json"] = json.loads("\n".join(e["data"]))
            except Exception:
                pass
    return events


def test_debug_frame_emitted(monkeypatch):
    # Enable streaming + debug + soft timeout (short) to force deterministic termination
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_HUB_DEBUG_METRICS", "1")
    monkeypatch.setenv("AETHERRA_STREAM_SOFT_TIMEOUT_S", "1")
    # Ensure engine wait exceeds soft timeout so Option B suppresses fallback and soft timeout triggers
    monkeypatch.setenv("AETHERRA_ENGINE_WAIT_MS", "2000")

    app = create_app()
    client = app.test_client()

    resp = client.post(
        "/api/ai/stream",
        json={"prompt": "hello debug"},
        headers={"Accept": "text/event-stream"},
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    events = _read_sse_events(body)
    kinds = [e.get("event") for e in events]
    assert "debug" in kinds, f"debug event not found in events: {kinds}"
    dbg_evt = next(e for e in events if e.get("event") == "debug")
    j = dbg_evt.get("json") or {}
    payload_raw = j.get("data") if isinstance(j, dict) else {}
    payload = payload_raw if isinstance(payload_raw, dict) else {}
    for k in [
        "engine_wait_ms",
        "soft_timeout_s",
        "replay_max_events",
        "replay_max_age_s",
    ]:
        assert k in payload  # type: ignore[operator]

    # Confirm soft timeout final sequence present
    assert "error" in kinds and "final" in kinds, (
        "Expected soft timeout error/final events"
    )

    # Metrics export includes soft timeout counter
    mresp = client.get("/metrics")
    assert mresp.status_code == 200
    mbody = mresp.get_data(as_text=True)
    assert "aetherra_chat_soft_timeouts_total" in mbody

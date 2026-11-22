"""Exercise the public chat boundaries before any Engine or memory work."""

# Standard library imports
import json
import time
from unittest.mock import Mock

# Third party imports
import pytest
from flask import Flask

# Aetherra imports
import aetherra_hub.services.ai_stream as stream_service
from aetherra_hub.blueprints import ai_ask, ai_stream, chat
from aetherra_hub.services import chat_bridge
from aetherra_hub.services.idempotency import manager


@pytest.fixture
def client(monkeypatch, tmp_path):
    for key in ("AETHERRA_AI_API_ENABLED", "AETHERRA_AI_API_STREAM"):
        monkeypatch.setenv(key, "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path))
    app = Flask(__name__)
    for bp in (ai_ask.bp, ai_stream.bp, chat.bp):
        app.register_blueprint(bp)
    return app.test_client()


@pytest.mark.parametrize(
    ("method", "route"),
    [
        ("POST", "/api/ai/ask"),
        ("POST", "/api/ai/stream"),
        ("GET", "/api/ai/stream"),
        ("POST", "/api/lyrixa/chat"),
    ],
)
@pytest.mark.parametrize(
    "expiry", [{"deadline_ts": 0}, {"deadline_ts": 1}, {"ttl_sec": -1}]
)
def test_expiry_prevents_dispatch_and_idempotency(
    client, monkeypatch, tmp_path, method, route, expiry
):
    dispatch = Mock(side_effect=AssertionError("expired request reached dispatch"))
    for module, name in (
        (ai_ask, "_get_engine"),
        (stream_service, "_get_engine"),
        (chat_bridge, "_registry_call"),
        (manager, "check_and_mark"),
    ):
        monkeypatch.setattr(module, name, dispatch)
    payload = {
        "message": "SYNTHETIC_PRIVATE",
        "client_message_id": "reusable",
        **expiry,
    }
    kwargs = {"query_string" if method == "GET" else "json": payload}
    response = client.open(
        route, method=method, headers={"X-Aetherra-Trace-Id": "expiry-trace"}, **kwargs
    )
    assert response.headers["X-Aetherra-Chat-Version"] == "2"
    assert response.headers["X-Aetherra-Trace-Id"] == "expiry-trace"
    assert isinstance(json.loads(response.headers["X-Aetherra-Policy"]), dict)
    if "stream" in route:
        assert response.status_code == 200
        events = [
            json.loads(line[6:])
            for line in response.text.splitlines()
            if line.startswith("data: ")
        ]
        assert [event["type"] for event in events] == ["error", "final"]
        assert all(event["trace_id"] == "expiry-trace" for event in events)
        assert all(
            event["data"]["error"]["code"] == "invalid_request" for event in events
        )
        assert events[-1]["data"]["ok"] is False
    else:
        assert response.status_code == 409
        assert response.json["error"]["code"] == "invalid_request"
    dispatch.assert_not_called()
    receipt = (tmp_path / "hub_chat_dlq.jsonl").read_text(encoding="utf-8")
    assert "SYNTHETIC_PRIVATE" not in receipt
    assert "reusable" not in receipt
    assert json.loads(receipt)["reason"] == "expired"


@pytest.mark.parametrize("route", ["/api/ai/ask", "/api/ai/stream"])
@pytest.mark.parametrize(
    ("state", "status"), [("disabled", 501), ("unauthorized", 403)]
)
def test_early_errors_have_headers_without_expiry_receipt(
    client, monkeypatch, tmp_path, route, state, status
):
    if state == "disabled":
        monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "0")
    else:
        monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
        monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "synthetic-token")
    response = client.post(
        route, json={"message": "private", "deadline_ts": 1, "trace_id": "bad\r\ntrace"}
    )
    assert response.status_code == status
    assert response.headers["X-Aetherra-Trace-Id"] == "badtrace"
    assert response.headers["X-Aetherra-Chat-Version"] == "2"
    assert not (tmp_path / "hub_chat_dlq.jsonl").exists()


def test_future_deadline_still_reaches_engine(client, monkeypatch):
    class Engine:
        async def process_message(self, message, context):
            assert message == "hello"
            return {"text": "synthetic answer"}

    monkeypatch.setattr(ai_ask, "_get_engine", lambda: Engine())
    response = client.post(
        "/api/ai/ask", json={"message": "hello", "deadline_ts": time.time() + 60}
    )
    assert response.status_code == 200
    assert response.json["result"]["text"] == "synthetic answer"
    assert response.headers["X-Aetherra-Trace-Id"]


@pytest.mark.parametrize(
    ("route", "status"),
    [("/api/ai/ask", 501), ("/api/ai/stream", 413), ("/api/lyrixa/chat", 400)],
)
def test_oversized_body_does_not_break_error_headers(
    client, monkeypatch, route, status
):
    client.application.config["MAX_CONTENT_LENGTH"] = 100
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "0")
    response = client.post(route, json={"message": "x" * 200})
    assert response.status_code == status
    assert response.headers["X-Aetherra-Chat-Version"] == "2"
    assert response.headers["X-Aetherra-Trace-Id"]


def test_expired_websocket_does_not_consume_message_id(monkeypatch):
    mark = Mock(side_effect=AssertionError("expired websocket marked as processed"))
    monkeypatch.setattr(manager, "check_and_mark", mark)
    assert (
        ai_stream._duplicate_ws_message(
            {"deadline_ts": 0, "client_message_id": "retry"}, {}
        )
        is None
    )
    mark.assert_not_called()

"""Exercise the public chat boundaries before any Engine or memory work."""

# Standard library imports
import json
import threading
import time
from types import SimpleNamespace
from unittest.mock import Mock

# Third party imports
import pytest
from flask import Flask

# Aetherra imports
import aetherra_hub.services.ai_stream as stream_service
from aetherra_hub.blueprints import ai_ask, ai_stream, chat
from aetherra_hub.services import chat_bridge, chat_contract
from aetherra_hub.services.idempotency import IdempotencyManager, manager


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


@pytest.mark.parametrize("stage", ["safety", "guardian", "engine"])
@pytest.mark.parametrize("expiry", [{"deadline_ts": 101}, {"ttl_sec": 1}])
def test_ask_rejects_expiry_during_admission(client, monkeypatch, stage, expiry):
    clock = [100.0]
    monkeypatch.setattr(chat_contract, "time", SimpleNamespace(time=lambda: clock[0]))
    dispatched = []
    mark = Mock(return_value=False)
    monkeypatch.setattr(manager, "check_and_mark", mark)

    class Engine:
        async def process_message(self, message, context):
            dispatched.append(message)
            return {"text": "should not answer"}

    def safety(*args):
        if stage == "safety":
            clock[0] = 102.0
        return {"allow": True}

    def guardian(**kwargs):
        if stage == "guardian":
            clock[0] = 102.0
        return SimpleNamespace(allowed=True)

    def engine():
        if stage == "engine":
            clock[0] = 102.0
        return Engine()

    monkeypatch.setattr(ai_ask, "safety_precheck", safety)
    monkeypatch.setattr(ai_ask, "evaluate_chat_ingress", guardian)
    monkeypatch.setattr(ai_ask, "_get_engine", engine)
    response = client.post(
        "/api/ai/ask",
        json={"message": "private", "client_message_id": "retry", **expiry},
    )
    assert response.status_code == 409
    assert response.json["error"]["code"] == "invalid_request"
    assert not dispatched
    mark.assert_not_called()


@pytest.mark.parametrize(
    "stage", ["safety", "lookup", "worker", "offline", "worker_wait", "offline_wait"]
)
def test_stream_rejects_expiry_before_worker_dispatch(client, monkeypatch, stage):
    clock = [100.0]
    monkeypatch.setattr(chat_contract, "time", SimpleNamespace(time=lambda: clock[0]))
    dispatched = []
    lookups = [0]
    active_before = stream_service.CHAT_METRICS.streams_current

    class Engine:
        async def process_message(self, message, context):
            dispatched.append(message)
            return {"response": "should not answer"}

    def safety(*args):
        if stage == "safety":
            clock[0] = 102.0
        return {"allow": True}

    def engine():
        lookups[0] += 1
        if stage in {"lookup", "offline"} or (stage == "worker" and lookups[0] == 2):
            clock[0] = 102.0
        return None if stage in {"offline", "offline_wait"} else Engine()

    if stage.endswith("_wait"):
        monkeypatch.setenv("AETHERRA_ENGINE_WAIT_MS", "1000")

        def wait(seconds):
            if seconds >= 1:
                clock[0] = 102.0

        monkeypatch.setattr(
            stream_service, "time", SimpleNamespace(time=time.time, sleep=wait)
        )

    monkeypatch.setattr(stream_service, "safety_precheck", safety)
    monkeypatch.setattr(
        stream_service,
        "evaluate_chat_ingress",
        lambda **kwargs: SimpleNamespace(allowed=True),
    )
    monkeypatch.setattr(stream_service, "_get_engine", engine)
    response = client.post("/api/ai/stream", json={"message": "private", "ttl_sec": 1})
    events = [
        json.loads(line[6:])
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    final = events[-1]["data"]
    assert final["ok"] is False
    assert final["error"]["code"] == "invalid_request"
    assert not dispatched
    assert not any(event["data"].get("text") == "offline" for event in events)
    assert stream_service.CHAT_METRICS.streams_current == active_before


@pytest.mark.parametrize("available", [True, False, "error"])
def test_lyrixa_rejects_expiry_during_registry_wait(client, monkeypatch, available):
    import aetherra_service_registry

    clock = [100.0]
    monkeypatch.setattr(chat_contract, "time", SimpleNamespace(time=lambda: clock[0]))
    dispatched = []

    class Service:
        async def handle_message(self, message_type, payload):
            dispatched.append(payload)
            return {"text": "should not answer"}

    async def registry():
        clock[0] = 102.0
        if available == "error":
            raise RuntimeError("registry unavailable")
        return SimpleNamespace(
            get_service=lambda name: Service() if available else None
        )

    monkeypatch.setattr(aetherra_service_registry, "get_service_registry", registry)
    monkeypatch.setattr(chat_bridge, "safety_precheck", lambda *args: {"allow": True})
    monkeypatch.setattr(
        chat_bridge,
        "evaluate_chat_ingress",
        lambda **kwargs: SimpleNamespace(allowed=True),
    )
    response = client.post(
        "/api/lyrixa/chat", json={"message": "private", "ttl_sec": 1}
    )
    assert response.status_code == 409
    assert response.json["error"]["code"] == "invalid_request"
    assert not dispatched


@pytest.mark.parametrize("method", ["POST", "GET", "WS"])
def test_expired_stream_id_can_retry_after_admission(client, monkeypatch, method):
    clock = [100.0]
    monkeypatch.setattr(chat_contract, "time", SimpleNamespace(time=lambda: clock[0]))
    isolated_manager = IdempotencyManager(ttl_sec=60, enforce=True)
    monkeypatch.setattr(ai_stream, "idempotency_manager", isolated_manager)

    class Engine:
        async def process_message(self, message, context):
            return {"response": "accepted"}

    def safety(*args):
        clock[0] = 102.0
        return {"allow": True}

    monkeypatch.setattr(stream_service, "safety_precheck", safety)
    monkeypatch.setattr(stream_service, "_get_engine", lambda: Engine())
    monkeypatch.setattr(
        stream_service,
        "evaluate_chat_ingress",
        lambda **kwargs: SimpleNamespace(allowed=True),
    )
    if method == "WS":
        import flask_sock

        routes = {}

        class Sock:
            def __init__(self, app):
                pass

            def route(self, path):
                def register(handler):
                    routes[path] = handler
                    return handler

                return register

        monkeypatch.setattr(flask_sock, "Sock", Sock)
        monkeypatch.setenv("AETHERRA_AI_API_WS", "1")
        assert ai_stream.register_websocket_routes(client.application)

    def request_turn(deadline):
        payload = {
            "message": "private",
            "client_message_id": "retry",
            "deadline_ts": deadline,
        }
        if method == "WS":
            frames = []
            ws = SimpleNamespace(
                receive=lambda: json.dumps(payload),
                send=lambda frame: frames.append(json.loads(frame)),
            )
            routes["/ws/ai/stream"](ws)
            return frames[-1].get("data", frames[-1])
        response = client.open(
            "/api/ai/stream",
            method=method,
            **{"query_string" if method == "GET" else "json": payload},
        )
        if response.is_json:
            return response.json
        return [
            json.loads(line[6:])["data"]
            for line in response.text.splitlines()
            if line.startswith("data: ")
        ][-1]

    assert request_turn(101)["error"]["code"] == "invalid_request"
    retry = request_turn(200)
    assert retry["ok"] is True
    assert retry["result"]["response"] == "accepted"
    assert request_turn(200)["error"]["code"] == "duplicate"


def test_stream_deadline_wins_while_worker_registry_blocks(client, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr(chat_contract, "time", SimpleNamespace(time=lambda: clock[0]))
    release = threading.Event()
    finished = threading.Event()
    lookups = [0]
    dispatched = []

    class Engine:
        async def process_message(self, message, context):
            dispatched.append(message)
            return {"response": "too late"}

    def engine():
        lookups[0] += 1
        if lookups[0] == 2:
            clock[0] = 102.0
            assert release.wait(timeout=8)
            finished.set()
        return Engine()

    monkeypatch.setattr(stream_service, "_get_engine", engine)
    monkeypatch.setattr(
        stream_service, "safety_precheck", lambda *args: {"allow": True}
    )
    monkeypatch.setattr(
        stream_service,
        "evaluate_chat_ingress",
        lambda **kwargs: SimpleNamespace(allowed=True),
    )
    try:
        response = client.post(
            "/api/ai/stream", json={"message": "private", "deadline_ts": 101}
        )
        final = [
            json.loads(line[6:])["data"]
            for line in response.text.splitlines()
            if line.startswith("data: ")
        ][-1]
    finally:
        release.set()
        assert finished.wait(timeout=2)
    assert final["ok"] is False
    assert final["error"]["code"] == "invalid_request"
    assert not dispatched


def test_release_cannot_remove_a_newer_idempotency_reservation(monkeypatch):
    monkeypatch.setenv("AETHERRA_IDEMPOTENCY_ENFORCE", "0")
    cache = IdempotencyManager(ttl_sec=60, enforce=False)
    first = cache.reserve("synthetic", "request")
    second = cache.reserve("synthetic", "request")
    cache.release("synthetic", "request", first)
    cache.enforce = True
    assert cache.check_and_mark("synthetic", "request") is True
    cache.release("synthetic", "request", second)
    assert cache.check_and_mark("synthetic", "request") is False

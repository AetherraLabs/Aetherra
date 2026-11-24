"""The normal Hub must answer health probes while generation is in flight."""

from __future__ import annotations

# Standard library imports
import asyncio
import http.client
import json
import socket
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

# Third party imports
import pytest
from flask import Flask
from flask_cors import CORS

# Aetherra imports
from tests.acceptance.continuity_runtime import ContextResponder


def _request(port, method, path, body=None, *, timeout=2, extra_headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        connection.request(
            method,
            path,
            body=json.dumps(body) if body is not None else None,
            headers={
                "Content-Type": "application/json",
                "X-Aetherra-Token": "synthetic-responsiveness-token",
                "X-Aetherra-Principal": "hub:chat",
                **(extra_headers or {}),
            },
        )
        response = connection.getresponse()
        raw = response.read()
        payload = (
            json.loads(raw)
            if raw and "application/json" in response.getheader("Content-Type", "")
            else raw.decode()
        )
        return response.status, payload, dict(response.getheaders())
    finally:
        connection.close()


@pytest.fixture
def paused_hub(tmp_path, monkeypatch):
    # Aetherra imports
    from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine
    from aetherra_hub import compat
    from aetherra_hub.blueprints import ai_ask, ai_stream, health, kernel
    from aetherra_hub.services import ai_stream as streaming

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "synthetic-responsiveness-token")
    monkeypatch.setenv("AETHERRA_REGISTRY_URL", "")
    monkeypatch.setenv("AETHERRA_AB_RECALL_MODE", "classical")
    monkeypatch.setenv("AETHERRA_IDEMPOTENCY_ENFORCE", "1")
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    policy = tmp_path / "policy"
    policy.mkdir()
    guardian = policy / "guardian.json"
    guardian.write_text(
        json.dumps(
            {
                "version": 1,
                "default": "deny",
                "allow": [
                    {
                        "requester": "hub:chat",
                        "subsystem": "chat",
                        "action": "chat.ingress",
                        "target": "chat_route:*",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AETHERRA_GUARDIAN_POLICY", str(guardian))
    entered, release = threading.Event(), threading.Event()
    calls = []

    class PausedResponder(ContextResponder):
        async def generate_response(self, prompt):
            calls.append(prompt)
            entered.set()
            if not await asyncio.to_thread(release.wait, 10):
                raise RuntimeError("test_generation_was_not_released")
            return await super().generate_response(prompt)

    engine = AetherraEngine()
    engine.initialized = True
    engine._llm_manager = PausedResponder()
    engine._llm_selected = True
    monkeypatch.setattr(ai_ask, "_get_engine", lambda: engine)
    monkeypatch.setattr(streaming, "_get_engine", lambda: engine)
    app = Flask(__name__)
    CORS(app, origins=["https://allowed.example"])
    app.register_blueprint(health.bp)
    app.register_blueprint(ai_ask.bp)
    app.register_blueprint(ai_stream.bp)
    app.register_blueprint(kernel.bp)
    mutations = []

    @app.get("/unknown")
    def unknown():
        mutations.append("called")
        return {"ok": True}

    @app.route("/api/agents", methods=["OPTIONS"])
    def custom_options():
        mutations.append("custom-options")
        return {"ok": True}

    monkeypatch.setattr(compat, "create_app", lambda: app)
    monkeypatch.setattr(compat._reg_client, "get_kernel_status", lambda: {})
    monkeypatch.setattr(compat._reg_client, "get_orchestrator_status", lambda: {})
    monkeypatch.setattr(
        compat._reg_client,
        "get_engine_status",
        lambda: asyncio.run(engine.get_system_status()),
    )
    server = compat.AetherraHubServer(port=0, host="127.0.0.1")
    try:
        assert server.start_server()
        yield SimpleNamespace(
            port=server._srv.server_port,
            server=server,
            engine=engine,
            entered=entered,
            release=release,
            mutations=mutations,
            calls=calls,
        )
    finally:
        release.set()
        server.stop_server()
        asyncio.run(engine.shutdown())


@pytest.mark.parametrize("chat_path", ["/api/ai/ask", "/api/ai/stream"])
def test_normal_hub_observation_routes_remain_responsive_during_generation(
    paused_hub, chat_path
):
    state = paused_hub
    with ThreadPoolExecutor(max_workers=1) as client:
        future = client.submit(
            _request,
            state.port,
            "POST",
            chat_path,
            {"message": "My synthetic favorite tea is jasmine."},
            timeout=15,
        )
        try:
            assert state.entered.wait(5), "Request did not reach the real Engine"
            for path in (
                "/health",
                "/api/hub/readiness",
                "/api/kernel/readiness",
                "/api/ai/status",
            ):
                status, payload, _headers = _request(
                    state.port, "GET", path, timeout=0.75
                )
                assert status == 200
                assert isinstance(payload, dict)
                assert not future.done(), "Probe must finish before generation"
                status, payload, _headers = _request(
                    state.port, "HEAD", path, timeout=0.75
                )
                assert status == 200
                assert payload == ""
        finally:
            state.release.set()
            status, response, _headers = future.result(timeout=5)
            assert status == 200
            if chat_path.endswith("ask"):
                assert response["result"]["memory_id"]
                assert response["result"]["llm"]["fallback"] is False


def test_busy_chat_preserves_contract_without_consuming_id_or_replaying(paused_hub):
    state = paused_hub
    retry_id = uuid.uuid4().hex
    retry_body = {
        "message": "My synthetic favorite instrument is the cello.",
        "client_message_id": retry_id,
    }
    with ThreadPoolExecutor(max_workers=1) as client:
        first = client.submit(
            _request,
            state.port,
            "POST",
            "/api/ai/ask",
            {"message": "What synthetic tea do I prefer?"},
            timeout=15,
        )
        try:
            assert state.entered.wait(5)
            for path in ("/api/ai/ask", "/api/ai/stream", "/api/lyrixa/chat"):
                status, payload, headers = _request(
                    state.port,
                    "POST",
                    path,
                    retry_body,
                    extra_headers={"X-Aetherra-Trace-Id": "busy-test-trace"},
                )
                assert status == 503
                assert payload["error"]["code"] == "hub_busy"
                assert payload["error"]["retryable"] is True
                assert payload["trace_id"] == "busy-test-trace"
                assert headers["X-Aetherra-Trace-Id"] == "busy-test-trace"
                assert headers["X-Aetherra-Chat-Version"] == "2"
                assert "X-Aetherra-Policy" in headers
                assert headers["Retry-After"] == "1"
            status, _, _ = _request(state.port, "GET", "/unknown")
            assert status == 503
            assert state.mutations == []
            assert len(state.calls) == 1
        finally:
            state.release.set()
            assert first.result(timeout=5)[0] == 200
    assert state.server._srv.wait_for_idle(timeout=2)
    assert len(state.calls) == 1, "Rejected requests must never be queued or replayed"
    status, payload, _ = _request(
        state.port, "POST", "/api/ai/ask", retry_body, timeout=10
    )
    assert status == 200, payload
    assert len(state.calls) == 2
    assert state.server._srv.wait_for_idle(timeout=2)
    assert _request(state.port, "POST", "/api/ai/ask", retry_body)[0] == 409


def test_expired_and_unauthorized_busy_requests_never_dispatch(paused_hub):
    state = paused_hub
    body = {
        "message": "This synthetic expired statement must not be written.",
        "client_message_id": uuid.uuid4().hex,
        "deadline_ts": time.time() - 1,
    }
    with ThreadPoolExecutor(max_workers=1) as client:
        first = client.submit(
            _request,
            state.port,
            "POST",
            "/api/ai/ask",
            {"message": "What synthetic tea do I prefer?"},
            timeout=15,
        )
        try:
            assert state.entered.wait(5)
            assert _request(state.port, "POST", "/api/ai/ask", body)[0] == 503
        finally:
            state.release.set()
            assert first.result(timeout=5)[0] == 200
    assert state.server._srv.wait_for_idle(timeout=2)
    assert _request(state.port, "POST", "/api/ai/ask", body)[0] == 409
    assert state.server._srv.wait_for_idle(timeout=2)
    body.pop("deadline_ts")
    assert (
        _request(
            state.port,
            "POST",
            "/api/ai/ask",
            body,
            extra_headers={"X-Aetherra-Token": "incorrect"},
        )[0]
        == 403
    )
    assert len(state.calls) == 1
    assert state.server._srv.wait_for_idle(timeout=2)
    assert _request(state.port, "POST", "/api/ai/ask", body, timeout=10)[0] == 200
    assert len(state.calls) == 2


def test_disconnected_stream_retains_worker_ownership(paused_hub, monkeypatch):
    state = paused_hub
    monkeypatch.setenv("AETHERRA_STREAM_SOFT_TIMEOUT_S", "1")
    connection = http.client.HTTPConnection("127.0.0.1", state.port, timeout=3)
    response = None
    try:
        connection.request(
            "POST",
            "/api/ai/stream",
            json.dumps({"message": "My synthetic favorite tea is jasmine."}),
            headers={
                "Content-Type": "application/json",
                "X-Aetherra-Token": "synthetic-responsiveness-token",
                "X-Aetherra-Principal": "hub:chat",
            },
        )
        response = connection.getresponse()
        assert response.status == 200
        assert state.entered.wait(5)
        response.close()
        connection.close()
        assert state.server._srv.wait_for_idle(timeout=3)
        assert state.server._ownership.active == 1
        assert not state.release.is_set()
        assert _request(state.port, "GET", "/unknown")[0] == 503
        assert state.mutations == []
        assert _request(state.port, "GET", "/health")[0] == 200
    finally:
        if response is not None:
            response.close()
        connection.close()
        state.release.set()


def test_stop_retains_resources_until_detached_worker_finishes(paused_hub, monkeypatch):
    # Aetherra imports
    from aetherra_hub import compat

    state = paused_hub
    monkeypatch.setenv("AETHERRA_STREAM_SOFT_TIMEOUT_S", "1")
    monkeypatch.setattr(compat, "REQUEST_DRAIN_TIMEOUT_SECONDS", 0.05)
    with ThreadPoolExecutor(max_workers=1) as client:
        first = client.submit(
            _request,
            state.port,
            "POST",
            "/api/ai/stream",
            {"message": "My synthetic favorite tea is jasmine."},
            timeout=5,
        )
        try:
            assert state.entered.wait(5)
            assert first.result(timeout=3)[0] == 200
            listener = state.server._srv
            ownership = state.server._ownership
            with pytest.raises(RuntimeError, match="drain timeout; resources retained"):
                state.server.stop_server()
            assert state.server._srv is listener
            assert state.server._ownership is ownership
            assert listener.socket.fileno() != -1
            assert ownership.draining
            assert not state.server.is_running()
        finally:
            state.release.set()
    assert ownership.wait_for_idle(timeout=5)
    state.server.stop_server()
    assert listener.socket.fileno() == -1
    assert state.server._srv is None
    assert state.server._ownership is None


def test_generation_can_outlive_socket_io_timeout(paused_hub, monkeypatch):
    # Aetherra imports
    from aetherra_hub import request_server

    state = paused_hub
    monkeypatch.setattr(request_server._RequestHandler, "timeout", 0.05)
    with ThreadPoolExecutor(max_workers=1) as client:
        first = client.submit(
            _request,
            state.port,
            "POST",
            "/api/ai/ask",
            {"message": "My synthetic favorite tea is jasmine."},
            timeout=5,
        )
        try:
            assert state.entered.wait(5)
            assert not state.release.wait(0.15)
            assert not first.done()
            assert _request(state.port, "GET", "/health")[0] == 200
        finally:
            state.release.set()
            assert first.result(timeout=5)[0] == 200


def test_request_workers_are_bounded_and_incomplete_headers_expire(
    paused_hub, monkeypatch
):
    # Aetherra imports
    from aetherra_hub import request_server

    state = paused_hub
    monkeypatch.setattr(request_server._RequestHandler, "timeout", 1.5)
    clients = []
    listener = state.server._srv
    try:
        for _ in range(request_server.MAX_REQUEST_WORKERS):
            client = socket.create_connection(("127.0.0.1", state.port), timeout=2)
            client.sendall(b"GET /health HTTP/1.1\r\nHost: localhost\r\n")
            clients.append(client)
        with listener._workers:
            assert listener._workers.wait_for(
                lambda: listener._active_workers == request_server.MAX_REQUEST_WORKERS,
                timeout=1,
            )
        # Capacity rejection happens before parsing any request. Read that raw
        # response without racing request bytes against close (which can reset
        # an ordinary HTTP client on Windows at this best-effort boundary).
        with socket.create_connection(("127.0.0.1", state.port), timeout=2) as sock:
            response = http.client.HTTPResponse(sock)
            response.begin()
            payload = json.loads(response.read())
            assert response.status == 503
            assert payload["error"]["code"] == "hub_saturated"
            assert payload["error"]["retryable"] is True
            assert response.getheader("Retry-After") == "1"
            assert response.getheader("X-Aetherra-Trace-Id") is None
            response.close()
        assert listener.wait_for_idle(timeout=3)
        assert _request(state.port, "GET", "/health")[0] == 200
    finally:
        for client in clients:
            client.close()


def test_incomplete_body_times_out_without_dispatch_or_stuck_ownership(
    paused_hub, monkeypatch
):
    # Aetherra imports
    from aetherra_hub import request_server

    state = paused_hub
    monkeypatch.setattr(request_server._RequestHandler, "timeout", 0.2)
    with socket.create_connection(("127.0.0.1", state.port), timeout=2) as client:
        client.sendall(
            b"POST /api/ai/ask HTTP/1.1\r\nHost: localhost\r\n"
            b"Content-Type: application/json\r\nContent-Length: 100\r\n"
            b"X-Aetherra-Token: synthetic-responsiveness-token\r\n\r\n{"
        )
        response = client.recv(4096)
        assert b"400 BAD REQUEST" in response
    assert state.server._srv.wait_for_idle(timeout=2)
    assert state.server._ownership.wait_for_idle(timeout=2)
    assert state.calls == []
    assert _request(state.port, "GET", "/unknown")[0] == 200


def test_request_worker_cannot_drain_itself():
    # Aetherra imports
    from aetherra_hub.services.request_ownership import (
        RequestOwnership,
        retain_current_request,
    )

    retained = []

    def app(_environ, start_response):
        retained.append(retain_current_request())
        start_response("200 OK", [])
        return [b"ok"]

    owner = RequestOwnership(app)
    response = owner(
        {"REQUEST_METHOD": "POST", "PATH_INFO": "/mutation"}, lambda *_: None
    )
    assert list(response) == [b"ok"]
    response.close()
    assert not owner.wait_for_idle(timeout=0)
    with (
        retained[0],
        pytest.raises(RuntimeError, match="cannot stop from its request worker"),
    ):
        owner.begin_drain()
    assert not owner.draining
    assert owner.wait_for_idle(timeout=0)


def test_busy_preserves_configured_cors_and_only_automatic_options(paused_hub):
    state = paused_hub
    with ThreadPoolExecutor(max_workers=1) as client:
        first = client.submit(
            _request,
            state.port,
            "POST",
            "/api/ai/ask",
            {"message": "My synthetic favorite tea is jasmine."},
            timeout=15,
        )
        try:
            assert state.entered.wait(5)
            for origin, allowed in (
                ("https://allowed.example", True),
                ("https://denied.example", False),
            ):
                headers = {
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type,X-Aetherra-Token",
                }
                status, _, response_headers = _request(
                    state.port, "OPTIONS", "/api/ai/ask", extra_headers=headers
                )
                assert status == 200
                assert (
                    response_headers.get("Access-Control-Allow-Origin") == origin
                ) == allowed
                status, payload, response_headers = _request(
                    state.port,
                    "POST",
                    "/api/ai/ask",
                    {"message": "This rejected fact must never be dispatched."},
                    extra_headers={"Origin": origin},
                )
                assert status == 503
                assert payload["error"]["code"] == "hub_busy"
                assert (
                    response_headers.get("Access-Control-Allow-Origin") == origin
                ) == allowed
            assert _request(state.port, "OPTIONS", "/api/agents")[0] == 503
            assert _request(state.port, "OPTIONS", "/missing-route")[0] == 503
            assert state.mutations == []
            assert len(state.calls) == 1
            # Leave a declared body incomplete: the busy response must arrive
            # without reading it, even through Flask's chat/CORS response hooks.
            with socket.create_connection(("127.0.0.1", state.port), timeout=1) as sock:
                sock.sendall(
                    b"POST /api/ai/ask HTTP/1.1\r\nHost: localhost\r\n"
                    b"Content-Type: application/json\r\nContent-Length: 1000\r\n"
                    b"Origin: https://allowed.example\r\n"
                    b"X-Aetherra-Trace-Id: unread-body-trace\r\n\r\n{"
                )
                response = http.client.HTTPResponse(sock)
                response.begin()
                assert response.status == 503
                assert response.getheader("X-Aetherra-Trace-Id") == "unread-body-trace"
                assert (
                    response.getheader("Access-Control-Allow-Origin")
                    == "https://allowed.example"
                )
                assert json.loads(response.read())["error"]["code"] == "hub_busy"
                response.close()
        finally:
            state.release.set()
            assert first.result(timeout=5)[0] == 200


def test_soft_timeout_does_not_release_worker_mutation_ownership(
    paused_hub, monkeypatch
):
    state = paused_hub
    monkeypatch.setenv("AETHERRA_STREAM_SOFT_TIMEOUT_S", "1")
    with ThreadPoolExecutor(max_workers=1) as client:
        future = client.submit(
            _request,
            state.port,
            "POST",
            "/api/ai/stream",
            {"message": "My synthetic favorite tea is jasmine."},
            timeout=5,
        )
        try:
            assert state.entered.wait(5)
            status, response, _headers = future.result(timeout=3)
            assert status == 200
            assert "soft_timeout" in response
            status, payload, headers = _request(state.port, "GET", "/unknown")
            assert status == 503
            assert payload["error"]["code"] == "hub_busy"
            assert headers["Retry-After"] == "1"
            assert state.mutations == []
        finally:
            state.release.set()

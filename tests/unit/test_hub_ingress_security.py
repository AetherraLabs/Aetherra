"""Security tests for Hub service-ingress endpoints."""

from __future__ import annotations

from flask import Flask

from aetherra_hub.blueprints import ai_stream, consciousness, telemetry, trainer
from aetherra_hub.services.state import hub_state


def _app(*blueprints) -> Flask:
    app = Flask(__name__)
    for blueprint in blueprints:
        app.register_blueprint(blueprint.bp)
    return app


def test_ai_stream_rejects_missing_and_unconfigured_tokens(monkeypatch):
    monkeypatch.setattr(ai_stream.metrics_accum, "inc_auth_missing_token", lambda: None)
    monkeypatch.setattr(ai_stream.metrics_accum, "inc_auth_invalid_token", lambda: None)
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    monkeypatch.delenv("AETHERRA_AI_API_TOKEN", raising=False)
    client = _app(ai_stream).test_client()

    response = client.post("/api/ai/stream", json={"message": "hello"})
    assert response.status_code == 503
    assert response.get_json()["error"] == "ai_token_not_configured"

    monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "secret")
    response = client.post("/api/ai/stream", json={"message": "hello"})
    assert response.status_code == 403


def test_consciousness_update_requires_control_auth_in_production(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "secret")
    hub_state.consciousness_state = {}
    client = _app(consciousness).test_client()

    denied = client.post("/api/consciousness/update", json={"tick_id": 1})
    assert denied.status_code == 401
    assert hub_state.consciousness_state == {}

    accepted = client.post(
        "/api/consciousness/update",
        json={"tick_id": 1, "qualia": {}, "focuses": [], "intentions": []},
        headers={"Authorization": "Bearer secret"},
    )
    assert accepted.status_code == 200
    assert hub_state.consciousness_state["tick_id"] == 1


def test_consciousness_rejects_invalid_state(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    client = _app(consciousness).test_client()

    response = client.post(
        "/api/consciousness/update",
        json={"tick_id": "not-an-integer"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_tick_id"


def test_telemetry_is_local_only_and_bounded_without_token(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "dev")
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    telemetry._events.clear()
    client = _app(telemetry).test_client()

    denied = client.post(
        "/api/telemetry",
        json={"event": "remote"},
        environ_base={"REMOTE_ADDR": "203.0.113.5"},
    )
    assert denied.status_code == 403

    for index in range(1_001):
        accepted = client.post("/api/telemetry", json={"event": index})
        assert accepted.status_code == 200
    assert len(telemetry._events) == 1_000
    assert telemetry._events[0]["event"] == 1


def test_trainer_submission_requires_control_auth(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "secret")
    monkeypatch.setenv("AETHERRA_TRAINER_ENABLED", "1")
    client = _app(trainer).test_client()

    denied = client.post("/api/trainer/jobs", json={"task": "sft"})
    assert denied.status_code == 401

    oversized = client.post(
        "/api/trainer/jobs",
        data=b"x" * 262_145,
        headers={
            "Authorization": "Bearer secret",
            "Content-Type": "application/json",
        },
    )
    assert oversized.status_code == 413

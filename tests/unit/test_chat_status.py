from aetherra_hub.app import create_app
from aetherra_hub.config import Settings
from aetherra_hub.services.chat_status import assess_chat_readiness


def _settings(**overrides):
    data = {"prod_profile": False}
    data.update(overrides)
    return Settings(**data)


def test_chat_status_endpoint_reports_degraded_when_ai_api_disabled(monkeypatch):
    monkeypatch.delenv("AETHERRA_AI_API_ENABLED", raising=False)
    client = create_app(_settings()).test_client()

    response = client.get("/api/chat/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert payload["ok"] is True
    assert payload["readiness"]["readiness"] == "degraded"
    assert "ai_developer_api_disabled" in payload["readiness"]["reasons"]


def test_chat_readiness_reports_ready_when_ask_and_stream_enabled(monkeypatch):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_CHAT_SAFETY_MODE", "strict")

    payload = assess_chat_readiness(_settings())

    assert payload["readiness"] == "ready"
    assert payload["safe_for_clients"] is True
    assert payload["checks"]["safety_mode"] == "strict"


def test_chat_readiness_blocks_in_insecure_prod_posture(monkeypatch):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    monkeypatch.delenv("AETHERRA_AI_API_TOKEN", raising=False)
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)

    payload = assess_chat_readiness(_settings(prod_profile=True))

    assert payload["readiness"] == "blocked"
    assert payload["safe_for_clients"] is False
    assert "prod_ai_chat_token_not_required" in payload["reasons"]
    assert "prod_ai_chat_token_missing" in payload["reasons"]


def test_chat_readiness_blocks_invalid_safety_mode(monkeypatch):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_CHAT_SAFETY_MODE", "unknown")

    payload = assess_chat_readiness(_settings())

    assert payload["readiness"] == "blocked"
    assert "invalid_safety_mode" in payload["reasons"]

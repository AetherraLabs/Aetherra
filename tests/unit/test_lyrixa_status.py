import types

from Aetherra.lyrixa.chat.lyrixa_chat_service import LyrixaChatService
from aetherra_hub.app import create_app
from aetherra_hub.services import chat_bridge


def test_lyrixa_service_status_reports_uninitialized_degraded(monkeypatch, tmp_path):
    monkeypatch.delenv("AETHERRA_LYRIXA_FORCE_OFFLINE", raising=False)
    service = LyrixaChatService(workspace_root=tmp_path)

    status = service.get_status()

    assert status["system"] == "lyrixa"
    assert status["service"] == "lyrixa_chat"
    assert status["readiness"] == "degraded"
    assert status["safe_for_interaction"] is True
    assert status["capabilities"]["offline_fallback"] is True
    assert status["capabilities"]["safe_edits_require_guardian"] is True


def test_lyrixa_service_status_reports_forced_offline(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_LYRIXA_FORCE_OFFLINE", "1")
    service = LyrixaChatService(workspace_root=tmp_path)

    status = service.get_status()

    assert status["readiness"] == "offline"
    assert status["forced_offline"] is True
    assert status["safe_for_interaction"] is False


def test_lyrixa_status_endpoint_reports_offline_fallback(monkeypatch):
    monkeypatch.setattr(chat_bridge, "_registry_status_call", lambda: None)
    client = create_app().test_client()

    response = client.get("/api/lyrixa/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert payload["readiness"] == "offline"
    assert payload["capabilities"]["offline_fallback"] is True


def test_lyrixa_status_endpoint_reports_registered_service(monkeypatch):
    monkeypatch.setattr(
        chat_bridge,
        "_registry_status_call",
        lambda: {
            "system": "lyrixa",
            "service": "lyrixa_chat",
            "readiness": "ready",
            "safe_for_interaction": True,
        },
    )
    client = create_app().test_client()

    response = client.get("/api/lyrixa/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["readiness"] == "ready"
    assert payload["safe_for_interaction"] is True


def test_openapi_advertises_lyrixa_status_endpoint():
    client = create_app().test_client()

    response = client.get("/api/openapi.json")
    spec = response.get_json()

    assert response.status_code == 200
    assert "/api/lyrixa/status" in spec["paths"]


def test_lyrixa_registry_status_call_accepts_service_status(monkeypatch):
    class _Service:
        def get_status(self):
            return {"readiness": "ready", "safe_for_interaction": True}

    class _Registry:
        def get_service(self, name):
            return _Service() if name == "lyrixa_chat" else None

    async def _get_registry():
        return _Registry()

    fake_registry = types.ModuleType("aetherra_service_registry")
    fake_registry.get_service_registry = _get_registry
    monkeypatch.setitem(__import__("sys").modules, "aetherra_service_registry", fake_registry)

    status = chat_bridge.get_lyrixa_status()

    assert status["readiness"] == "ready"
    assert status["system"] == "lyrixa"
    assert status["service"] == "lyrixa_chat"

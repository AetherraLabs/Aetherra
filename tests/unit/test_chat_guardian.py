import json

from aetherra_hub.app import create_app
from aetherra_hub.services import ai_stream, chat_bridge


class _FakeEngine:
    def __init__(self):
        self.called = False

    async def process_message(self, message, context):
        self.called = True
        return {"response": "ok", "context_used": bool(context)}


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def _audit_text(tmp_path):
    return (tmp_path / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _last_audit_entry(tmp_path):
    entries = [
        json.loads(line)
        for line in _audit_text(tmp_path).splitlines()
        if line.strip()
    ]
    return entries[-1]


def test_ai_ask_chat_ingress_guardian_audit_without_prompt(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    engine = _FakeEngine()
    monkeypatch.setattr("aetherra_hub.blueprints.ai_ask._get_engine", lambda: engine)

    response = create_app().test_client().post(
        "/api/ai/ask",
        json={
            "message": "do-not-audit-this-chat-prompt",
            "priority": "normal",
        },
    )

    assert response.status_code == 200
    assert engine.called is True
    ledger_text = _audit_text(tmp_path)
    assert "do-not-audit-this-chat-prompt" not in ledger_text
    assert _last_audit_entry(tmp_path)["details"]["intent"]["action"] == "chat.ingress"


def test_ai_ask_chat_ingress_guardian_denial_stops_engine(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-chat-client",
        strict=True,
    )
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    engine = _FakeEngine()
    monkeypatch.setattr("aetherra_hub.blueprints.ai_ask._get_engine", lambda: engine)

    response = create_app().test_client().post(
        "/api/ai/ask",
        json={"message": "blocked prompt"},
        headers={"X-Aetherra-Principal": "external-chat-client"},
    )

    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "guardian_denied"
    assert engine.called is False


def test_ai_stream_chat_ingress_guardian_denial_stops_final_processing(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-chat-client",
        strict=True,
    )
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    engine = _FakeEngine()
    monkeypatch.setattr(ai_stream, "_get_engine", lambda: engine)

    frames = list(
        ai_stream.stream_sse(
            {"message": "blocked stream"},
            {"X-Aetherra-Principal": "external-chat-client"},
        )
    )
    joined = "".join(frames)

    assert '"code": "guardian_denied"' in joined
    assert "event: final" in joined
    assert engine.called is False


def test_lyrixa_chat_bridge_guardian_denial_stops_registry(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-chat-client",
        strict=True,
    )
    called = False

    def _registry_call(*args, **kwargs):
        nonlocal called
        called = True
        return {"text": "should-not-run"}

    monkeypatch.setattr(chat_bridge, "_registry_call", _registry_call)

    body, code, _headers = chat_bridge.handle_chat(
        {
            "message": "blocked lyrixa chat",
            "principal": "external-chat-client",
        }
    )

    assert code == 403
    assert body["error"] == "guardian_denied"
    assert called is False

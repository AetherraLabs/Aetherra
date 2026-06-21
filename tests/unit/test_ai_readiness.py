from Aetherra.aetherra_core.engine import assess_ai_readiness
from aetherra_hub.app import create_app
from aetherra_hub.blueprints import ai_ask


def _ready_status(**overrides):
    status = {
        "engine_status": "active",
        "session_active": False,
        "memory_system": {"status": "healthy", "total_memories": 0},
        "improvement_system": {"status": "active", "improvements": 0},
        "agent_orchestrator": {"status": "active", "pending_tasks": 0},
        "health_monitoring": {"status": "healthy", "health": "healthy"},
        "session_metrics": {
            "messages": 0,
            "rag_hits": 0,
            "rag_misses": 0,
            "safety_filters_triggered": 0,
        },
    }
    status.update(overrides)
    return status


def test_ai_readiness_reports_ready_for_complete_active_status():
    payload = assess_ai_readiness(_ready_status())

    assert payload["readiness"] == "ready"
    assert payload["safe_for_requests"] is True
    assert payload["reasons"] == ["ready"]
    assert payload["checks"]["status_contract_complete"] is True


def test_ai_readiness_reports_offline_when_status_missing():
    payload = assess_ai_readiness(None)

    assert payload["readiness"] == "offline"
    assert payload["safe_for_requests"] is False
    assert "engine_status_unavailable" in payload["reasons"]


def test_ai_readiness_blocks_incomplete_or_unavailable_components():
    payload = assess_ai_readiness(
        _ready_status(memory_system={"status": "unavailable", "error": "missing"})
    )

    assert payload["readiness"] == "blocked"
    assert payload["safe_for_requests"] is False
    assert "component_unavailable:memory_system" in payload["reasons"]


def test_ai_readiness_degrades_when_engine_inactive():
    payload = assess_ai_readiness(_ready_status(engine_status="inactive"))

    assert payload["readiness"] == "degraded"
    assert payload["safe_for_requests"] is False
    assert "engine_not_active" in payload["reasons"]


def test_ai_status_endpoint_reports_readiness(monkeypatch):
    monkeypatch.setattr(
        ai_ask.registry_client,
        "get_engine_status",
        lambda: _ready_status(),
    )
    client = create_app().test_client()

    response = client.get("/api/ai/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert payload["ok"] is True
    assert payload["readiness"]["readiness"] == "ready"
    assert payload["readiness"]["safe_for_requests"] is True

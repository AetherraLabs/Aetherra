from Aetherra.aetherra_core.engine import (
    assess_ai_readiness,
    build_ai_readiness_payload,
)
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


def test_ai_readiness_blocks_when_engine_import_failed():
    payload = assess_ai_readiness(
        _ready_status(
            engine_import_error="ImportError: token=t-1 C:/Users/example/private.py"
        )
    )

    assert payload["readiness"] == "blocked"
    assert payload["safe_for_requests"] is False
    assert "engine_import_unavailable" in payload["reasons"]


def test_ai_readiness_degrades_for_engine_diagnostic_failures():
    payload = assess_ai_readiness(
        _ready_status(
            persistent_memory={
                "status": "degraded",
                "error": {
                    "code": "persistent_memory_setup_failed",
                    "trace_id": "trace-1",
                },
            },
            task_execution={
                "status": "submission_failed",
                "error": {"code": "task_submission_failed", "trace_id": "trace-2"},
            },
            response_persistence={
                "assistant_memory": {
                    "status": "degraded",
                    "error": {
                        "code": "assistant_memory_store_failed",
                        "trace_id": "trace-3",
                    },
                }
            },
            scratchpad={
                "status": "degraded",
                "error": {"code": "scratchpad_update_failed", "trace_id": "trace-4"},
            },
            coherence={
                "status": "degraded",
                "error": {
                    "code": "coherence_metric_estimate_failed",
                    "trace_id": "trace-5",
                },
            },
            reflection={
                "status": "ok",
                "memory": {
                    "status": "degraded",
                    "error": {
                        "code": "reflection_memory_store_failed",
                        "trace_id": "trace-6",
                    },
                },
            },
            lifecycle={"diagnostics": [{"code": "component_start_failed"}]},
        )
    )

    assert payload["readiness"] == "degraded"
    assert payload["safe_for_requests"] is False
    assert "persistent_memory_degraded" in payload["reasons"]
    assert "task_execution_degraded" in payload["reasons"]
    assert "lifecycle_diagnostics_present" in payload["reasons"]
    assert (
        "diagnostic_degraded:response_persistence.assistant_memory"
        in payload["reasons"]
    )
    assert "diagnostic_degraded:scratchpad" in payload["reasons"]
    assert "diagnostic_degraded:coherence" in payload["reasons"]
    assert "diagnostic_degraded:reflection.memory" in payload["reasons"]
    assert payload["checks"]["persistent_memory"] == "degraded"
    assert payload["checks"]["task_execution"] == "degraded"
    assert payload["checks"]["lifecycle_diagnostic_count"] == 1


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


def test_ai_ask_reports_engine_unavailable_without_success(monkeypatch):
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    monkeypatch.setattr(ai_ask, "_get_engine", lambda: None)
    client = create_app().test_client()

    response = client.post(
        "/api/ai/ask",
        json={"message": "hello", "trace_id": "trace-test"},
    )
    payload = response.get_json()

    assert response.status_code == 503
    assert payload["ok"] is False
    assert payload["error"] == {
        "code": "engine_unavailable",
        "message": "AI engine is unavailable",
        "details": {"trace_id": "trace-test"},
    }


def test_ai_ask_sanitizes_engine_processing_exception(monkeypatch):
    class FailingEngine:
        async def process_message(self, message, context):
            raise RuntimeError("sensitive path C:/Users/example/engine-secret.db")

    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
    monkeypatch.setattr(ai_ask, "_get_engine", lambda: FailingEngine())
    client = create_app().test_client()

    response = client.post(
        "/api/ai/ask",
        json={"message": "hello", "trace_id": "trace-fail"},
    )
    payload = response.get_json()

    assert response.status_code == 500
    assert payload["ok"] is False
    assert payload["error"] == {
        "code": "engine_processing_failed",
        "message": "AI engine request failed",
        "details": {"trace_id": "trace-fail"},
    }
    assert "engine-secret.db" not in str(payload)
    assert "sensitive path" not in str(payload)


def test_ai_readiness_payload_does_not_reflect_raw_engine_status_details():
    payload = build_ai_readiness_payload(
        _ready_status(
            memory_system={
                "status": "healthy",
                "path": "C:/Users/example/private-memory.db",
                "token": "token=t-1",
            },
            engine_import_error="ImportError: token=t-1 C:/Users/example/private.py",
        )
    )

    assert payload["engine"] == {
        "engine_status": "active",
        "session_active": False,
        "components": {
            "memory_system": "available",
            "improvement_system": "available",
            "agent_orchestrator": "available",
            "health_monitoring": "available",
        },
        "engine_import_error": "engine_import_unavailable",
        "diagnostics": {
            "persistent_memory": "unknown",
            "task_execution": "unknown",
            "lifecycle_diagnostics": 0,
        },
    }
    assert "private-memory.db" not in str(payload)
    assert "private.py" not in str(payload)
    assert "t-1" not in str(payload)

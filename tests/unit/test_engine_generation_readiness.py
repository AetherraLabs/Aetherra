"""Provider configuration is observed read-only and is not a live API proof."""

# Standard library imports
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine
from Aetherra.aetherra_core.engine.readiness import (
    assess_ai_readiness,
    build_ai_readiness_payload,
)
from tests.unit.test_ai_readiness import _ready_status


def status_engine(manager, selected):
    engine = AetherraEngine.__new__(AetherraEngine)
    engine.initialized = True
    engine.session_id = None
    engine.session_metrics = {}
    engine.memory_system = SimpleNamespace(
        get_memory_stats=AsyncMock(return_value={"status": "healthy"})
    )
    engine.improvement_engine = SimpleNamespace(
        get_improvement_status=lambda: {"status": "healthy"}
    )
    engine.agent_orchestrator = SimpleNamespace(
        get_system_status=lambda: {"status": "healthy"}
    )
    engine.introspection = SimpleNamespace(
        get_health_status=lambda: {"status": "healthy"}
    )
    engine._lifecycle_diagnostics = []
    for name in (
        "session_start",
        "persistent_memory",
        "input_persistence",
        "response_persistence",
        "optional_processing",
        "task_execution",
        "scratchpad",
        "coherence",
        "reflection",
    ):
        setattr(engine, f"_last_{name}_info", {})
    engine._persistent_memory = None
    engine._llm_manager = manager
    engine._llm_selected = selected
    return engine


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("primary", "current", "selected", "expected"),
    [
        ("openai", {"provider": "openai"}, True, "configured"),
        ("deterministic", {"provider": "deterministic"}, True, "configured"),
        ("openai", {"provider": "openai"}, False, "not_selected"),
        ("openai", None, True, "not_selected"),
        ("openai", {"provider": "ollama"}, True, "not_selected"),
        (None, {"provider": "openai"}, True, "not_selected"),
    ],
)
async def test_live_engine_status_reports_only_current_selected_primary(
    primary, current, selected, expected
):
    manager = SimpleNamespace(
        primary_provider=SimpleNamespace(value=primary),
        get_current_model_info=Mock(return_value=current),
        generate_response=Mock(
            side_effect=AssertionError("readiness must not generate")
        ),
        list_available_models=Mock(
            side_effect=AssertionError("readiness must not select")
        ),
    )
    engine = status_engine(manager, selected)
    status = await engine.get_system_status()
    evidence = status["generation"]
    assert evidence["status"] == expected
    assert evidence["model_selected"] is (expected == "configured")
    assert evidence["check_scope"] == "configuration_only"
    manager.get_current_model_info.assert_called_once()
    manager.generate_response.assert_not_called()
    manager.list_available_models.assert_not_called()
    assert "provider" not in evidence  # do not expose arbitrary manager metadata
    assert assess_ai_readiness(status)["safe_for_requests"] is (
        expected == "configured"
    )


@pytest.mark.asyncio
async def test_no_manager_and_private_status_error_remain_unavailable():
    missing = await status_engine(None, False).get_system_status()
    assert missing["generation"]["status"] == "unavailable"
    manager = SimpleNamespace(
        get_current_model_info=Mock(side_effect=RuntimeError("PRIVATE_KEY"))
    )
    broken = await status_engine(manager, True).get_system_status()
    assert broken["generation"]["status"] == "unknown"
    assert "PRIVATE_KEY" not in str(build_ai_readiness_payload(broken))
    assert assess_ai_readiness(broken)["safe_for_requests"] is False


def test_legacy_status_without_generation_keeps_its_existing_contract():
    assert assess_ai_readiness(_ready_status())["safe_for_requests"] is True


@pytest.mark.parametrize(
    "generation",
    [
        {},
        {"status": "configured", "model_selected": False},
        {"status": "unknown"},
        {"status": []},
        None,
    ],
)
def test_malformed_explicit_generation_evidence_is_not_ready(generation):
    report = assess_ai_readiness(_ready_status(generation=generation))
    assert report["safe_for_requests"] is False
    assert "generation_unavailable" in report["reasons"]

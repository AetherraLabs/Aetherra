"""Consciousness status must reflect completed observer work without side effects."""

# Standard library imports
import time
from datetime import datetime, timedelta
from types import SimpleNamespace

# Third party imports
import pytest
from flask import Flask

# Aetherra imports
import aetherra_service_registry as registry_module
from Aetherra.runtime_ui import collect_runtime_ui_system_status
from aetherra_hub.blueprints.runtime_ui import bp
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceInfo,
    ServiceStatus,
)


def _status(**overrides):
    return {
        "runtime_state": "running",
        "running": True,
        "thread_alive": True,
        "ticks_attempted": 4,
        "ticks_completed": 3,
        "last_tick_at": time.time(),
        "last_tick_age_seconds": 0.0,
        "tick_interval_seconds": 0.2,
        "events_processed": 11,
        "autonomy_mode": "observe",
        "persistence_enabled": False,
        "qfac_persistence_enabled": False,
        "action_execution_enabled": False,
        "think_stream_available": True,
        "last_error_code": None,
        **overrides,
    }


@pytest.fixture
def registry(monkeypatch):
    registry = AetherraServiceRegistry()
    registry._running = True
    monkeypatch.setattr(registry_module, "_service_registry", registry)
    return registry


def _register(registry, raw, *, status=ServiceStatus.HEALTHY, stale=False):
    def forbidden():
        raise AssertionError("GET must not evaluate autopilot or mutate core state")

    instance = SimpleNamespace(get_runtime_status=lambda: raw, get_status=forbidden)
    registry._services["consciousness_core"] = ServiceInfo(
        name="consciousness_core",
        instance=instance,
        status=status,
        last_heartbeat=datetime.now() - timedelta(hours=1 if stale else 0),
        metadata={"phase": "phase_c1_observer", "observer_only": True},
    )
    return instance


def test_observatory_projects_actual_ticks_and_events_without_core_status(registry):
    raw = _status(private_path="private/path", recent_narrative=["private narrative"])
    _register(registry, raw)
    app = Flask(__name__)
    app.register_blueprint(bp)
    body = app.test_client().get("/api/runtime-ui/bootstrap").get_json()
    observed = next(
        s for s in body["observatory"]["subsystems"] if s["name"] == "consciousness"
    )
    assert observed["status"] == "active"
    metrics = observed["metrics"]
    assert metrics["evidence"] == "observer_runtime"
    assert metrics["runtime_state"] == "running"
    assert metrics["ticks_completed"] == 3
    assert metrics["events_processed"] == 11
    assert metrics["authority"] == "observe"
    assert metrics["autonomy_mode"] == "observe"
    assert metrics["action_execution_enabled"] is False
    assert metrics["persistence_enabled"] is False
    assert metrics["freshness"] == "fresh"
    assert metrics["readiness_verified"] is False
    assert "private" not in str(observed)
    assert "last_error_code" not in metrics
    assert raw["ticks_completed"] == 3


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("starting", "unknown"),
        ("blocked", "degraded"),
        ("failed", "offline"),
        ("stopping", "offline"),
        ("stopped", "offline"),
    ],
)
def test_lifecycle_state_overrides_registry_presence(registry, state, expected):
    _register(
        registry,
        _status(runtime_state=state, running=False, thread_alive=False),
        status=ServiceStatus.FAILED,
        stale=True,
    )
    observed = collect_runtime_ui_system_status()["consciousness"]
    assert observed["status"] == expected
    assert observed["metrics"]["runtime_state"] == state
    assert observed["metrics"]["available"] is False


@pytest.mark.parametrize(
    "change",
    [
        {"last_tick_at": None},
        {"last_tick_at": float("nan")},
        {"last_tick_at": float("inf")},
        {"last_tick_at": time.time() + 3600},
        {"ticks_completed": 0},
        {"ticks_completed": True},
        {"ticks_completed": -1},
        {"ticks_attempted": 1},
        {"thread_alive": False},
        {"thread_alive": "yes"},
        {"running": False},
        {"tick_interval_seconds": 0},
        {"tick_interval_seconds": float("inf")},
        {"autonomy_mode": "auto"},
        {"persistence_enabled": True},
        {"action_execution_enabled": True},
    ],
)
def test_unverified_runtime_is_never_active(registry, change):
    _register(registry, _status(**change))
    observed = collect_runtime_ui_system_status()["consciousness"]
    assert observed["status"] != "active"
    assert observed["metrics"]["available"] is False


def test_actual_timestamp_rejects_stale_tick_despite_claimed_fresh_age(registry):
    _register(registry, _status(last_tick_at=time.time() - 20, last_tick_age_seconds=0))
    observed = collect_runtime_ui_system_status()["consciousness"]
    assert observed["status"] == "degraded"
    assert observed["metrics"]["freshness"] == "stale"


def test_legacy_registered_core_does_not_get_mutating_status_call(registry):
    instance = _register(registry, _status())
    del instance.get_runtime_status
    observed = collect_runtime_ui_system_status()["consciousness"]
    assert observed["status"] == "unknown"
    assert observed["metrics"]["evidence"] == "service_status_unavailable"


def test_no_registry_is_created_for_observatory(monkeypatch):
    monkeypatch.setattr(registry_module, "_service_registry", None)

    def forbidden():
        raise AssertionError("status must not create a registry")

    monkeypatch.setattr(registry_module, "get_service_registry", forbidden)
    assert collect_runtime_ui_system_status()["consciousness"]["status"] == "unknown"
    assert registry_module._service_registry is None

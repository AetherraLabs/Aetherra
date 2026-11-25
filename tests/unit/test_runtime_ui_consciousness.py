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
        {"last_tick_at": 10**500},
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
    assert observed["metrics"]["evidence"] == "observer_runtime"


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


def test_checkpoint_persistence_does_not_fabricate_live_ticks(registry):
    _register(
        registry,
        _status(
            ticks_completed=0,
            persistence_enabled=True,
            legacy_file_persistence_enabled=False,
            continuity={
                "enabled": True,
                "state": "restored",
                "selected_checkpoint_id": "a" * 32,
                "restored_record_id": "row-original",
                "saved_checkpoint_id": None,
                "saved_record_id": None,
                "outstanding": False,
                "last_error_code": None,
            },
        ),
    )
    observed = collect_runtime_ui_system_status()["consciousness"]
    assert observed["status"] != "active"
    assert observed["metrics"]["continuity_state"] == "restored"


def test_live_observer_with_governed_checkpoint_persistence_remains_active(registry):
    _register(
        registry,
        _status(
            persistence_enabled=True,
            legacy_file_persistence_enabled=False,
            continuity={
                "enabled": True,
                "state": "fresh",
                "selected_checkpoint_id": None,
                "restored_record_id": None,
                "saved_checkpoint_id": None,
                "saved_record_id": None,
                "outstanding": False,
                "last_error_code": None,
            },
        ),
    )
    observed = collect_runtime_ui_system_status()["consciousness"]
    assert observed["status"] == "active"
    assert observed["metrics"]["persistence_enabled"] is True


@pytest.mark.parametrize(
    ("state", "acceptance"), [("saving", "pending"), ("saved", "acknowledged")]
)
def test_automatic_periodic_save_keeps_observer_available(registry, state, acceptance):
    _register(
        registry,
        _status(
            persistence_enabled=True,
            legacy_file_persistence_enabled=False,
            continuity={
                "enabled": True,
                "state": state,
                "ownership_state": "last_observed_owned",
                "ownership_checked_at_unix_s": 150,
                "observed_writer_epoch": 2,
                "observed_generation": 1,
                "last_save_trigger": "periodic",
                "last_save_acceptance": acceptance,
                "outstanding": state == "saving",
            },
        ),
    )
    observed = collect_runtime_ui_system_status()["consciousness"]
    assert observed["status"] == "active"
    assert observed["metrics"]["available"] is True
    assert observed["metrics"]["continuity_health"] == "ok"
    assert observed["metrics"]["continuity_ownership_checked_at_unix_s"] == 150
    assert observed["metrics"]["continuity_observed_writer_epoch"] == 2
    assert observed["metrics"]["continuity_last_save_trigger"] == "periodic"
    assert observed["metrics"]["continuity_last_save_acceptance"] == acceptance


@pytest.mark.parametrize(
    ("state", "ownership", "error", "retention_needed"),
    [
        ("blocked", "lost", "writer_fenced", False),
        ("uncertain", "uncertain", "uncertain", False),
        ("retention_blocked", "uncertain", "denied", True),
    ],
)
def test_live_ticks_and_old_receipt_do_not_mask_persistence_fault(
    registry, state, ownership, error, retention_needed
):
    _register(
        registry,
        _status(
            persistence_enabled=True,
            legacy_file_persistence_enabled=False,
            continuity={
                "enabled": True,
                "state": state,
                "last_error_code": error,
                "ownership_state": ownership,
                "ownership_lost_at_unix_s": 300 if ownership == "lost" else None,
                "last_save_acceptance": "acknowledged",
                "saved_checkpoint_id": "b" * 32,
                "saved_record_id": "row-previous",
                "retention_needed": retention_needed,
            },
        ),
    )
    observed = collect_runtime_ui_system_status()["consciousness"]
    assert observed["status"] == "degraded"
    metrics = observed["metrics"]
    assert metrics["available"] is True
    assert metrics["ticks_completed"] == 3
    assert metrics["continuity_health"] == "degraded"
    assert metrics["continuity_state"] == state
    assert metrics["continuity_error_code"] == error
    assert metrics["continuity_ownership_state"] == ownership
    assert metrics["continuity_ownership_lost_at_unix_s"] == (
        300 if ownership == "lost" else None
    )
    assert metrics["continuity_saved_record_id"] == "row-previous"
    assert metrics["continuity_retention_needed"] is retention_needed


@pytest.mark.parametrize(
    ("state", "runtime_state", "outcome", "error", "health"),
    [
        ("restoring", "starting", "not_attempted", None, "pending"),
        ("blocked", "blocked", "blocked", "corrupt", "degraded"),
    ],
)
def test_startup_has_no_live_ticks_and_distinguishes_pending_from_corruption(
    registry, state, runtime_state, outcome, error, health
):
    _register(
        registry,
        _status(
            runtime_state=runtime_state,
            running=False,
            ticks_completed=0,
            persistence_enabled=True,
            continuity={
                "enabled": True,
                "state": state,
                "recovery_method": "exact_inspection",
                "recovery_outcome": outcome,
                "last_error_code": error,
            },
        ),
    )
    metrics = collect_runtime_ui_system_status()["consciousness"]["metrics"]
    assert metrics["available"] is False
    assert metrics["continuity_health"] == health
    assert metrics["continuity_recovery_outcome"] == outcome
    assert metrics["continuity_error_code"] == error


@pytest.mark.parametrize(
    ("start", "gap", "gap_state"),
    [
        (100, None, "clock_inconsistent"),
        (200, 0, "host_wall_clock_estimate"),
        (345800, 345600, "host_wall_clock_estimate"),
    ],
)
def test_restored_clock_provenance_stays_distinct_from_current_session(
    registry, start, gap, gap_state
):
    _register(
        registry,
        _status(
            continuity={
                "enabled": True,
                "state": "restored",
                "recovery_method": "durable_head",
                "recovery_outcome": "restored",
                "session_id": "a" * 32,
                "session_started_at_unix_s": start,
                "session_uptime_seconds": 5,
                "last_verified_observation_at_unix_s": 200,
                "captured_at_unix_s": 201,
                "restored_session_id": "b" * 32,
                "restored_session_started_at_unix_s": 180,
                "restored_observation_uptime_s": 20,
                "restored_capture_uptime_s": 21,
                "restored_save_trigger": "orderly_stop",
                "observation_gap_seconds": gap,
                "observation_gap_state": gap_state,
                "offline_duration_seconds": None,
                "offline_duration_state": "unknown",
            },
        ),
    )
    metrics = collect_runtime_ui_system_status()["consciousness"]["metrics"]
    assert metrics["continuity_session_id"] == "a" * 32
    assert metrics["continuity_session_started_at_unix_s"] == start
    assert metrics["continuity_session_uptime_seconds"] == 5
    assert metrics["continuity_last_verified_observation_at_unix_s"] == 200
    assert metrics["continuity_captured_at_unix_s"] == 201
    assert metrics["continuity_restored_session_id"] == "b" * 32
    assert metrics["continuity_restored_session_started_at_unix_s"] == 180
    assert metrics["continuity_restored_observation_uptime_s"] == 20
    assert metrics["continuity_restored_capture_uptime_s"] == 21
    assert metrics["continuity_restored_save_trigger"] == "orderly_stop"
    assert metrics["continuity_observation_gap_seconds"] == gap
    assert metrics["continuity_observation_gap_state"] == gap_state
    assert metrics["continuity_offline_duration_seconds"] is None
    assert metrics["continuity_offline_duration_state"] == "unknown"
    assert metrics["continuity_previous_save_acceptance"] == "unknown"
    assert metrics["continuity_previous_shutdown_evidence"] == "unknown"


def test_legacy_checkpoint_metadata_stays_unavailable(registry):
    _register(
        registry,
        _status(
            persistence_enabled=True,
            legacy_file_persistence_enabled=False,
            continuity={
                "enabled": True,
                "state": "restored",
                "selected_checkpoint_id": "c" * 32,
                "restored_record_id": "row-legacy",
            },
        ),
    )
    metrics = collect_runtime_ui_system_status()["consciousness"]["metrics"]
    assert metrics["available"] is True
    assert metrics["continuity_restored_record_id"] == "row-legacy"
    assert metrics["continuity_last_verified_observation_at_unix_s"] is None
    assert metrics["continuity_captured_at_unix_s"] is None
    assert metrics["continuity_restored_save_trigger"] is None
    assert metrics["continuity_observation_gap_state"] == "unknown"
    assert metrics["continuity_previous_shutdown_evidence"] == "unknown"


def test_continuity_projection_rejects_malformed_scalars_and_nested_data(registry):
    _register(
        registry,
        _status(
            continuity={
                "enabled": True,
                "state": "saved",
                "start_mode": "resume",
                "stream_id": "x" * 128,
                "observed_writer_epoch": True,
                "observed_generation": 2**100,
                "recovery_method": ["private"],
                "recovery_outcome": "private",
                "previous_shutdown_evidence": "unexpected",
                "last_save_trigger": {"private": "payload"},
                "previous_save_acceptance": "acknowledged",
                "last_save_acceptance": "private",
                "ownership_state": ["private"],
                "ownership_checked_at_unix_s": True,
                "ownership_lost_at_unix_s": 10**500,
                "session_started_at_unix_s": float("nan"),
                "last_verified_observation_at_unix_s": -1,
                "captured_at_unix_s": float("inf"),
                "observation_gap_seconds": "12",
                "observation_gap_state": "host_wall_clock_estimate",
                "offline_duration_seconds": 12,
                "offline_duration_state": "measured",
                "restored_observation_uptime_s": 9,
                "restored_capture_uptime_s": 2,
                "current_attempt": {
                    "operation_id": "d" * 32,
                    "checkpoint_id": False,
                    "token": "private",
                    "payload_digest": "private",
                },
                "payload": "private",
            },
        ),
    )
    metrics = collect_runtime_ui_system_status()["consciousness"]["metrics"]
    for field in (
        "stream_id",
        "observed_writer_epoch",
        "observed_generation",
        "last_save_trigger",
        "ownership_checked_at_unix_s",
        "ownership_lost_at_unix_s",
        "session_started_at_unix_s",
        "last_verified_observation_at_unix_s",
        "captured_at_unix_s",
        "observation_gap_seconds",
        "offline_duration_seconds",
        "restored_observation_uptime_s",
        "restored_capture_uptime_s",
        "current_attempt_checkpoint_id",
    ):
        assert metrics[f"continuity_{field}"] is None
    assert metrics["continuity_health"] == "pending"
    assert metrics["continuity_current_attempt_operation_id"] == "d" * 32
    assert metrics["continuity_observation_gap_state"] == "unknown"
    assert metrics["continuity_offline_duration_state"] == "unknown"
    assert metrics["continuity_previous_shutdown_evidence"] == "unknown"
    assert metrics["continuity_previous_save_acceptance"] == "unknown"
    assert metrics["continuity_last_save_acceptance"] == "unknown"
    assert "private" not in str(metrics)
    assert "continuity_current_attempt" not in metrics

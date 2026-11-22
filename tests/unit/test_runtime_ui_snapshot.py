# Standard library imports
from datetime import datetime, timedelta
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
import aetherra_service_registry as registry_module
from Aetherra.runtime_ui import (
    collect_runtime_ui_events,
    collect_runtime_ui_system_status,
)
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceInfo,
    ServiceStatus,
)


@pytest.fixture
def registry(monkeypatch):
    # Populate registry records directly: registration itself performs governed writes.
    current = AetherraServiceRegistry()
    current._running = True
    monkeypatch.setattr(registry_module, "_service_registry", current)
    return current


def _record(registry, name, instance=None, **overrides):
    values = {"status": ServiceStatus.HEALTHY, "last_heartbeat": datetime.now()}
    values.update(overrides)
    info = ServiceInfo(name=name, instance=instance or object(), **values)
    registry._services[name] = info
    return info


def _engine_status(**overrides):
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


def test_snapshot_does_not_create_registry_or_claim_unobserved_health(monkeypatch):
    monkeypatch.setattr(registry_module, "_service_registry", None)

    status = collect_runtime_ui_system_status()

    assert registry_module._service_registry is None
    for name, subsystem in status.items():
        assert subsystem["health"] is None, name
        assert subsystem["activity"] == 0.0, name
        assert subsystem["metrics"]["activity_measured"] is False, name
        if name != "guardian":
            assert subsystem["status"] == "unknown", name
            assert subsystem["metrics"]["evidence"] == "registry_unavailable", name
    assert status["security"]["metrics"]["authority"] == "enforce"
    assert status["homeostasis"]["metrics"]["authority"] == "observe_verify"


def test_snapshot_does_not_restart_a_stopped_registry(registry):
    registry._running = False
    _record(registry, "memory_system")

    memory = collect_runtime_ui_system_status()["memory"]

    assert registry._running is False
    assert memory["status"] == "unknown"
    assert memory["metrics"]["evidence"] == "registry_unavailable"


def test_missing_service_is_unknown_instead_of_stable(registry):
    status = collect_runtime_ui_system_status()

    assert status["memory"]["status"] == "unknown"
    assert status["memory"]["metrics"]["evidence"] == "service_unregistered"


def test_registry_heartbeat_is_labeled_as_registry_evidence_not_readiness(registry):
    _record(registry, "memory_system", metadata={"self_heartbeat": False})

    memory = collect_runtime_ui_system_status()["memory"]

    assert memory["status"] == "active"
    assert memory["health"] is None
    assert memory["metrics"]["evidence"] == "registry_heartbeat"
    assert memory["metrics"]["self_heartbeat"] is False
    assert memory["metrics"]["readiness_verified"] is False
    assert memory["metrics"]["freshness"] == "fresh"
    assert memory["metrics"]["observed_at"].endswith("Z")


def test_stale_heartbeat_cannot_be_overridden_by_healthy_service_status(registry):
    def must_not_read_stale_status():
        raise AssertionError("stale service should not be queried")

    _record(
        registry,
        "kernel_loop",
        SimpleNamespace(get_status=must_not_read_stale_status),
        last_heartbeat=datetime.now() - timedelta(hours=1),
    )

    kernel = collect_runtime_ui_system_status()["kernel"]

    assert kernel["status"] == "unknown"
    assert kernel["metrics"]["freshness"] == "stale"
    assert kernel["metrics"]["evidence"] == "heartbeat_stale"


@pytest.mark.parametrize(
    ("service_status", "expected"),
    [
        (ServiceStatus.DEGRADED, "degraded"),
        (ServiceStatus.FAILED, "offline"),
        (ServiceStatus.STOPPING, "offline"),
        (ServiceStatus.STARTING, "unknown"),
    ],
)
def test_registry_failure_and_lifecycle_state_are_not_reported_healthy(
    registry,
    service_status,
    expected,
):
    _record(registry, "memory_system", status=service_status)

    memory = collect_runtime_ui_system_status()["memory"]

    assert memory["status"] == expected
    assert memory["metrics"]["registry_status"] == service_status.value
    assert memory["health"] is None


@pytest.mark.parametrize(
    ("component_status", "readiness", "status"),
    [
        ("healthy", "ready", "active"),
        ("degraded", "degraded", "degraded"),
        ("unavailable", "blocked", "degraded"),
    ],
)
def test_engine_uses_actual_readiness_instead_of_registration_health(
    registry,
    component_status,
    readiness,
    status,
):
    class Engine:
        async def get_system_status(self):
            return _engine_status(
                memory_system={
                    "status": component_status,
                    "path": "private-memory.db",
                }
            )

    _record(registry, "aetherra_engine", Engine())

    engine = collect_runtime_ui_system_status()["engine"]

    assert engine["status"] == status
    assert engine["metrics"]["readiness"] == readiness
    assert engine["metrics"]["safe_for_requests"] is (readiness == "ready")
    assert engine["metrics"]["evidence"] == "service_readiness"
    assert "private-memory.db" not in str(engine)
    assert engine["health"] is None


def test_status_reader_failure_is_unknown_and_does_not_expose_exception(registry):
    def failed_status():
        raise RuntimeError("private-token-and-path")

    _record(registry, "kernel_loop", SimpleNamespace(get_status=failed_status))

    kernel = collect_runtime_ui_system_status()["kernel"]

    assert kernel["status"] == "unknown"
    assert kernel["metrics"]["evidence"] == "service_status_unavailable"
    assert "private-token-and-path" not in str(kernel)


def test_homeostasis_observation_uses_running_state(registry):
    _record(
        registry,
        "homeostasis_system",
        SimpleNamespace(
            get_orchestrator_status=lambda: {"running": False, "initialized": True},
        ),
    )

    homeostasis = collect_runtime_ui_system_status()["homeostasis"]

    assert homeostasis["status"] == "offline"
    assert homeostasis["metrics"]["evidence"] == "service_status"
    assert homeostasis["metrics"]["controller_mode"] is None
    assert homeostasis["metrics"]["actuator_actions_attempted"] is None


@pytest.mark.parametrize(
    ("requested", "mode", "attempted", "executed", "blocked", "restarts", "recoveries"),
    [
        (True, "observe_only", 0, 0, 0, 0, 0),
        (False, "active", 7, 3, 4, 2, 1),
    ],
)
def test_homeostasis_snapshot_exposes_registered_mode_and_actuator_counters(
    registry, requested, mode, attempted, executed, blocked, restarts, recoveries
):
    _record(
        registry,
        "homeostasis_system",
        SimpleNamespace(
            get_orchestrator_status=lambda: {
                "running": True,
                "initialized": True,
                "observe_only_requested": requested,
                "controller": {"mode": mode, "stats": {"private": "secret"}},
                "actuators": {
                    "actions_attempted": attempted,
                    "actions_executed": executed,
                    "actions_blocked": blocked,
                    "last_action_time": "private-action-detail",
                },
                "restart_count": restarts,
                "error_recovery_count": recoveries,
            }
        ),
    )

    homeostasis = collect_runtime_ui_system_status()["homeostasis"]
    metrics = homeostasis["metrics"]

    assert metrics["service_name"] == "homeostasis_system"
    assert metrics["observe_only_requested"] is requested
    assert metrics["controller_mode"] == mode
    assert metrics["actuator_actions_attempted"] == attempted
    assert metrics["actuator_actions_executed"] == executed
    assert metrics["actuator_actions_blocked"] == blocked
    assert metrics["restart_count"] == restarts
    assert metrics["error_recovery_count"] == recoveries
    assert "private" not in str(homeostasis)
    assert all(
        value is None or isinstance(value, (str, int, float, bool))
        for value in metrics.values()
    )


def test_homeostasis_snapshot_rejects_malformed_mode_and_counters(registry):
    _record(
        registry,
        "homeostasis_system",
        SimpleNamespace(
            get_orchestrator_status=lambda: {
                "running": True,
                "initialized": True,
                "observe_only_requested": "private-input",
                "controller": {"mode": "private-input"},
                "actuators": {
                    "actions_attempted": "private-input",
                    "actions_executed": -1,
                    "actions_blocked": True,
                },
                "restart_count": {"private": "input"},
                "error_recovery_count": 1.5,
            }
        ),
    )

    metrics = collect_runtime_ui_system_status()["homeostasis"]["metrics"]

    for name in (
        "observe_only_requested",
        "controller_mode",
        "actuator_actions_attempted",
        "actuator_actions_executed",
        "actuator_actions_blocked",
        "restart_count",
        "error_recovery_count",
    ):
        assert metrics[name] is None
    assert "private" not in str(metrics)


def test_runtime_ui_snapshot_events_describe_observations_not_lifecycle_actions():
    events = collect_runtime_ui_events()

    assert [event["source"] for event in events] == [
        "runtime_ui",
        "guardian",
        "homeostasis",
    ]
    assert events[0]["details"]["authority"] == "observe_only"
    assert all(event["details"]["observation_only"] is True for event in events)
    assert all(event["occurred_at"].endswith("Z") for event in events)
    assert events[1]["event_type"] == "guardian_status_observed"
    assert events[2]["event_type"] == "homeostasis_status_observed"


@pytest.mark.parametrize(
    "heartbeat", [None, "not-a-timestamp", datetime.now() + timedelta(hours=1)]
)
def test_invalid_heartbeat_cannot_claim_current_service_health(registry, heartbeat):
    _record(registry, "memory_system", last_heartbeat=heartbeat)

    memory = collect_runtime_ui_system_status()["memory"]

    assert memory["status"] == "unknown"
    assert memory["metrics"]["freshness"] == "unknown"


def test_stub_registration_is_not_a_live_service_observation(registry):
    _record(registry, "memory_system", metadata={"type": "mock", "stub": True})

    memory = collect_runtime_ui_system_status()["memory"]

    assert memory["status"] == "unknown"
    assert memory["metrics"]["evidence"] == "placeholder_service"


@pytest.mark.parametrize(
    ("paused", "expected"), [(False, "active"), (True, "degraded")]
)
def test_kernel_readiness_comes_from_registered_live_getter(registry, paused, expected):
    _record(
        registry,
        "kernel_loop",
        SimpleNamespace(
            get_status=lambda: {
                "running": True,
                "paused": paused,
                "queue_sizes": {"normal": 0},
                "queue_limits": {"normal": 10},
                "metrics": {},
                "backpressure_guard_pass": True,
                "night_schedule_guard_pass": True,
                "plugin_cb_open": False,
                "dlq_count": 0,
                "hmr": {},
                "inflight": {},
            }
        ),
    )

    kernel = collect_runtime_ui_system_status()["kernel"]

    assert kernel["status"] == expected
    assert kernel["metrics"]["safe_to_schedule"] is (not paused)
    assert kernel["metrics"]["evidence"] == "service_readiness"
    assert all(
        value is None or isinstance(value, (str, int, float, bool))
        for value in kernel["metrics"].values()
    )


def test_blocked_status_getter_returns_unknown_within_read_budget(
    registry, monkeypatch
):
    # Standard library imports
    from threading import Event
    from time import monotonic

    # Aetherra imports
    from Aetherra.runtime_ui import snapshot

    release = Event()
    exited = Event()

    def blocked_status():
        try:
            release.wait(2)
            return {"running": True}
        finally:
            exited.set()

    _record(registry, "kernel_loop", SimpleNamespace(get_status=blocked_status))
    monkeypatch.setattr(snapshot, "_STATUS_TIMEOUT_SECONDS", 0.01)
    started = monotonic()
    try:
        kernel = collect_runtime_ui_system_status()["kernel"]
        assert monotonic() - started < 1.0
        assert kernel["status"] == "unknown"
        assert kernel["metrics"]["evidence"] == "service_status_unavailable"
    finally:
        release.set()
        assert exited.wait(1)


def test_guardian_audit_read_is_bounded(monkeypatch):
    # Standard library imports
    from threading import Event
    from time import monotonic

    # Aetherra imports
    import Aetherra.guardian as guardian
    from Aetherra.runtime_ui import snapshot

    release = Event()
    exited = Event()

    def blocked_audit():
        try:
            release.wait(1.5)
            return True
        finally:
            exited.set()

    monkeypatch.setattr(registry_module, "_service_registry", None)
    monkeypatch.setattr(guardian, "guardian_audit_integrity_ok", blocked_audit)
    monkeypatch.setattr(snapshot, "_STATUS_TIMEOUT_SECONDS", 0.01)
    started = monotonic()
    try:
        result = collect_runtime_ui_system_status()["guardian"]
        assert monotonic() - started < 1.0
        assert result["status"] == "unknown"
    finally:
        release.set()
        assert exited.wait(1)

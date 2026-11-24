"""Only actually observed provider fields may feed the proposal bridge."""

# Standard library imports
import math
import time
from datetime import datetime
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
import Aetherra.homeostasis.stability_metrics as metrics_module
from Aetherra.homeostasis.stability_metrics import MetricSnapshot, StabilityMetrics
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceInfo,
    ServiceStatus,
)


def _observed(snapshot):
    return set(snapshot.raw_data.get("measured_metrics", []))


def _registry_with(*names):
    registry = AetherraServiceRegistry()
    registry._running = True
    for name in names:
        registry._services[name] = ServiceInfo(
            name=name,
            instance=object(),
            status=ServiceStatus.HEALTHY,
            last_heartbeat=datetime.now(),
        )
    return registry


def _use_registry(monkeypatch, metrics, registry):
    async def existing():
        return registry

    monkeypatch.setattr(metrics, "_get_service_registry", existing)


def _unavailable_sources(monkeypatch, metrics):
    _use_registry(monkeypatch, metrics, None)
    monkeypatch.setattr(metrics_module, "get_registry_status", lambda: None)
    monkeypatch.setattr(metrics_module, "get_kernel_status", lambda: None)
    monkeypatch.setattr(metrics_module, "get_hmr_audit_counters", lambda: {})
    monkeypatch.setattr(
        metrics_module, "get_memory_quantum_status", lambda **kwargs: {"enabled": False}
    )
    monkeypatch.setattr(metrics_module, "get_memory_audit", lambda **kwargs: {})


@pytest.mark.asyncio
async def test_registry_metrics_use_the_actual_running_and_service_count_contract(
    monkeypatch,
):
    metrics = StabilityMetrics()
    registry = _registry_with("aetherra_hub", "kernel_loop")
    monkeypatch.setattr(
        metrics_module, "get_registry_status", registry.get_registry_status
    )
    snapshot = MetricSnapshot(timestamp=time.time())

    await metrics._collect_service_registry_metrics(snapshot)

    assert snapshot.registry_health == 1.0
    assert snapshot.service_count == 2
    assert {"registry_health", "service_count"} <= _observed(snapshot)


@pytest.mark.asyncio
async def test_lowercase_healthy_services_do_not_become_false_degradation(monkeypatch):
    metrics = StabilityMetrics()
    registry = _registry_with("aetherra_hub", "plugin_example", "lyrixa_gui")
    _use_registry(monkeypatch, metrics, registry)
    snapshot = MetricSnapshot(timestamp=time.time())

    await metrics._collect_plugin_metrics(snapshot)
    await metrics._collect_hub_metrics(snapshot)
    await metrics._collect_gui_metrics(snapshot)

    assert snapshot.plugin_load_success == 100.0
    assert snapshot.hub_connection == 1.0
    assert {"plugin_load_success", "hub_connection"} <= _observed(snapshot)
    assert "hub_websocket_status" not in _observed(snapshot)
    assert "gui_heartbeat" not in _observed(snapshot)
    assert "gui_responsiveness" not in _observed(snapshot)


@pytest.mark.asyncio
async def test_absent_sources_leave_dataclass_defaults_unmeasured(monkeypatch):
    metrics = StabilityMetrics()
    _unavailable_sources(monkeypatch, metrics)

    snapshot = await metrics.collect_snapshot()

    assert "measured_metrics" in snapshot.raw_data
    assert _observed(snapshot) == set()
    # Keep legacy numeric shape; absence is expressed by the measurement metadata.
    assert isinstance(snapshot.memory_rtt, (int, float))
    assert isinstance(snapshot.task_throughput, (int, float))


@pytest.mark.asyncio
async def test_memory_observed_zero_is_retained_and_status_reads_never_start_fallback(
    monkeypatch,
):
    metrics = StabilityMetrics()
    _unavailable_sources(monkeypatch, metrics)
    calls = []

    def quantum(*, allow_fallback=True):
        calls.append(("quantum", allow_fallback))
        return {
            "enabled": True,
            "quantum_data": {"avg_response_time": 0.0, "timeout_count": 0},
        }

    def audit(*, allow_fallback=True):
        calls.append(("audit", allow_fallback))
        return {}

    monkeypatch.setattr(metrics_module, "get_memory_quantum_status", quantum)
    monkeypatch.setattr(metrics_module, "get_memory_audit", audit)
    snapshot = MetricSnapshot(timestamp=time.time())
    await metrics._collect_memory_metrics(snapshot)

    assert calls == [("quantum", False), ("audit", False)]
    assert snapshot.memory_rtt == 0.0
    assert snapshot.memory_timeouts == 0
    assert {"memory_rtt", "memory_timeouts"} <= _observed(snapshot)


@pytest.mark.asyncio
async def test_sparse_memory_status_does_not_invent_rtt_or_timeouts(monkeypatch):
    metrics = StabilityMetrics()
    _unavailable_sources(monkeypatch, metrics)
    monkeypatch.setattr(
        metrics_module,
        "get_memory_quantum_status",
        lambda **kwargs: {
            "enabled": True,
            "quantum_data": {},
        },
    )
    snapshot = MetricSnapshot(timestamp=time.time())
    await metrics._collect_memory_metrics(snapshot)

    assert "memory_rtt" not in _observed(snapshot)
    assert "memory_timeouts" not in _observed(snapshot)


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, True, "12"])
async def test_nonfinite_and_non_numeric_provider_values_are_not_measurements(
    monkeypatch, value
):
    metrics = StabilityMetrics()
    _unavailable_sources(monkeypatch, metrics)
    monkeypatch.setattr(
        metrics_module,
        "get_memory_quantum_status",
        lambda **kwargs: {
            "enabled": True,
            "quantum_data": {"avg_response_time": value, "timeout_count": value},
        },
    )
    monkeypatch.setattr(
        metrics_module,
        "get_hmr_audit_counters",
        lambda: {
            "tasks_per_second": value,
            "avg_task_latency_ms": value,
            "queue_depth": value,
        },
    )
    snapshot = MetricSnapshot(timestamp=time.time())
    await metrics._collect_memory_metrics(snapshot)
    await metrics._collect_kernel_metrics(snapshot)

    assert not {
        "memory_rtt",
        "memory_timeouts",
        "task_throughput",
        "task_latency",
        "queue_depth",
    } & _observed(snapshot)


@pytest.mark.asyncio
async def test_explicit_zero_kernel_samples_are_distinct_from_absent_counter_keys(
    monkeypatch,
):
    metrics = StabilityMetrics()
    _unavailable_sources(monkeypatch, metrics)
    monkeypatch.setattr(
        metrics_module,
        "get_hmr_audit_counters",
        lambda: {
            "tasks_per_second": 0.0,
            "avg_task_latency_ms": 0.0,
            "queue_depth": 0,
        },
    )
    snapshot = MetricSnapshot(timestamp=time.time())
    await metrics._collect_kernel_metrics(snapshot)
    assert {"task_throughput", "task_latency", "queue_depth"} <= _observed(snapshot)
    assert (
        snapshot.task_throughput == snapshot.task_latency == snapshot.queue_depth == 0
    )

    monkeypatch.setattr(
        metrics_module, "get_hmr_audit_counters", lambda: {"audit_count": 2}
    )
    sparse = MetricSnapshot(timestamp=time.time())
    await metrics._collect_kernel_metrics(sparse)
    assert not {"task_throughput", "task_latency", "queue_depth"} & _observed(sparse)


@pytest.mark.asyncio
async def test_cognitive_fields_require_actual_finite_provider_values(monkeypatch):
    metrics = StabilityMetrics()
    registry = _registry_with("aetherra_engine")

    async def learning():
        return {"learning_rate": 0.0, "confidence": math.nan, "private": "not-a-metric"}

    registry._services["aetherra_engine"].instance = SimpleNamespace(
        get_learning_metrics=learning
    )
    _use_registry(monkeypatch, metrics, registry)
    snapshot = MetricSnapshot(timestamp=time.time())
    await metrics._collect_cognitive_metrics(snapshot)

    assert snapshot.learning_rate == 0.0
    assert _observed(snapshot) == {"learning_rate"}

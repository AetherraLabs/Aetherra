"""Read-only Homeostasis observation reports.

Phase 1 Homeostasis answers "what is happening?" without recommending or
executing corrective actions. The report intentionally summarizes metric
pressure and runtime state without mutating controller, actuator, or Guardian
state.
"""

from __future__ import annotations

import time
from dataclasses import asdict, is_dataclass
from typing import Any

_OBSERVED_METRICS = (
    "task_throughput",
    "task_latency",
    "queue_depth",
    "memory_rtt",
    "memory_timeouts",
    "exception_suppression",
    "plugin_load_success",
    "plugin_timeout_rate",
    "hub_connection",
    "hub_websocket_status",
    "gui_heartbeat",
    "gui_responsiveness",
    "learning_rate",
    "learning_cycle_time",
    "confidence_level",
    "uncertainty_level",
    "model_fallback_rate",
    "reflection_stability",
    "registry_health",
    "service_count",
    "kernel_loop_health",
)


def build_observation_report(
    *,
    metrics_snapshot: Any | None = None,
    health_summary: dict[str, Any] | None = None,
    controller_status: dict[str, Any] | None = None,
    control_loops: dict[str, Any] | None = None,
    actuator_status: dict[str, Any] | None = None,
    supervisor_status: dict[str, Any] | None = None,
    setpoints: dict[str, Any] | None = None,
    collected_at: float | None = None,
) -> dict[str, Any]:
    """Build a read-only Homeostasis awareness report."""

    snapshot = _as_mapping(metrics_snapshot)
    metric_values = _metric_values(snapshot)
    pressure = _pressure_report(metric_values, setpoints or {})
    health = dict(health_summary or {})
    controller = dict(controller_status or {})
    supervisor = dict(supervisor_status or {})
    actuators = dict(actuator_status or {})

    risk = _risk_report(
        health=health,
        pressure=pressure,
        controller=controller,
        supervisor=supervisor,
    )

    return {
        "phase": "observation",
        "collected_at": collected_at or time.time(),
        "actions_enabled": False,
        "state": {
            "homeostasis_status": health.get("status") or "unknown",
            "controller_mode": controller.get("mode") or "unknown",
            "controller_running": bool(controller.get("running", False)),
            "emergency_stop": bool(controller.get("emergency_stop", False)),
            "pending_actions": int(controller.get("pending_actions") or 0),
            "confirmation_pending": int(controller.get("confirmation_pending") or 0),
            "supervisor_runlevel": supervisor.get("runlevel")
            or supervisor.get("current_runlevel")
            or "unknown",
            "actuator_history_size": int(actuators.get("actions_executed") or 0),
        },
        "metrics": {
            "values": metric_values,
            "sample_timestamp": snapshot.get("timestamp"),
            "sample_age_seconds": _sample_age(snapshot.get("timestamp"), collected_at),
        },
        "health": health,
        "pressure": pressure,
        "risk": risk,
        "control_loops": _summarize_control_loops(control_loops or {}),
    }


def _as_mapping(value: Any | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _metric_values(snapshot: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    for name in _OBSERVED_METRICS:
        if name not in snapshot:
            continue
        number = _to_float(snapshot.get(name))
        if number is not None:
            values[name] = number
    return values


def _pressure_report(
    values: dict[str, float],
    setpoints: dict[str, Any],
) -> dict[str, Any]:
    metrics: dict[str, dict[str, Any]] = {}
    counts = {"nominal": 0, "elevated": 0, "high": 0, "critical": 0}

    for name, value in values.items():
        config = _find_metric_config(name, setpoints)
        metric_pressure = _metric_pressure(name, value, config)
        metrics[name] = metric_pressure
        counts[metric_pressure["level"]] += 1

    highest = "nominal"
    for level in ("critical", "high", "elevated"):
        if counts[level]:
            highest = level
            break

    return {
        "level": highest,
        "counts": counts,
        "metrics": metrics,
    }


def _metric_pressure(
    name: str,
    value: float,
    config: dict[str, Any],
) -> dict[str, Any]:
    target = _to_float(config.get("target"))
    min_acceptable = _to_float(config.get("min_acceptable"))
    max_acceptable = _to_float(config.get("max_acceptable"))
    critical_threshold = _to_float(config.get("critical_threshold"))

    direction = "within_bounds"
    level = "nominal"

    if critical_threshold is not None and _breaches_critical(
        value,
        target,
        critical_threshold,
    ):
        level = "critical"
        direction = "below_critical" if _is_lower_better(target, critical_threshold) else "above_critical"
    elif min_acceptable is not None and value < min_acceptable:
        level = "high"
        direction = "below_minimum"
    elif max_acceptable is not None and value > max_acceptable:
        level = "high"
        direction = "above_maximum"
    elif target is not None and _outside_target_band(value, target, config):
        level = "elevated"
        direction = "above_target" if value > target else "below_target"

    return {
        "level": level,
        "value": value,
        "target": target,
        "direction": direction,
    }


def _risk_report(
    *,
    health: dict[str, Any],
    pressure: dict[str, Any],
    controller: dict[str, Any],
    supervisor: dict[str, Any],
) -> dict[str, Any]:
    score = 0
    factors: list[str] = []
    pressure_counts = pressure.get("counts") or {}

    critical_count = int(pressure_counts.get("critical") or 0)
    high_count = int(pressure_counts.get("high") or 0)
    elevated_count = int(pressure_counts.get("elevated") or 0)
    score += critical_count * 35 + high_count * 20 + elevated_count * 8
    if critical_count:
        factors.append("critical_metric_pressure")
    if high_count:
        factors.append("high_metric_pressure")
    if elevated_count:
        factors.append("elevated_metric_pressure")

    health_status = str(health.get("status") or "").lower()
    if health_status in {"critical", "failed"}:
        score += 35
        factors.append("critical_health_status")
    elif health_status in {"unhealthy", "degraded"}:
        score += 20
        factors.append("degraded_health_status")

    if controller.get("emergency_stop"):
        score += 30
        factors.append("emergency_stop_active")
    if int(controller.get("pending_actions") or 0) > 0:
        score += 8
        factors.append("pending_homeostasis_actions")

    runlevel = str(
        supervisor.get("runlevel") or supervisor.get("current_runlevel") or ""
    ).lower()
    if runlevel in {"failed", "offline"}:
        score += 35
        factors.append("failed_supervisor_runlevel")
    elif runlevel in {"degraded", "warning"}:
        score += 15
        factors.append("degraded_supervisor_runlevel")

    bounded_score = max(0, min(score, 100))
    if bounded_score >= 80:
        level = "critical"
    elif bounded_score >= 50:
        level = "high"
    elif bounded_score >= 20:
        level = "elevated"
    else:
        level = "nominal"

    return {
        "level": level,
        "score": bounded_score,
        "factors": factors,
    }


def _summarize_control_loops(control_loops: dict[str, Any]) -> dict[str, Any]:
    summarized: dict[str, Any] = {}
    for name, raw_loop in control_loops.items():
        loop = _as_mapping(raw_loop)
        summarized[str(name)] = {
            "metric": loop.get("metric"),
            "type": loop.get("type"),
            "enabled": bool(loop.get("enabled", False)),
            "current_value": _to_float(loop.get("current_value")),
            "setpoint": _to_float(loop.get("setpoint")),
            "output": _to_float(loop.get("output")),
        }
    return summarized


def _find_metric_config(name: str, setpoints: dict[str, Any]) -> dict[str, Any]:
    for category in ("core_metrics", "cognitive_metrics", "service_metrics"):
        category_config = setpoints.get(category)
        if not isinstance(category_config, dict):
            continue
        metric_config = category_config.get(name)
        if isinstance(metric_config, dict):
            return metric_config
    return {}


def _outside_target_band(value: float, target: float, config: dict[str, Any]) -> bool:
    band = _to_float(config.get("control_band"))
    if band is None:
        return False
    return abs(value - target) > abs(band)


def _breaches_critical(
    value: float,
    target: float | None,
    threshold: float,
) -> bool:
    if target is not None and threshold < target:
        return value <= threshold
    return value >= threshold


def _is_lower_better(target: float | None, threshold: float) -> bool:
    return target is not None and threshold < target


def _sample_age(timestamp: Any, collected_at: float | None) -> float | None:
    ts = _to_float(timestamp)
    if ts is None:
        return None
    return max(0.0, (collected_at or time.time()) - ts)


def _to_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None

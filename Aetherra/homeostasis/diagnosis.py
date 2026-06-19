"""Read-only Homeostasis diagnosis reports.

Phase 2 Homeostasis answers "why is it happening?" using bounded, explainable
cause categories. It does not recommend or execute corrective actions.
"""

from __future__ import annotations

from typing import Any

_CATEGORY_METRICS = {
    "memory_pressure": ("memory_rtt", "memory_timeouts"),
    "agent_or_kernel_overload": ("task_latency", "queue_depth", "task_throughput"),
    "service_degradation": (
        "plugin_load_success",
        "plugin_timeout_rate",
        "hub_connection",
        "hub_websocket_status",
        "registry_health",
        "service_count",
        "kernel_loop_health",
    ),
    "cognitive_instability": (
        "confidence_level",
        "uncertainty_level",
        "model_fallback_rate",
        "reflection_stability",
        "learning_cycle_time",
    ),
    "interface_degradation": ("gui_heartbeat", "gui_responsiveness"),
}


def build_diagnosis_report(observation: dict[str, Any]) -> dict[str, Any]:
    """Build a causal diagnosis from a Homeostasis observation report."""

    pressure_metrics = (
        ((observation.get("pressure") or {}).get("metrics") or {})
        if isinstance(observation, dict)
        else {}
    )
    causes = [
        cause
        for cause in (
            _diagnose_metric_category(category, metric_names, pressure_metrics)
            for category, metric_names in _CATEGORY_METRICS.items()
        )
        if cause is not None
    ]
    causes.extend(_diagnose_state_causes(observation))
    causes.sort(key=lambda cause: _severity_rank(cause["severity"]), reverse=True)

    return {
        "phase": "diagnosis",
        "actions_enabled": False,
        "source_phase": observation.get("phase") if isinstance(observation, dict) else None,
        "summary": _summary(causes),
        "causes": causes,
    }


def _diagnose_metric_category(
    category: str,
    metric_names: tuple[str, ...],
    pressure_metrics: dict[str, Any],
) -> dict[str, Any] | None:
    contributing = []
    for metric_name in metric_names:
        metric = pressure_metrics.get(metric_name)
        if not isinstance(metric, dict):
            continue
        level = str(metric.get("level") or "nominal")
        if level == "nominal":
            continue
        contributing.append(
            {
                "metric": metric_name,
                "level": level,
                "direction": metric.get("direction"),
                "value": metric.get("value"),
                "target": metric.get("target"),
            }
        )

    if not contributing:
        return None

    severity = max(
        (str(item["level"]) for item in contributing),
        key=_severity_rank,
    )
    return {
        "category": category,
        "severity": severity,
        "confidence": _confidence(contributing),
        "evidence": contributing,
    }


def _diagnose_state_causes(observation: dict[str, Any]) -> list[dict[str, Any]]:
    state = observation.get("state") or {}
    risk = observation.get("risk") or {}
    causes: list[dict[str, Any]] = []

    if state.get("emergency_stop"):
        causes.append(
            {
                "category": "emergency_state",
                "severity": "critical",
                "confidence": 1.0,
                "evidence": [{"state": "emergency_stop", "value": True}],
            }
        )

    pending_actions = _to_int(state.get("pending_actions"))
    if pending_actions > 0:
        causes.append(
            {
                "category": "controller_backlog",
                "severity": "elevated" if pending_actions < 5 else "high",
                "confidence": 0.8,
                "evidence": [{"state": "pending_actions", "value": pending_actions}],
            }
        )

    factors = risk.get("factors") if isinstance(risk, dict) else None
    if isinstance(factors, list) and "guardian_containment_active" in factors:
        causes.append(
            {
                "category": "guardian_containment",
                "severity": "high",
                "confidence": 0.9,
                "evidence": [{"risk_factor": "guardian_containment_active"}],
            }
        )

    return causes


def _summary(causes: list[dict[str, Any]]) -> dict[str, Any]:
    if not causes:
        return {
            "status": "no_clear_cause",
            "primary_cause": None,
            "cause_count": 0,
            "highest_severity": "nominal",
        }
    primary = causes[0]
    return {
        "status": "causes_identified",
        "primary_cause": primary["category"],
        "cause_count": len(causes),
        "highest_severity": primary["severity"],
    }


def _confidence(contributing: list[dict[str, Any]]) -> float:
    if not contributing:
        return 0.0
    score = 0.5 + min(len(contributing), 4) * 0.1
    if any(item.get("level") == "critical" for item in contributing):
        score += 0.1
    return min(score, 0.95)


def _severity_rank(level: str) -> int:
    return {
        "nominal": 0,
        "elevated": 1,
        "high": 2,
        "critical": 3,
    }.get(str(level), 0)


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

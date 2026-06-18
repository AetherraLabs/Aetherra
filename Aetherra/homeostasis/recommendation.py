"""Read-only Homeostasis recommendation reports.

Phase 3 Homeostasis answers "what should be done?" by suggesting bounded,
reviewable actions. It does not execute actions; controlled execution remains
behind Guardian, Security, and actuator enforcement.
"""

from __future__ import annotations

from typing import Any

_RECOMMENDATION_RULES = {
    "memory_pressure": {
        "action_type": "optimize_memory_cache",
        "target_service": "memory_system",
        "parameters": {"cache_size_multiplier": 1.5},
        "capabilities": ("homeostasis:actuate",),
        "expected_impact": "reduce memory latency and timeout pressure",
    },
    "agent_or_kernel_overload": {
        "action_type": "increase_task_workers",
        "target_service": "kernel_system",
        "parameters": {"worker_count_delta": 1},
        "capabilities": ("homeostasis:actuate",),
        "expected_impact": "reduce task latency or queue backlog",
    },
    "service_degradation": {
        "action_type": "inspect_service_health",
        "target_service": "service_registry",
        "capabilities": ("homeostasis:control",),
        "expected_impact": "identify degraded services before restart or isolation",
    },
    "cognitive_instability": {
        "action_type": "adjust_learning_rate",
        "target_service": "cognitive_system",
        "parameters": {"new_learning_rate": 0.01},
        "capabilities": ("homeostasis:actuate",),
        "expected_impact": "stabilize learning or confidence drift",
    },
    "interface_degradation": {
        "action_type": "inspect_interface_health",
        "target_service": "lyrixa_interface",
        "capabilities": ("homeostasis:control",),
        "expected_impact": "confirm UI heartbeat and responsiveness degradation",
    },
    "controller_backlog": {
        "action_type": "review_pending_actions",
        "target_service": "homeostasis_controller",
        "capabilities": ("homeostasis:control",),
        "expected_impact": "reduce stale or unsafe queued control pressure",
    },
    "emergency_state": {
        "action_type": "manual_emergency_review",
        "target_service": "homeostasis",
        "capabilities": ("homeostasis:emergency",),
        "expected_impact": "preserve halt state until human review completes",
    },
    "guardian_containment": {
        "action_type": "review_guardian_containment",
        "target_service": "guardian",
        "capabilities": ("homeostasis:control",),
        "expected_impact": "understand active containment before any correction",
    },
}


def build_recommendation_report(
    observation: dict[str, Any],
    diagnosis: dict[str, Any],
) -> dict[str, Any]:
    """Build non-executing recommendations from diagnosis causes."""

    causes = diagnosis.get("causes") if isinstance(diagnosis, dict) else []
    recommendations = []
    for cause in causes if isinstance(causes, list) else []:
        if not isinstance(cause, dict):
            continue
        recommendation = _recommendation_for_cause(cause)
        if recommendation is not None:
            recommendations.append(recommendation)

    recommendations = _dedupe_recommendations(recommendations)
    recommendations.sort(key=lambda item: item["priority"], reverse=True)

    return {
        "phase": "recommendation",
        "actions_enabled": False,
        "source_phase": diagnosis.get("phase") if isinstance(diagnosis, dict) else None,
        "summary": {
            "status": "recommendations_available"
            if recommendations
            else "no_recommendations",
            "recommendation_count": len(recommendations),
            "highest_priority": recommendations[0]["priority"] if recommendations else None,
            "requires_guardian_before_execution": bool(recommendations),
        },
        "recommendations": recommendations,
        "execution": {
            "performed": False,
            "reason": "recommendation_phase_is_read_only",
        },
        "risk_context": observation.get("risk") if isinstance(observation, dict) else {},
    }


def _recommendation_for_cause(cause: dict[str, Any]) -> dict[str, Any] | None:
    category = str(cause.get("category") or "")
    rule = _RECOMMENDATION_RULES.get(category)
    if rule is None:
        return None

    severity = str(cause.get("severity") or "elevated")
    priority = {
        "critical": 90,
        "high": 70,
        "elevated": 50,
        "nominal": 10,
    }.get(severity, 30)

    return {
        "cause_category": category,
        "severity": severity,
        "priority": priority,
        "action_type": rule["action_type"],
        "target_service": rule["target_service"],
        "parameters": dict(rule.get("parameters") or {}),
        "expected_impact": rule["expected_impact"],
        "requires_guardian": True,
        "required_capabilities": list(rule["capabilities"]),
        "evidence": cause.get("evidence") or [],
    }


def _dedupe_recommendations(
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    deduped: dict[tuple[str, str], dict[str, Any]] = {}
    for recommendation in recommendations:
        key = (
            str(recommendation.get("action_type")),
            str(recommendation.get("target_service")),
        )
        current = deduped.get(key)
        if current is None or recommendation["priority"] > current["priority"]:
            deduped[key] = recommendation
    return list(deduped.values())

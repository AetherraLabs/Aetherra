"""Read-only readiness contract for the Aetherra AI engine."""

from __future__ import annotations

from contextlib import suppress
from collections.abc import Mapping
from typing import Any

AI_READINESS_CONTRACT_VERSION = "1.0"

_REQUIRED_STATUS_KEYS = frozenset(
    {
        "engine_status",
        "memory_system",
        "improvement_system",
        "agent_orchestrator",
        "health_monitoring",
        "session_metrics",
    }
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _component_state(value: Any) -> str:
    data = _mapping(value)
    status = str(data.get("status") or data.get("health") or "").lower()
    if status in {"unavailable", "failed", "error", "critical"}:
        return "unavailable"
    if status in {"degraded", "warning"}:
        return "degraded"
    if not data:
        return "unknown"
    return "available"


def assess_ai_readiness(status: Mapping[str, Any] | None) -> dict[str, Any]:
    """Assess whether the AI engine foundation is safe enough for clients."""

    status_map = _mapping(status)
    reasons: list[str] = []
    missing_keys = sorted(_REQUIRED_STATUS_KEYS.difference(status_map))

    if not status_map:
        reasons.append("engine_status_unavailable")
    elif status_map.get("status") == "not_initialized":
        reasons.append("engine_not_initialized")
    elif missing_keys:
        reasons.append("status_contract_incomplete")

    engine_active = status_map.get("engine_status") == "active"
    if status_map and not engine_active:
        reasons.append("engine_not_active")

    components = {
        "memory_system": _component_state(status_map.get("memory_system")),
        "improvement_system": _component_state(status_map.get("improvement_system")),
        "agent_orchestrator": _component_state(status_map.get("agent_orchestrator")),
        "health_monitoring": _component_state(status_map.get("health_monitoring")),
    }
    unavailable_components = sorted(
        name for name, state in components.items() if state == "unavailable"
    )
    degraded_components = sorted(
        name for name, state in components.items() if state in {"degraded", "unknown"}
    )
    for name in unavailable_components:
        reasons.append(f"component_unavailable:{name}")
    for name in degraded_components:
        reasons.append(f"component_degraded:{name}")

    session_metrics = _mapping(status_map.get("session_metrics"))
    safety_filters = 0
    with suppress(TypeError, ValueError):
        safety_filters = int(session_metrics.get("safety_filters_triggered", 0) or 0)
    if safety_filters > 0:
        reasons.append("safety_filters_triggered")

    if not status_map:
        readiness = "offline"
    elif missing_keys or "engine_not_initialized" in reasons:
        readiness = "blocked"
    elif unavailable_components:
        readiness = "blocked"
    elif not engine_active or degraded_components or safety_filters > 0:
        readiness = "degraded"
    else:
        readiness = "ready"

    return {
        "ok": readiness in {"ready", "degraded", "offline"},
        "system": "artificial_intelligence",
        "contract_version": AI_READINESS_CONTRACT_VERSION,
        "readiness": readiness,
        "safe_for_requests": readiness == "ready",
        "reasons": sorted(set(reasons)) or ["ready"],
        "checks": {
            "status_contract_complete": not missing_keys,
            "missing_status_keys": missing_keys,
            "engine_active": engine_active,
            "components": components,
            "safety_filters_triggered": safety_filters,
            "session_active": bool(status_map.get("session_active", False)),
        },
        "authority": {
            "owns": [
                "AI message processing",
                "reasoning context construction",
                "conversation memory handoff",
                "AI task submission to agent orchestration",
                "AI subsystem status reporting",
            ],
            "does_not_own": [
                "Guardian approval decisions",
                "Security capability policy",
                "Kernel scheduling",
                "Memory persistence authority",
                "Self-Improvement proposal approval",
                "Self-Incorporation execution",
                "Chat transport policy",
            ],
        },
    }

def build_ai_readiness_payload(status: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build the public AI status/readiness response."""

    return {
        "ok": True,
        "engine": status if isinstance(status, Mapping) else None,
        "readiness": assess_ai_readiness(status),
    }

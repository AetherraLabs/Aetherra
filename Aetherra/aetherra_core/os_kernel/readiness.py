"""Read-only readiness contract for the Aetherra OS Kernel."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

KERNEL_READINESS_CONTRACT_VERSION = "1.0"

_REQUIRED_STATUS_KEYS = frozenset(
    {
        "running",
        "paused",
        "queue_sizes",
        "queue_limits",
        "metrics",
        "backpressure_guard_pass",
        "night_schedule_guard_pass",
        "plugin_cb_open",
        "dlq_count",
        "hmr",
        "inflight",
    }
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _non_negative_ints(values: Mapping[str, Any]) -> bool:
    for value in values.values():
        try:
            if int(value) < 0:
                return False
        except (TypeError, ValueError):
            return False
    return True


def _queue_pressure_checks(
    queue_sizes: Mapping[str, Any], queue_limits: Mapping[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    pressure: dict[str, Any] = {}
    reasons: list[str] = []
    for queue_name, raw_size in queue_sizes.items():
        try:
            size = max(0, int(raw_size))
        except (TypeError, ValueError):
            pressure[str(queue_name)] = {"valid": False}
            reasons.append(f"invalid_queue_size:{queue_name}")
            continue

        try:
            limit = max(0, int(queue_limits.get(queue_name, 0)))
        except (TypeError, ValueError):
            pressure[str(queue_name)] = {"valid": False, "size": size}
            reasons.append(f"invalid_queue_limit:{queue_name}")
            continue

        ratio = None
        if limit > 0:
            ratio = size / limit
            if ratio >= 1:
                reasons.append(f"queue_at_or_over_limit:{queue_name}")
            elif ratio >= 0.8:
                reasons.append(f"queue_near_limit:{queue_name}")

        pressure[str(queue_name)] = {
            "valid": True,
            "size": size,
            "limit": limit,
            "bounded": limit > 0,
            "ratio": ratio,
        }
    return pressure, reasons


def assess_kernel_readiness(status: Mapping[str, Any] | None) -> dict[str, Any]:
    """Assess whether the Kernel status is safe enough for alpha scheduling.

    This does not mutate the kernel, registry, queues, or control plane. It only
    interprets the current status contract into a small operator-facing result.
    """

    status_map = _mapping(status)
    missing_keys = sorted(_REQUIRED_STATUS_KEYS.difference(status_map))
    reasons: list[str] = []

    if not status_map:
        reasons.append("kernel_status_unavailable")
    if missing_keys:
        reasons.append("status_contract_incomplete")

    running = bool(status_map.get("running", False))
    paused = bool(status_map.get("paused", False))
    if not running:
        reasons.append("kernel_not_running")
    if paused:
        reasons.append("kernel_paused")

    backpressure_ok = status_map.get("backpressure_guard_pass")
    if backpressure_ok is False:
        reasons.append("backpressure_guard_failed")

    night_schedule_ok = status_map.get("night_schedule_guard_pass")
    if night_schedule_ok is False:
        reasons.append("night_schedule_guard_failed")

    plugin_cb_open = bool(status_map.get("plugin_cb_open", False))
    if plugin_cb_open:
        reasons.append("plugin_circuit_breaker_open")

    queue_sizes = _mapping(status_map.get("queue_sizes"))
    queue_limits = _mapping(status_map.get("queue_limits"))
    queue_pressure, queue_reasons = _queue_pressure_checks(queue_sizes, queue_limits)
    reasons.extend(queue_reasons)

    inflight = _mapping(status_map.get("inflight"))
    inflight_valid = _non_negative_ints(inflight)
    if not inflight_valid:
        reasons.append("invalid_inflight_counts")

    blocking_reasons = {
        "kernel_status_unavailable",
        "status_contract_incomplete",
        "backpressure_guard_failed",
        "night_schedule_guard_failed",
        "invalid_inflight_counts",
    }
    if any(reason.startswith("invalid_queue_") for reason in reasons):
        readiness = "blocked"
    elif any(reason in blocking_reasons for reason in reasons):
        readiness = "blocked"
    elif not running:
        readiness = "offline"
    elif paused or plugin_cb_open or any("queue_near_limit" in r for r in reasons):
        readiness = "degraded"
    elif any("queue_at_or_over_limit" in r for r in reasons):
        readiness = "degraded"
    else:
        readiness = "ready"

    safe_to_schedule = readiness == "ready"
    if readiness == "degraded":
        safe_to_schedule = False

    return {
        "ok": readiness in {"ready", "degraded", "offline"},
        "system": "kernel",
        "contract_version": KERNEL_READINESS_CONTRACT_VERSION,
        "readiness": readiness,
        "safe_to_schedule": safe_to_schedule,
        "reasons": sorted(set(reasons)) or ["ready"],
        "checks": {
            "status_contract_complete": not missing_keys,
            "missing_status_keys": missing_keys,
            "running": running,
            "paused": paused,
            "backpressure_guard_pass": backpressure_ok is not False,
            "night_schedule_guard_pass": night_schedule_ok is not False,
            "plugin_circuit_breaker_open": plugin_cb_open,
            "queue_pressure": queue_pressure,
            "inflight_valid": inflight_valid,
        },
        "authority": {
            "owns": [
                "runtime loop scheduling",
                "priority queues",
                "service heartbeat coordination",
                "kernel lifecycle state",
                "kernel-held HMR swaps",
            ],
            "does_not_own": [
                "Guardian approval policy",
                "Security enforcement policy",
                "Homeostasis diagnosis",
                "Self-Improvement proposal generation",
                "Self-Incorporation execution authority",
                "Runtime UI rendering",
            ],
        },
        "source": str(status_map.get("_source") or "live_kernel"),
    }


def build_kernel_readiness_payload(status: Mapping[str, Any] | None) -> dict[str, Any]:
    """Build the public Kernel readiness response."""

    return {
        "ok": True,
        "kernel": status if isinstance(status, Mapping) else {"running": False},
        "readiness": assess_kernel_readiness(status),
    }

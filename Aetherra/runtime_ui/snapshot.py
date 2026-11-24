"""Read-only Runtime UI observations from existing, fresh runtime evidence."""

from __future__ import annotations

# Standard library imports
import asyncio
import inspect
from datetime import UTC, datetime
from hashlib import sha256
from threading import BoundedSemaphore, Event, Thread
from typing import Any

# Only these known read-only status interfaces are queried. Registry evidence is
# sufficient for presence, but must never be presented as measured readiness.
_SERVICES = {
    "security": ("security",),
    "homeostasis": ("homeostasis_system", "aetherra_homeostasis"),
    "memory": ("memory_system",),
    "consciousness": ("consciousness_core",),
    "agents": ("agent_fabric",),
    "self_improvement": ("self_improvement_engine",),
    "self_incorporation": ("self_incorporation",),
    "maintenance": ("maintenance_system", "aetherra_maintenance"),
    "aether_script": ("aether_script_service",),
    "kernel": ("kernel_loop",),
    "engine": ("aetherra_engine",),
    "integration_validation": ("integration_validation",),
}
_AUTHORITIES = {
    "security": "enforce",
    "homeostasis": "observe_verify",
    "agents": "observe",
    "self_improvement": "diagnose_propose",
    "self_incorporation": "execute_after_approval",
    "maintenance": "coordinate",
    "kernel": "runtime_core",
}
_STATUS_METHODS = {
    "kernel": "get_status",
    "engine": "get_system_status",
    "homeostasis": "get_orchestrator_status",
    "maintenance": "get_status",
}
_STATUS_TIMEOUT_SECONDS = 0.5
_STATUS_READ_SLOTS = BoundedSemaphore(3)


def _observation(evidence: str, observed_at: str) -> dict[str, Any]:
    return {
        "status": "unknown",
        "health": None,
        # Neutral rendering value for the existing scene contract, not a sample.
        "activity": 0.0,
        "summary": "No fresh runtime evidence is available for this subsystem.",
        "metrics": {
            "available": False,
            "evidence": evidence,
            "observed_at": observed_at,
            "freshness": "unknown",
            "readiness_verified": False,
            "activity_measured": False,
        },
    }


def collect_runtime_ui_system_status() -> dict[str, dict[str, Any]]:
    """Observe existing services; never start a registry, service, or fallback."""
    now = datetime.now(UTC)
    observed_at = now.isoformat().replace("+00:00", "Z")
    registry = None
    try:
        # Aetherra imports
        from aetherra_service_registry import get_existing_service_registry

        registry = get_existing_service_registry()
        if registry is not None and not registry.get_registry_status().get("running"):
            registry = None
    except Exception:
        registry = None

    status = {}
    for name, service_names in _SERVICES.items():
        observation = _observation("registry_unavailable", observed_at)
        if name in _AUTHORITIES:
            observation["metrics"]["authority"] = _AUTHORITIES[name]
        if registry is not None:
            try:
                _observe_service(name, service_names, registry, observation, now)
            except Exception:
                observation["status"] = "unknown"
                observation["summary"] = "Runtime evidence could not be collected."
                observation["metrics"]["evidence"] = "service_status_unavailable"
        status[name] = observation
    status["guardian"] = _guardian_status(observed_at)
    return status


def _observe_service(name, service_names, registry, observation, now) -> None:
    metrics = observation["metrics"]
    metrics["source"] = "in_process_registry"
    info = next(
        (
            info
            for service in service_names
            if (info := registry.get_service_info(service)) is not None
        ),
        None,
    )
    if info is None:
        metrics["evidence"] = "service_unregistered"
        return

    registry_status = str(getattr(info.status, "value", info.status))
    metrics.update(
        {
            "service_name": info.name,
            "registry_status": registry_status,
            "self_heartbeat": bool(info.metadata.get("self_heartbeat")),
        }
    )
    if info.metadata.get("stub") or info.metadata.get("type") == "mock":
        metrics["evidence"] = "placeholder_service"
        observation["summary"] = (
            "Only a placeholder is registered; live service status is unknown."
        )
        return
    heartbeat = info.last_heartbeat
    if not isinstance(heartbeat, datetime):
        metrics["evidence"] = "heartbeat_unavailable"
        return
    # Registry timestamps are local naive datetimes; astimezone also handles UTC.
    heartbeat = heartbeat.astimezone(UTC)
    age = (now - heartbeat).total_seconds()
    stale_after = max(1, int(getattr(registry, "_stale_sec", 180)))
    metrics.update(
        {
            "last_heartbeat": heartbeat.isoformat().replace("+00:00", "Z"),
            "heartbeat_age_seconds": round(age, 3),
            "stale_after_seconds": stale_after,
        }
    )
    if age < 0 or age > stale_after:
        metrics["freshness"] = "stale" if age > stale_after else "unknown"
        metrics["evidence"] = (
            "heartbeat_stale" if age > stale_after else "heartbeat_invalid"
        )
        observation["summary"] = (
            "Registry heartbeat is stale or invalid; current status is unknown."
        )
        return
    metrics.update(
        {"available": True, "freshness": "fresh", "evidence": "registry_heartbeat"}
    )
    observation["status"] = {
        "healthy": "active",
        "degraded": "degraded",
        "failed": "offline",
        "stopping": "offline",
    }.get(registry_status, "unknown")
    observation["summary"] = (
        f"Registry reports {registry_status}; subsystem readiness has not been verified."
    )
    if registry_status not in {"healthy", "degraded"}:
        return
    method = _STATUS_METHODS.get(name)
    if method is None:
        return
    raw = _read_status(getattr(info.instance, method, None))
    if not raw:
        observation["status"] = "unknown"
        observation["summary"] = (
            "The registered service did not provide a bounded status observation."
        )
        metrics["evidence"] = "service_status_unavailable"
        return

    if name == "homeostasis":
        running = raw.get("running")
        observation["status"] = (
            "offline"
            if running is False
            else (
                "active"
                if running is True and raw.get("initialized") is True
                else "unknown"
            )
        )
        if observation["status"] == "active" and registry_status == "degraded":
            observation["status"] = "degraded"
        metrics.update(
            {
                "evidence": "service_status",
                **_homeostasis_metrics(raw),
            }
        )
        observation["summary"] = (
            f"Homeostasis reports {observation['status']}; this is a lifecycle observation, not a health score."
        )
        return

    if name == "maintenance":
        available = raw.get("available")
        if raw.get("degraded") is True or registry_status == "degraded":
            observation["status"] = "degraded"
        else:
            observation["status"] = "active" if available is True else "unknown"
        metrics.update(
            {
                "available": available is True,
                "evidence": "service_status",
                **_maintenance_metrics(raw),
            }
        )
        observation["summary"] = (
            "Maintenance record status observed; proposals do not imply approval or execution."
        )
        return

    if name == "engine":
        # Aetherra imports
        from Aetherra.aetherra_core.engine.readiness import build_ai_readiness_payload

        readiness = build_ai_readiness_payload(raw)["readiness"]
    else:
        # Aetherra imports
        from Aetherra.aetherra_core.os_kernel.readiness import assess_kernel_readiness

        readiness = assess_kernel_readiness(raw)
    metrics.update(
        {
            "evidence": "service_readiness",
            "readiness_verified": True,
            "readiness": readiness["readiness"],
            "readiness_reasons": ", ".join(readiness.get("reasons", [])),
        }
    )
    safety_key = "safe_for_requests" if name == "engine" else "safe_to_schedule"
    metrics[safety_key] = readiness[safety_key]
    observation["status"] = {
        "ready": "active",
        "degraded": "degraded",
        "blocked": "degraded",
        "offline": "offline",
    }.get(readiness["readiness"], "unknown")
    if observation["status"] == "active" and registry_status == "degraded":
        observation["status"] = "degraded"
    reasons = ", ".join(readiness.get("reasons", []))
    observation["summary"] = (
        f"Service readiness: {readiness['readiness']} ({reasons}); registry: {registry_status}."
    )


def _homeostasis_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    """Whitelist lifecycle/mode counters; missing evidence is never a zero."""
    result: dict[str, Any] = {
        key: raw[key] if isinstance(raw.get(key), bool) else None
        for key in ("running", "initialized", "observe_only_requested")
    }
    controller = raw.get("controller")
    mode = controller.get("mode") if isinstance(controller, dict) else None
    result["controller_mode"] = (
        mode
        if isinstance(mode, str)
        and mode
        in {
            "observe_only",
            "advisory",
            "active_limited",
            "active",
            "emergency",
            "disabled",
        }
        else None
    )
    actuators = raw.get("actuators")
    actuators = actuators if isinstance(actuators, dict) else {}
    counts = {
        "restart_count": raw.get("restart_count"),
        "error_recovery_count": raw.get("error_recovery_count"),
        "actuator_actions_attempted": actuators.get("actions_attempted"),
        "actuator_actions_executed": actuators.get("actions_executed"),
        "actuator_actions_blocked": actuators.get("actions_blocked"),
    }
    for key, value in counts.items():
        result[key] = (
            value
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0
            else None
        )
    return result


def _maintenance_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    """Project bounded record evidence, excluding raw events, paths, and text."""
    result: dict[str, Any] = {}
    for key in (
        "cycle_count",
        "active_cycle_count",
        "terminal_cycle_count",
        "failure_count",
    ):
        value = raw.get(key)
        result[key] = (
            value
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0
            else None
        )

    recent = raw.get("recent_cycles")
    latest = recent[0] if isinstance(recent, list) and recent else None
    result["latest_cycle_present"] = (
        True if isinstance(latest, dict) else False if recent == [] else None
    )
    latest = latest if isinstance(latest, dict) else {}
    for key in ("cycle_id", "proposal_id", "guardian_audit_id"):
        value = latest.get(key)
        result[f"latest_{key}_hash"] = (
            sha256(value.encode("utf-8")).hexdigest()[:16]
            if isinstance(value, str) and 0 < len(value) <= 256
            else None
        )
    for key in ("has_diagnosis", "has_proposal", "security_enforced"):
        value = latest.get(key)
        result[f"latest_{key}"] = value if isinstance(value, bool) else None
    observations = latest.get("observations")
    result["latest_observations"] = (
        observations
        if isinstance(observations, int)
        and not isinstance(observations, bool)
        and observations >= 0
        else None
    )
    states = {
        "status": {
            "created",
            "observed",
            "observation_degraded",
            "diagnosed",
            "proposed",
            "approved",
            "denied",
            "contained",
            "security_enforced",
            "security_blocked",
            "executed",
            "execution_failed",
            "verified",
            "verification_failed",
            "learned",
        },
        "guardian_status": {
            "allow",
            "allow_limited",
            "deny",
            "require_approval",
            "contain",
        },
        "execution_status": {
            "applied",
            "accepted",
            "succeeded",
            "success",
            "failed",
            "blocked",
            "skipped",
            "denied",
        },
        "verification_status": {"passed", "stable", "improved", "failed"},
    }
    for key, allowed in states.items():
        value = latest.get(key)
        output_key = "latest_cycle_status" if key == "status" else f"latest_{key}"
        result[output_key] = (
            value
            if isinstance(value, str) and value in allowed
            else (
                "not_recorded"
                if key != "status" and key in latest and value is None
                else None
            )
        )
    result["latest_updated_at"] = None
    updated_at = latest.get("updated_at")
    if isinstance(updated_at, str) and len(updated_at) <= 64:
        try:
            stamp = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            if stamp.tzinfo is not None:
                result["latest_updated_at"] = (
                    stamp.astimezone(UTC).isoformat().replace("+00:00", "Z")
                )
        except ValueError:
            pass
    return result


def _read_status(method: Any) -> dict[str, Any] | None:
    """Bound reads, including a blocked sync getter, without accumulating workers."""
    if not callable(method) or not _STATUS_READ_SLOTS.acquire(blocking=False):
        return None
    done = Event()
    result: list[dict[str, Any]] = []

    async def resolve(awaitable):
        return await asyncio.wait_for(awaitable, timeout=_STATUS_TIMEOUT_SECONDS)

    def read() -> None:
        try:
            value = method()
            if inspect.isawaitable(value):
                value = asyncio.run(resolve(value))
            if isinstance(value, dict):
                result.append(value)
        except Exception:
            return  # Raw service exceptions can include secrets and paths.
        finally:
            _STATUS_READ_SLOTS.release()
            done.set()

    try:
        Thread(target=read, name="runtime-ui-status", daemon=True).start()
    except RuntimeError:
        _STATUS_READ_SLOTS.release()
        return None
    if not done.wait(_STATUS_TIMEOUT_SECONDS):
        return None
    return result[0] if result else None


def collect_runtime_ui_events() -> list[dict[str, Any]]:
    """Return bounded snapshot observations, never invented lifecycle events."""
    observed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return [
        {
            "source": "runtime_ui",
            "event_type": "observatory_snapshot",
            "summary": "Read-only Observatory observation requested; unavailable evidence is marked unknown.",
            "severity": "info",
            "occurred_at": observed_at,
            "details": {"authority": "observe_only", "observation_only": True},
        },
        {
            "source": "guardian",
            "event_type": "guardian_status_observed",
            "summary": "Guardian configuration observation requested; this is not an approval or decision event.",
            "severity": "notice",
            "occurred_at": observed_at,
            "details": {"view": "summary_only", "observation_only": True},
        },
        {
            "source": "homeostasis",
            "event_type": "homeostasis_status_observed",
            "summary": "Homeostasis status observation requested; this is not a recovery or verification event.",
            "severity": "info",
            "occurred_at": observed_at,
            "details": {"view": "health_summary", "observation_only": True},
        },
    ]


def _guardian_status(observed_at: str) -> dict[str, Any]:
    observation = _observation("guardian_status_unavailable", observed_at)

    def read_guardian() -> dict[str, Any]:
        # Aetherra imports
        from Aetherra.guardian import (
            guardian_audit_integrity_ok,
            guardian_enabled,
            guardian_mode,
            guardian_mode_status,
        )

        return {
            "enabled": guardian_enabled(),
            "audit_integrity_ok": guardian_audit_integrity_ok(),
            "mode": guardian_mode().value,
            "mode_state": guardian_mode_status().get("state"),
        }

    raw = _read_status(read_guardian)
    if not raw:
        return observation

    enabled = raw["enabled"]
    audit_ok = raw["audit_integrity_ok"]
    observation["status"] = (
        "offline" if not enabled else "active" if audit_ok else "degraded"
    )
    observation["summary"] = (
        "Guardian configuration and audit integrity observed; execution readiness is not measured."
    )
    observation["metrics"].update(
        {
            "available": True,
            "evidence": "guardian_configuration_and_audit",
            "freshness": "fresh",
            **raw,
        }
    )
    return observation

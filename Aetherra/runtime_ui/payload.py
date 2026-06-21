"""Runtime UI payload builders for Hub and future clients."""

from __future__ import annotations

from typing import Any

from .contract import validate_runtime_ui_payload
from .manifest import build_runtime_ui_manifest
from .observatory import ObservatoryMode, build_observatory_state
from .profiles import get_subsystem_profile, subsystem_guidance
from .scene import build_observatory_scene
from .snapshot import collect_runtime_ui_events, collect_runtime_ui_system_status


def build_runtime_ui_state(
    mode: ObservatoryMode,
    *,
    user_name: str | None = None,
):
    """Build the current read-only Runtime UI state."""

    return build_observatory_state(
        system_status=collect_runtime_ui_system_status(),
        events=collect_runtime_ui_events(),
        mode=mode,
        user_name=user_name,
    )


def build_runtime_ui_observatory_payload(
    mode: ObservatoryMode,
    *,
    user_name: str | None = None,
) -> dict[str, Any]:
    """Build the Observatory state response payload."""

    state = build_runtime_ui_state(mode, user_name=user_name)
    return {"ok": True, "observatory": state.to_dict()}


def build_runtime_ui_scene_payload(
    mode: ObservatoryMode,
    *,
    user_name: str | None = None,
) -> dict[str, Any]:
    """Build the Observatory scene response payload."""

    state = build_runtime_ui_state(mode, user_name=user_name)
    scene = build_observatory_scene(state)
    return {
        "ok": True,
        "observatory": state.to_dict(),
        "scene": scene.to_dict(),
    }


def build_runtime_ui_bootstrap_payload(
    *,
    mode: ObservatoryMode,
    user_name: str | None,
    limit: int,
) -> dict[str, Any]:
    """Build the first-load Runtime UI payload."""

    state = build_runtime_ui_state(mode, user_name=user_name)
    scene = build_observatory_scene(state)
    events = _events_payload(state, limit=limit)
    return {
        "ok": True,
        "read_only": True,
        "manifest": build_runtime_ui_manifest(),
        "observatory": state.to_dict(),
        "scene": scene.to_dict(),
        "activity": {
            "events": events,
            "total": len(state.events),
            "limit": limit,
        },
    }


def build_runtime_ui_status_payload() -> dict[str, Any]:
    """Build compact Runtime UI health/readiness payload."""

    payload = build_runtime_ui_bootstrap_payload(
        mode=ObservatoryMode.OVERVIEW,
        user_name=None,
        limit=25,
    )
    validation = validate_runtime_ui_payload(payload)
    manifest = payload["manifest"]
    return {
        "ok": validation.ok,
        "status": "healthy" if validation.ok else "degraded",
        "read_only": True,
        "contract_version": manifest["contract_version"],
        "controls_enabled": manifest["controls_enabled"],
        "legacy_ui_enabled": manifest["legacy_ui_enabled"],
        "validation": validation.to_dict(),
        "endpoints": manifest["endpoints"],
    }


def build_runtime_ui_contract_validation_payload(
    *,
    mode: ObservatoryMode,
    user_name: str | None,
    limit: int,
) -> dict[str, Any]:
    """Build the Runtime UI contract validation response payload."""

    payload = build_runtime_ui_bootstrap_payload(
        mode=mode,
        user_name=user_name,
        limit=limit,
    )
    validation = validate_runtime_ui_payload(payload)
    return {
        "ok": True,
        "read_only": True,
        "validation": validation.to_dict(),
    }


def build_runtime_ui_activity_payload(
    *,
    channel: str | None,
    source: str | None,
    limit: int,
) -> dict[str, Any]:
    """Build bounded Runtime UI activity response payload."""

    state = build_runtime_ui_state(ObservatoryMode.OVERVIEW)
    events = [event.to_dict() for event in state.events]
    if channel:
        events = [event for event in events if event.get("visual_channel") == channel]
    if source:
        events = [event for event in events if event.get("source") == source]
    total = len(events)
    return {
        "ok": True,
        "read_only": True,
        "events": events[-limit:],
        "total": total,
        "filters": {"channel": channel, "source": source, "limit": limit},
    }


def build_runtime_ui_subsystem_payload(
    subsystem_name: str,
    *,
    user_name: str | None = None,
) -> dict[str, Any] | None:
    """Build a focused subsystem payload, or None when unknown."""

    state = build_runtime_ui_state(ObservatoryMode.SUBSYSTEM, user_name=user_name)
    normalized_name = subsystem_name.strip().lower().replace("-", "_")
    subsystems = {subsystem.name: subsystem for subsystem in state.subsystems}
    subsystem = subsystems.get(normalized_name)
    if subsystem is None:
        return None

    related_connections = [
        connection.to_dict()
        for connection in state.connections
        if connection.source == subsystem.name or connection.target == subsystem.name
    ]
    return {
        "ok": True,
        "read_only": True,
        "subsystem": subsystem.to_dict(),
        "profile": get_subsystem_profile(subsystem.name),
        "connections": related_connections,
        "events": [event.to_dict() for event in state.events],
        "lyrixa_guidance": subsystem_guidance(subsystem.name),
    }


def runtime_ui_subsystem_names() -> list[str]:
    """Return all current Observatory subsystem names."""

    state = build_runtime_ui_state(ObservatoryMode.SUBSYSTEM)
    return sorted(subsystem.name for subsystem in state.subsystems)


def _events_payload(state, *, limit: int) -> list[dict[str, Any]]:
    return [event.to_dict() for event in state.events][-limit:]

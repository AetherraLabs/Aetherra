"""Contract validation helpers for Runtime UI payloads."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeUiContractValidation:
    """Validation result for a Runtime UI payload."""

    ok: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    checked: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_runtime_ui_payload(payload: dict[str, Any]) -> RuntimeUiContractValidation:
    """Validate cross-object consistency for a Runtime UI bootstrap payload."""

    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    manifest = _object(payload.get("manifest"))
    observatory = _object(payload.get("observatory"))
    scene = _object(payload.get("scene"))
    activity = _object(payload.get("activity"))
    checked.extend(["manifest", "observatory", "scene", "activity"])

    _validate_read_only(payload, manifest, observatory, scene, errors)
    _validate_manifest(manifest, errors)
    _validate_scene_matches_observatory(scene, observatory, errors, warnings)
    _validate_activity(activity, manifest, errors, warnings)

    return RuntimeUiContractValidation(
        ok=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        checked=tuple(checked),
    )


def _validate_read_only(
    payload: dict[str, Any],
    manifest: dict[str, Any],
    observatory: dict[str, Any],
    scene: dict[str, Any],
    errors: list[str],
) -> None:
    if payload.get("read_only") is not True:
        errors.append("payload.read_only must be true")
    if manifest.get("read_only") is not True:
        errors.append("manifest.read_only must be true")
    if manifest.get("controls_enabled") is not False:
        errors.append("manifest.controls_enabled must be false")
    if observatory.get("read_only") is not True:
        errors.append("observatory.read_only must be true")
    if scene.get("read_only") is not True:
        errors.append("scene.read_only must be true")


def _validate_manifest(manifest: dict[str, Any], errors: list[str]) -> None:
    endpoints = _object(manifest.get("endpoints"))
    required_endpoints = {
        "activity",
        "bootstrap",
        "manifest",
        "observatory",
        "openapi",
        "scene",
        "status",
        "subsystem",
    }
    missing = sorted(required_endpoints - set(endpoints))
    if missing:
        errors.append(f"manifest.endpoints missing: {', '.join(missing)}")

    authority = _object(manifest.get("authority"))
    for key in ("observe", "approve", "enforce", "execute", "verify"):
        if key not in authority:
            errors.append(f"manifest.authority missing: {key}")


def _validate_scene_matches_observatory(
    scene: dict[str, Any],
    observatory: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    subsystems = {
        subsystem.get("name")
        for subsystem in _list(observatory.get("subsystems"))
        if isinstance(subsystem, dict)
    }
    nodes = {
        node.get("name")
        for node in _list(scene.get("nodes"))
        if isinstance(node, dict)
    }
    if subsystems != nodes:
        errors.append("scene.nodes must match observatory.subsystems")

    for connection in _list(scene.get("connections")):
        if not isinstance(connection, dict):
            errors.append("scene.connections entries must be objects")
            continue
        source = connection.get("source")
        target = connection.get("target")
        if source not in nodes or target not in nodes:
            errors.append("scene connection references unknown node")
        for numeric_key in ("pulse", "thickness"):
            if not _bounded_number(connection.get(numeric_key)):
                errors.append(f"scene connection {numeric_key} must be between 0 and 1")

    if scene.get("coordinate_space") != "normalized_3d":
        warnings.append("scene.coordinate_space is not normalized_3d")


def _validate_activity(
    activity: dict[str, Any],
    manifest: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    channels = set(_list(manifest.get("supported_activity_channels")))
    events = _list(activity.get("events"))
    if not _bounded_number(activity.get("limit"), minimum=1.0, maximum=100.0):
        errors.append("activity.limit must be between 1 and 100")
    if len(events) > int(activity.get("limit", 0) or 0):
        errors.append("activity.events exceeds activity.limit")

    for event in events:
        if not isinstance(event, dict):
            errors.append("activity.events entries must be objects")
            continue
        channel = event.get("visual_channel")
        if channel not in channels:
            errors.append("activity event visual_channel is unsupported")
        if event.get("details") and not isinstance(event.get("details"), dict):
            errors.append("activity event details must be an object")

    if activity.get("total", 0) < len(events):
        warnings.append("activity.total is less than returned events")


def _object(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _bounded_number(
    value: Any,
    *,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return minimum <= number <= maximum

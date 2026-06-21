"""Read-only state contract for the Aetherra Cognitive Observatory.

The Runtime UI foundation starts with a stable data model rather than a visual
implementation. Future 2D/3D clients should render this state without owning
system authority or bypassing Guardian/Security controls.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class SubsystemStatus(StrEnum):
    """Display status for an observable Aetherra subsystem."""

    ACTIVE = "active"
    STABLE = "stable"
    DEGRADED = "degraded"
    CONTAINED = "contained"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class ObservatoryMode(StrEnum):
    """Runtime UI presentation mode."""

    FIRST_LAUNCH = "first_launch"
    OVERVIEW = "overview"
    ARCHITECT = "architect"
    SUBSYSTEM = "subsystem"


@dataclass(frozen=True, slots=True)
class ObservatorySubsystem:
    """A node in the Cognitive Observatory architecture map."""

    name: str
    label: str
    status: SubsystemStatus = SubsystemStatus.UNKNOWN
    health: float | None = None
    activity: float = 0.0
    summary: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True, slots=True)
class ObservatoryConnection:
    """A read-only relationship between two observable subsystems."""

    source: str
    target: str
    label: str
    activity: float = 0.0
    status: SubsystemStatus = SubsystemStatus.UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True, slots=True)
class ObservatoryEvent:
    """A bounded event for the UI activity stream."""

    source: str
    event_type: str
    summary: str
    severity: str = "info"
    visual_channel: str = "system"
    action_required: bool = False
    occurred_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z")
    )
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ObservatoryState:
    """Top-level read-only state rendered by the Runtime UI."""

    mode: ObservatoryMode
    core_label: str
    greeting: str
    generated_at: str
    read_only: bool
    subsystems: tuple[ObservatorySubsystem, ...]
    connections: tuple[ObservatoryConnection, ...]
    events: tuple[ObservatoryEvent, ...] = ()
    lyrixa_guidance: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "core_label": self.core_label,
            "greeting": self.greeting,
            "generated_at": self.generated_at,
            "read_only": self.read_only,
            "subsystems": [subsystem.to_dict() for subsystem in self.subsystems],
            "connections": [connection.to_dict() for connection in self.connections],
            "events": [event.to_dict() for event in self.events],
            "lyrixa_guidance": self.lyrixa_guidance,
        }


def build_observatory_state(
    *,
    system_status: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
    mode: ObservatoryMode = ObservatoryMode.OVERVIEW,
    user_name: str | None = None,
) -> ObservatoryState:
    """Build a read-only Cognitive Observatory state snapshot.

    `system_status` accepts a shallow mapping keyed by subsystem name. Each
    subsystem value may provide `status`, `health`, `activity`, `summary`, and
    `metrics`. Missing systems are represented as unknown/stable defaults so the
    UI can render a consistent architecture map during early boot.
    """

    status_map = system_status or {}
    subsystems = tuple(
        _build_subsystem(name, label, status_map.get(name))
        for name, label in _SUBSYSTEM_LABELS
    )
    connection_lookup = {subsystem.name: subsystem for subsystem in subsystems}
    connections = tuple(
        _build_connection(source, target, label, connection_lookup)
        for source, target, label in _CONNECTIONS
    )
    observatory_events = tuple(_build_event(event) for event in events or [])
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    greeting_name = (user_name or "").strip()
    greeting = f"Good morning, {greeting_name}." if greeting_name else "System Online"

    return ObservatoryState(
        mode=mode,
        core_label="AETHERRA",
        greeting=greeting,
        generated_at=generated_at,
        read_only=True,
        subsystems=subsystems,
        connections=connections,
        events=observatory_events,
        lyrixa_guidance=_lyrixa_guidance(mode),
    )


def _build_subsystem(
    name: str,
    label: str,
    raw_status: Any,
) -> ObservatorySubsystem:
    raw = raw_status if isinstance(raw_status, dict) else {}
    status = _coerce_status(raw.get("status"))
    health = _coerce_health(raw.get("health"))
    return ObservatorySubsystem(
        name=name,
        label=label,
        status=status,
        health=health,
        activity=_coerce_activity(raw.get("activity")),
        summary=str(raw.get("summary") or ""),
        metrics=dict(raw.get("metrics") or {}),
    )


def _build_connection(
    source: str,
    target: str,
    label: str,
    subsystems: dict[str, ObservatorySubsystem],
) -> ObservatoryConnection:
    source_state = subsystems.get(source)
    target_state = subsystems.get(target)
    activity = max(
        source_state.activity if source_state else 0.0,
        target_state.activity if target_state else 0.0,
    )
    status = _connection_status(source_state, target_state)
    return ObservatoryConnection(
        source=source,
        target=target,
        label=label,
        activity=activity,
        status=status,
    )


def _build_event(raw_event: dict[str, Any]) -> ObservatoryEvent:
    details = raw_event.get("details") if isinstance(raw_event, dict) else None
    severity = _coerce_event_severity(raw_event.get("severity"))
    event_type = str(raw_event.get("event_type") or "status")
    return ObservatoryEvent(
        source=str(raw_event.get("source") or "runtime_ui"),
        event_type=event_type,
        summary=str(raw_event.get("summary") or ""),
        severity=severity,
        visual_channel=_event_visual_channel(event_type, severity),
        action_required=_event_action_required(raw_event.get("action_required"), severity),
        occurred_at=str(
            raw_event.get("occurred_at")
            or datetime.now(UTC).isoformat().replace("+00:00", "Z")
        ),
        details=dict(details or {}),
    )


def _connection_status(
    source: ObservatorySubsystem | None,
    target: ObservatorySubsystem | None,
) -> SubsystemStatus:
    statuses = {
        source.status if source else SubsystemStatus.UNKNOWN,
        target.status if target else SubsystemStatus.UNKNOWN,
    }
    if SubsystemStatus.CONTAINED in statuses:
        return SubsystemStatus.CONTAINED
    if SubsystemStatus.DEGRADED in statuses:
        return SubsystemStatus.DEGRADED
    if SubsystemStatus.OFFLINE in statuses:
        return SubsystemStatus.OFFLINE
    if SubsystemStatus.ACTIVE in statuses:
        return SubsystemStatus.ACTIVE
    if SubsystemStatus.STABLE in statuses:
        return SubsystemStatus.STABLE
    return SubsystemStatus.UNKNOWN


def _coerce_status(value: Any) -> SubsystemStatus:
    normalized = str(value or "").strip().lower()
    if normalized in {"healthy", "online", "running", "allow", "allow_limited"}:
        return SubsystemStatus.ACTIVE
    if normalized in {status.value for status in SubsystemStatus}:
        return SubsystemStatus(normalized)
    return SubsystemStatus.UNKNOWN


def _coerce_health(value: Any) -> float | None:
    try:
        if value is None:
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, number if number <= 1.0 else number / 100.0))


def _coerce_activity(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _coerce_event_severity(value: Any) -> str:
    normalized = str(value or "info").strip().lower()
    if normalized in {"debug", "info", "notice", "warning", "error", "critical"}:
        return normalized
    return "info"


def _event_visual_channel(event_type: str, severity: str) -> str:
    normalized_type = event_type.strip().lower()
    if severity in {"error", "critical"}:
        return "containment"
    if normalized_type in {"approval", "decision", "guardian_decision"}:
        return "governance"
    if normalized_type in {"proposal", "hypothesis", "simulation"}:
        return "evolution"
    if normalized_type in {"health", "diagnosis", "verification"}:
        return "regulation"
    return "system"


def _event_action_required(value: Any, severity: str) -> bool:
    if isinstance(value, bool):
        return value
    if severity in {"critical"}:
        return True
    return False


def _lyrixa_guidance(mode: ObservatoryMode) -> str:
    if mode == ObservatoryMode.ARCHITECT:
        return "Architect Mode shows services, capabilities, events, queues, and safety decisions."
    if mode == ObservatoryMode.FIRST_LAUNCH:
        return "Aetherra is online. The observatory is read-only until governed controls are enabled."
    return "You are viewing Aetherra as a living architecture map."


_SUBSYSTEM_LABELS: tuple[tuple[str, str], ...] = (
    ("security", "Security"),
    ("guardian", "Guardian"),
    ("homeostasis", "Homeostasis"),
    ("memory", "Memory"),
    ("consciousness", "Consciousness"),
    ("agents", "Agents"),
    ("self_improvement", "Self-Improvement"),
    ("self_incorporation", "Self-Incorporation"),
    ("maintenance", "Maintenance"),
    ("aether_script", "Aether Script"),
    ("kernel", "Kernel"),
    ("integration_validation", "Integration Validation"),
)

_CONNECTIONS: tuple[tuple[str, str, str], ...] = (
    ("guardian", "security", "policy_enforcement"),
    ("homeostasis", "maintenance", "observe_verify"),
    ("self_improvement", "guardian", "proposal_review"),
    ("guardian", "self_incorporation", "approved_execution"),
    ("self_incorporation", "homeostasis", "outcome_verification"),
    ("memory", "consciousness", "continuity_context"),
    ("agents", "aether_script", "task_runtime"),
    ("kernel", "integration_validation", "runtime_readiness"),
)

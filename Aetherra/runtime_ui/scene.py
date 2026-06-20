"""Renderer-agnostic scene contract for the Cognitive Observatory."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .observatory import ObservatoryState, SubsystemStatus


@dataclass(frozen=True, slots=True)
class ObservatorySceneNode:
    """Stable visual metadata for a subsystem node."""

    name: str
    label: str
    group: str
    x: float
    y: float
    z: float
    radius: float
    emphasis: float
    status: SubsystemStatus
    accessibility_label: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True, slots=True)
class ObservatorySceneConnection:
    """Stable visual metadata for a relationship between scene nodes."""

    source: str
    target: str
    label: str
    status: SubsystemStatus
    pulse: float
    thickness: float

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True, slots=True)
class ObservatoryScene:
    """Top-level scene contract consumed by future Observatory renderers."""

    core_label: str
    read_only: bool
    coordinate_space: str
    nodes: tuple[ObservatorySceneNode, ...]
    connections: tuple[ObservatorySceneConnection, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "core_label": self.core_label,
            "read_only": self.read_only,
            "coordinate_space": self.coordinate_space,
            "nodes": [node.to_dict() for node in self.nodes],
            "connections": [connection.to_dict() for connection in self.connections],
        }


def build_observatory_scene(state: ObservatoryState) -> ObservatoryScene:
    """Build a stable scene layout from an Observatory state snapshot."""

    nodes = tuple(_scene_node(subsystem) for subsystem in state.subsystems)
    connections = tuple(
        ObservatorySceneConnection(
            source=connection.source,
            target=connection.target,
            label=connection.label,
            status=connection.status,
            pulse=connection.activity,
            thickness=_connection_thickness(connection.status),
        )
        for connection in state.connections
    )
    return ObservatoryScene(
        core_label=state.core_label,
        read_only=True,
        coordinate_space="normalized_3d",
        nodes=nodes,
        connections=connections,
    )


def _scene_node(subsystem) -> ObservatorySceneNode:
    layout = _NODE_LAYOUT.get(
        subsystem.name,
        {"group": "system", "position": (0.0, 0.0, -0.4), "radius": 0.1},
    )
    x, y, z = layout["position"]
    return ObservatorySceneNode(
        name=subsystem.name,
        label=subsystem.label,
        group=str(layout["group"]),
        x=float(x),
        y=float(y),
        z=float(z),
        radius=float(layout["radius"]),
        emphasis=_node_emphasis(subsystem.status, subsystem.activity),
        status=subsystem.status,
        accessibility_label=f"{subsystem.label}: {subsystem.status.value}",
    )


def _node_emphasis(status: SubsystemStatus, activity: float) -> float:
    status_weight = {
        SubsystemStatus.CONTAINED: 1.0,
        SubsystemStatus.DEGRADED: 0.85,
        SubsystemStatus.ACTIVE: 0.75,
        SubsystemStatus.STABLE: 0.55,
        SubsystemStatus.OFFLINE: 0.35,
        SubsystemStatus.UNKNOWN: 0.25,
    }[status]
    return max(status_weight, min(1.0, activity))


def _connection_thickness(status: SubsystemStatus) -> float:
    if status == SubsystemStatus.CONTAINED:
        return 0.9
    if status == SubsystemStatus.DEGRADED:
        return 0.7
    if status == SubsystemStatus.ACTIVE:
        return 0.55
    if status == SubsystemStatus.STABLE:
        return 0.4
    return 0.25


_NODE_LAYOUT: dict[str, dict[str, object]] = {
    "guardian": {"group": "governance", "position": (0.62, 0.34, 0.0), "radius": 0.16},
    "security": {"group": "governance", "position": (0.88, 0.04, 0.0), "radius": 0.14},
    "homeostasis": {"group": "regulation", "position": (0.58, -0.42, 0.0), "radius": 0.15},
    "maintenance": {"group": "regulation", "position": (0.0, -0.72, 0.0), "radius": 0.14},
    "self_improvement": {"group": "evolution", "position": (-0.42, -0.46, 0.0), "radius": 0.14},
    "self_incorporation": {"group": "evolution", "position": (0.02, -0.24, 0.08), "radius": 0.13},
    "memory": {"group": "cognition", "position": (-0.7, 0.16, 0.0), "radius": 0.16},
    "consciousness": {"group": "cognition", "position": (-0.22, 0.62, 0.0), "radius": 0.17},
    "agents": {"group": "runtime", "position": (-0.78, -0.32, 0.0), "radius": 0.13},
    "aether_script": {"group": "runtime", "position": (-0.34, -0.08, 0.0), "radius": 0.12},
    "kernel": {"group": "runtime", "position": (0.24, 0.66, 0.0), "radius": 0.14},
    "integration_validation": {"group": "readiness", "position": (0.0, 0.92, -0.02), "radius": 0.11},
}

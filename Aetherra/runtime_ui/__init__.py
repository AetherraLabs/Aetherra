"""Runtime UI foundation for the Aetherra Cognitive Observatory."""

from .contract import RuntimeUiContractValidation, validate_runtime_ui_payload
from .manifest import build_runtime_ui_manifest
from .observatory import (
    ObservatoryConnection,
    ObservatoryEvent,
    ObservatoryMode,
    ObservatoryState,
    ObservatorySubsystem,
    SubsystemStatus,
    build_observatory_state,
)
from .payload import (
    build_runtime_ui_activity_payload,
    build_runtime_ui_bootstrap_payload,
    build_runtime_ui_contract_validation_payload,
    build_runtime_ui_observatory_payload,
    build_runtime_ui_scene_payload,
    build_runtime_ui_state,
    build_runtime_ui_status_payload,
    build_runtime_ui_subsystem_payload,
    runtime_ui_subsystem_names,
)
from .profiles import get_subsystem_profile, subsystem_guidance, supported_subsystems
from .query import (
    ParsedLimit,
    allowed_observatory_modes,
    bounded_filter_value,
    bounded_user_name,
    parse_limit,
    parse_observatory_mode,
)
from .scene import (
    ObservatoryScene,
    ObservatorySceneConnection,
    ObservatorySceneNode,
    build_observatory_scene,
)
from .snapshot import collect_runtime_ui_events, collect_runtime_ui_system_status

__all__ = [
    "ObservatoryConnection",
    "ObservatoryEvent",
    "ObservatoryMode",
    "ObservatoryScene",
    "ObservatorySceneConnection",
    "ObservatorySceneNode",
    "ObservatoryState",
    "ObservatorySubsystem",
    "ParsedLimit",
    "RuntimeUiContractValidation",
    "SubsystemStatus",
    "build_observatory_scene",
    "build_observatory_state",
    "build_runtime_ui_activity_payload",
    "build_runtime_ui_bootstrap_payload",
    "build_runtime_ui_contract_validation_payload",
    "build_runtime_ui_manifest",
    "build_runtime_ui_observatory_payload",
    "build_runtime_ui_scene_payload",
    "build_runtime_ui_state",
    "build_runtime_ui_status_payload",
    "build_runtime_ui_subsystem_payload",
    "collect_runtime_ui_events",
    "collect_runtime_ui_system_status",
    "allowed_observatory_modes",
    "bounded_filter_value",
    "bounded_user_name",
    "get_subsystem_profile",
    "parse_limit",
    "parse_observatory_mode",
    "runtime_ui_subsystem_names",
    "subsystem_guidance",
    "supported_subsystems",
    "validate_runtime_ui_payload",
]

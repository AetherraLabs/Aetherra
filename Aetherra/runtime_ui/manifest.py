"""Runtime UI manifest contract for Cognitive Observatory clients."""

from __future__ import annotations

from typing import Any

from .observatory import ObservatoryMode
from .profiles import supported_subsystems


def build_runtime_ui_manifest() -> dict[str, Any]:
    """Build the read-only Runtime UI capability and safety manifest."""

    return {
        "name": "Aetherra Cognitive Observatory",
        "contract_version": "1.0",
        "status": "functional_api_foundation",
        "read_only": True,
        "controls_enabled": False,
        "legacy_ui_enabled": False,
        "supported_modes": [mode.value for mode in ObservatoryMode],
        "supported_subsystems": supported_subsystems(),
        "supported_activity_channels": [
            "containment",
            "evolution",
            "governance",
            "regulation",
            "system",
        ],
        "endpoints": {
            "manifest": "/api/runtime-ui/manifest",
            "status": "/api/runtime-ui/status",
            "bootstrap": "/api/runtime-ui/bootstrap",
            "observatory": "/api/runtime-ui/observatory",
            "scene": "/api/runtime-ui/scene",
            "activity": "/api/runtime-ui/activity",
            "subsystem": "/api/runtime-ui/subsystems/{subsystem_name}",
            "openapi": "/api/openapi.json",
        },
        "authority": {
            "observe": "runtime_ui",
            "approve": "guardian",
            "enforce": "security",
            "execute": "self_incorporation",
            "verify": "homeostasis",
        },
        "safety_rules": [
            "read_only_foundation",
            "no_direct_memory_mutation",
            "no_direct_code_mutation",
            "no_privileged_execution",
            "raw_audit_logs_not_exposed",
            "future_controls_require_guardian_security_and_control_auth",
        ],
    }

"""Decision-tier classification for Guardian intent declarations."""

from __future__ import annotations

from .models import (
    GuardianDecisionTier,
    IntentDeclaration,
    RiskAssessment,
    RiskLevel,
)

_CRITICAL_CAPABILITIES = {
    "security:modify",
    "memory:modify_identity",
    "plugin:install",
    "plugin:load",
    "plugin:uninstall",
    "self:modify",
    "system:restart",
    "system:reload",
}

_PRIVILEGED_CAPABILITY_PREFIXES = (
    "agent:",
    "homeostasis:",
    "kernel:",
    "maintenance:",
    "memory:",
    "module:",
    "network:",
    "plugin:",
    "registry:",
    "script:",
)

_PRIVILEGED_CAPABILITIES = {
    "event:command",
    "executor:execute",
    "fs:delete",
    "fs:write",
    "python:execute",
    "system:execute",
}

_OBSERVATIONAL_ACTIONS = {
    "inspect",
    "list",
    "read",
    "report",
    "status",
}

_TELEMETRY_MARKERS = (
    "heartbeat",
    "metric",
    "metrics",
    "progress",
    "telemetry",
)


def classify_decision_tier(
    intent: IntentDeclaration,
    risk: RiskAssessment,
) -> GuardianDecisionTier:
    """Classify an intent into a Guardian performance/scope tier.

    This is intentionally conservative. The tier is advisory metadata for
    later caching, preauthorization, and async work. It does not weaken the
    current allow/deny path.
    """

    action = intent.action.lower()
    target = intent.target.lower()
    capabilities = {cap.lower() for cap in intent.capabilities}
    risk_factors = set(risk.factors)

    if (
        risk.level == RiskLevel.CRITICAL
        or risk_factors
        & {
            "emergency_mode",
            "identity_modification",
            "security_modification",
            "self_modification",
        }
        or capabilities & _CRITICAL_CAPABILITIES
        or action
        in {
            "hub.plugin_install",
            "plugin.install",
            "plugin.load",
            "plugin.uninstall",
            "self.apply_proposal",
        }
    ):
        return GuardianDecisionTier.CRITICAL

    if (
        risk.level == RiskLevel.HIGH
        or capabilities & _PRIVILEGED_CAPABILITIES
        or any(
            capability.startswith(prefix)
            for capability in capabilities
            for prefix in _PRIVILEGED_CAPABILITY_PREFIXES
        )
        or action.startswith(
            (
                "agent.",
                "executor.",
                "homeostasis.",
                "kernel.",
                "maintenance.",
                "memory.",
                "module_manager.",
                "network.",
                "plugin.",
                "script.",
                "service_registry.",
            )
        )
    ):
        return GuardianDecisionTier.PRIVILEGED

    if any(marker in action or marker in target for marker in _TELEMETRY_MARKERS):
        return GuardianDecisionTier.TELEMETRY_INTERNAL

    if action in _OBSERVATIONAL_ACTIONS or action.endswith(".status"):
        return GuardianDecisionTier.OBSERVATIONAL

    return GuardianDecisionTier.ROUTINE_GUARDED

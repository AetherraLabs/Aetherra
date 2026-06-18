"""Aetherra Guardian System public API."""

from __future__ import annotations

from .core import evaluate_intent, guardian_enabled, guardian_mode
from .models import (
    ApprovalRequest,
    ApprovalState,
    ApprovalValidationResult,
    CapabilityGrant,
    ContainmentAction,
    ContainmentResult,
    GuardianDecision,
    GuardianDecisionTier,
    GuardianMode,
    GuardianStatus,
    IntentDeclaration,
    PolicyResult,
    PreauthorizationGrant,
    PreauthorizationValidationResult,
    ReversibilityResult,
    RiskAssessment,
    RiskLevel,
)
from .policy import GuardianPolicy, load_guardian_policy
from .preauthorization import (
    consume_preauthorization,
    create_preauthorization,
    list_preauthorization_events,
    list_preauthorization_statuses,
    preauthorization_status,
    validate_preauthorization,
)
from .tiers import classify_decision_tier

__all__ = [
    "ApprovalRequest",
    "ApprovalState",
    "ApprovalValidationResult",
    "CapabilityGrant",
    "ContainmentAction",
    "ContainmentResult",
    "GuardianDecision",
    "GuardianDecisionTier",
    "GuardianMode",
    "GuardianPolicy",
    "GuardianStatus",
    "IntentDeclaration",
    "PolicyResult",
    "PreauthorizationGrant",
    "PreauthorizationValidationResult",
    "ReversibilityResult",
    "RiskAssessment",
    "RiskLevel",
    "evaluate_intent",
    "consume_preauthorization",
    "create_preauthorization",
    "classify_decision_tier",
    "guardian_enabled",
    "guardian_mode",
    "list_preauthorization_events",
    "list_preauthorization_statuses",
    "load_guardian_policy",
    "preauthorization_status",
    "validate_preauthorization",
]

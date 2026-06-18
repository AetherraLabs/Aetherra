"""Aetherra Guardian System public API."""

from __future__ import annotations

from .audit import guardian_audit_integrity_ok, list_guardian_audit_records
from .core import evaluate_intent, guardian_enabled, guardian_mode, record_outcome
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
from .mode import guardian_mode_events, guardian_mode_status, set_guardian_mode
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
    "guardian_audit_integrity_ok",
    "guardian_enabled",
    "guardian_mode",
    "guardian_mode_events",
    "guardian_mode_status",
    "list_guardian_audit_records",
    "list_preauthorization_events",
    "list_preauthorization_statuses",
    "load_guardian_policy",
    "preauthorization_status",
    "record_outcome",
    "set_guardian_mode",
    "validate_preauthorization",
]

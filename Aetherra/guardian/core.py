"""Core evaluator for the Aetherra Guardian System."""

from __future__ import annotations

import os

from .approval import consume_approval, create_approval_request
from .audit import append_guardian_decision
from .containment import find_active_containment, record_containment
from .models import (
    ContainmentAction,
    GuardianDecision,
    GuardianMode,
    GuardianStatus,
    IntentDeclaration,
    RiskLevel,
)
from .policy import CapabilityChecker, evaluate_capabilities, evaluate_guardian_policy
from .reversibility import validate_reversibility
from .risk import assess_risk
from .tiers import classify_decision_tier


def guardian_enabled() -> bool:
    """Return whether Guardian enforcement is enabled by configuration."""

    return (os.getenv("AETHERRA_GUARDIAN_ENABLED", "1") or "").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }


def guardian_mode() -> GuardianMode:
    """Return the configured Guardian operating mode."""

    raw = (os.getenv("AETHERRA_GUARDIAN_MODE", "enforcing") or "").strip().lower()
    try:
        return GuardianMode(raw)
    except ValueError:
        return GuardianMode.ENFORCING


def evaluate_intent(
    intent: IntentDeclaration,
    *,
    approval_id: str | None = None,
    capability_checker: CapabilityChecker | None = None,
    write_audit: bool = True,
) -> GuardianDecision:
    """Evaluate a declared intent and return the Guardian decision."""

    risk = assess_risk(intent)
    tier = classify_decision_tier(intent, risk)
    mode = guardian_mode()

    if not guardian_enabled():
        decision = GuardianDecision(
            status=GuardianStatus.ALLOW,
            risk_level=risk.level,
            reason="guardian_disabled",
            details=_decision_details(mode, risk, tier),
        )
        return _with_audit(intent, risk, decision, write_audit)

    active_containment = find_active_containment(intent)
    if active_containment is not None and intent.action not in {"inspect", "status", "recover"}:
        decision = GuardianDecision(
            status=GuardianStatus.CONTAIN,
            risk_level=RiskLevel.CRITICAL,
            reason="active_containment",
            containment_actions=(ContainmentAction.BLOCK_ACTION,),
            details={
                **_decision_details(mode, risk, tier),
                "containment_id": active_containment.get("containment_id"),
            },
        )
        return _with_audit(intent, risk, decision, write_audit)

    if mode == GuardianMode.EMERGENCY and intent.action not in {"inspect", "status", "recover"}:
        containment = record_containment(
            intent,
            ContainmentAction.BLOCK_ACTION,
            reason="guardian_emergency_mode",
        )
        decision = GuardianDecision(
            status=GuardianStatus.CONTAIN,
            risk_level=RiskLevel.CRITICAL,
            reason="guardian_emergency_mode",
            containment_actions=(ContainmentAction.BLOCK_ACTION,),
            details={
                **_decision_details(mode, risk, tier),
                "containment_id": containment.containment_id,
            },
        )
        return _with_audit(intent, risk, decision, write_audit)

    guardian_policy = evaluate_guardian_policy(intent)
    if not guardian_policy.allowed:
        decision = GuardianDecision(
            status=GuardianStatus.DENY,
            risk_level=risk.level,
            reason=guardian_policy.reason,
            details={
                **_decision_details(mode, risk, tier),
                "policy": guardian_policy.details,
            },
        )
        return _with_audit(intent, risk, decision, write_audit)

    policy = evaluate_capabilities(intent, capability_checker=capability_checker)
    if not policy.allowed:
        decision = GuardianDecision(
            status=GuardianStatus.DENY,
            risk_level=risk.level,
            reason=policy.reason,
            details={
                **_decision_details(mode, risk, tier),
                "missing_capabilities": policy.missing_capabilities,
            },
        )
        return _with_audit(intent, risk, decision, write_audit)

    reversibility = validate_reversibility(intent, risk)
    if not reversibility.valid and not risk.requires_containment:
        approved = consume_approval(approval_id, intent) if approval_id else None
        if approved and approved.valid:
            decision = GuardianDecision(
                status=GuardianStatus.ALLOW_LIMITED,
                risk_level=risk.level,
                reason="approved_with_guardian_approval",
                constraints=("guardian_approval_consumed", "rollback_missing_user_approved"),
                rollback_required=True,
                details={
                    **_decision_details(mode, risk, tier),
                    "approval_request_id": approved.request_id,
                    "approver": approved.approver,
                    "reversibility": {
                        "required": reversibility.required,
                        "valid": reversibility.valid,
                        "reason": reversibility.reason,
                    },
                },
            )
            return _with_audit(intent, risk, decision, write_audit)
        approval = create_approval_request(intent, risk)
        decision = GuardianDecision(
            status=GuardianStatus.REQUIRE_APPROVAL,
            risk_level=risk.level,
            reason=reversibility.reason,
            required_approvals=("user",),
            rollback_required=True,
            details={
                **_decision_details(mode, risk, tier),
                "approval_request_id": approval.request_id,
                "reversibility": {
                    "required": reversibility.required,
                    "valid": reversibility.valid,
                    "reason": reversibility.reason,
                },
            },
        )
        return _with_audit(intent, risk, decision, write_audit)

    if risk.requires_containment:
        containment = record_containment(
            intent,
            ContainmentAction.BLOCK_ACTION,
            reason="critical_risk_requires_containment",
        )
        decision = GuardianDecision(
            status=GuardianStatus.CONTAIN,
            risk_level=risk.level,
            reason="critical_risk_requires_containment",
            containment_actions=(ContainmentAction.BLOCK_ACTION,),
            rollback_required=True,
            details={
                **_decision_details(mode, risk, tier),
                "containment_id": containment.containment_id,
            },
        )
        return _with_audit(intent, risk, decision, write_audit)

    if risk.requires_approval and mode in {GuardianMode.ENFORCING, GuardianMode.STRICT}:
        approved = consume_approval(approval_id, intent) if approval_id else None
        if approved and approved.valid:
            decision = GuardianDecision(
                status=GuardianStatus.ALLOW_LIMITED,
                risk_level=risk.level,
                reason="approved_with_guardian_approval",
                constraints=("guardian_approval_consumed",),
                rollback_required=reversibility.required and not reversibility.valid,
                details={
                    **_decision_details(mode, risk, tier),
                    "approval_request_id": approved.request_id,
                    "approver": approved.approver,
                    "reversibility": {
                        "required": reversibility.required,
                        "valid": reversibility.valid,
                        "reason": reversibility.reason,
                    },
                },
            )
            return _with_audit(intent, risk, decision, write_audit)
        approval = create_approval_request(intent, risk)
        decision = GuardianDecision(
            status=GuardianStatus.REQUIRE_APPROVAL,
            risk_level=risk.level,
            reason="risk_requires_approval",
            required_approvals=("user",),
            rollback_required=reversibility.required and not reversibility.valid,
            details={
                **_decision_details(mode, risk, tier),
                "approval_request_id": approval.request_id,
                "reversibility": {
                    "required": reversibility.required,
                    "valid": reversibility.valid,
                    "reason": reversibility.reason,
                },
            },
        )
        return _with_audit(intent, risk, decision, write_audit)

    if risk.level == RiskLevel.MEDIUM:
        decision = GuardianDecision(
            status=GuardianStatus.ALLOW_LIMITED,
            risk_level=risk.level,
            reason="allowed_with_constraints",
            constraints=("respect_existing_security_controls",),
            rollback_required=reversibility.required and not reversibility.valid,
            details=_decision_details(mode, risk, tier),
        )
        return _with_audit(intent, risk, decision, write_audit)

    decision = GuardianDecision(
        status=GuardianStatus.ALLOW,
        risk_level=risk.level,
        reason="allowed",
        details=_decision_details(mode, risk, tier),
    )
    return _with_audit(intent, risk, decision, write_audit)


def _with_audit(
    intent: IntentDeclaration,
    risk,
    decision: GuardianDecision,
    write_audit: bool,
) -> GuardianDecision:
    if not write_audit:
        return decision
    audit_id = append_guardian_decision(intent, risk, decision)
    return decision.with_audit_id(audit_id)


def _decision_details(mode, risk, tier) -> dict:
    return {
        "mode": mode.value,
        "risk_score": risk.score,
        "risk_factors": risk.factors,
        "decision_tier": tier.value,
    }

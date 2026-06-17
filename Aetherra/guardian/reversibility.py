"""Reversibility checks for Guardian intents."""

from __future__ import annotations

from .models import IntentDeclaration, ReversibilityResult, RiskAssessment, RiskLevel

_MUTATING_FACTORS = {
    "write_action",
    "delete_action",
    "identity_modification",
    "security_modification",
    "self_modification",
}


def validate_reversibility(
    intent: IntentDeclaration,
    risk: RiskAssessment,
) -> ReversibilityResult:
    """Validate that risky meaningful actions provide rollback metadata."""

    required = risk.level in {RiskLevel.HIGH, RiskLevel.CRITICAL} or any(
        factor in risk.factors for factor in _MUTATING_FACTORS
    )
    if not required:
        return ReversibilityResult(valid=True, required=False, reason="not_required")

    if intent.reversible and (intent.rollback_plan or "").strip():
        return ReversibilityResult(
            valid=True,
            required=True,
            reason="rollback_available",
            rollback_plan=intent.rollback_plan,
        )

    return ReversibilityResult(
        valid=False,
        required=True,
        reason="rollback_required",
        rollback_plan=intent.rollback_plan,
        details={"reversible": intent.reversible},
    )

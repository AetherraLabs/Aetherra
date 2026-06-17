"""Guardian audit integration with the signed Security audit ledger."""

from __future__ import annotations

from .models import GuardianDecision, IntentDeclaration, RiskAssessment


def append_guardian_decision(
    intent: IntentDeclaration,
    risk: RiskAssessment,
    decision: GuardianDecision,
) -> str | None:
    """Append a Guardian decision to the central signed Security audit ledger."""

    from Aetherra.aetherra_core.system.security_system import append_security_audit_entry

    path = append_security_audit_entry(
        "guardian",
        "guardian_decision",
        reason=decision.reason,
        details={
            "intent": intent.to_audit_dict(),
            "risk": {
                "level": risk.level.value,
                "score": risk.score,
                "factors": list(risk.factors),
            },
            "decision": decision.to_audit_dict(),
        },
    )
    return str(path) if path is not None else None

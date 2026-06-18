"""Guardian audit integration with the signed Security audit ledger."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .models import GuardianDecision, IntentDeclaration, RiskAssessment
from .paths import workspace_root

_MAX_TEXT_LENGTH = 240
_MAX_METRIC_FIELDS = 25
_MAX_OMITTED_FIELDS = 50
_MAX_AUDIT_RECORD_LIMIT = 200
GUARDIAN_AUDIT_EVENT_TYPES = frozenset(
    {
        "guardian_decision",
        "guardian_mode_changed",
        "guardian_outcome",
    }
)
_OUTCOME_SCALAR_FIELDS = {
    "status",
    "summary",
    "reason",
    "error_type",
    "duration_ms",
    "affected_count",
    "rollback_performed",
    "containment_action",
}


def guardian_audit_integrity_ok() -> bool:
    """Return whether the signed Security audit ledger verifies successfully."""

    from Aetherra.security.audit_ledger import SecurityAuditLedger

    return SecurityAuditLedger(_security_audit_path()).verify_integrity()


def list_guardian_audit_records(
    *,
    limit: int = 50,
    event_type: str | None = None,
) -> list[dict[str, Any]]:
    """Return recent Guardian audit records from the signed Security ledger.

    The ledger is append-only and may contain unrelated Security records, so the
    read model is intentionally narrow: Guardian actor, known Guardian event
    types, bounded result size, and no mutation.
    """

    if not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    bounded_limit = max(1, min(limit, _MAX_AUDIT_RECORD_LIMIT))

    normalized_event_type = event_type.strip() if isinstance(event_type, str) else None
    if normalized_event_type and normalized_event_type not in GUARDIAN_AUDIT_EVENT_TYPES:
        raise ValueError(f"unsupported Guardian audit event type: {normalized_event_type}")

    audit_path = _security_audit_path()
    if not audit_path.exists():
        return []

    records: list[dict[str, Any]] = []
    with audit_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                continue
            if record.get("actor") != "guardian":
                continue
            record_type = record.get("event_type")
            if record_type not in GUARDIAN_AUDIT_EVENT_TYPES:
                continue
            if normalized_event_type and record_type != normalized_event_type:
                continue
            records.append(record)

    return records[-bounded_limit:]


def append_guardian_decision(
    intent: IntentDeclaration,
    risk: RiskAssessment,
    decision: GuardianDecision,
) -> str | None:
    """Append a Guardian decision to the central signed Security audit ledger."""

    return _append_guardian_event(
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


def record_guardian_outcome(audit_id: str, outcome: Mapping[str, Any]) -> str | None:
    """Append a bounded post-action outcome linked to a Guardian decision record."""

    if not isinstance(audit_id, str) or not audit_id.strip():
        raise ValueError("audit_id must be a non-empty string")
    if not isinstance(outcome, Mapping):
        raise TypeError("outcome must be a mapping")

    sanitized = _sanitize_outcome(outcome)
    return _append_guardian_event(
        "guardian_outcome",
        reason=str(sanitized.get("status") or "outcome_recorded"),
        details={
            "decision_audit_id": audit_id.strip(),
            "outcome": sanitized,
        },
    )


def append_guardian_mode_change(record: Mapping[str, Any]) -> str | None:
    """Append a Guardian operating-mode change to the signed Security audit ledger."""

    new_mode = str(record.get("mode") or "unknown")
    return _append_guardian_event(
        "guardian_mode_changed",
        reason=str(record.get("reason") or "mode_changed"),
        details={
            "previous_mode": record.get("previous_mode"),
            "mode": new_mode,
            "changed_by": record.get("changed_by"),
            "changed_at": record.get("changed_at"),
            "env_override_active": record.get("env_override_active"),
            "metadata": record.get("metadata") or {},
        },
    )


def _append_guardian_event(
    event_type: str,
    *,
    reason: str | None,
    details: Mapping[str, Any],
) -> str | None:
    from Aetherra.aetherra_core.system.security_system import redact_secrets
    from Aetherra.security.audit_ledger import AuditLedgerError, SecurityAuditLedger

    audit_path = _security_audit_path()
    audit_details = dict(details)
    if event_type != "guardian_outcome":
        audit_details = redact_secrets(audit_details)
    try:
        record = SecurityAuditLedger(audit_path).append(
            actor="guardian",
            event_type=event_type,
            reason=reason,
            details=audit_details,
        )
    except (AuditLedgerError, OSError, TypeError, ValueError):
        return None
    record_hash = record.get("hash")
    return record_hash if isinstance(record_hash, str) else None


def _security_audit_path() -> Path:
    return workspace_root() / ".aetherra" / "security" / "audit.jsonl"


def _sanitize_outcome(outcome: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {"field_count": len(outcome)}

    for field_name in sorted(_OUTCOME_SCALAR_FIELDS):
        if field_name in outcome:
            sanitized[field_name] = _sanitize_scalar(outcome[field_name])

    metrics = outcome.get("metrics")
    if isinstance(metrics, Mapping):
        sanitized["metrics"] = {
            str(key)[:_MAX_TEXT_LENGTH]: _sanitize_metric_value(value)
            for key, value in list(metrics.items())[:_MAX_METRIC_FIELDS]
        }
        if len(metrics) > _MAX_METRIC_FIELDS:
            sanitized["metrics_truncated"] = True

    omitted = sorted(
        str(key)
        for key in outcome
        if key not in _OUTCOME_SCALAR_FIELDS and key != "metrics"
    )
    if omitted:
        sanitized["omitted_fields"] = omitted[:_MAX_OMITTED_FIELDS]
        if len(omitted) > _MAX_OMITTED_FIELDS:
            sanitized["omitted_fields_truncated"] = True

    if "status" not in sanitized:
        sanitized["status"] = "unspecified"
    return sanitized


def _sanitize_scalar(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, str):
        return value[:_MAX_TEXT_LENGTH]
    return {"type": type(value).__name__}


def _sanitize_metric_value(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, str):
        encoded = value.encode("utf-8", errors="replace")
        return {
            "type": "str",
            "length": len(value),
            "sha256": hashlib.sha256(encoded).hexdigest(),
        }
    return {"type": type(value).__name__}

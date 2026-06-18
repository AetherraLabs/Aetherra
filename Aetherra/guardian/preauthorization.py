"""Scoped preauthorization grants for low-risk Guardian decisions."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from typing import Any

from .approval import intent_fingerprint
from .models import (
    GuardianDecisionTier,
    GuardianMode,
    IntentDeclaration,
    PreauthorizationGrant,
    PreauthorizationValidationResult,
    RiskAssessment,
    RiskLevel,
)
from .paths import guardian_state_dir
from .policy import load_guardian_policy
from .state import append_jsonl, read_jsonl


def _preauthorization_log_path():
    return guardian_state_dir() / "preauthorizations.jsonl"


def create_preauthorization(
    intent: IntentDeclaration,
    risk: RiskAssessment,
    *,
    decision_tier: GuardianDecisionTier,
    guardian_mode: GuardianMode,
    max_uses: int = 1,
    ttl_seconds: int | None = None,
    granted_by: str = "guardian",
    audit_required: bool = True,
    metadata: dict[str, Any] | None = None,
) -> PreauthorizationGrant:
    """Create a short-lived grant for one exact routine guarded intent scope."""

    _validate_preauthorizable(intent, risk, decision_tier)
    now = datetime.now(UTC)
    ttl = _preauthorization_ttl_seconds() if ttl_seconds is None else ttl_seconds
    grant = PreauthorizationGrant(
        grant_id=f"pag_{secrets.token_hex(12)}",
        requester=intent.requester,
        subsystem=intent.subsystem,
        action=intent.action,
        target=intent.target,
        capabilities=tuple(intent.capabilities),
        intent_fingerprint=intent_fingerprint(intent),
        decision_tier=decision_tier,
        guardian_mode=guardian_mode,
        policy_fingerprint=guardian_policy_fingerprint(),
        max_uses=max(1, int(max_uses)),
        created_at=now.isoformat().replace("+00:00", "Z"),
        expires_at=(now + timedelta(seconds=max(1, int(ttl))))
        .isoformat()
        .replace("+00:00", "Z"),
        granted_by=granted_by,
        audit_required=audit_required,
        metadata=metadata or {},
    )
    append_jsonl(_preauthorization_log_path(), {"event": "created", **grant.to_record()})
    return grant


def validate_preauthorization(
    grant_id: str | None,
    intent: IntentDeclaration,
    risk: RiskAssessment,
    *,
    decision_tier: GuardianDecisionTier,
    guardian_mode: GuardianMode,
) -> PreauthorizationValidationResult:
    """Validate that a grant can authorize this exact low-risk routine intent."""

    if not grant_id:
        return PreauthorizationValidationResult(False, "preauthorization_id_required")

    events = list_preauthorization_events()
    created = next(
        (
            event
            for event in events
            if event.get("event") == "created" and event.get("grant_id") == grant_id
        ),
        None,
    )
    if created is None:
        return PreauthorizationValidationResult(
            False,
            "preauthorization_not_found",
            grant_id,
        )

    if _is_expired(created):
        return PreauthorizationValidationResult(False, "preauthorization_expired", grant_id)

    used = sum(
        1
        for event in events
        if event.get("event") == "used" and event.get("grant_id") == grant_id
    )
    max_uses = _int_field(created.get("max_uses"), default=1)
    if used >= max_uses:
        return PreauthorizationValidationResult(False, "preauthorization_exhausted", grant_id)

    if decision_tier != GuardianDecisionTier.ROUTINE_GUARDED or risk.level != RiskLevel.LOW:
        return PreauthorizationValidationResult(
            False,
            "preauthorization_tier_or_risk_not_allowed",
            grant_id,
            {"decision_tier": decision_tier.value, "risk_level": risk.level.value},
        )

    expected_fingerprint = created.get("intent_fingerprint")
    actual_fingerprint = intent_fingerprint(intent)
    if expected_fingerprint != actual_fingerprint:
        return PreauthorizationValidationResult(
            False,
            "preauthorization_intent_mismatch",
            grant_id,
        )

    if created.get("guardian_mode") != guardian_mode.value:
        return PreauthorizationValidationResult(False, "preauthorization_mode_changed", grant_id)

    if created.get("policy_fingerprint") != guardian_policy_fingerprint():
        return PreauthorizationValidationResult(
            False,
            "preauthorization_policy_changed",
            grant_id,
        )

    return PreauthorizationValidationResult(
        True,
        "preauthorization_valid",
        grant_id,
        {"uses_remaining": max_uses - used},
    )


def consume_preauthorization(
    grant_id: str,
    intent: IntentDeclaration,
    risk: RiskAssessment,
    *,
    decision_tier: GuardianDecisionTier,
    guardian_mode: GuardianMode,
) -> PreauthorizationValidationResult:
    """Validate and record one use of a matching preauthorization grant."""

    result = validate_preauthorization(
        grant_id,
        intent,
        risk,
        decision_tier=decision_tier,
        guardian_mode=guardian_mode,
    )
    if not result.valid:
        return result
    append_jsonl(
        _preauthorization_log_path(),
        {
            "event": "used",
            "grant_id": grant_id,
            "intent_fingerprint": intent_fingerprint(intent),
            "used_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        },
    )
    return result


def list_preauthorization_events() -> list[dict[str, Any]]:
    return read_jsonl(_preauthorization_log_path())


def preauthorization_status(grant_id: str) -> dict[str, Any]:
    """Return a summarized status for one preauthorization grant."""

    events = list_preauthorization_events()
    created = next(
        (
            event
            for event in events
            if event.get("event") == "created" and event.get("grant_id") == grant_id
        ),
        None,
    )
    if created is None:
        return {"grant_id": grant_id, "state": "not_found"}
    uses = sum(
        1
        for event in events
        if event.get("event") == "used" and event.get("grant_id") == grant_id
    )
    max_uses = _int_field(created.get("max_uses"), default=1)
    if _is_expired(created):
        state = "expired"
    elif uses >= max_uses:
        state = "exhausted"
    else:
        state = "active"
    return {**created, "state": state, "uses": uses, "uses_remaining": max(0, max_uses - uses)}


def list_preauthorization_statuses() -> list[dict[str, Any]]:
    """Return one summarized status per preauthorization grant."""

    grant_ids = [
        event["grant_id"]
        for event in list_preauthorization_events()
        if event.get("event") == "created" and event.get("grant_id")
    ]
    return [preauthorization_status(grant_id) for grant_id in grant_ids]


def guardian_policy_fingerprint() -> str:
    """Return a stable fingerprint for the active Guardian policy document."""

    try:
        policy = load_guardian_policy()
        payload = asdict(policy)
    except Exception as exc:
        payload = {"error_type": type(exc).__name__, "error": str(exc)}
    encoded = json.dumps(
        payload,
        default=str,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_preauthorizable(
    intent: IntentDeclaration,
    risk: RiskAssessment,
    decision_tier: GuardianDecisionTier,
) -> None:
    if decision_tier != GuardianDecisionTier.ROUTINE_GUARDED:
        raise ValueError("preauthorization is only valid for routine_guarded intents")
    if risk.level != RiskLevel.LOW:
        raise ValueError("preauthorization is only valid for low-risk intents")
    if not intent.reversible or not intent.rollback_plan:
        raise ValueError("preauthorization requires a reversible intent with rollback metadata")


def _preauthorization_ttl_seconds() -> int:
    raw = os.getenv("AETHERRA_GUARDIAN_PREAUTH_TIMEOUT_SEC", "60")
    return _int_field(raw, default=60, minimum=1)


def _int_field(value: Any, *, default: int, minimum: int | None = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    if minimum is not None:
        return max(minimum, parsed)
    return parsed


def _is_expired(record: dict[str, Any]) -> bool:
    expires_at = record.get("expires_at")
    if not isinstance(expires_at, str) or not expires_at:
        return False
    try:
        parsed = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    return datetime.now(UTC) > parsed

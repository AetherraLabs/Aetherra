"""Approval request persistence for Guardian."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import UTC, datetime, timedelta

from .models import ApprovalRequest, ApprovalValidationResult, IntentDeclaration, RiskAssessment
from .paths import guardian_state_dir
from .state import append_jsonl, read_jsonl


def _approval_log_path():
    return guardian_state_dir() / "approvals.jsonl"


def create_approval_request(
    intent: IntentDeclaration,
    risk: RiskAssessment,
    *,
    required_approvers: tuple[str, ...] = ("user",),
) -> ApprovalRequest:
    """Persist and return a pending approval request."""

    created_at = datetime.now(UTC)
    expires_at = created_at + timedelta(seconds=_approval_timeout_seconds())
    request = ApprovalRequest(
        request_id=f"apr_{secrets.token_hex(12)}",
        intent=intent,
        risk=risk,
        created_at=created_at.isoformat().replace("+00:00", "Z"),
        expires_at=expires_at.isoformat().replace("+00:00", "Z"),
        required_approvers=required_approvers,
    )
    append_jsonl(_approval_log_path(), {"event": "created", **request.to_record()})
    return request


def intent_fingerprint(intent: IntentDeclaration) -> str:
    """Return a stable fingerprint binding approvals to one intent."""

    encoded = json.dumps(
        intent.to_audit_dict(),
        default=str,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def resolve_approval(request_id: str, *, approved: bool, approver: str) -> dict:
    """Append an approval resolution event."""

    current = get_approval_request(request_id)
    if current is None:
        return {
            "event": "resolve_failed",
            "request_id": request_id,
            "state": "not_found",
            "approver": approver,
            "resolved_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
    if _is_expired(current):
        return {
            "event": "resolve_failed",
            "request_id": request_id,
            "state": "expired",
            "approver": approver,
            "resolved_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }

    status = "approved" if approved else "denied"
    record = {
        "event": "resolved",
        "request_id": request_id,
        "state": status,
        "approver": approver,
        "resolved_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    append_jsonl(_approval_log_path(), record)
    return record


def get_approval_request(request_id: str | None) -> dict | None:
    """Return the creation record for an approval request."""

    if not request_id:
        return None
    return next(
        (
            event
            for event in list_approval_events()
            if event.get("event") == "created" and event.get("request_id") == request_id
        ),
        None,
    )


def validate_approval(request_id: str | None, intent: IntentDeclaration) -> ApprovalValidationResult:
    """Validate that an approval exists, is approved, unused, and matches intent."""

    if not request_id:
        return ApprovalValidationResult(valid=False, reason="approval_id_required")

    events = list_approval_events()
    created = next(
        (
            event
            for event in events
            if event.get("event") == "created" and event.get("request_id") == request_id
        ),
        None,
    )
    if created is None:
        return ApprovalValidationResult(
            valid=False,
            reason="approval_not_found",
            request_id=request_id,
        )
    if _is_expired(created):
        return ApprovalValidationResult(
            valid=False,
            reason="approval_expired",
            request_id=request_id,
        )

    created_intent = created.get("intent")
    if not isinstance(created_intent, dict):
        return ApprovalValidationResult(
            valid=False,
            reason="approval_record_invalid",
            request_id=request_id,
        )
    expected = _fingerprint_dict(created_intent)
    actual = intent_fingerprint(intent)
    if expected != actual:
        return ApprovalValidationResult(
            valid=False,
            reason="approval_intent_mismatch",
            request_id=request_id,
        )

    consumed = any(
        event.get("event") == "consumed" and event.get("request_id") == request_id
        for event in events
    )
    if consumed:
        return ApprovalValidationResult(
            valid=False,
            reason="approval_already_consumed",
            request_id=request_id,
        )

    resolutions = [
        event
        for event in events
        if event.get("event") == "resolved" and event.get("request_id") == request_id
    ]
    if not resolutions:
        return ApprovalValidationResult(
            valid=False,
            reason="approval_pending",
            request_id=request_id,
        )
    latest = resolutions[-1]
    if latest.get("state") != "approved":
        return ApprovalValidationResult(
            valid=False,
            reason="approval_denied",
            request_id=request_id,
            approver=latest.get("approver"),
        )

    return ApprovalValidationResult(
        valid=True,
        reason="approval_valid",
        request_id=request_id,
        approver=latest.get("approver"),
    )


def consume_approval(request_id: str, intent: IntentDeclaration) -> ApprovalValidationResult:
    """Validate and consume one approval for one matching intent."""

    result = validate_approval(request_id, intent)
    if not result.valid:
        return result
    record = {
        "event": "consumed",
        "request_id": request_id,
        "intent_fingerprint": intent_fingerprint(intent),
        "consumed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    append_jsonl(_approval_log_path(), record)
    return result


def list_approval_events() -> list[dict]:
    return read_jsonl(_approval_log_path())


def approval_status(request_id: str) -> dict:
    """Summarize the current status for one approval request."""

    created = get_approval_request(request_id)
    if created is None:
        return {"request_id": request_id, "state": "not_found"}
    events = [
        event for event in list_approval_events() if event.get("request_id") == request_id
    ]
    if any(event.get("event") == "consumed" for event in events):
        return {**created, "state": "consumed"}
    if _is_expired(created):
        return {**created, "state": "expired"}
    resolutions = [event for event in events if event.get("event") == "resolved"]
    if resolutions:
        return {**created, "state": resolutions[-1].get("state")}
    return {**created, "state": "pending_user"}


def list_approval_statuses() -> list[dict]:
    """Return one summarized status per approval request."""

    request_ids = [
        event["request_id"]
        for event in list_approval_events()
        if event.get("event") == "created" and event.get("request_id")
    ]
    return [approval_status(request_id) for request_id in request_ids]


def _fingerprint_dict(intent_data: dict) -> str:
    encoded = json.dumps(
        intent_data,
        default=str,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _approval_timeout_seconds() -> int:
    raw = os.getenv("AETHERRA_GUARDIAN_APPROVAL_TIMEOUT_SEC", "900")
    try:
        value = int(raw)
    except ValueError:
        value = 900
    return max(1, value)


def _is_expired(record: dict) -> bool:
    expires_at = record.get("expires_at")
    if not isinstance(expires_at, str) or not expires_at:
        return False
    try:
        parsed = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    return datetime.now(UTC) > parsed

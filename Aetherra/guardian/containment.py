"""Containment event persistence for Guardian."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from typing import Any

from .models import ContainmentAction, ContainmentResult, IntentDeclaration
from .paths import guardian_state_dir
from .state import append_jsonl, read_jsonl


def _containment_log_path():
    return guardian_state_dir() / "containment.jsonl"


def record_containment(
    intent: IntentDeclaration,
    action: ContainmentAction,
    *,
    reason: str,
) -> ContainmentResult:
    """Persist and return a containment event."""

    result = ContainmentResult(
        containment_id=f"cnt_{secrets.token_hex(12)}",
        action=action,
        intent=intent,
        reason=reason,
    )
    append_jsonl(_containment_log_path(), {"event": "created", **result.to_record()})
    return result


def list_containment_events() -> list[dict]:
    return read_jsonl(_containment_log_path())


def clear_containment(containment_id: str, *, cleared_by: str, reason: str) -> dict:
    """Clear an active containment record."""

    current = containment_status(containment_id)
    if current.get("state") == "not_found":
        return {
            "event": "clear_failed",
            "containment_id": containment_id,
            "state": "not_found",
            "cleared_by": cleared_by,
            "reason": reason,
            "cleared_at": _now(),
        }
    if current.get("state") == "cleared":
        return {
            "event": "clear_failed",
            "containment_id": containment_id,
            "state": "already_cleared",
            "cleared_by": cleared_by,
            "reason": reason,
            "cleared_at": _now(),
        }
    record = {
        "event": "cleared",
        "containment_id": containment_id,
        "state": "cleared",
        "cleared_by": cleared_by,
        "reason": reason,
        "cleared_at": _now(),
    }
    append_jsonl(_containment_log_path(), record)
    return record


def containment_status(containment_id: str) -> dict[str, Any]:
    """Return one containment status summary."""

    events = [
        event
        for event in list_containment_events()
        if event.get("containment_id") == containment_id
    ]
    created = next((event for event in events if event.get("event") == "created"), None)
    if created is None:
        return {"containment_id": containment_id, "state": "not_found"}
    if any(event.get("event") == "cleared" for event in events):
        return {**created, "state": "cleared"}
    return {**created, "state": "active"}


def list_containment_statuses() -> list[dict[str, Any]]:
    """Return one summarized status per containment record."""

    ids = [
        event["containment_id"]
        for event in list_containment_events()
        if event.get("event") == "created" and event.get("containment_id")
    ]
    return [containment_status(containment_id) for containment_id in ids]


def find_active_containment(intent: IntentDeclaration) -> dict[str, Any] | None:
    """Return the first active containment record matching an intent."""

    for status in active_containments_for_intent(intent):
        return status
    return None


def active_containments_for_intent(intent: IntentDeclaration) -> list[dict[str, Any]]:
    """Return every active containment record matching an intent."""

    matches: list[dict[str, Any]] = []
    for status in list_containment_statuses():
        if status.get("state") != "active":
            continue
        contained_intent = status.get("intent")
        if isinstance(contained_intent, dict) and _intent_matches(contained_intent, intent):
            matches.append(status)
    return matches


def _intent_matches(contained: dict[str, Any], intent: IntentDeclaration) -> bool:
    requester = str(contained.get("requester") or "")
    subsystem = str(contained.get("subsystem") or "")
    target = str(contained.get("target") or "")
    return any(
        (
            requester and requester == intent.requester,
            subsystem
            and subsystem == intent.subsystem
            and (not target or target == "*" or target == intent.target),
            target and target == intent.target,
        )
    )


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")

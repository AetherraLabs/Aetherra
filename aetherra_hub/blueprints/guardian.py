"""Guardian administrative API endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from Aetherra.guardian.audit import (
    GUARDIAN_AUDIT_EVENT_TYPES,
    guardian_audit_integrity_ok,
    list_guardian_audit_records,
)
from Aetherra.guardian.approval import (
    approval_status,
    list_approval_statuses,
    resolve_approval,
)
from Aetherra.guardian.containment import (
    clear_containment,
    containment_status,
    list_containment_statuses,
)
from Aetherra.guardian.core import guardian_enabled, guardian_mode
from Aetherra.guardian.mode import (
    guardian_mode_events,
    guardian_mode_status,
    set_guardian_mode,
)
from Aetherra.guardian.preauthorization import (
    list_preauthorization_statuses,
    preauthorization_status,
)

from ..services.control_auth import authorize_control_request

bp = Blueprint("guardian", __name__, url_prefix="/api/guardian")


def _authorize_control() -> ResponseReturnValue | None:
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"ok": False, "error": decision.error}), decision.status_code


@bp.get("/status")
def guardian_status() -> ResponseReturnValue:
    """Return a read-only Guardian operations summary."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error

    approvals = list_approval_statuses()
    containment = list_containment_statuses()
    preauthorizations = list_preauthorization_statuses()
    pending_approvals = [
        approval for approval in approvals if approval.get("state") == "pending_user"
    ]
    active_containment = [
        record for record in containment if record.get("state") == "active"
    ]
    active_preauthorizations = [
        grant for grant in preauthorizations if grant.get("state") == "active"
    ]
    return jsonify(
        {
            "ok": True,
            "guardian": {
                "enabled": guardian_enabled(),
                "mode": guardian_mode().value,
                "mode_state": guardian_mode_status().get("state"),
                "approvals": {
                    "total": len(approvals),
                    "pending": len(pending_approvals),
                },
                "containment": {
                    "total": len(containment),
                    "active": len(active_containment),
                },
                "preauthorizations": {
                    "total": len(preauthorizations),
                    "active": len(active_preauthorizations),
                },
                "audit": {
                    "integrity_ok": guardian_audit_integrity_ok(),
                },
            },
        }
    )


@bp.get("/mode")
def get_guardian_mode() -> ResponseReturnValue:
    """Return Guardian operating-mode state and bounded history."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    try:
        limit = int(request.args.get("limit", "25"))
    except ValueError:
        return jsonify({"ok": False, "error": "limit must be an integer"}), 400
    limit = max(1, min(limit, 100))
    events = guardian_mode_events()
    return jsonify(
        {
            "ok": True,
            "mode": guardian_mode_status(),
            "events": events[-limit:],
            "total": len(events),
        }
    )


@bp.get("/audit")
def list_guardian_audit() -> ResponseReturnValue:
    """Return bounded Guardian audit records from the signed Security ledger."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error

    try:
        limit = int(request.args.get("limit", "50"))
    except ValueError:
        return jsonify({"ok": False, "error": "limit must be an integer"}), 400

    event_type = request.args.get("event_type")
    if event_type is not None:
        event_type = event_type.strip()
    if event_type and event_type not in GUARDIAN_AUDIT_EVENT_TYPES:
        return jsonify({"ok": False, "error": "unsupported event_type"}), 400

    records = list_guardian_audit_records(limit=limit, event_type=event_type)
    return jsonify(
        {
            "ok": True,
            "audit": {
                "integrity_ok": guardian_audit_integrity_ok(),
                "records": records,
                "total_returned": len(records),
            },
        }
    )


@bp.post("/mode")
def change_guardian_mode() -> ResponseReturnValue:
    """Persist a Guardian operating-mode change."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    payload = request.get_json(silent=True) or {}
    mode = str(payload.get("mode") or "").strip().lower()
    reason = str(payload.get("reason") or "").strip()
    if not mode:
        return jsonify({"ok": False, "error": "mode required"}), 400
    if not reason:
        return jsonify({"ok": False, "error": "reason required"}), 400
    changed_by = (
        request.headers.get("X-Aetherra-Principal")
        or payload.get("changed_by")
        or "user"
    )
    try:
        result = set_guardian_mode(mode, reason=reason, changed_by=str(changed_by))
    except ValueError:
        return jsonify({"ok": False, "error": "invalid_guardian_mode"}), 400
    return jsonify({"ok": True, "mode": result})


@bp.get("/approvals")
def list_approvals() -> ResponseReturnValue:
    """List Guardian approval requests with summarized state."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    approvals = list_approval_statuses()
    return jsonify({"ok": True, "approvals": approvals, "total": len(approvals)})


@bp.get("/approvals/<request_id>")
def get_approval(request_id: str) -> ResponseReturnValue:
    """Return one Guardian approval request summary."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    status = approval_status(request_id)
    code = 404 if status.get("state") == "not_found" else 200
    return jsonify({"ok": code == 200, "approval": status}), code


@bp.post("/approvals/<request_id>/resolve")
def resolve_approval_request(request_id: str) -> ResponseReturnValue:
    """Approve or deny a pending Guardian approval request."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    payload = request.get_json(silent=True) or {}
    approved = payload.get("approved")
    if not isinstance(approved, bool):
        return jsonify({"ok": False, "error": "approved boolean required"}), 400
    approver = (
        request.headers.get("X-Aetherra-Principal")
        or payload.get("approver")
        or "user"
    )
    result = resolve_approval(request_id, approved=approved, approver=str(approver))
    if result.get("event") == "resolve_failed":
        state = result.get("state")
        code = 404 if state == "not_found" else 409
        return jsonify({"ok": False, "approval": result, "error": state}), code
    return jsonify({"ok": True, "approval": result})


@bp.get("/containment")
def list_containment() -> ResponseReturnValue:
    """List Guardian containment records with summarized state."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    records = list_containment_statuses()
    return jsonify({"ok": True, "containment": records, "total": len(records)})


@bp.get("/containment/<containment_id>")
def get_containment(containment_id: str) -> ResponseReturnValue:
    """Return one Guardian containment status summary."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    status = containment_status(containment_id)
    code = 404 if status.get("state") == "not_found" else 200
    return jsonify({"ok": code == 200, "containment": status}), code


@bp.post("/containment/<containment_id>/clear")
def clear_containment_record(containment_id: str) -> ResponseReturnValue:
    """Clear an active Guardian containment record."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    payload = request.get_json(silent=True) or {}
    reason = str(payload.get("reason") or "").strip()
    if not reason:
        return jsonify({"ok": False, "error": "reason required"}), 400
    cleared_by = (
        request.headers.get("X-Aetherra-Principal")
        or payload.get("cleared_by")
        or "user"
    )
    result = clear_containment(
        containment_id,
        cleared_by=str(cleared_by),
        reason=reason,
    )
    if result.get("event") == "clear_failed":
        state = result.get("state")
        code = 404 if state == "not_found" else 409
        return jsonify({"ok": False, "containment": result, "error": state}), code
    return jsonify({"ok": True, "containment": result})


@bp.get("/preauthorizations")
def list_preauthorizations() -> ResponseReturnValue:
    """List Guardian preauthorization grants with summarized state."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    grants = list_preauthorization_statuses()
    return jsonify({"ok": True, "preauthorizations": grants, "total": len(grants)})


@bp.get("/preauthorizations/<grant_id>")
def get_preauthorization(grant_id: str) -> ResponseReturnValue:
    """Return one Guardian preauthorization grant summary."""

    auth_error = _authorize_control()
    if auth_error is not None:
        return auth_error
    status = preauthorization_status(grant_id)
    code = 404 if status.get("state") == "not_found" else 200
    return jsonify({"ok": code == 200, "preauthorization": status}), code

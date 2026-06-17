"""Guardian administrative API endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

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
    pending_approvals = [
        approval for approval in approvals if approval.get("state") == "pending_user"
    ]
    active_containment = [
        record for record in containment if record.get("state") == "active"
    ]
    return jsonify(
        {
            "ok": True,
            "guardian": {
                "enabled": guardian_enabled(),
                "mode": guardian_mode().value,
                "approvals": {
                    "total": len(approvals),
                    "pending": len(pending_approvals),
                },
                "containment": {
                    "total": len(containment),
                    "active": len(active_containment),
                },
            },
        }
    )


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

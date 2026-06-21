"""Read-only Coding System status API."""

from __future__ import annotations

from flask import Blueprint, jsonify

from Aetherra.coding import build_coding_status_payload

from ..services.state import hub_state

bp = Blueprint("coding", __name__)


@bp.get("/api/coding/status")
def coding_status():
    """Return Coding System readiness without applying code changes."""

    hub_state.incr_requests()
    response = jsonify(build_coding_status_payload())
    response.headers["Cache-Control"] = "no-store"
    return response

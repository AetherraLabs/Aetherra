"""Module Manager (KLM) status + metrics."""

from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify

# Local imports
from ..services import registry_client
from ..services.state import hub_state

bp = Blueprint("klm", __name__, url_prefix="/api/klm")


@bp.get("/status")
def klm_status():
    hub_state.incr_requests()
    st = registry_client.get_klm_status() or {"enabled": False}
    return jsonify(st)


@bp.get("/metrics")
def klm_metrics():
    hub_state.incr_requests()
    mt = registry_client.get_klm_metrics() or {}
    return jsonify(mt)

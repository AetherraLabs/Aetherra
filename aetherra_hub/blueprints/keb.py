"""Event Bus (KEB) status + metrics."""

from __future__ import annotations

from flask import Blueprint, jsonify

from ..services import registry_client
from ..services.state import hub_state

bp = Blueprint("keb", __name__, url_prefix="/api/keb")


@bp.get("/status")
def keb_status():
    hub_state.incr_requests()
    st = registry_client.get_keb_status() or {"enabled": False}
    return jsonify(st)


@bp.get("/metrics")
def keb_metrics():
    hub_state.incr_requests()
    mt = registry_client.get_keb_metrics() or {}
    return jsonify(mt)

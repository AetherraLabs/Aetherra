"""Kernel status + metrics endpoints."""

from __future__ import annotations

# Standard library imports
from datetime import datetime

# Third party imports
from flask import Blueprint, jsonify

# Local imports
from ..services import registry_client
from ..services.state import hub_state

bp = Blueprint("kernel", __name__, url_prefix="/api/kernel")


@bp.get("/status")
def kernel_status():
    hub_state.incr_requests()
    ks = registry_client.get_kernel_status() or {"running": False}
    return jsonify(ks)


@bp.get("/metrics")
def kernel_metrics():
    hub_state.incr_requests()
    ks = registry_client.get_kernel_status() or {"running": False}
    hmr = registry_client.get_hmr_config_metrics() or {}
    payload = {"hub_ts": datetime.now().isoformat(), "kernel": ks}
    if hmr:
        payload["hmr"] = hmr
    return jsonify(payload)

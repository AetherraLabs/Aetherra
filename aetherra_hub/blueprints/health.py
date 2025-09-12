"""Health endpoints: /health and /status.

Low-risk extraction from monolith. Uses shared hub_state.
"""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify

from ..services.state import hub_state

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    hub_state.incr_requests()
    return jsonify(
        {
            "status": "healthy",
            "uptime_seconds": (datetime.now() - hub_state.startup_time).total_seconds(),
            "plugins_registered": hub_state.plugins_total(),
            "requests_served": hub_state.requests_served,
        }
    )


@bp.get("/status")
def status():
    hub_state.incr_requests()
    return jsonify(
        {
            "status": "online",
            "running": True,
            "uptime_seconds": (datetime.now() - hub_state.startup_time).total_seconds(),
            "plugins_registered": hub_state.plugins_total(),
            "requests_served": hub_state.requests_served,
            "hub_connected": True,
            "services": ["hub_server", "plugin_registry"],
            "capabilities": ["plugin_registration", "plugin_discovery", "marketplace"],
        }
    )

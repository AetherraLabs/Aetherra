"""Health endpoints: /health and /status.

Low-risk extraction from monolith. Uses shared hub_state.
"""

from __future__ import annotations

# Standard library imports
from datetime import datetime

# Third party imports
from flask import Blueprint, jsonify

# Local imports
from ..services.state import hub_state

# Aetherra imports
try:
    from aetherra_service_registry import get_service_registry
except ImportError:
    get_service_registry = None

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
            "homeostasis": {
                "enabled": True,
                "endpoint": "/homeostasis",
                "description": "Autonomous system stability control",
            },
        }
    )


@bp.get("/homeostasis")
def homeostasis_health():
    """Get homeostasis system health information."""
    hub_state.incr_requests()

    # Return basic homeostasis status - detailed integration would require async context
    return jsonify(
        {
            "status": "available",
            "description": "Aetherra Homeostasis System - Autonomous Stability Control",
            "features": [
                "stability_metrics_collection",
                "pid_control_loops",
                "system_supervision",
                "emergency_procedures",
                "policy_enforcement",
            ],
            "endpoints": {"status": "/homeostasis", "health": "/health"},
            "note": "Detailed runtime status available through service registry",
        }
    )

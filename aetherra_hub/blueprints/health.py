"""Health endpoints: /health and /status.

Low-risk extraction from monolith. Uses shared hub_state.
"""

from __future__ import annotations

# Standard library imports
from datetime import datetime

# Third party imports
from flask import Blueprint, current_app, jsonify

# Local imports
from ..config import settings as default_settings
from ..services import registry_client
from ..services.readiness import build_hub_readiness_payload
from ..services.state import hub_state

# Aetherra imports
try:
    from aetherra_service_registry import get_service_registry
except ImportError:
    get_service_registry = None

bp = Blueprint("health", __name__)


def _json_no_store(payload):
    response = jsonify(payload)
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/health")
def health():
    hub_state.incr_requests()
    return _json_no_store(
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

    return _json_no_store(
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
    return _json_no_store(
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


@bp.get("/api/hub/readiness")
def hub_readiness():
    """Return Hub-level readiness without mutating runtime state."""
    hub_state.incr_requests()
    settings = getattr(current_app, "settings", default_settings)
    payload = build_hub_readiness_payload(
        app=current_app,
        settings=settings,
        kernel_status=registry_client.get_kernel_status(),
        registry_status=registry_client.get_registry_status(),
    )
    return _json_no_store(payload)

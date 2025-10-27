"""Memory endpoints (graph + status).

Returns status/graph data or 501 for unimplemented features.
"""

from __future__ import annotations

# Third party imports
from typing import Any

from flask import Blueprint, jsonify

# Local imports
from ..services import registry_client

bp = Blueprint("memory", __name__)


@bp.get("/api/memory/status")
def memory_status():
    """Return memory system status including STORM metrics if enabled.

    Returns dict with memory engine status, STORM configuration, and metrics.
    Best-effort via service registry; falls back to disabled status.
    """
    try:
        # Get STORM metrics from registry client
        storm_metrics = registry_client.get_storm_metrics()

        # Build response with STORM status
        enabled = bool(storm_metrics.get("enabled", False))
        status: dict[str, Any] = {"ok": True, "enabled": enabled}

        # If STORM enabled, include all metrics and provide backward-compatible 'storm' key
        if enabled:
            # Flatten metrics at top-level for current UI
            status.update(storm_metrics)
            # Back-compat for consumers expecting a nested 'storm' object (e.g., OS post-boot probe)
            status["storm"] = dict(storm_metrics)

        return jsonify(status), 200
    except Exception as exc:
        # Fallback to disabled status on error
        return (
            jsonify(
                {"ok": False, "enabled": False, "error": f"status_unavailable: {exc}"}
            ),
            200,
        )


@bp.get("/api/memory/graph")
def graph():  # pragma: no cover
    return (
        jsonify(
            {
                "ok": False,
                "status": "memory_graph_disabled",
                "detail": "Memory graph endpoint not implemented yet",
            }
        ),
        501,
    )


@bp.get("/api/memory/audit")
def memory_audit():
    """Return memory audit DAG/status if available.

    Best-effort: returns 200 with ok flag and enabled status even on failures,
    matching the resilience pattern used elsewhere.
    """
    try:
        data = registry_client.get_memory_audit()
        if isinstance(data, dict):
            # Ensure ok present; keep original keys from service client
            out = {"ok": True}
            out.update(data)
            # Default enabled to False if missing
            out.setdefault("enabled", False)
            return jsonify(out), 200
        # Fallback: audit not available
        return jsonify({"ok": True, "enabled": False, "audit": None}), 200
    except Exception as exc:  # pragma: no cover - defensive best-effort
        return (
            jsonify(
                {"ok": False, "enabled": False, "error": f"audit_unavailable: {exc}"}
            ),
            200,
        )

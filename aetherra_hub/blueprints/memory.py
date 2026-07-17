"""Memory endpoints (graph + status).

Returns status/graph data or 501 for unimplemented features.
"""

from __future__ import annotations

# Third party imports
import logging
from typing import Any

from flask import Blueprint, jsonify

# Local imports
from ..services import registry_client

bp = Blueprint("memory", __name__)
logger = logging.getLogger(__name__)


@bp.get("/api/memory/status")
def memory_status():
    """Return memory system status including STORM metrics if enabled.

    Returns dict with memory engine status, STORM configuration, and metrics.
    Best-effort via service registry; falls back to disabled status.
    """
    try:
        # Get STORM metrics and status from registry client
        storm_metrics = registry_client.get_storm_metrics()
        storm_status = registry_client.get_storm_status() or {}

        # Build response with STORM status
        enabled = bool(
            storm_metrics.get("enabled", False) or storm_status.get("enabled", False)
        )
        status: dict[str, Any] = {"ok": True, "enabled": enabled}

        # If STORM enabled, include all metrics and provide backward-compatible 'storm' key
        if enabled:
            # Flatten metrics at top-level for current UI
            status.update(storm_metrics)
            # Merge selected config/status fields used by UI (e.g., shadow_mode)
            if isinstance(storm_status, dict) and storm_status:
                # Mirror a few useful fields at the top-level for convenience
                for k in ("shadow_mode", "selected_backend", "tt_rank_cap", "k_coarse"):
                    if k in storm_status:
                        status[k] = storm_status[k]
                # Provide nested object for more advanced consumers
                status.setdefault("storm_status", {}).update(storm_status)
            # Back-compat for consumers expecting a nested 'storm' object (e.g., OS post-boot probe)
            status["storm"] = dict(storm_metrics)

        return jsonify(status), 200
    except Exception:
        # Fallback to disabled status on error
        logger.exception("Memory status unavailable")
        return (
            jsonify({"ok": False, "enabled": False, "error": "status_unavailable"}),
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
    except Exception:  # pragma: no cover - defensive best-effort
        logger.exception("Memory audit unavailable")
        return (
            jsonify({"ok": False, "enabled": False, "error": "audit_unavailable"}),
            200,
        )

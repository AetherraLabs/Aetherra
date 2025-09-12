"""/site_status aggregated bundle.

Simplified extraction: kernel + plugin counts + hub stats.
"""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify

from ..services import registry_client
from ..services.state import hub_state

bp = Blueprint("site_status", __name__)


@bp.get("/site_status")
@bp.get("/api/site_status")
def site_status():
    hub_state.incr_requests()
    ks = registry_client.get_kernel_status() or {}
    running = bool(
        ks.get("running") is True or str(ks.get("state", "")).lower() == "running"
    )
    try:
        if isinstance(ks.get("uptime"), (int, float)):
            uptime = float(ks.get("uptime") or 0.0)
        else:
            uptime = float((ks.get("metrics", {}) or {}).get("uptime", 0.0))
    except Exception:
        uptime = 0.0
    qs = ks.get("queue_sizes") if isinstance(ks.get("queue_sizes"), dict) else {}
    return jsonify(
        {
            "ok": True,
            "hub": {
                "ts": datetime.now().isoformat(),
                "requests_served": hub_state.requests_served,
            },
            "plugins": {"total": hub_state.plugins_total()},
            "kernel": {
                "running": running,
                "uptime_seconds": uptime,
                "queue_sizes": {
                    "high_priority": int((qs or {}).get("high_priority", 0) or 0),
                    "normal_priority": int((qs or {}).get("normal_priority", 0) or 0),
                    "background": int((qs or {}).get("background", 0) or 0),
                },
            },
        }
    )

"""Telemetry ingest blueprint.

Implements /api/telemetry (POST) to accept simple JSON events and increments an
in-memory counter exposed via /api/stats for backward compatibility with tests.
Also provides /api/stats returning a snapshot including telemetry_received.
"""

from __future__ import annotations

import threading
from typing import Any, Dict

from flask import Blueprint, jsonify, request

bp = Blueprint("telemetry", __name__)

_lock = threading.Lock()
_state: Dict[str, Any] = {"telemetry_received": 0}
_events: list[Dict[str, Any]] = []  # future: ring buffer / size limit


@bp.post("/api/telemetry")
def ingest():  # pragma: no cover - validated via capability tests
    try:
        data = request.get_json(silent=True) or {}
    except Exception:
        data = {}
    with _lock:
        _state["telemetry_received"] = int(_state.get("telemetry_received", 0)) + 1
        if isinstance(data, dict):
            # store shallow copy to avoid later mutation surprises
            _events.append(dict(data))
    return jsonify({"ok": True}), 200


@bp.get("/api/stats")
def stats():  # pragma: no cover
    with _lock:
        # Don't expose full events to keep payload small
        return jsonify(dict(_state)), 200

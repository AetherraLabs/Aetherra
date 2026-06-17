"""Telemetry ingest blueprint.

Implements /api/telemetry (POST) to accept simple JSON events and increments an
in-memory counter exposed via /api/stats for backward compatibility with tests.
Also provides /api/stats returning a snapshot including telemetry_received.
"""

from __future__ import annotations

# Standard library imports
import threading
from collections import deque
from typing import Any

# Third party imports
from flask import Blueprint, jsonify, request

from ..services.control_auth import authorize_control_request

try:  # optional import; if missing we just omit field
    # Local imports
    from .plugins import _PARALLEL_SAMPLE_LAST  # type: ignore
except Exception:  # pragma: no cover
    _PARALLEL_SAMPLE_LAST = None  # type: ignore

bp = Blueprint("telemetry", __name__)

_lock = threading.Lock()
_state: dict[str, Any] = {"telemetry_received": 0}
_events: deque[dict[str, Any]] = deque(maxlen=1_000)


@bp.post("/api/telemetry")
def ingest():  # pragma: no cover - validated via capability tests
    decision = authorize_control_request(request.headers, request.remote_addr)
    if not decision.allowed:
        return jsonify({"ok": False, "error": decision.error}), decision.status_code
    if request.content_length is not None and request.content_length > 65_536:
        return jsonify({"ok": False, "error": "payload_too_large"}), 413
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"ok": False, "error": "invalid_json_object"}), 400
    with _lock:
        _state["telemetry_received"] = int(_state.get("telemetry_received", 0)) + 1
        _events.append(dict(data))
    return jsonify({"ok": True}), 200


@bp.get("/api/stats")
def stats():  # pragma: no cover
    with _lock:
        # Don't expose full events to keep payload small
        payload = dict(_state)
        if _PARALLEL_SAMPLE_LAST:
            payload["parallel_sample_last"] = _PARALLEL_SAMPLE_LAST
        return jsonify(payload), 200

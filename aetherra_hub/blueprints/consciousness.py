# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2025 Aetherra AI. Licensed under the GNU Affero General Public License v3.
#
# consciousness.py
# Flask blueprint for consciousness state API endpoints
# Provides /api/consciousness/state endpoint for ThinkStream visualization

"""Consciousness endpoints: /api/consciousness/state

Exposes real-time consciousness state from ThinkStream for UI visualization.
"""

from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import Any

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services.control_auth import authorize_control_request
from ..services.state import hub_state

bp = Blueprint("consciousness", __name__, url_prefix="/api/consciousness")

# Preserve the legacy callback registration without importing or starting a core.
_think_stream: Any | None = None


def _update_state_snapshot(state: dict[str, Any]):
    """Callback invoked by ThinkStream to update state snapshot."""
    hub_state.update_consciousness(state)


def _authorize_internal_request():
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"error": decision.error}), decision.status_code


def _validate_state(state: Any) -> str | None:
    if not isinstance(state, dict):
        return "invalid_state"
    tick_id = state.get("tick_id")
    if tick_id is not None and (
        not isinstance(tick_id, int) or isinstance(tick_id, bool)
    ):
        return "invalid_tick_id"
    qualia = state.get("qualia")
    if qualia is not None and not isinstance(qualia, dict):
        return "invalid_qualia"
    for field in ("focuses", "intentions", "recent_narrative"):
        if field in state and not isinstance(state[field], list):
            return f"invalid_{field}"
    return None


def _unavailable_observer_state(metrics):
    state = metrics["runtime_state"] or "unknown"
    if state == "running":
        state = "stale" if metrics["freshness"] == "stale" else "unavailable"
    return {
        "status": state,
        "runtime": metrics,
        "message": "Consciousness observer is unavailable.",
    }


def _owned_observer_state():
    """Read an existing observer only; an unavailable owner suppresses old push state."""
    # Aetherra imports
    from Aetherra.runtime_ui.snapshot import _read_status, consciousness_runtime_metrics
    from aetherra_service_registry import get_existing_service_registry

    try:
        registry = get_existing_service_registry()
        info = registry.get_service_info("consciousness_core") if registry else None
        instance = info.instance if info is not None else None
        getter = getattr(instance, "get_runtime_status", None)
        owned = callable(getter) or (
            info is not None and info.metadata.get("phase") == "phase_c1_observer"
        )
        if not owned:
            return None
        if not registry.get_registry_status().get("running"):
            return {
                "status": "unavailable",
                "message": "Consciousness registry is not running.",
            }, 503
        raw = _read_status(getter)
        metrics = consciousness_runtime_metrics(raw or {})
        unavailable = _unavailable_observer_state(metrics)
        if not metrics["available"] or metrics["think_stream_available"] is not True:
            return unavailable, 503
        snapshot = _read_status(getattr(instance, "get_think_stream", None))
        if not snapshot or snapshot.get("status") != "running":
            return unavailable, 503
        # Lifecycle can change while reading a cached snapshot. Recheck without
        # invoking get_status(), which evaluates autopilot and writes audit state.
        metrics = consciousness_runtime_metrics(_read_status(getter) or {})
        if not metrics["available"] or metrics["think_stream_available"] is not True:
            return _unavailable_observer_state(metrics), 503
        payload = {
            key: snapshot[key]
            for key in (
                "tick_id",
                "timestamp",
                "qualia",
                "focuses",
                "intentions",
                "recent_narrative",
            )
            if key in snapshot
        }
        payload.update(
            status="running",
            runtime_state="running",
            runtime=metrics,
            events_processed=metrics["events_processed"],
            autonomy_mode=metrics["autonomy_mode"],
        )
        return payload, 200
    except Exception:
        # Lookup/read failures may contain private paths. They are never a reason
        # to substitute a potentially stale legacy snapshot.
        return {
            "status": "unknown",
            "message": "Consciousness observer status is unavailable.",
        }, 503


@bp.get("/state")
def get_consciousness_state():
    """
    Get current consciousness state snapshot.

    Returns:
        JSON with qualia vector, focuses, intentions, narrative moments
    """
    hub_state.incr_requests()
    owned_state = _owned_observer_state()
    if owned_state is not None:
        payload, status = owned_state
        return jsonify(payload), status

    # Get state from hub_state (shared singleton)
    current_state = hub_state.get_consciousness()

    # If consciousness system is not running, return offline state
    if not current_state:
        return (
            jsonify(
                {
                    "status": "offline",
                    "message": "Consciousness system not running. Start with runners/run_consciousness.py",
                    "tick_id": 0,
                    "timestamp": datetime.now().isoformat(),
                    "qualia": {
                        "valence": 0.0,
                        "arousal": 0.0,
                        "certainty": 0.0,
                        "curiosity": 0.0,
                        "care": 0.0,
                        "fatigue": 0.0,
                    },
                    "focuses": [],
                    "intentions": [],
                    "recent_narrative": [],
                    "events_processed": 0,
                    "autonomy_mode": "unknown",
                }
            ),
            503,
        )  # Service Unavailable

    # Return latest snapshot from ThinkStream
    return jsonify(current_state)


@bp.post("/update")
def update_consciousness_state():
    """
    (Internal) Receive consciousness state updates from ThinkStream via HTTP.

    This endpoint is called by the consciousness runner process to push state
    updates to the Hub's shared state, enabling cross-process communication.
    """
    auth_error = _authorize_internal_request()
    if auth_error is not None:
        return auth_error
    if request.content_length is not None and request.content_length > 262_144:
        return jsonify({"error": "payload_too_large"}), 413
    state = request.get_json(silent=True)
    validation_error = _validate_state(state)
    if validation_error is not None:
        return jsonify({"error": validation_error}), 400

    # Update shared hub state
    hub_state.update_consciousness(state)

    return jsonify({"status": "ok", "tick_id": state.get("tick_id")})


@bp.post("/register_callback")
def register_think_stream_callback():
    """
    (Internal) Allows ThinkStream to register its state update callback.

    This would be called by the consciousness runner on startup to wire
    the ThinkStream's _ui_callback to our _update_state_snapshot function.
    """
    auth_error = _authorize_internal_request()
    if auth_error is not None:
        return auth_error
    # In production, this would be called from run_consciousness.py
    # to register the callback when the consciousness loop starts
    return jsonify({"status": "ok", "message": "Callback registration endpoint ready"})


def register_think_stream(think_stream: Any):
    """
    Register ThinkStream instance to receive state updates.

    This should be called from run_consciousness.py after creating ThinkStream:
        from aetherra_hub.blueprints.consciousness import register_think_stream
        register_think_stream(think_stream)

    Args:
        think_stream: ThinkStream instance to connect
    """
    global _think_stream
    _think_stream = think_stream

    # Register our snapshot callback with ThinkStream
    think_stream._ui_callback = _update_state_snapshot

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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
    from Aetherra.consciousness.core.think_stream import ThinkStream

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services.control_auth import authorize_control_request
from ..services.state import hub_state

# Aetherra imports
try:
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
    from Aetherra.consciousness.core.think_stream import ThinkStream
except ImportError:
    ConsciousnessCore = None
    ThinkStream = None

bp = Blueprint("consciousness", __name__, url_prefix="/api/consciousness")

# Module-level state for consciousness system (initialized on demand)
_consciousness_core: Any | None = None
_think_stream: Any | None = None


def _init_consciousness_if_needed():
    """Initialize consciousness system on first API call if not already running."""
    global _consciousness_core, _think_stream

    if _consciousness_core is not None:
        return  # Already initialized

    if ConsciousnessCore is None or ThinkStream is None:
        # Consciousness module not available
        return

    # Note: Full initialization with PerceptionBus and Actuator would happen in
    # run_consciousness.py. Here we just create a minimal core for state access.
    # In production, this would connect to the existing consciousness loop.

    # For now, we'll just track state snapshots from ThinkStream callbacks
    # The actual consciousness loop would be running separately


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
    if tick_id is not None and (not isinstance(tick_id, int) or isinstance(tick_id, bool)):
        return "invalid_tick_id"
    qualia = state.get("qualia")
    if qualia is not None and not isinstance(qualia, dict):
        return "invalid_qualia"
    for field in ("focuses", "intentions", "recent_narrative"):
        if field in state and not isinstance(state[field], list):
            return f"invalid_{field}"
    return None


@bp.get("/state")
def get_consciousness_state():
    """
    Get current consciousness state snapshot.

    Returns:
        JSON with qualia vector, focuses, intentions, narrative moments
    """
    hub_state.incr_requests()
    _init_consciousness_if_needed()

    # Get state from hub_state (shared singleton)
    current_state = hub_state.get_consciousness()

    # If consciousness system is not running, return offline state
    if not current_state:
        return jsonify(
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
        ), 503  # Service Unavailable

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

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
from flask import Blueprint, jsonify

# Local imports
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
    print(
        f"[Consciousness API] Received state update: tick={state.get('tick_id')}, qualia_valence={state.get('qualia', {}).get('valence')}"
    )
    print(f"  Callback hub_state object id: {id(hub_state)}")
    print(f"  Callback consciousness_state id: {id(hub_state.consciousness_state)}")
    print(
        f"  Callback consciousness_state has {len(hub_state.consciousness_state)} keys"
    )


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

    # Debug: Check state with full diagnostic
    print("[Consciousness API] GET /state called")
    print(f"  hub_state object id: {id(hub_state)}")
    print(f"  consciousness_state id: {id(hub_state.consciousness_state)}")
    print(
        f"  consciousness_state keys: {list(current_state.keys()) if current_state else 'EMPTY'}"
    )
    print(f"  consciousness_state is truthy: {bool(current_state)}")

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
    from flask import request

    state = request.get_json()
    if not state:
        return jsonify({"error": "No state data provided"}), 400

    # Update shared hub state
    hub_state.update_consciousness(state)

    # Optional debug output
    print(
        f"[Consciousness API] POST /update: tick={state.get('tick_id')}, "
        f"qualia_valence={state.get('qualia', {}).get('valence')}"
    )

    return jsonify({"status": "ok", "tick_id": state.get("tick_id")})


@bp.post("/register_callback")
def register_think_stream_callback():
    """
    (Internal) Allows ThinkStream to register its state update callback.

    This would be called by the consciousness runner on startup to wire
    the ThinkStream's _ui_callback to our _update_state_snapshot function.
    """
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

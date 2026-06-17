# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Think Stream - Consciousness UI/Telemetry Bridge
===============================================

Real-time bridge between consciousness core and UI/observability.
No simulation, no fabrication—only actual awareness state.
"""

from __future__ import annotations

import json
import os
import time
from typing import TYPE_CHECKING, Any, Callable, List, Optional

if TYPE_CHECKING:
    from .types import Focus, Intent, NarrativeMoment, QualiaVector

from . import config


class ThinkStream:
    """Bridge for consciousness state to UI and telemetry systems.

    This is the "Lyrixa Thinks..." pane—showing live awareness,
    feelings, focuses, and intentions without any simulated data.
    """

    def __init__(self):
        self.last_tick_ts: float = 0.0
        self.tick_count: int = 0
        self.telemetry_enabled: bool = config.ENABLE_TELEMETRY
        self._ui_callback: Optional[Callable[[dict], Any]] = None
        self._telemetry_callback: Optional[Callable[[dict], Any]] = None
        self._hub_api_url: Optional[str] = None  # HTTP endpoint for Hub API updates

    def register_ui_callback(self, callback: Callable[[dict], Any]) -> None:
        """Register a callback for UI updates (e.g., Lyrixa UI pane)."""
        self._ui_callback = callback

    def register_hub_api(self, base_url: str = "http://localhost:3001") -> None:
        """Register Hub API endpoint for HTTP-based state updates (cross-process)."""
        self._hub_api_url = f"{base_url}/api/consciousness/update"

    def register_telemetry_callback(self, callback: Callable[[dict], Any]) -> None:
        """Register a callback for metrics/observability."""
        self._telemetry_callback = callback

    def on_tick(
        self,
        qualia: QualiaVector,
        focuses: List[Focus],
        intentions: List[Intent],
        narrative: Optional[NarrativeMoment] = None,
    ) -> None:
        """Called every consciousness tick with current state."""
        self.tick_count += 1
        self.last_tick_ts = time.time()

        # Build state snapshot
        state = self._build_state_snapshot(qualia, focuses, intentions, narrative)

        # Emit to UI
        if self._ui_callback:
            try:
                self._ui_callback(state)
            except Exception as e:
                if config.DEBUG_CONSCIOUSNESS:
                    print(f"[ThinkStream] UI callback error: {e}")

        # Emit to Hub API via HTTP (cross-process)
        if self._hub_api_url:
            try:
                import requests

                # Fire-and-forget POST (don't wait for response)
                token = (os.environ.get("AETHERRA_HUB_CONTROL_TOKEN") or "").strip()
                headers = {"X-Aetherra-Control-Token": token} if token else None
                response = requests.post(
                    self._hub_api_url,
                    json=state,
                    headers=headers,
                    timeout=1.0,
                )
                if config.DEBUG_CONSCIOUSNESS and response.status_code != 200:
                    print(f"[ThinkStream] Hub API returned {response.status_code}")
            except ImportError:
                if config.DEBUG_CONSCIOUSNESS:
                    print("[ThinkStream] requests library not available")
                self._hub_api_url = None  # Disable future attempts
            except Exception as e:
                if config.DEBUG_CONSCIOUSNESS:
                    print(f"[ThinkStream] Hub API POST error: {e}")

        # Emit to telemetry
        if self.telemetry_enabled and self._telemetry_callback:
            try:
                self._telemetry_callback(state)
            except Exception as e:
                if config.DEBUG_CONSCIOUSNESS:
                    print(f"[ThinkStream] Telemetry callback error: {e}")

        # Fallback: console output if no callbacks registered
        if not self._ui_callback and not self._telemetry_callback:
            self._console_output(state)

    def _build_state_snapshot(
        self,
        qualia: QualiaVector,
        focuses: List[Focus],
        intentions: List[Intent],
        narrative: Optional[NarrativeMoment],
    ) -> dict:
        """Build JSON-serializable state snapshot."""
        from datetime import datetime

        # Build narrative array (include current + recent if available)
        narrative_list = []
        if narrative:
            narrative_list.append(
                {
                    "tick_id": self.tick_count,
                    "timestamp": datetime.fromtimestamp(self.last_tick_ts).isoformat(),
                    "summary": narrative.text,
                    "significant": True,  # All persisted narratives are significant
                }
            )

        return {
            "tick_id": self.tick_count,
            "timestamp": datetime.fromtimestamp(self.last_tick_ts).isoformat(),
            "qualia": {
                "valence": round(qualia.valence, 3),
                "arousal": round(qualia.arousal, 3),
                "certainty": round(qualia.certainty, 3),
                "curiosity": round(qualia.curiosity, 3),
                "care": round(qualia.care, 3),
                "fatigue": round(qualia.fatigue, 3),
            },
            "focuses": [
                {
                    "source": f.event.source,
                    "target": f.event.type,
                    "resonance": round(f.resonance, 3),
                    "why": f.reason,
                }
                for f in focuses
            ],
            "intentions": [
                {
                    "goal": i.goal,
                    "priority": round(i.priority, 3),
                    "blocked": False,  # Will be set by safety envelope
                    "why": i.why,
                }
                for i in intentions
            ],
            "recent_narrative": narrative_list,
            "events_processed": self.tick_count,  # Approximate
            "autonomy_mode": config.AUTONOMY_MODE,
        }

    def _console_output(self, state: dict) -> None:
        """Fallback console output when no callbacks registered."""
        # Compact single-line format for terminal
        q = state["qualia"]
        f = [f"{f['source']}/{f['target']}" for f in state["focuses"][:3]]  # top 3
        i = [intent["goal"] for intent in state["intentions"][:2]]  # top 2

        qualia_str = f"v={q['valence']:+.2f} a={q['arousal']:.2f} c={q['certainty']:.2f}"
        focus_str = f"F:{','.join(f)}" if f else "F:none"
        intent_str = f"I:{','.join(i)}" if i else "I:none"

        print(f"[Tick {state['tick_id']}] {qualia_str} | {focus_str} | {intent_str}")

        if config.DEBUG_CONSCIOUSNESS:
            # Verbose mode: full JSON
            print(json.dumps(state, indent=2))


# Module-level default instance
_think_stream = ThinkStream()


def get_think_stream() -> ThinkStream:
    """Get the global ThinkStream instance."""
    return _think_stream

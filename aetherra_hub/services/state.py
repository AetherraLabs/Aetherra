"""Global hub state (lightweight) for modular blueprints.

This replaces the monolith's AetherraHubServer.stats + plugin registry usage for
extracted routes. When plugin routes are migrated, they can integrate with this
state object.
"""

from __future__ import annotations

# Standard library imports
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class HubState:
    startup_time: datetime = field(default_factory=datetime.now)
    requests_served: int = 0
    plugins: dict[str, dict[str, Any]] = field(default_factory=dict)
    consciousness_state: dict[str, Any] = field(default_factory=dict)

    def incr_requests(self):
        self.requests_served += 1

    def plugins_total(self) -> int:
        return len(self.plugins)

    def update_consciousness(self, state: dict[str, Any]):
        """Update consciousness state snapshot (called by ThinkStream callback)."""
        self.consciousness_state = state

    def get_consciousness(self) -> dict[str, Any]:
        """Get current consciousness state snapshot."""
        return self.consciousness_state


hub_state = HubState()

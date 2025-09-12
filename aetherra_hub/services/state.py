"""Global hub state (lightweight) for modular blueprints.

This replaces the monolith's AetherraHubServer.stats + plugin registry usage for
extracted routes. When plugin routes are migrated, they can integrate with this
state object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class HubState:
    startup_time: datetime = field(default_factory=datetime.now)
    requests_served: int = 0
    plugins: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def incr_requests(self):
        self.requests_served += 1

    def plugins_total(self) -> int:
        return len(self.plugins)


hub_state = HubState()

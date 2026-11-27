"""Global hub state (lightweight) for modular blueprints.

This replaces the monolith's AetherraHubServer.stats + plugin registry usage for
extracted routes. When plugin routes are migrated, they can integrate with this
state object.
"""

from __future__ import annotations

# Standard library imports
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any
from weakref import WeakMethod, ref


@dataclass
class HubState:
    startup_time: datetime = field(default_factory=datetime.now)
    requests_served: int = 0
    plugins: dict[str, dict[str, Any]] = field(default_factory=dict)
    consciousness_state: dict[str, Any] = field(default_factory=dict)

    _temporal_binding: Any = field(default=None, init=False, repr=False, compare=False)
    _temporal_lock: Any = field(
        default_factory=Lock, init=False, repr=False, compare=False
    )

    def bind_temporal_status(self, *, owner, registry, provider) -> bool:
        if getattr(provider, "__self__", None) is not owner:
            return False
        try:
            binding = (ref(owner), ref(registry), WeakMethod(provider))
        except TypeError:
            return False
        with self._temporal_lock:
            existing = self._temporal_binding
            if existing and existing[1]() is registry:
                current = existing[0]()
                if current is not None and current is not owner:
                    return False
            self._temporal_binding = binding
            return True

    def temporal_status_provider(self, registry):
        with self._temporal_lock:
            existing = self._temporal_binding
            if registry is not None and existing and existing[1]() is registry:
                return existing[2]()
            return None

    def clear_temporal_status(self, *, owner, registry) -> bool:
        with self._temporal_lock:
            existing = self._temporal_binding
            if existing and existing[0]() is owner and existing[1]() is registry:
                self._temporal_binding = None
                return True
            return False

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

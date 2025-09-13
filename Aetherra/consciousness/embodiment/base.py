#!/usr/bin/env python3
"""Embodiment Base Interfaces (MVP)

Defines abstract Sensor and Actuator classes for Phase 1. Sensors produce observations
periodically or event-driven; actuators execute actions with optional result metadata.
Bridge integration: sensor events are logged as episodic events and may enqueue workspace candidates.
"""

from __future__ import annotations

import abc
import os
import time
from typing import Any, Dict, Optional

from ..episodic_store import get_episodic_store
from ..workspace_core import get_workspace


class Sensor(abc.ABC):
    def __init__(self, name: str):
        self.name = name
        self.last_observed: Optional[float] = None

    @abc.abstractmethod
    def poll(self) -> Optional[Dict[str, Any]]:
        """Return an observation dict or None if no change."""

    def observe(self) -> Optional[Dict[str, Any]]:
        data = self.poll()
        if data is None:
            return None
        self.last_observed = time.time()
        # Log episodic event
        if os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1":
            try:
                store = get_episodic_store()
                store.new_event(
                    type="perception",
                    content=f"sensor {self.name} observation",
                    source=self.name,
                    importance=data.get("importance", 0.3),
                    raw=data,
                )
                ws = get_workspace()
                if ws.enabled():
                    ws.add_candidate(
                        payload={
                            "type": "sensor_observation",
                            "sensor": self.name,
                            "data_keys": list(data.keys()),
                        },
                        priority=int(data.get("priority", 0)),
                        weight=1.0,
                        source=self.name,
                        phase="perception",
                    )
            except Exception:
                pass
        return data


class Actuator(abc.ABC):
    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def perform(self, command: str, **params) -> Dict[str, Any]:
        """Execute an action and return result metadata."""

    def execute(self, command: str, **params) -> Dict[str, Any]:
        result = self.perform(command, **params)
        if os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1":
            try:
                store = get_episodic_store()
                store.new_event(
                    type="action",
                    content=f"actuator {self.name} command {command}",
                    source=self.name,
                    importance=result.get("importance", 0.4),
                    raw={"command": command, **result},
                    workspace_priority=int(result.get("priority", 1)),
                )
            except Exception:
                pass
        return result

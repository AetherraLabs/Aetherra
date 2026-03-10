# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Perception Adapter Base
=======================

Base class for all OS perception adapters.
Adapters connect real-world signals to the perception bus.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from Aetherra.consciousness.core.types import Event

from ..event_types import SENSOR_OFFLINE, SENSOR_ONLINE

if TYPE_CHECKING:
    from ..bus import PerceptionBus


class AdapterBase:
    """Base class for perception adapters.

    All adapters must:
    - Start background collection (thread/async)
    - Publish only real data (never simulate)
    - Emit SENSOR_OFFLINE if data source unavailable
    - Handle errors gracefully without crashing
    """

    name: str = "adapter.base"

    def __init__(self, bus: PerceptionBus):
        """Initialize adapter.

        Args:
            bus: PerceptionBus to publish events to
        """
        self.bus = bus
        self.is_running: bool = False

    def start(self) -> None:
        """Start background data collection (override in subclass)."""
        raise RuntimeError(f"{self.name}.start() is not implemented for this adapter")

    def stop(self) -> None:
        """Stop background collection (override if needed)."""
        self.is_running = False

    def emit_offline(self, reason: str) -> None:
        """Emit sensor offline event."""
        self.bus.publish(
            Event(
                type=SENSOR_OFFLINE,
                payload={"sensor": self.name, "reason": reason},
                source=self.name,
            )
        )

    def emit_online(self) -> None:
        """Emit sensor online event."""
        self.bus.publish(Event(type=SENSOR_ONLINE, payload={"sensor": self.name}, source=self.name))

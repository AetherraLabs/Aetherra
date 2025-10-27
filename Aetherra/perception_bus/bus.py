# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Perception Bus - Real-world Event Stream
========================================

Lock-free event bus for real OS telemetry.
No simulation, no mocks—only actual system signals.
"""

from __future__ import annotations

import contextlib
import threading
from collections import deque
from typing import Any, Callable, List

from Aetherra.consciousness.core.types import Event

Subscriber = Callable[[Event], None]


class PerceptionBus:
    """Lock-free event bus for consciousness perception.

    All OS adapters publish here; consciousness core drains from here.
    This is the sensory substrate—what Aetherra can actually perceive.
    """

    def __init__(self, maxlen: int = 10000):
        """Initialize perception bus.

        Args:
            maxlen: Maximum queue size before old events are dropped
        """
        self._q: deque[Event] = deque(maxlen=maxlen)
        self._subs: List[Subscriber] = []
        self._lock = threading.Lock()
        self._total_published: int = 0
        self._total_dropped: int = 0

    def publish(self, ev: Event) -> None:
        """Publish an event to the bus (non-blocking).

        Args:
            ev: Event to publish
        """
        # Check if we're about to drop an event
        if len(self._q) >= self._q.maxlen:  # type: ignore
            self._total_dropped += 1

        self._q.append(ev)
        self._total_published += 1

        # Notify subscribers (best-effort, non-blocking)
        with self._lock:
            for fn in self._subs:
                with contextlib.suppress(Exception):
                    # Subscriber errors don't block the bus
                    fn(ev)

    def drain(self, max_items: int = 256) -> List[Event]:
        """Drain events from the bus (consume).

        Args:
            max_items: Maximum events to drain per call

        Returns:
            List of events (up to max_items)
        """
        out: List[Event] = []
        for _ in range(min(max_items, len(self._q))):
            out.append(self._q.popleft())
        return out

    def peek(self, max_items: int = 10) -> List[Event]:
        """Peek at recent events without consuming.

        Args:
            max_items: Maximum events to return

        Returns:
            List of recent events (not consumed)
        """
        return list(self._q)[-max_items:]

    def subscribe(self, fn: Subscriber) -> None:
        """Subscribe to real-time event stream.

        Args:
            fn: Callback function(Event) -> None
        """
        with self._lock:
            self._subs.append(fn)

    def unsubscribe(self, fn: Subscriber) -> None:
        """Unsubscribe from event stream.

        Args:
            fn: Previously subscribed callback
        """
        with self._lock:
            if fn in self._subs:
                self._subs.remove(fn)

    def get_stats(self) -> dict[str, Any]:
        """Get bus statistics for monitoring."""
        return {
            "queue_size": len(self._q),
            "queue_maxlen": self._q.maxlen,
            "total_published": self._total_published,
            "total_dropped": self._total_dropped,
            "subscriber_count": len(self._subs),
        }


# Module-level default bus
_bus = PerceptionBus()


def get_perception_bus() -> PerceptionBus:
    """Get the global perception bus instance."""
    return _bus

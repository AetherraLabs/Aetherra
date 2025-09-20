#!/usr/bin/env python3
"""Sensor Base Class (Phase 1)

Defines a minimal interface for sensors that produce events into the event bus.
Sensors may be polling or push-based; for now we implement simple periodic polling stubs.
"""

from __future__ import annotations

# Standard library imports
import threading
import time
from typing import Any, Dict, Optional

# Local imports
from ..event_bus import get_event_bus


class BaseSensor:
    def __init__(self, name: str, interval_sec: float = 30.0):
        self.name = name
        self.interval_sec = interval_sec
        self._thread: Optional[threading.Thread] = None
        self._stop = False
        self._started = False
        self._emissions = 0

    def start(self):
        if self._started:
            return
        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._started = True

    def stop(self):
        self._stop = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def _loop(self):
        while not self._stop:
            try:
                payload = self.sample()
                if payload is not None:
                    bus = get_event_bus()
                    bus.publish(
                        f"sensor.{self.name}",
                        payload,
                        to_workspace=True,
                        priority=0,
                        weight=1.0,
                        source=f"sensor:{self.name}",
                    )
                    self._emissions += 1
            except Exception:
                pass
            time.sleep(self.interval_sec)

    def sample(self) -> Optional[Dict[str, Any]]:  # override
        return None

    def emissions(self) -> int:
        return self._emissions

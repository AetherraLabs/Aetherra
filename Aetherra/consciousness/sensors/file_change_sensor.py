#!/usr/bin/env python3
"""File Change Sensor Stub

Watches a single file's mtime (if exists) at an interval; emits when mtime changes.
Future: integrate with a real watcher library.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from .base_sensor import BaseSensor


class FileChangeSensor(BaseSensor):
    def __init__(self, path: str | None = None, interval_sec: float = 45.0):
        super().__init__("file_change", interval_sec)
        self._path = Path(path or "self_model.json")
        self._last_mtime: float | None = None
        self._pending: bool = False
        self._debounce_start: float | None = None
        self._debounce_sec = float(
            os.getenv("AETHERRA_FILE_SENSOR_DEBOUNCE_SEC", "2.0")
        )

    def sample(self):
        try:
            if not self._path.exists():
                return None
            mtime = os.path.getmtime(self._path)
            if self._last_mtime is None:
                self._last_mtime = mtime
                return None
            if mtime != self._last_mtime:
                self._last_mtime = mtime
                # Start debounce window
                if not self._pending:
                    self._pending = True
                    self._debounce_start = time.time()
                # If debounce elapsed, emit aggregated change event
                if self._pending and self._debounce_start is not None:
                    if (time.time() - self._debounce_start) >= self._debounce_sec:
                        self._pending = False
                        self._debounce_start = None
                        return {
                            "path": str(self._path),
                            "changed": True,
                            "debounced": True,
                        }
                return None
            # If no new change but a pending debounce window exists, check if time elapsed
            if self._pending and self._debounce_start is not None:
                if (time.time() - self._debounce_start) >= self._debounce_sec:
                    self._pending = False
                    self._debounce_start = None
                    return {"path": str(self._path), "changed": True, "debounced": True}
        except Exception:
            return None
        return None

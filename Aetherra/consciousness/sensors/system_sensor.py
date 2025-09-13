#!/usr/bin/env python3
"""System Sensor Stub

Emits rudimentary system heartbeat metrics (time only for Phase 1). Future: CPU, memory, fd counts.
"""

from __future__ import annotations

import os
import time

try:  # optional psutil
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

from .base_sensor import BaseSensor


class SystemSensor(BaseSensor):
    def __init__(self, interval_sec: float = 60.0):
        super().__init__("system", interval_sec)

    def sample(self):  # noqa: D401
        docpu = os.getenv("AETHERRA_SENSOR_SYSTEM_CPU", "1") == "1"
        domem = os.getenv("AETHERRA_SENSOR_SYSTEM_MEM", "1") == "1"
        payload: dict[str, object] = {"epoch": int(time.time())}
        if psutil is not None and (docpu or domem):
            try:
                if docpu:
                    payload["cpu_pct"] = float(psutil.cpu_percent(interval=None))
                if domem:
                    vm = psutil.virtual_memory()
                    payload["mem_used_mb"] = float(round(vm.used / (1024 * 1024), 2))
                    payload["mem_pct"] = float(vm.percent)
            except Exception:
                # Silently ignore sampling errors
                pass
        return payload

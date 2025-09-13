#!/usr/bin/env python3
"""Sensor Registry / Starter

Provides a simple function to start a default set of sensors.
"""

from __future__ import annotations

from .file_change_sensor import FileChangeSensor
from .system_sensor import SystemSensor

_DEFAULT_SENSORS = []


def start_default_sensors():
    global _DEFAULT_SENSORS
    if _DEFAULT_SENSORS:
        return _DEFAULT_SENSORS
    # Intervals kept short for future tests can adjust via env if needed
    sys_sensor = SystemSensor(interval_sec=5.0)
    file_sensor = FileChangeSensor(interval_sec=5.0)
    for s in (sys_sensor, file_sensor):
        s.start()
        _DEFAULT_SENSORS.append(s)
    return _DEFAULT_SENSORS


def stop_all_sensors():
    global _DEFAULT_SENSORS
    for s in _DEFAULT_SENSORS:
        try:
            s.stop()
        except Exception:
            pass
    _DEFAULT_SENSORS = []

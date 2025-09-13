import time

from Aetherra.consciousness.event_bus import get_event_bus
from Aetherra.consciousness.sensors.registry import (
    start_default_sensors,
    stop_all_sensors,
)


def test_sensor_stubs_emit(monkeypatch):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    bus = get_event_bus()
    received = []
    bus.subscribe("sensor.system", lambda e: received.append(e))
    start_default_sensors()
    try:
        # Wait up to 2 intervals (5s each reduced for test config) but cap at 3s to keep test quick
        timeout = time.time() + 3.0
        while time.time() < timeout and not received:
            time.sleep(0.2)
    finally:
        stop_all_sensors()
    assert received, "system sensor should have emitted at least one event"

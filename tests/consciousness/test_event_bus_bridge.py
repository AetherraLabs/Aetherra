from Aetherra.consciousness.event_bus import get_event_bus
from Aetherra.consciousness.workspace_core import get_workspace


def test_event_bus_bridge_workspace_enqueue(monkeypatch):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    bus = get_event_bus()
    ws = get_workspace()
    start_size = ws.queue_size()
    bus.publish(
        "sensor.tick", {"value": 42}, to_workspace=True, priority=1, source="sensor"
    )
    assert ws.queue_size() == start_size + 1

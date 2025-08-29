import asyncio

from aetherra_event_bus import EventBus
from aetherra_module_manager import ModuleManager
from aetherra_service_registry import get_service_registry


def _run(coro):
    return asyncio.run(coro)


def test_klm_rollback_increments_counter():
    reg = _run(get_service_registry())
    mm = ModuleManager(reg)

    # Ensure module exists
    _run(mm.load_module("modZ", {"version": "0.1"}))

    # Perform rollback
    res = _run(mm.rollback_module("modZ"))
    assert res["ok"] is True

    m = mm.get_metrics()
    assert m.get("rollbacks_total", 0) >= 1


def test_keb_burst_drop_counter_increments():
    reg = _run(get_service_registry())
    eb = EventBus(reg)

    # Configure a very low rate to force burst drops
    eb._rate_per_sec = 0.5  # allow one token every 2 seconds

    # First publish typically succeeds (bucket fills up at init)
    _run(eb.publish("burst", {"i": 0}))

    # Immediately publish multiple times to trigger drops
    drops = 0
    for i in range(5):
        r = _run(eb.publish("burst", {"i": i + 1}))
        if not r.get("ok") and r.get("error") == "burst":
            drops += 1

    m = eb.get_metrics()
    assert m.get("events_dropped_burst", 0) >= drops >= 1

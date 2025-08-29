import asyncio

from aetherra_event_bus import EventBus
from aetherra_module_manager import ModuleManager
from aetherra_service_registry import get_service_registry


def _run(coro):
    return asyncio.run(coro)


def test_module_manager_basic_lifecycle():
    reg = _run(get_service_registry())
    mm = ModuleManager(reg)

    # Load module
    res = _run(mm.load_module("modA", {"version": "1.0"}))
    assert res["ok"] is True
    assert res["module"]["name"] == "modA"
    assert res["module"]["status"] == "active"

    # Reload module
    res2 = _run(mm.reload_module("modA", {"version": "1.1"}))
    assert res2["ok"] is True
    assert res2["module"]["version"] == "1.1"

    # List modules
    res3 = _run(mm.list_modules())
    assert res3["ok"] is True
    names = {m["name"] for m in res3["modules"]}
    assert "modA" in names

    # Unload module
    res4 = _run(mm.unload_module("modA"))
    assert res4["ok"] is True

    # Metrics sanity
    m = mm.get_metrics()
    assert "loads_total" in m and m["loads_total"] >= 1
    assert "reloads_total" in m and m["reloads_total"] >= 1


def test_event_bus_pub_sub_ack_and_metrics():
    reg = _run(get_service_registry())
    eb = EventBus(reg)

    # Subscribe a service name
    res_s = _run(eb.subscribe("topicX", "svc1"))
    assert res_s["ok"] is True

    # Publish an event
    res_p = _run(eb.publish("topicX", {"k": "v"}))
    # Allow small burst control; publish should succeed normally
    assert res_p["ok"] is True

    # Ack head-of-line
    res_a = _run(eb.ack("topicX", 1))
    assert res_a["ok"] is True

    # Metrics sanity
    m = eb.get_metrics()
    assert m["events_published_total"] >= 1
    # delivered_total increments by number of subscribers per fanout
    assert m["events_delivered_total"] >= 1
    tb = m.get("topic_backlog", {})
    assert isinstance(tb, dict)

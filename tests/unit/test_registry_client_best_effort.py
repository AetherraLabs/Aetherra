import asyncio

from aetherra_hub.services import registry_client as rc

class _DummySvc:
    def __init__(self):
        self.calls = 0
    def get_status(self):
        self.calls += 1
        return {"dummy": True}

class _Info:
    def __init__(self, inst):
        self.instance = inst

def test_generic_service_call_returns_empty_when_missing(monkeypatch):
    # monkeypatch async registry getter to return object lacking service
    async def _fake_get():
        class _Reg:
            def get_service_info(self, name):
                return None
        return _Reg()
    monkeypatch.setattr(rc, "_get_registry_async", _fake_get)
    assert rc.get_klm_status() == {}


def test_generic_service_call_success(monkeypatch):
    dummy = _DummySvc()
    async def _fake_get():
        class _Reg:
            def get_service_info(self, name):
                if name == "module_manager":
                    return _Info(dummy)
                return None
        return _Reg()
    monkeypatch.setattr(rc, "_get_registry_async", _fake_get)
    res = rc.get_klm_status()
    assert res == {"dummy": True}
    assert dummy.calls == 1


def test_get_service_handles_running_loop(monkeypatch):
    # Simulate running loop path by providing a loop and scheduling coro
    class _Reg:
        def get_service_info(self, name):
            return _Info(object())
    async def _fake_get():
        return _Reg()
    monkeypatch.setattr(rc, "_get_registry_async", _fake_get)
    # Start a loop to exercise create_task path
    async def _inner():
        rc.get_service("any")
    asyncio.run(_inner())

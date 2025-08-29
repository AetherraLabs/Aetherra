import importlib


def test_hmr_source_gating_blocks_unlisted(monkeypatch):
    # Gate to only allow a fake.allowed module
    monkeypatch.setenv("AETHERRA_HMR_ALLOWED_SOURCES", "fake.allowed")
    mod = importlib.import_module("Aetherra.aetherra_core.os_kernel")
    kernel = mod.get_kernel()
    # attach controller if not present
    if not getattr(kernel, "hmr_controller", None):
        reg_mod = importlib.import_module("aetherra_service_registry")
        registry = getattr(reg_mod, "get_service_registry")()
        ctrl = mod.HMRController(registry, kernel, strict=True)
        # simulate start
        import asyncio

        asyncio.get_event_loop().run_until_complete(ctrl.start())
        kernel.hmr_controller = ctrl

    # attempt a reload with an unlisted source
    import asyncio

    async def run():
        res = await kernel.hmr_controller.handle_kernel_task(
            {
                "type": "hmr_reload",
                "data": {"target": "engine", "source": "not.allowed"},
            }
        )
        return res

    res = asyncio.get_event_loop().run_until_complete(run())
    assert res.get("ok") is False
    assert res.get("error") == "source_not_allowed"


def test_inflight_shows_up_in_status(monkeypatch):
    mod = importlib.import_module("Aetherra.aetherra_core.os_kernel")
    kernel = mod.get_kernel()
    # simulate inflight increments
    if hasattr(kernel, "_inflight_inc") and hasattr(kernel, "_inflight_dec"):
        kernel._inflight_inc("adapter:plugin")
        s = kernel.get_status()
        assert s.get("inflight", {}).get("adapter:plugin", 0) >= 1
        kernel._inflight_dec("adapter:plugin")

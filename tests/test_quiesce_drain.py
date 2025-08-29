import asyncio
import importlib


def test_quiesce_waits_for_inflight_to_drain():
    mod = importlib.import_module("Aetherra.aetherra_core.os_kernel")
    kernel = mod.get_kernel()

    # simulate some in-flight work for adapter:plugin
    if not hasattr(kernel, "_inflight_inc"):
        return  # skip if not available

    kernel._inflight_inc("adapter:plugin")

    async def drain_later():
        await asyncio.sleep(0.1)
        kernel._inflight_dec("adapter:plugin")

    loop = asyncio.get_event_loop()
    loop.create_task(drain_later())

    async def run_quiesce():
        return await kernel.quiesce_for_target("adapter:plugin", timeout_sec=5)

    ok = loop.run_until_complete(run_quiesce())
    assert ok is True

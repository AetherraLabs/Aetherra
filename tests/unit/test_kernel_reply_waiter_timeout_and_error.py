# SPDX-License-Identifier: GPL-3.0-or-later
# Additional tests for kernel submit_plugin_invoke_and_wait timeout and error paths

# Standard library imports
import asyncio

# Third party imports
import pytest

# Aetherra imports
from aetherra_kernel_loop import AetherraKernelLoop


class SlowPluginManager:
    async def invoke_plugin(self, data):
        # Sleep longer than requested timeout to force timeout
        await asyncio.sleep(1.0)
        return {"ok": True}


class ErrorPluginManager:
    async def invoke_plugin(self, data):
        raise RuntimeError("boom")


async def _drain_once(kernel: AetherraKernelLoop):
    task = await asyncio.wait_for(kernel.normal_priority_queue.get(), timeout=1.0)
    await kernel._execute_task(task)


@pytest.mark.asyncio
async def test_waiter_times_out_and_raises():
    kernel = AetherraKernelLoop()
    kernel.inject_systems(None, SlowPluginManager(), None, None, None)

    drain_task = asyncio.create_task(_drain_once(kernel))

    with pytest.raises(asyncio.TimeoutError):
        await kernel.submit_plugin_invoke_and_wait(
            "slow-plugin",
            capability="cpu:optimize",
            timeout_sec=0.2,
            requester="tester",
            wait_timeout=0.3,
        )

    await asyncio.wait_for(drain_task, timeout=1.0)


@pytest.mark.asyncio
async def test_waiter_propagates_errors():
    kernel = AetherraKernelLoop()
    kernel.inject_systems(None, ErrorPluginManager(), None, None, None)

    drain_task = asyncio.create_task(_drain_once(kernel))

    with pytest.raises(RuntimeError):
        await kernel.submit_plugin_invoke_and_wait(
            "err-plugin",
            capability="cpu:optimize",
            requester="tester",
            timeout_sec=0.5,
            wait_timeout=0.6,
        )

    await asyncio.wait_for(drain_task, timeout=1.0)

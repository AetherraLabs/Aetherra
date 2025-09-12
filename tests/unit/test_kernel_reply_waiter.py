# SPDX-License-Identifier: GPL-3.0-or-later
# Unit test for kernel submit_plugin_invoke_and_wait (reply waiter path)

import asyncio

import pytest

from aetherra_kernel_loop import AetherraKernelLoop


class MockPluginManager:
    async def invoke_plugin(self, data):
        # Echo back a simplified result
        return {
            "ok": True,
            "name": data.get("name"),
            "args": data.get("args"),
            "kwargs": data.get("kwargs"),
            "cap": data.get("capability") or data.get("cap"),
        }


async def _drain_once(kernel: AetherraKernelLoop):
    # Drain a single task from the normal queue and execute it
    task = await asyncio.wait_for(kernel.normal_priority_queue.get(), timeout=1.0)
    await kernel._execute_task(task)


@pytest.mark.asyncio
async def test_submit_plugin_invoke_and_wait_success():
    kernel = AetherraKernelLoop()
    # inject mock plugin manager
    kernel.inject_systems(None, MockPluginManager(), None, None, None)

    # Start a one-shot drain task to process the enqueued invoke
    drain_task = asyncio.create_task(_drain_once(kernel))

    result = await kernel.submit_plugin_invoke_and_wait(
        "optimizer",
        capability="cpu:optimize",
        kwargs={"text": "hello"},
        timeout_sec=2.0,
        requester="tester",
        wait_timeout=3.0,
    )

    # Validate result fulfilled by reply waiter
    assert result["ok"] is True
    assert result["name"] == "optimizer"
    assert result["kwargs"]["text"] == "hello"
    assert result["cap"] == "cpu:optimize"

    # Ensure drain task completed
    await asyncio.wait_for(drain_task, timeout=1.0)

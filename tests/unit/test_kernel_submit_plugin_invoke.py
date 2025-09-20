# SPDX-License-Identifier: GPL-3.0-or-later
# Basic unit test for kernel submit_plugin_invoke envelope formation

# Standard library imports
import asyncio

# Aetherra imports
from aetherra_kernel_loop import AetherraKernelLoop


async def drain_one(q):
    return await asyncio.wait_for(q.get(), timeout=1.0)


def test_submit_plugin_invoke_envelope():
    loop = AetherraKernelLoop()

    async def run():
        # Avoid starting full kernel; just enqueue via helper
        await loop.submit_plugin_invoke(
            "executor",
            capability="os:execute",
            args=["run"],
            kwargs={"cmd": "echo hi"},
            timeout_sec=5.5,
            memory_mb=128,
            requester="agent.executor",
            priority="high",
        )
        # Pull from the high-priority queue and inspect shape
        task = await drain_one(loop.high_priority_queue)
        assert task["type"] == "plugin_invoke"
        data = task["data"]
        assert data["name"] == "executor"
        assert data["capability"] == "os:execute"
        assert data["args"] == ["run"]
        assert data["kwargs"]["cmd"] == "echo hi"
        # numeric types preserved
        assert data["timeout_sec"] == 5.5
        assert data["memory_mb"] == 128
        # envelope fields exist
        assert task.get("trace_id") and task.get("enqueued_ts")

    asyncio.run(run())

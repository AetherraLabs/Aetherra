# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio
import importlib


def test_quiesce_waits_for_inflight_to_drain():
    mod = importlib.import_module("Aetherra.aetherra_core.os_kernel")
    kernel = mod.AetherraKernelLoop()
    kernel._inflight_inc("adapter:plugin")

    async def run_quiesce():
        task = asyncio.create_task(
            kernel.quiesce_for_target("adapter:plugin", timeout_sec=5)
        )
        try:
            # Let quiesce start while work is still in flight.
            await asyncio.sleep(0)
            assert not task.done()
            kernel._inflight_dec("adapter:plugin")
            assert await asyncio.wait_for(task, timeout=1) is True
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(run_quiesce())

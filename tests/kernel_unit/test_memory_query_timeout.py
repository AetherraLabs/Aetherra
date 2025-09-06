#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Kernel memory_query timeout path coverage.

Creates a stub memory system whose process_query sleeps longer than a forced
per-task timeout to exercise asyncio.wait_for timeout handling in _execute_task.
"""

import asyncio

import pytest

from aetherra_kernel_loop import AetherraKernelLoop

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_memory_query_timeout():
    kernel = AetherraKernelLoop()

    class SlowMemory:
        def __init__(self):
            self.calls = 0

        async def process_query(self, data):  # pragma: no cover - simple
            self.calls += 1
            await asyncio.sleep(0.2)  # > timeout

    mem = SlowMemory()
    kernel.inject_systems(mem, None, None, None, None)

    task = {"type": "memory_query", "timeout_sec": 0.05, "data": {"q": "x"}}

    # Execute directly (white-box)
    await kernel._execute_task(task)
    assert mem.calls == 1
    # No explicit metric today for memory timeouts; just ensure no crash.

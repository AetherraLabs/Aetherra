#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Kernel circuit breaker open path coverage.

Forces plugin invoke failures until circuit opens, then verifies subsequent
invoke is short-circuited without calling plugin manager.
"""

import pytest

from aetherra_kernel_loop import AetherraKernelLoop

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_plugin_circuit_breaker_opens(monkeypatch):
    # Threshold=1 so first failure opens immediately
    monkeypatch.setenv("AETHERRA_PLUGIN_CB_THRESHOLD", "1")
    monkeypatch.setenv("AETHERRA_PLUGIN_CB_COOLDOWN_SEC", "5")

    kernel = AetherraKernelLoop()

    class FailingPluginMgr:
        def __init__(self):
            self.calls = 0

        async def invoke_plugin(self, data):  # pragma: no cover - trivial body
            self.calls += 1
            raise RuntimeError("boom")

        async def execute_scheduled_tasks(self):  # pragma: no cover
            return

    pm = FailingPluginMgr()
    kernel.inject_systems(None, pm, None, None, None)

    task = {"type": "plugin_invoke", "data": {"plugin_id": "failer"}}
    await kernel._execute_task(task)  # first failure -> open breaker
    assert pm.calls == 1

    # Second invoke should be dropped (short-circuit) without calling plugin
    await kernel._execute_task(task)
    assert pm.calls == 1, "circuit breaker did not short-circuit second call"

    status = kernel.get_status()
    metrics = status.get("metrics", {})
    assert metrics.get("plugin_cb_open_count", 0) >= 1
    assert metrics.get("plugin_cb_dropped", 0) >= 1

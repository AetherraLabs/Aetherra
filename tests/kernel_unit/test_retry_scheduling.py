#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Kernel retry scheduling coverage for plugin invoke timeouts.

Configures retry_max=1 and a tiny timeout so that one timeout triggers a retry
scheduling path inside _maybe_retry.
"""

import asyncio

import pytest

from aetherra_kernel_loop import AetherraKernelLoop

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_plugin_timeout_retry_schedules(monkeypatch):
    monkeypatch.setenv("AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC", "0.05")
    monkeypatch.setenv("AETHERRA_KERNEL_RETRY_MAX", "1")
    monkeypatch.setenv("AETHERRA_KERNEL_RETRY_BASE_DELAY_MS", "10")

    kernel = AetherraKernelLoop()

    class SlowPluginMgr:
        async def invoke_plugin(self, data):  # pragma: no cover - trivial
            await asyncio.sleep(0.2)

        async def execute_scheduled_tasks(self):  # pragma: no cover
            return

    pm = SlowPluginMgr()
    kernel.inject_systems(None, pm, None, None, None)

    task = {"type": "plugin_invoke", "data": {"plugin_id": "slow"}, "timeout_sec": 0.05}
    await kernel._execute_task(task)

    metrics = kernel.get_status().get("metrics", {})
    # Should have one timeout and one retry scheduled
    assert metrics.get("plugin_invoke_timeouts", 0) >= 1
    assert metrics.get("plugin_invoke_retries_scheduled", 0) >= 1

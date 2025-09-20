#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Failure injection: plugin invoke timeout should increment timeout metrics.

This test runs the kernel loop in isolation with a stub plugin manager to produce a
deterministic timeout (sleep > configured timeout). We avoid the full OS launcher here
to reduce variability and external dependencies (LLM providers, hub, etc.).
"""

# Standard library imports
import asyncio

# Third party imports
import pytest

# Aetherra imports
from aetherra_kernel_loop import AetherraKernelLoop  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_plugin_invoke_timeout(monkeypatch):
    # Configure a very small global plugin invoke timeout
    monkeypatch.setenv("AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC", "0.05")

    # Create kernel and stub plugin manager that always sleeps longer than timeout
    kernel = AetherraKernelLoop()

    class StubPluginManager:
        async def invoke_plugin(
            self, data
        ):  # pragma: no cover - body intentionally simple
            await asyncio.sleep(0.2)  # > 0.05 -> guarantee TimeoutError in wait_for
            return {"ok": True}

        async def execute_scheduled_tasks(self):  # pragma: no cover
            return

        async def get_health_status(self):  # pragma: no cover
            return "ok"

    stub = StubPluginManager()
    # Inject only the plugin manager (others can be None safely for this short run)
    kernel.inject_systems(None, stub, None, None, None)

    # Instead of spinning full loops (which sleep), directly invoke the internal executor for speed/determinism.
    # This hits the same code path executed from queue processing.
    task = {
        "type": "plugin_invoke",
        "timeout_sec": 0.05,
        "data": {"plugin_id": "stub_plugin", "action": "demo"},
    }
    # Call the private executor (test-level white-box acceptable for failure injection)
    await kernel._execute_task(task)  # type: ignore[attr-defined]

    status = kernel.get_status()
    metrics = status.get("metrics", {})
    timeout_count = metrics.get("plugin_invoke_timeouts", 0)
    error_count = metrics.get("plugin_invoke_errors", 0)
    assert (
        timeout_count > 0 or error_count > 0
    ), f"Expected timeout/error metric increment. Metrics: {metrics}"

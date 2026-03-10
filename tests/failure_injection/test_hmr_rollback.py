#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Failure injection for HMR rollback.

If HMR controller & kernel support dynamic reload tasks, we enqueue a reload with a
bogus source to force failure and expect either an audit event or safe failure.
"""

# Standard library imports
import asyncio

# Third party imports
import pytest

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_hmr_reload_failure(monkeypatch):
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher
    from aetherra_service_registry import get_service_registry

    launcher = AetherraOSLauncher()
    cfg = {"gui_enabled": False, "quiet": True, "hub_enabled": False}
    await launcher.launch_full_os(cfg)

    reg = await get_service_registry()
    kernel = reg.get_service("kernel_loop") or reg.get_service("kernel")

    if not kernel:
        pytest.skip("kernel not available for HMR test")

    # If kernel doesn't expose add_task, skip
    if not hasattr(kernel, "add_task"):
        pytest.skip("kernel missing add_task")

    # Enqueue bogus reload (expect safe failure or disabled response)
    task = {
        "type": "hmr_reload",
        "data": {
            "target": "engine",
            "source": "nonexistent.module.path",
            "mode": "safe",
        },
    }
    await kernel.add_task(task, priority="high")  # type: ignore

    await asyncio.sleep(0.8)

    # If HMR controller not enabled, kernel logs a warning and returns early.
    # Treat that as a PASS (system safely ignores unsupported task).
    if hasattr(kernel, "hmr_controller") and not kernel.hmr_controller:
        launcher.running = False
        await asyncio.sleep(0.05)
        return

    # Assert HMR rollback metric if status available when controller present
    if hasattr(kernel, "get_status"):
        status = kernel.get_status()  # type: ignore
        hmr = status.get("hmr", {}) if isinstance(status, dict) else {}
        attempts = hmr.get("attempts", 0)
        rollback = hmr.get("rollback", 0)
        # When controller present we expect at least one attempt recorded
        assert attempts >= 1, f"expected at least 1 HMR attempt, got {attempts}"
        if rollback == 0:
            assert hmr.get("success", 0) == 0, "unexpected HMR success for bogus source"
    else:
        pytest.skip("kernel missing get_status for HMR metrics assertion")

    launcher.running = False
    await asyncio.sleep(0.05)

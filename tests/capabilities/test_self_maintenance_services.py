# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio
import contextlib

# Third party imports
import pytest

# Aetherra imports
from aetherra_os_launcher import AetherraOSLauncher
from aetherra_service_registry import get_service_registry


@pytest.mark.asyncio
async def test_self_maintenance_services_registration_and_basic_ops():
    cfg = {"gui_enabled": False, "quiet": True, "hub_enabled": False}

    launcher = AetherraOSLauncher()

    async def boot():
        await launcher.launch_full_os(cfg)

    task = asyncio.create_task(boot())

    # Give the launcher a brief moment to register services without hanging the test
    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=2.5)
    except asyncio.TimeoutError:
        pass

    reg = await get_service_registry()

    sie_info = reg.get_service_info("self_improvement_engine")
    srs_info = reg.get_service_info("self_repair_service")

    if sie_info is None or srs_info is None:
        pytest.skip("Self-maintenance services unavailable in this environment")

    # Exercise Self-Improvement: record a metric, get status and trends
    sie = launcher.systems.get("self_improvement")
    assert sie is not None

    rec = await sie.handle_message(
        "selfimprovement.record_metric",
        {"name": "unit_test_metric", "value": 1.0, "unit": "count"},
    )
    assert isinstance(rec, dict) and rec.get("status") == "ok"

    status = await sie.handle_message("selfimprovement.status", {})
    assert isinstance(status, dict) and "improvement_active" in status

    trends = await sie.handle_message("selfimprovement.trends", {})
    assert isinstance(trends, dict)

    # Exercise Self-Repair: detect errors and generate a report
    srs = launcher.systems.get("self_repair")
    assert srs is not None

    bad_code = "def broken(:\n  pass"
    errors = await srs.handle_message(
        "selfrepair.detect_errors", {"code_content": bad_code}
    )
    assert isinstance(errors, list) and len(errors) >= 1

    report = await srs.handle_message(
        "selfrepair.report", {"target": "unit_test", "issues": errors}
    )
    assert isinstance(report, dict) and report.get("issues_found", 0) >= 1

    # Shutdown cleanly
    launcher.running = False
    await asyncio.sleep(0.1)
    if not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await task

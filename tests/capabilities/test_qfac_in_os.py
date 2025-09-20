# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio
import contextlib
import os

# Third party imports
import pytest

# Aetherra imports
from aetherra_os_launcher import AetherraOSLauncher
from aetherra_service_registry import (
    ServiceStatus,
    get_service_registry,
    shutdown_service_registry,
)


@pytest.mark.asyncio
async def test_qfac_optional_service_registration():
    cfg = {"gui_enabled": False, "quiet": True, "hub_enabled": False}

    os.environ["AETHERRA_QFAC_IN_OS"] = "1"
    os.environ["AETHERRA_QFAC_MODE"] = "hybrid"

    launcher = AetherraOSLauncher()

    async def boot():
        await launcher.launch_full_os(cfg)

    task = asyncio.create_task(boot())

    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=2.5)
    except asyncio.TimeoutError:
        pass

    reg = await get_service_registry()

    qfac_info = reg.get_service_info("qfac_memory_system")
    if qfac_info is None:
        pytest.skip("QFAC not available in this environment")

    assert qfac_info is not None
    # Registry metadata sanity
    assert qfac_info.metadata.get("qfac_mode") in {"classical", "hybrid", "quantum"}
    # Should reflect the env value we set above
    assert qfac_info.metadata.get("qfac_mode") == os.environ["AETHERRA_QFAC_MODE"]
    # Optional extra metadata set by launcher
    assert qfac_info.metadata.get("type") == "memory_extension"
    assert qfac_info.metadata.get("version") == "1.0"
    # Health status should be healthy once registered without dependencies
    assert qfac_info.status == ServiceStatus.HEALTHY

    # Also visible via list_services() with healthy status
    all_services = reg.list_services()
    assert "qfac_memory_system" in all_services
    assert all_services["qfac_memory_system"].status == ServiceStatus.HEALTHY

    # Simple lifecycle smoke: store and retrieve via the system reference
    qfac = launcher.systems.get("qfac_memory")
    assert qfac is not None

    node_id = await qfac.store_memory({"text": "hello"}, "qfac_os_smoke")
    data = await qfac.retrieve_memory(node_id)
    assert data.get("text") == "hello"

    # System status shape sanity
    status = await qfac.get_system_status()
    assert isinstance(status, dict)
    for key in ("node_statistics", "size_statistics", "system_health"):
        assert key in status
    assert "total_nodes" in status["node_statistics"]
    assert "overall_compression_ratio" in status["size_statistics"]

    # Dashboard summary should be callable. If stub, it returns unavailable.
    if hasattr(qfac, "dashboard") and qfac.dashboard is not None:
        summary = await qfac.dashboard.get_dashboard_summary()
        assert isinstance(summary, dict)
        assert "status" in summary
        if summary.get("status") == "unavailable":
            # Fallback stub path
            assert summary.get("reason") == "dashboard stub"
        else:
            # Real dashboard path: expect rich metrics
            assert summary.get("status") == "ok"
            assert "performance" in summary
            perf = summary["performance"]
            assert isinstance(perf, dict)
            assert "overall_health" in perf
            assert "performance_by_type" in perf
            assert "phases" in summary

    # Shutdown
    launcher.running = False
    await asyncio.sleep(0.1)
    if not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await task

    # Reset registry to avoid re-registration warnings in subsequent tests
    await shutdown_service_registry()

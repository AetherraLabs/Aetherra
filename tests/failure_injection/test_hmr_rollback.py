#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""A missing HMR source must fail safely without replacing the active engine.

Exercise the real kernel executor and HMR controller directly. The OS launcher
owns a lifetime loop, so awaiting launch_full_os cannot be a test setup step.
"""

# Standard library imports
import asyncio
import json

# Third party imports
import pytest

# Aetherra imports
from aetherra_hmr_controller import HMRController
from aetherra_kernel_loop import AetherraKernelLoop
from aetherra_service_registry import AetherraServiceRegistry

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", [False, True])
async def test_hmr_reload_failure(monkeypatch, tmp_path, enabled):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    source = str(tmp_path / "missing_hmr_source.py")
    monkeypatch.setenv("AETHERRA_HMR_ALLOWED_SOURCES", source)
    audit_path = tmp_path / "hmr_audit.jsonl"
    monkeypatch.setenv("AETHERRA_HMR_AUDIT_PATH", str(audit_path))
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)

    kernel = AetherraKernelLoop()
    original_engine = object()
    kernel.aetherra_engine = original_engine
    if enabled:
        kernel.hmr_controller = HMRController(
            AetherraServiceRegistry(), kernel, strict=True
        )

    result = await asyncio.wait_for(
        kernel._execute_task(
            {
                "type": "hmr_reload",
                "data": {"target": "engine", "source": source, "mode": "safe"},
            }
        ),
        timeout=5.0,
    )

    assert result == {
        "ok": False,
        "error": "load_failed" if enabled else "hmr_disabled",
    }
    assert kernel.aetherra_engine is original_engine
    metrics = kernel.get_status()["hmr"]
    assert metrics["attempts"] == int(enabled)
    assert metrics["success"] == 0
    if enabled:
        entries = [json.loads(line) for line in audit_path.read_text().splitlines()]
        assert entries[-1]["event"] == "load_failed"
        assert entries[-1]["ok"] is False

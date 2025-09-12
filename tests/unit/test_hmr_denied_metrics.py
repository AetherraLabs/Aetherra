import importlib
import re
import sys

import pytest

# We will simulate HMR enabled with production profile but missing strict/allowed envs
# to trigger the denial path and metrics increment.


@pytest.mark.asyncio
async def test_hmr_denied_metric_increments(monkeypatch):
    # Ensure fresh module import (launcher holds global state)
    if "aetherra_os_launcher" in sys.modules:
        importlib.reload(importlib.import_module("aetherra_os_launcher"))
    # Set environment for production + HMR enabled but without strict + allowed sources
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_HMR_ENABLED", "1")
    # Intentionally omit AETHERRA_HMR_STRICT and AETHERRA_HMR_ALLOWED_SOURCES
    # Provide prod overrides required by hub prod guard to avoid early abort
    monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "t")
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_SCRIPT_VERIFY", "1")
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    monkeypatch.setenv("AETHERRA_NETWORK_STRICT", "1")
    monkeypatch.setenv("AETHERRA_PROD_UNSAFE_ALLOW", "1")  # allow unsafe for test

    # Launch minimal path: import launcher and construct, then invoke _load_core_systems directly
    from aetherra_os_launcher import AetherraOSLauncher

    launcher = AetherraOSLauncher()
    # We only need service registry and core systems up to HMR attempt
    await launcher._initialize_service_registry()
    try:
        await launcher._load_core_systems({})
    except Exception:
        # HMR denial raises RuntimeError("hmr_requirements_not_met") which is fine
        pass

    # Now scrape metrics via hub metrics module builder directly (lighter than HTTP)
    from aetherra_hub.services.metrics_accum import build_all_metrics_lines

    lines = build_all_metrics_lines()
    body = "\n".join(lines)
    # Assert total counter incremented
    assert re.search(r"^aetherra_hmr_denied_total\s+1$", body, re.MULTILINE), body
    # Assert reason counter present
    assert re.search(
        r'aetherra_hmr_denied_reasons_total\{reason="requirements_not_met"\}\s+1', body
    ), body

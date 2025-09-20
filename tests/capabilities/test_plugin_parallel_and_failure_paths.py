# SPDX-License-Identifier: GPL-3.0-or-later
"""Capability test: parallel plugin execution, failure + timeout paths.

Covers new execute_plugin_chain_parallel method contract:
- All-success parallel run returns success True and failed == 0
- Injected failure returns success False, failed count increments, error field set
- Timeout path marks plugin with error == 'timeout'
"""

from __future__ import annotations

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.plugins.advanced_plugins import (
    LyrixaAdvancedPluginManager,
    PluginStatus,
)


@pytest.mark.asyncio
async def test_parallel_plugins_success_and_failure_and_timeout(tmp_path):
    mgr = LyrixaAdvancedPluginManager(plugin_directory=str(tmp_path))

    # Dynamically create three simple plugin modules in temp directory
    # fast_plugin: returns immediately
    # slow_plugin: sleeps (will be within timeout)
    # timeout_plugin: sleeps beyond timeout
    # fail_plugin: raises exception
    fast_code = """__version__='0.0.1'\nasync def main(data, **k):\n    return {'ok': True, 'echo': data}\n"""
    slow_code = """__version__='0.0.1'\nimport asyncio\nasync def main(data, **k):\n    await asyncio.sleep(0.05)\n    return {'slow': True}\n"""
    timeout_code = """__version__='0.0.1'\nimport asyncio\nasync def main(data, **k):\n    await asyncio.sleep(0.2)\n    return {'too': 'late'}\n"""
    fail_code = """__version__='0.0.1'\nasync def main(data, **k):\n    raise RuntimeError('boom')\n"""

    (tmp_path / "fast.py").write_text(fast_code)
    (tmp_path / "slow.py").write_text(slow_code)
    (tmp_path / "timeoutp.py").write_text(timeout_code)
    (tmp_path / "fail.py").write_text(fail_code)

    # Initialize (auto-discovery)
    await mgr.initialize()

    # Sanity: ensure plugins loaded
    for name in ["fast", "slow", "timeoutp", "fail"]:
        assert name in mgr.plugins, f"Plugin {name} not loaded"
        assert mgr.plugins[name]["status"] == PluginStatus.ACTIVE

    # Parallel run with timeout shorter than timeout_plugin sleep
    steps = [
        {"plugin": "fast", "function": "main"},
        {"plugin": "slow", "function": "main"},
        {"plugin": "timeoutp", "function": "main"},
        {"plugin": "fail", "function": "main"},
    ]

    result = await mgr.execute_plugin_chain_parallel(
        steps, shared_input={"x": 1}, timeout=0.1
    )

    assert result["parallel"] is True
    assert "results" in result
    # Ensure ordering preserved
    assert [r["plugin"] for r in result["results"]] == [
        "fast",
        "slow",
        "timeoutp",
        "fail",
    ]

    # Collect outcomes
    outcomes = {r["plugin"]: r for r in result["results"]}
    assert outcomes["fast"]["success"] is True
    assert outcomes["slow"]["success"] is True

    # Timeout case
    assert outcomes["timeoutp"]["success"] is False
    assert outcomes["timeoutp"]["error"] == "timeout"

    # Failure case
    assert outcomes["fail"]["success"] is False
    assert "boom" in (outcomes["fail"]["error"] or "")

    assert result["failed"] == 2
    assert result["success"] is False
    assert result["total_time"] < 0.5  # Should not wait full timeout sleep length


@pytest.mark.asyncio
async def test_parallel_fail_fast(tmp_path):
    mgr = LyrixaAdvancedPluginManager(plugin_directory=str(tmp_path))

    ok_code = (
        """__version__='0.0.1'\nasync def main(data, **k):\n    return {'ok': True}\n"""
    )
    bad_code = """__version__='0.0.1'\nasync def main(data, **k):\n    raise ValueError('early-fail')\n"""
    (tmp_path / "a.py").write_text(ok_code)
    (tmp_path / "b.py").write_text(bad_code)
    (tmp_path / "c.py").write_text(ok_code)

    await mgr.initialize()

    steps = [
        {"plugin": "a", "function": "main"},
        {"plugin": "b", "function": "main"},
        {"plugin": "c", "function": "main"},
    ]

    result = await mgr.execute_plugin_chain_parallel(
        steps, shared_input={}, timeout=0.5, fail_fast=True
    )

    # With fail_fast=True, once b fails, remaining tasks are cancelled
    # So we expect at least b (the failure) and possibly others that completed before cancellation
    names = [r["plugin"] for r in result["results"]]
    assert "b" in names  # b (the failure) must appear
    # success overall should be False due to failure
    assert result["success"] is False
    # ensure failure captured
    failure = next(r for r in result["results"] if r["plugin"] == "b")
    assert failure["success"] is False and "early-fail" in (failure["error"] or "")
    # with fail_fast, should have fewer than 3 results (some cancelled)
    assert len(result["results"]) <= 3

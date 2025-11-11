#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Additional runtime coverage: max-retries failure, tiny timeout fast-path,
retry=3 backoff duration, and metadata parity checks.
"""

import asyncio
import time

from aetherra_script_service import AetherScriptService


def run(script: str) -> dict:
    service = AetherScriptService()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(
        service.execute_script_content(script, filename="<workflow-additional>")
    )


def extract_steps(payload: dict) -> list[dict]:
    for rec in payload.get("result", {}).get("results", []):
        if rec.get("type") == "workflow":
            return rec.get("steps", [])
    return []


def test_max_retries_failure_path():
    script = """
    goal "max retries"
    workflow
        - fail_step retry=5
    """
    payload = run(script)
    assert payload.get("success") is True
    steps = extract_steps(payload)
    assert len(steps) == 1
    s = steps[0]
    assert s["success"] is False
    assert s["attempts"] == 6  # initial + 5 retries
    assert "error" in s
    assert isinstance(s["error"], str)
    # timing metadata
    assert isinstance(s.get("start_time"), float)
    assert isinstance(s.get("end_time"), float)
    assert isinstance(s.get("duration_ms"), float)
    assert s["end_time"] >= s["start_time"]


def test_tiny_timeout_fast_path():
    # Very small timeouts should trigger immediate timeout path without large sleeps.
    script = """
    goal "tiny timeout"
    workflow
        - slow_step timeout=5ms
    """
    t0 = time.time()
    payload = run(script)
    t1 = time.time()
    steps = extract_steps(payload)
    assert len(steps) == 1
    s = steps[0]
    assert s["success"] is False
    assert "Timeout" in s.get("error", "")
    wall = t1 - t0
    # Should be very quick (<0.1s on typical schedulers); allow leeway for CI.
    assert wall < 0.2, f"expected fast-path timeout under ~200ms, got {wall:.3f}s"
    assert s.get("duration_ms", 0.0) >= 0.0


def test_retry_three_backoff_duration():
    # retry=3 -> backoffs: 0.1 + 0.2 + 0.4 = 0.7s lower bound
    script = """
    goal "retry=3 backoff"
    workflow
        - fail_step retry=3
    """
    t0 = time.time()
    payload = run(script)
    t1 = time.time()
    steps = extract_steps(payload)
    assert len(steps) == 1
    s = steps[0]
    assert s["success"] is False
    assert s["attempts"] == 4
    wall = t1 - t0
    assert wall >= 0.6, f"expected at least ~0.6s (backoff), got {wall:.3f}s"
    assert float(s.get("duration_ms", 0)) >= 600.0


essential_keys = {"start_time", "end_time", "duration_ms", "attempts", "success"}


def test_metadata_parity_success_vs_failure():
    script = """
    goal "parity"
    workflow
        - load_data as good
        - fail_step retry=1
    """
    payload = run(script)
    steps = extract_steps(payload)
    assert len(steps) == 2
    a, b = steps
    # success step
    assert a["success"] is True
    assert set(a.keys()) >= essential_keys
    assert "result" in a
    assert isinstance(a["result"], str)
    assert "error" not in a or a["error"] in (None, "")
    # failure step
    assert b["success"] is False
    assert set(b.keys()) >= essential_keys
    assert "error" in b
    assert isinstance(b["error"], str)
    assert "result" not in b or b["result"] in (None, "")

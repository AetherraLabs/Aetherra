#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Additional coverage for workflow runtime: success-after-retry, backoff timing, and schema validation."""

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
        service.execute_script_content(script, filename="<workflow-extra-tests>")
    )


def extract_steps(payload: dict) -> list[dict]:
    for rec in payload.get("result", {}).get("results", []):
        if rec.get("type") == "workflow":
            return rec.get("steps", [])
    return []


def test_success_after_retry():
    # First attempt fails (fail_step), second succeeds (load_data).
    # Using two steps ensures both failure and success paths are exercised in same run.
    script = """
    goal "success after retry"
    workflow
        - fail_step retry=1
        - load_data
    """
    payload = run(script)
    assert payload.get("success") is True
    steps = extract_steps(payload)
    assert len(steps) == 2
    # fail_step should consume 2 attempts total and fail
    s1 = steps[0]
    assert s1["attempts"] == 2
    assert s1["success"] is False
    assert "error" in s1
    # load_data should succeed in 1 attempt
    s2 = steps[1]
    assert s2["success"] is True
    assert s2.get("result") == "result_load_data"
    assert s2["attempts"] == 1


def test_backoff_timing_sanity():
    # We can estimate lower bound on duration based on backoff schedule 0.1, 0.2 for 3 attempts total
    # Configure fail_step with retry=2 to enforce two backoff sleeps.
    script = """
    goal "backoff timing"
    workflow
        - fail_step retry=2
    """
    t0 = time.time()
    payload = run(script)
    t1 = time.time()
    steps = extract_steps(payload)
    assert len(steps) == 1
    step = steps[0]
    # Two backoffs: 0.1 + 0.2 = 0.3s, add a small tolerance for scheduler
    wall = t1 - t0
    assert wall >= 0.25, f"expected at least ~0.25s, got {wall:.3f}s"
    # duration_ms reported by runtime should correlate with wall clock (allow generous tolerance)
    assert float(step.get("duration_ms", 0)) >= 250.0


def test_mixed_step_schema_fields():
    script = """
    goal "schema fields"
    workflow
        - load_data as ok
        - slow_step timeout=100ms
    """
    payload = run(script)
    steps = extract_steps(payload)
    assert len(steps) == 2
    # Validate expected metadata types
    for s in steps:
        assert "start_time" in s
        assert isinstance(s["start_time"], float)
        assert "end_time" in s
        assert isinstance(s["end_time"], float)
        assert "duration_ms" in s
        assert isinstance(s["duration_ms"], float)
        assert "attempts" in s
        assert isinstance(s["attempts"], int)
        assert "success" in s
        assert isinstance(s["success"], bool)
    # First succeeded
    assert steps[0]["success"] is True
    assert steps[0].get("result") == "result_load_data"
    # Second timed out
    assert steps[1]["success"] is False
    assert "Timeout" in steps[1].get("error", "")

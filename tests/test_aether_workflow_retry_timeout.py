#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Workflow retry + timeout execution tests."""

import asyncio

from aetherra_script_service import AetherScriptService


def run(script: str) -> dict:
    service = AetherScriptService()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(
        service.execute_script_content(script, filename="<retry-timeout-test>")
    )


def extract_steps(payload: dict) -> list[dict]:
    for rec in payload.get("result", {}).get("results", []):
        if rec.get("type") == "workflow":
            return rec.get("steps", [])
    return []


def test_retry_on_failure():
    script = """
    goal "retry failure"
    workflow
        - fail_step retry=3
    """
    payload = run(script)
    assert payload.get("success") is True
    steps = extract_steps(payload)
    assert len(steps) == 1
    step = steps[0]
    assert step["attempts"] == 4  # initial + 3 retries
    assert step["success"] is False
    # timing metadata present
    assert "start_time" in step
    assert "end_time" in step
    assert isinstance(step["start_time"], float)
    assert isinstance(step["end_time"], float)
    assert step["end_time"] >= step["start_time"]
    assert "error" in step


def test_timeout_enforcement():
    script = """
    goal "timeout"
    workflow
        - slow_step timeout=100ms
    """
    payload = run(script)
    assert payload.get("success") is True
    steps = extract_steps(payload)
    assert len(steps) == 1
    step = steps[0]
    assert step["success"] is False
    assert "Timeout" in step.get("error", "")
    # timing metadata present
    assert "start_time" in step
    assert "end_time" in step
    assert isinstance(step["start_time"], float)
    assert isinstance(step["end_time"], float)
    assert step["end_time"] >= step["start_time"]


def test_success_first_attempt():
    script = """
    goal "success immediate"
    workflow
        - load_data retry=2 timeout="2s" as data
    """
    payload = run(script)
    assert payload.get("success") is True
    steps = extract_steps(payload)
    assert len(steps) == 1
    step = steps[0]
    assert step["attempts"] == 1
    assert step["success"] is True
    assert step.get("result") == "result_load_data"
    assert isinstance(step.get("duration_ms"), float)
    assert step["duration_ms"] >= 0.0
    # timing metadata present
    assert "start_time" in step
    assert "end_time" in step
    assert isinstance(step["start_time"], float)
    assert isinstance(step["end_time"], float)
    assert step["end_time"] >= step["start_time"]


def test_alias_binding_success():
    script = """
    goal "alias binding"
    workflow
        - load_data as data
        - fail_step retry=1
    """
    payload = run(script)
    assert payload.get("success") is True
    steps = extract_steps(payload)
    assert len(steps) == 2
    first = steps[0]
    assert first.get("success") is True
    assert first.get("result") == "result_load_data"
    second = steps[1]
    assert second.get("attempts") == 2
    assert second.get("success") is False
    # timing metadata present
    assert "start_time" in second
    assert "end_time" in second
    assert isinstance(second["start_time"], float)
    assert isinstance(second["end_time"], float)
    assert second["end_time"] >= second["start_time"]

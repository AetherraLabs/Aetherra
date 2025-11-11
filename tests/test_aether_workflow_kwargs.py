#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Workflow kwargs and timeout normalization tests.
"""

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
        service.execute_script_content(script, filename="<workflow-kwargs-test>")
    )


def get_workflow(payload: dict) -> dict:
    for rec in payload.get("result", {}).get("results", []):
        if rec.get("type") == "workflow":
            return rec
    return {}


def test_workflow_step_kwargs_and_timeout_normalization():
    script = """
    goal "workflow kwargs"
    workflow
        - export_game(scene, target="rbxmx", quality=2) as out retry=2 timeout=30s requires=["render"]
    """
    payload = run(script)
    assert payload.get("success") is True
    wf = get_workflow(payload)
    assert wf
    steps = wf.get("steps", [])
    assert len(steps) == 1
    step = steps[0]
    # Args and kwargs parsed
    assert step["name"] == "export_game"
    assert step.get("args") == ["scene"]
    assert step.get("kwargs", {}).get("target") == "rbxmx"
    assert step.get("kwargs", {}).get("quality") == 2
    # Retry and requires preserved
    assert step.get("retry") == 2
    assert step.get("requires") == ["render"]
    # Timeout normalization
    assert step.get("timeout") == "30s"
    # Normalized seconds should be float(30.0)
    assert abs(step.get("timeout_secs") - 30.0) < 1e-6

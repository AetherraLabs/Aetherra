#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Workflow requires inheritance tests.
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
        service.execute_script_content(script, filename="<workflow-requires-test>")
    )


def test_workflow_requires_inheritance():
    """Workflow-level requires should merge into each step's requires field."""
    script = """
    goal "workflow requires inheritance"
    workflow
        requires = ["auth", "network"]
        - step_one requires=["storage"]
        - step_two
    """
    payload = run(script)
    assert payload.get("success") is True
    results = payload.get("result", {}).get("results", [])
    wf = [r for r in results if r.get("type") == "workflow"]
    assert len(wf) == 1
    steps = wf[0].get("steps", [])
    assert len(steps) == 2
    # step_one should have merged requires: auth, network, storage
    step1 = steps[0]
    assert sorted(step1.get("requires", [])) == ["auth", "network", "storage"]
    # step_two should inherit workflow requires only
    step2 = steps[1]
    assert sorted(step2.get("requires", [])) == ["auth", "network"]


def test_workflow_requires_deduplication():
    """Workflow and step requires should deduplicate common capabilities."""
    script = """
    goal "workflow requires dedupe"
    workflow
        requires = ["auth", "network"]
        - step_alpha requires=["network", "db"]
    """
    payload = run(script)
    assert payload.get("success") is True
    results = payload.get("result", {}).get("results", [])
    wf = [r for r in results if r.get("type") == "workflow"]
    assert len(wf) == 1
    steps = wf[0].get("steps", [])
    assert len(steps) == 1
    # step_alpha: auth, network, db (network not duplicated)
    step = steps[0]
    req = step.get("requires", [])
    assert len(req) == 3
    assert sorted(req) == ["auth", "db", "network"]

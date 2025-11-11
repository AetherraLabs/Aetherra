#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Policy duration normalization tests.
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
        service.execute_script_content(script, filename="<policy-duration-test>")
    )


def test_policy_duration_normalization_inline():
    """Policy statement with timeout/duration keys should produce *_secs fields."""
    script = """
    goal "inline policy durations"
    policy request_timeout=30s, retry_duration="2m"
    """
    payload = run(script)
    assert payload.get("success") is True
    policy = payload.get("result", {}).get("policy", {})
    assert policy.get("request_timeout") == "30s"
    assert policy.get("request_timeout_secs") == 30.0
    assert policy.get("retry_duration") == "2m"
    assert policy.get("retry_duration_secs") == 120.0


def test_policy_duration_normalization_block():
    """Policy block with timeout/duration keys should produce *_secs fields."""
    script = """
    goal "policy block durations"
    policy
        max_timeout = "5m"
        step_duration = 10
    """
    payload = run(script)
    assert payload.get("success") is True
    results = payload.get("result", {}).get("results", [])
    pol = [r for r in results if r.get("type") == "policy"]
    assert len(pol) == 1
    p = pol[0]
    assert p.get("max_timeout") == "5m"
    assert p.get("max_timeout_secs") == 300.0
    # step_duration is numeric → treat as seconds
    assert p.get("step_duration") == 10
    assert p.get("step_duration_secs") == 10.0

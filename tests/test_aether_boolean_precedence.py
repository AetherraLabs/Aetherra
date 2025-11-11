#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Boolean logic precedence tests (not > and > or).
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
        service.execute_script_content(script, filename="<bool-test>")
    )


def test_boolean_not_precedence_over_and():
    """not should bind tighter than and: not false and true => true and true => true."""
    script = """
    goal "bool precedence"
    result = not false and true
    """
    payload = run(script)
    assert payload.get("success") is True
    results = payload.get("result", {}).get("results", [])
    assign = [r for r in results if r.get("type") == "assignment"]
    assert len(assign) == 1
    # not false = true; true and true = true
    assert assign[0]["value"] is True


def test_boolean_and_precedence_over_or():
    """and should bind tighter than or: false or true and false => false or false => false."""
    script = """
    goal "bool precedence"
    result = false or true and false
    """
    payload = run(script)
    assert payload.get("success") is True
    results = payload.get("result", {}).get("results", [])
    assign = [r for r in results if r.get("type") == "assignment"]
    assert len(assign) == 1
    # (true and false) => false; false or false => false
    assert assign[0]["value"] is False


def test_boolean_parentheses_override():
    """Parentheses should override default precedence."""
    script = """
    goal "bool parentheses"
    result = (false or true) and false
    """
    payload = run(script)
    assert payload.get("success") is True
    results = payload.get("result", {}).get("results", [])
    assign = [r for r in results if r.get("type") == "assignment"]
    assert len(assign) == 1
    # (false or true) => true; true and false => false
    assert assign[0]["value"] is False


def test_boolean_with_comparisons():
    """Comparisons should be atoms within boolean expressions."""
    script = """
    goal "bool + comparison"
    a = 5
    b = 10
    result = a < b and b > 8
    """
    payload = run(script)
    assert payload.get("success") is True
    results = payload.get("result", {}).get("results", [])
    assign = [r for r in results if r.get("variable") == "result"]
    assert len(assign) == 1
    # 5 < 10 => true; 10 > 8 => true; true and true => true
    assert assign[0]["value"] is True

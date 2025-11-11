#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Arithmetic expression tests for the minimal interpreter:
- Precedence: * and / and % over + and -
- Parentheses grouping
- Unary minus
- Mixed with identifiers
- String concatenation with + remains supported
- Mixed with comparisons and booleans
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
        service.execute_script_content(script, filename="<arith-test>")
    )


def extract_assignments(payload: dict) -> dict:
    out = {}
    if payload.get("result") and "results" in payload["result"]:
        for res in payload["result"]["results"]:
            if res.get("type") in ("assignment", "typed_assignment"):
                out[res.get("variable", res.get("var"))] = res.get("value")
    return out


def test_precedence_basic():
    script = """
    goal "precedence"
    a = 2 + 3 * 4
    b = (2 + 3) * 4
    c = 7 % 4
    d = 7 / 2
    e = 10 - 3 * 2
    """
    payload = run(script)
    assert payload.get("success") is True
    vals = extract_assignments(payload)
    assert vals["a"] == 14
    assert vals["b"] == 20
    assert vals["c"] == 3
    assert vals["d"] == 3.5
    assert vals["e"] == 4


def test_unary_minus_and_identifiers():
    script = """
    goal "unary and idents"
    x = 10
    y = 3
    z = -2 * y + 4
    w = x - y * 2
    """
    payload = run(script)
    assert payload.get("success") is True
    vals = extract_assignments(payload)
    assert vals["z"] == -2
    assert vals["w"] == 4


def test_string_concatenation():
    script = """
    goal "strings"
    s = "a" + "b" + "c"
    """
    payload = run(script)
    assert payload.get("success") is True
    vals = extract_assignments(payload)
    assert vals["s"] == "abc"


def test_mixed_with_comparisons_and_booleans():
    script = """
    goal "mixed"
    a = 1 + 2
    b = 4 * 2
    # Below comparisons are not assignments; ensure they are evaluable in conditionals
    if a < 5
        x = 1
    else
        x = 0
    if (1 + 2) < 3 or b == 8
        y = 1
    else
        y = 0
    """
    payload = run(script)
    assert payload.get("success") is True
    vals = extract_assignments(payload)
    assert vals["x"] == 1
    assert vals["y"] == 1

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Transaction rollback plan tests.
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
        service.execute_script_content(script, filename="<rollback-test>")
    )


def test_transaction_rollback_plan_creation():
    """Transaction block should capture pre-transaction values in rollback_plan.

    New assignments during the transaction should list the prior value if any,
    or be listed for deletion if they are newly introduced.
    """
    script = """
    goal "rollback plan test"
    x = 10
    transaction
        x = 20
        y = 30
    """
    payload = run(script)
    assert payload.get("success") is True
    txs = payload.get("result", {}).get("transactions", [])
    assert len(txs) == 1
    tx = txs[0]
    assert tx.get("ops_count") == 2
    # rollback_plan should restore x to 10, delete y
    plan = tx.get("rollback_plan")
    assert plan is not None
    assert plan["restore"] == {"x": 10}
    assert plan["delete"] == ["y"]
    # token and registry
    assert "rollback_token" in tx
    registry = payload.get("result", {}).get("rollback_registry", {})
    assert tx["rollback_token"] in registry
    assert registry[tx["rollback_token"]] == plan


def test_transaction_simulated_error_flag():
    """simulate_error statement inside a transaction sets rollback_simulated to True."""
    script = """
    goal "rollback simulation"
    transaction
        x = 42
        simulate_error
        y = 99
    """
    payload = run(script)
    assert payload.get("success") is True
    txs = payload.get("result", {}).get("transactions", [])
    assert len(txs) == 1
    tx = txs[0]
    assert tx.get("rollback_simulated") is True
    # plan should include both assignments
    plan = tx.get("rollback_plan")
    assert "x" in plan["delete"] and "y" in plan["delete"]

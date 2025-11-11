# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Option 2 tests: parallel, await, transaction, policy block, require block, plugin_contract.
"""

import pytest

from aetherra_script_service import AetherScriptService


@pytest.mark.asyncio
async def test_parallel_and_await_basic():
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    # simple base assignments
    a = 1
    b = 2

    parallel
        x = "sys"
        y = "usr"

    await x, y

    z = x + y
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    types = [r.get("type") for r in payload["results"]]
    assert "parallel" in types
    assert "await" in types

    par = [r for r in payload["results"] if r.get("type") == "parallel"][0]
    assert set(par.get("tasks", [])) == {"x", "y"}
    assert par.get("count") == 2

    awaited = [r for r in payload["results"] if r.get("type") == "await"][0]
    assert awaited.get("vars") == ["x", "y"]

    # ensure assignment using awaited variables was performed
    assigns = [r for r in payload["results"] if r.get("type") == "assignment"]
    assert any(a.get("variable") == "z" and a.get("value") == "sysusr" for a in assigns)


@pytest.mark.asyncio
async def test_transaction_block_counts_ops():
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    transaction
        narrate "one"
        temp = 123
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    txn = [r for r in payload["results"] if r.get("type") == "transaction"][0]
    # two inner statements
    assert txn.get("ops") == 2


@pytest.mark.asyncio
async def test_policy_block_sets_context_and_result():
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    policy
        deterministic = true
        seed = 42
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    # result entry exists
    types = [r.get("type") for r in payload["results"]]
    assert "policy" in types

    pol = [r for r in payload["results"] if r.get("type") == "policy"][0]
    assert pol.get("deterministic") is True
    assert pol.get("seed") == 42

    # top-level payload should also expose policy
    assert payload.get("policy", {}).get("deterministic") is True
    assert payload.get("policy", {}).get("seed") == 42


@pytest.mark.asyncio
async def test_require_block_structural_capture():
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    require
        plugins:
            - "anomaly_detector>=0.3,<0.5"
            - "report_merger==1.2.1"
        capabilities: ["storage.write", "network.read"]
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    req = [r for r in payload["results"] if r.get("type") == "require"][0]
    assert req.get("plugins") == [
        "anomaly_detector>=0.3,<0.5",
        "report_merger==1.2.1",
    ]
    assert req.get("capabilities") == ["storage.write", "network.read"]


@pytest.mark.asyncio
async def test_plugin_contract_block():
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    plugin_contract
        id = "anomaly_detector"
        version = ">=0.3,<0.5"
        deterministic = true
        side_effects = false
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    pc = [r for r in payload["results"] if r.get("type") == "plugin_contract"][0]
    assert pc.get("id") == "anomaly_detector"
    assert pc.get("version") == ">=0.3,<0.5"
    assert pc.get("deterministic") is True
    assert pc.get("side_effects") is False

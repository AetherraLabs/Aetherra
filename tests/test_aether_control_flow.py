# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Tests for .aether control flow: conditionals, loops, workflows.
Following TDD approach - these tests define the expected behavior.
"""

# Third party imports
import pytest

# Aetherra imports
from aetherra_script_service import AetherScriptService


@pytest.mark.asyncio
async def test_simple_if_true_condition():
    """Test if statement with true condition executes block."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    value = 10

    if value > 5
        result = "high"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    # Should have assignment for value, conditional, and assignment for result
    types = [r.get("type") for r in payload["results"]]
    assert "assignment" in types
    assert "conditional" in types

    # Check that result was assigned
    assignments = [r for r in payload["results"] if r.get("type") == "assignment"]
    assert any(
        a.get("variable") == "result" and a.get("value") == "high" for a in assignments
    )


@pytest.mark.asyncio
async def test_simple_if_false_condition():
    """Test if statement with false condition skips block."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    value = 3

    if value > 5
        result = "high"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    # Should have assignment for value and conditional
    types = [r.get("type") for r in payload["results"]]
    assert "assignment" in types
    assert "conditional" in types

    # Result should NOT be assigned
    assignments = [r for r in payload["results"] if r.get("type") == "assignment"]
    assert not any(a.get("variable") == "result" for a in assignments)


@pytest.mark.asyncio
async def test_if_else_branches():
    """Test if/else branches execute correctly."""
    svc = AetherScriptService()
    await svc.initialize()

    script_true = """
    value = 10

    if value > 5
        result = "high"
    else
        result = "low"
    """

    result = await svc.execute_script_content(script_true, filename="<test>")
    assert result["success"] is True
    assignments = [
        r for r in result["result"]["results"] if r.get("type") == "assignment"
    ]
    assert any(
        a.get("variable") == "result" and a.get("value") == "high" for a in assignments
    )

    script_false = """
    value = 3

    if value > 5
        result = "high"
    else
        result = "low"
    """

    result = await svc.execute_script_content(script_false, filename="<test>")
    assert result["success"] is True
    assignments = [
        r for r in result["result"]["results"] if r.get("type") == "assignment"
    ]
    assert any(
        a.get("variable") == "result" and a.get("value") == "low" for a in assignments
    )


@pytest.mark.asyncio
async def test_if_elif_else_chain():
    """Test if/elif/else chain logic."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    score = 75

    if score >= 90
        grade = "A"
    elif score >= 80
        grade = "B"
    elif score >= 70
        grade = "C"
    else
        grade = "F"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    assignments = [
        r for r in result["result"]["results"] if r.get("type") == "assignment"
    ]
    assert any(
        a.get("variable") == "grade" and a.get("value") == "C" for a in assignments
    )


@pytest.mark.asyncio
async def test_comparison_operators():
    """Test various comparison operators in conditions."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    a = 10
    b = 20

    if a == 10
        result1 = "equal"

    if a != b
        result2 = "not_equal"

    if a < b
        result3 = "less_than"

    if b > a
        result4 = "greater_than"

    if a <= 10
        result5 = "less_equal"

    if b >= 20
        result6 = "greater_equal"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    assignments = [
        r for r in result["result"]["results"] if r.get("type") == "assignment"
    ]

    # All result variables should be assigned
    result_vars = {
        a["variable"]: a["value"]
        for a in assignments
        if a["variable"].startswith("result")
    }
    assert result_vars == {
        "result1": "equal",
        "result2": "not_equal",
        "result3": "less_than",
        "result4": "greater_than",
        "result5": "less_equal",
        "result6": "greater_equal",
    }


@pytest.mark.asyncio
async def test_boolean_operators():
    """Test and/or/not boolean operators."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    a = true
    b = false

    if a and b
        result1 = "both"

    if a or b
        result2 = "either"

    if not b
        result3 = "not_b"

    if a and not b
        result4 = "a_and_not_b"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    assignments = [
        r for r in result["result"]["results"] if r.get("type") == "assignment"
    ]

    result_vars = {
        a["variable"]: a["value"]
        for a in assignments
        if a["variable"].startswith("result")
    }
    assert "result1" not in result_vars  # a and b is false
    assert result_vars.get("result2") == "either"  # a or b is true
    assert result_vars.get("result3") == "not_b"  # not b is true
    assert result_vars.get("result4") == "a_and_not_b"  # a and not b is true


@pytest.mark.asyncio
async def test_for_loop_over_list():
    """Test for-in loop over a list."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    items = ["apple", "banana", "cherry"]
    count = 0

    for item in items
        count = count + 1
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    # Should have loop result
    types = [r.get("type") for r in payload["results"]]
    assert "for_loop" in types

    # Loop should execute 3 times - count final value
    loop_result = [r for r in payload["results"] if r.get("type") == "for_loop"][0]
    assert loop_result.get("iterations") == 3


@pytest.mark.asyncio
async def test_while_loop():
    """Test while loop with condition."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    counter = 0

    while counter < 5
        counter = counter + 1
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    # Should have while_loop result
    types = [r.get("type") for r in payload["results"]]
    assert "while_loop" in types

    # Loop should execute 5 times
    loop_result = [r for r in payload["results"] if r.get("type") == "while_loop"][0]
    assert loop_result.get("iterations") == 5


@pytest.mark.asyncio
async def test_nested_conditionals():
    """Test nested if statements."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    x = 10
    y = 20

    if x > 5
        if y > 15
            result = "both_high"
        else
            result = "x_high_y_low"
    else
        result = "x_low"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    assignments = [
        r for r in result["result"]["results"] if r.get("type") == "assignment"
    ]
    assert any(
        a.get("variable") == "result" and a.get("value") == "both_high"
        for a in assignments
    )


@pytest.mark.asyncio
async def test_workflow_simple():
    """Test basic workflow block with steps."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    goal "Process data workflow"

    workflow
        input = "data.json"
        - load_data
        - process_data
        - save_results
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    # Should have workflow result
    types = [r.get("type") for r in payload["results"]]
    assert "workflow" in types

    # Workflow should list steps
    workflow_result = [r for r in payload["results"] if r.get("type") == "workflow"][0]
    assert "steps" in workflow_result
    assert len(workflow_result["steps"]) == 3


@pytest.mark.asyncio
async def test_workflow_with_step_options():
    """Test workflow with step options (as, retry, timeout, requires)."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    workflow
        - load_data as data retry=2 timeout="30s"
        - process_data(data) as result requires=["compute"]
        - save_results(result)
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    workflow_result = [
        r for r in result["result"]["results"] if r.get("type") == "workflow"
    ][0]

    steps = workflow_result["steps"]
    assert len(steps) == 3

    # First step should have as, retry, timeout
    assert steps[0].get("name") == "load_data"
    assert steps[0].get("as") == "data"
    assert steps[0].get("retry") == 2
    assert steps[0].get("timeout") == "30s"

    # Second step should have args, as, requires
    assert steps[1].get("name") == "process_data"
    assert steps[1].get("args") == ["data"]
    assert steps[1].get("as") == "result"
    assert steps[1].get("requires") == ["compute"]


@pytest.mark.asyncio
async def test_meta_block():
    """Test meta block parsing."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    meta
        version = "1.1"
        author = "Test User"
        seed = 42

    goal "Test script"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    # Should have meta result
    types = [r.get("type") for r in payload["results"]]
    assert "meta" in types

    # Meta should contain all fields
    meta_result = [r for r in payload["results"] if r.get("type") == "meta"][0]
    assert meta_result.get("version") == "1.1"
    assert meta_result.get("author") == "Test User"
    assert meta_result.get("seed") == 42


@pytest.mark.asyncio
async def test_on_error_block():
    """Test on_error block parsing."""
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    on_error
        - when Timeout
          do escalate_to("Ops")
        - when PermissionError
          do narrate("Missing permission")

    goal "Test error handling"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]

    # Should have on_error result
    types = [r.get("type") for r in payload["results"]]
    assert "on_error" in types

    # Should have error handlers
    on_error_result = [r for r in payload["results"] if r.get("type") == "on_error"][0]
    handlers = on_error_result.get("handlers", [])
    assert len(handlers) == 2
    assert handlers[0]["when"] == "Timeout"
    assert "escalate_to" in handlers[0]["do"]
    assert handlers[1]["when"] == "PermissionError"
    assert "narrate" in handlers[1]["do"]

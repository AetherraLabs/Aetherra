# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Third party imports
import pytest

# Aetherra imports
from aetherra_script_service import AetherScriptService


@pytest.mark.asyncio
async def test_basic_goal_and_assignment():
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    # Simple goal
    goal "Improve developer experience"

    # Assignment
    user = "alice"

    remember "user alice logged in" as "auth"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]
    types = [r.get("type") for r in payload["results"]]

    # Ensure both goal and assignment recognized
    assert "goal" in types
    assert any(
        r.get("type") == "assignment" and r.get("variable") == "user"
        for r in payload["results"]
    )

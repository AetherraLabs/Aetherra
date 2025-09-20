# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Third party imports
import pytest

# Aetherra imports
from aetherra_script_service import AetherScriptService


class FakePlugins:
    def __init__(self):
        self.last_policy = None

    def set_policy(self, policy):
        self.last_policy = dict(policy)
        return {"success": True, "policy": self.last_policy}


@pytest.mark.asyncio
async def test_policy_sets_on_plugins_when_available():
    svc = AetherScriptService()
    await svc.initialize()
    fake = FakePlugins()

    script = """
    policy max_executions=2 allow_untrusted_secret=true
    goal "x"
    """

    result = await svc.execute_script_content(
        script, filename="<test>", context={"plugins": fake}
    )
    assert result["success"] is True
    results = result["result"]["results"]
    # First result should be policy_set
    assert results[0]["type"] == "policy_set"
    assert results[0]["policy"]["max_executions"] == 2
    assert results[0]["policy"]["allow_untrusted_secret"] is True
    # The fake plugin system received it
    assert fake.last_policy == {"max_executions": 2, "allow_untrusted_secret": True}


@pytest.mark.asyncio
async def test_policy_parses_without_plugins():
    svc = AetherScriptService()
    await svc.initialize()

    script = """
    policy max_executions=1
    goal "y"
    """

    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    results = result["result"]["results"]
    assert any(r.get("type") == "policy_set" for r in results)

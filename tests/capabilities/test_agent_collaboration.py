# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import pytest

from aetherra_service_registry import get_service_registry


@pytest.mark.asyncio
async def test_agent_collaboration_via_registry():
    registry = await get_service_registry()

    class Agent:
        def __init__(self, name):
            self.name = name
            self.shared = {}

        async def handle_message(self, msg_type, data):
            if msg_type == "set":
                self.shared[data["key"]] = data["value"]
            elif msg_type == "get":
                return self.shared.get(data["key"])  # pragma: no cover

    a1 = Agent("a1")
    a2 = Agent("a2")

    await registry.register_service("agent_a1", a1)
    await registry.register_service("agent_a2", a2)

    await registry.send_message("agent_a1", "set", {"key": "topic", "value": "X"})
    await registry.send_message("agent_a2", "set", {"key": "topic", "value": "X"})

    assert a1.shared.get("topic") == "X"
    assert a2.shared.get("topic") == "X"

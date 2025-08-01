#!/usr/bin/env python3
"""Test for the Lyrixa Agent Integration module"""

import asyncio

from Aetherra.lyrixa.interfaces.lyrixa_agent_integration import LyrixaAgentInterface


async def test_agent_interface():
    """Test the agent interface functionality"""
    print("Creating agent interface...")
    interface = LyrixaAgentInterface("test_workspace")

    print("Initializing...")
    init_result = await interface.initialize()
    print(f"Initialization result: {init_result}")

    print("Getting agent status...")
    status = await interface.get_agent_status()
    print(f"Agent Status: {status}")

    print("Executing test task...")
    task_result = await interface.execute_task(
        {"type": "test", "description": "This is a test task"}
    )
    print(f"Task result: {task_result}")

    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_agent_interface())

#!/usr/bin/env python3
"""
Final comprehensive test for the Lyrixa Agent Integration module.
Tests the agent interface's ability to update system availability and create components.
"""

import asyncio
import os
from pathlib import Path

from Aetherra.lyrixa.interfaces.lyrixa_agent_integration import LyrixaAgentInterface


async def test_system_availability_check():
    """Test the agent interface's ability to check and update system availability"""
    print("\n🔍 Testing system availability checking and component creation")

    # Create test directory
    test_dir = str(Path(__file__).parent / "test_workspace")
    os.makedirs(test_dir, exist_ok=True)

    # Initialize interface
    print("📋 Initializing interface...")
    interface = LyrixaAgentInterface(test_dir)
    await interface.initialize()

    # Check initial status
    status = await interface.get_agent_status()
    print(f"Initial system availability: {status['agent_system_available']}")

    # Try to create components
    print("\n🔧 Attempting to create components (should fail due to unavailability):")
    executor = await interface.create_agent_component("executor")
    print(f"  - Executor component created: {executor is not None}")

    manager = await interface.create_agent_component("manager")
    print(f"  - Manager component created: {manager is not None}")

    task = await interface.create_agent_component(
        "task", task_id="test_task", description="Test task"
    )
    print(f"  - Task component created: {task is not None}")

    # Update system availability
    print("\n🔄 Checking for system availability updates...")
    updated = await interface.update_system_availability()
    print(f"  - System availability updated: {updated}")
    status = await interface.get_agent_status()
    print(f"  - Current system availability: {status['agent_system_available']}")

    # Execute a test task
    print("\n🎯 Executing a test task with current availability...")
    result = await interface.execute_task(
        {
            "type": "integration_test",
            "description": "Testing agent system integration",
            "context": {"test_mode": True},
        }
    )

    print("\n📊 Task result:")
    for key, value in result.items():
        if isinstance(value, dict):
            print(f"  - {key}:")
            for subkey, subvalue in value.items():
                print(f"    - {subkey}: {subvalue}")
        else:
            print(f"  - {key}: {value}")

    print("\n✅ System availability test complete")


if __name__ == "__main__":
    asyncio.run(test_system_availability_check())

#!/usr/bin/env python3
"""
Comprehensive test for the Lyrixa Agent Integration module.
Tests various task types and agent interface functions.
"""

import asyncio
import json
import os
from typing import Any, Dict

from Aetherra.lyrixa.interfaces.lyrixa_agent_integration import LyrixaAgentInterface

# Create a test directory if it doesn't exist
TEST_DIR = os.path.join(os.path.dirname(__file__), "test_workspace")
os.makedirs(TEST_DIR, exist_ok=True)


async def test_task_execution(
    interface: LyrixaAgentInterface, task: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute a task and print formatted results"""
    print(f"\n📋 Testing task type: {task.get('type', 'unknown')}")
    print(f"Description: {task.get('description', 'No description')}")

    result = await interface.execute_task(task)

    # Pretty print the result
    print("\n📊 Result:")
    print(json.dumps(result, indent=2))

    return result


async def run_comprehensive_tests():
    """Run a comprehensive suite of tests for the LyrixaAgentInterface"""
    print("\n🚀 Starting comprehensive Lyrixa Agent Interface tests\n")
    print("=" * 80)

    # Initialize the interface
    print("\n[TOOL] Initializing agent interface...")
    interface = LyrixaAgentInterface(TEST_DIR)
    init_result = await interface.initialize()

    print(f"✅ Initialization result: {init_result}")

    # Test agent status
    print("\n📊 Getting agent status...")
    status = await interface.get_agent_status()
    print("Agent Status:")
    print(json.dumps(status, indent=2))

    # Test various task types
    tasks = [
        {
            "type": "conversation",
            "description": "Help me understand quantum computing",
            "context": {"conversation_id": "test_conversation_1"},
        },
        {
            "type": "analysis",
            "description": "Analyze the performance trends of the system",
            "context": {"data_source": "simulated_metrics"},
        },
        {
            "type": "research",
            "description": "Research the latest advancements in AI",
            "context": {"depth": "comprehensive"},
        },
        {
            "type": "code_generation",
            "description": "Generate a function to calculate Fibonacci sequence",
            "context": {"language": "python", "complexity": "medium"},
        },
        {
            "type": "test",
            "description": "Run unit tests for the core module",
            "context": {"test_suite": "core_tests"},
        },
        {
            "type": "general",
            "description": "Custom task with specific requirements",
            "context": {"custom_parameter": "custom_value"},
        },
    ]

    # Execute each task
    results = []
    for task in tasks:
        result = await test_task_execution(interface, task)
        results.append(result)

    # Test communication with another agent
    print("\n📡 Testing agent communication...")
    comm_result = await interface.communicate_with_agent(
        "test_target_agent", {"content": "Hello from Lyrixa test!", "type": "greeting"}
    )
    print("Communication result:")
    print(json.dumps(comm_result, indent=2))

    # Test task delegation
    print("\n🤝 Testing task delegation...")
    delegation_result = await interface.delegate_task(
        {"type": "delegated_task", "description": "This is a delegated task"},
        "test_assistant_agent",
    )
    print("Delegation result:")
    print(json.dumps(delegation_result, indent=2))

    # Get task queue
    print("\n📋 Getting task queue...")
    task_queue = interface.get_task_queue()
    print(f"Task queue size: {len(task_queue)}")

    # Get communication log
    print("\n📝 Getting communication log...")
    comm_log = interface.get_communication_log()
    print(f"Communication log size: {len(comm_log)}")

    print("\n" + "=" * 80)
    print(f"✅ All tests completed. Executed {len(tasks)} tasks.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())

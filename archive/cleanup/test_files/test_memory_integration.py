#!/usr/bin/env python3
"""
Test script for memory integration in the .aether interpreter.
"""

import asyncio

from lyrixa.core.aether_interpreter import AetherInterpreter
from lyrixa.core.memory import LyrixaMemorySystem


async def test_memory_operations():
    """
    Test memory operations in the .aether interpreter.
    """
    memory_system = LyrixaMemorySystem()
    interpreter = AetherInterpreter()

    # Simulate memory operations
    memory_ops = {
        "retrieve": {
            "from": "system.logs.daily",
            "limit": 1,
        },
        "store": {
            "content": {"summary": "Test log summary"},
            "context": {"source": "test_logs"},
            "tags": ["test", "logs"],
            "importance": 0.8,
            "type": "project",
        },
    }

    try:
        # Execute memory operations
        results = await interpreter.execute_memory_operations(memory_ops, memory_system)
        print("✅ Memory operations executed successfully")
        print(results)

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_memory_operations())

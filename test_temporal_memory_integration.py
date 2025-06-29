#!/usr/bin/env python3
"""
Test the enhanced memory system through the NeuroCode interpreter.
This test demonstrates the integration of temporal filtering with the enhanced interpreter.
"""

import os
import sys

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from interpreter import NeuroCodeInterpreter


def test_temporal_memory_integration():
    """Test temporal memory features through the interpreter"""
    print("🧠 Testing Memory Temporal Integration with NeuroCode Interpreter")
    print("=" * 60)

    interpreter = NeuroCodeInterpreter()

    # Test memory with time filtering
    test_commands = [
        'memory "Working on temporal enhancements" tags=["development", "memory"] category="work"',
        'memory "Testing new features" tags=["testing"] category="validation"',
        'memory "Great progress today" tags=["progress"] category="reflection"',
        'recall tags=["development"]',
        'recall category="work"',
        'recall time_filter="today"',
        "memory_stats",
    ]

    print("Testing temporal memory commands:")
    for cmd in test_commands:
        print(f"\n📝 Command: {cmd}")
        try:
            result = interpreter.execute(cmd)
            print(f"✅ Result: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n🎯 Temporal memory integration test completed!")


if __name__ == "__main__":
    test_temporal_memory_integration()

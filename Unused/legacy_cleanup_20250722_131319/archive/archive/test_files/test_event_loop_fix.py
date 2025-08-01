#!/usr/bin/env python3
"""Test the event loop fix for intelligence stack"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.intelligence_integration import LyrixaIntelligenceStack


def test_event_loop_fix():
    """Test that generate_response doesn't cause event loop errors"""
    print("Testing event loop fix...")

    # Create intelligence stack
    workspace_path = str(project_root)
    intelligence_stack = LyrixaIntelligenceStack(workspace_path)

    # Test the sync method that was causing issues
    test_messages = [
        "what is aetherra",
        "what si aetherra",
        "hello",
        "help me",
        "system status",
    ]

    for message in test_messages:
        print(f"\nTesting message: '{message}'")
        try:
            response = intelligence_stack.generate_response(message)
            print(f"✅ Success: {response[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✅ Event loop fix test completed!")


if __name__ == "__main__":
    test_event_loop_fix()

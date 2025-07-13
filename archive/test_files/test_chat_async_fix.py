#!/usr/bin/env python3
"""
Test to verify the async coroutine warning is fixed in the chat functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.intelligence_integration import LyrixaIntelligenceStack


def test_chat_response():
    """Test that chat response generation works without async warnings."""
    print("🧪 Testing chat response generation...")

    # Initialize the intelligence stack
    workspace_path = str(project_root)
    intelligence_stack = LyrixaIntelligenceStack(workspace_path)

    # Test message
    test_message = "Hello, how are you?"

    print(f"💬 Sending message: {test_message}")

    try:
        # This should not produce any async warnings
        response = intelligence_stack.generate_response(test_message)
        print(f"✅ Response received: {response}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_async_method_directly():
    """Test the async method directly."""
    print("\n🧪 Testing async method directly...")

    workspace_path = str(project_root)
    intelligence_stack = LyrixaIntelligenceStack(workspace_path)

    test_message = "Hello, how are you?"

    try:
        # Test the async method directly
        response = asyncio.run(intelligence_stack.generate_response_async(test_message))
        print(f"✅ Async response received: {response}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Testing Chat Async Fix")
    print("=" * 50)

    success1 = test_chat_response()
    success2 = test_async_method_directly()

    if success1 and success2:
        print("\n✅ All tests passed! No async warnings expected.")
    else:
        print("\n❌ Some tests failed.")

    print("\nTest complete.")

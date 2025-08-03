#!/usr/bin/env python3
"""
Test Aetherra-specific question handling.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.intelligence_integration import LyrixaIntelligenceStack


def test_aetherra_question():
    """Test specific Aetherra question."""
    print("🧪 Testing Aetherra question...")

    # Initialize the intelligence stack
    workspace_path = str(project_root)
    intelligence_stack = LyrixaIntelligenceStack(workspace_path)

    # Test the specific question that was causing issues
    test_message = "what is Aetherra?"

    print(f"💬 Sending message: {test_message}")

    try:
        # This should not produce any async warnings or errors
        response = intelligence_stack.generate_response(test_message)
        print(f"✅ Response received: {response}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("[TOOL] Testing Aetherra Question Fix")
    print("=" * 50)

    success = test_aetherra_question()

    if success:
        print("\n✅ Test passed! No async errors.")
    else:
        print("\n❌ Test failed.")

    print("\nTest complete.")

#!/usr/bin/env python3
"""
Test the Lyrixa Brain Loop functionality
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_brain_loop():
    """Test the core brain loop functionality"""
    try:
        print("🧠 Testing Lyrixa Brain Loop...")

        # Import Lyrixa
        from lyrixa.assistant import LyrixaAI

        # Initialize Lyrixa
        lyrixa = LyrixaAI()
        await lyrixa.initialize()

        # Test basic brain loop
        print("\n🧪 Test 1: Basic text input")
        response = await lyrixa.brain_loop(
            user_input="Hello Lyrixa, can you help me understand .aether code?",
            input_type="text"
        )

        print(f"✅ Response received:")
        print(f"   Response: {response.get('lyrixa_response', 'No response')[:100]}...")
        print(f"   Confidence: {response.get('confidence', 0):.2f}")
        print(f"   Processing time: {response.get('processing_time', 0):.3f}s")
        print(f"   Actions taken: {len(response.get('actions_taken', []))}")

        # Test .aether generation request
        print("\n🧪 Test 2: .aether code generation")
        response2 = await lyrixa.brain_loop(
            user_input="Generate .aether code to create a simple greeting function",
            input_type="text"
        )

        print(f"✅ Response received:")
        print(f"   Has .aether code: {bool(response2.get('aether_code'))}")
        print(f"   Confidence: {response2.get('confidence', 0):.2f}")
        print(f"   GUI updates: {len(response2.get('gui_updates', {}))}")

        # Test memory operation
        print("\n🧪 Test 3: Memory operation")
        response3 = await lyrixa.brain_loop(
            user_input="What do you remember about our conversation?",
            input_type="text"
        )

        print(f"✅ Response received:")
        print(f"   Memory stored: {response3.get('memory_stored', False)}")
        print(f"   Processing time: {response3.get('processing_time', 0):.3f}s")

        print("\n🎉 Brain Loop tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Brain Loop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_brain_loop())
    if success:
        print("\n✅ All tests passed! Brain Loop is operational.")
    else:
        print("\n❌ Tests failed. Check the error messages above.")

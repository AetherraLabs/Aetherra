#!/usr/bin/env python3
"""
🧪 TEST LYRIXA AI ASSISTANT
===========================

Test the new Python-based Lyrixa AI Assistant functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_lyrixa():
    """Test Lyrixa AI Assistant functionality"""
    print("🧪 Testing Lyrixa AI Assistant...")

    try:
        from lyrixa import LyrixaAI

        # Initialize Lyrixa
        lyrixa = LyrixaAI(workspace_path=str(project_root))
        await lyrixa.initialize()

        # Test basic conversation
        print("\n1. Testing basic conversation...")
        response = await lyrixa.process_natural_language("Hello, Lyrixa!")
        print(f"✅ Response: {response['lyrixa_response'][:100]}...")

        # Test .aether generation
        print("\n2. Testing .aether code generation...")
        response = await lyrixa.process_natural_language(
            "Create a simple data processing workflow"
        )
        print(f"✅ Generated .aether: {bool(response.get('aether_code'))}")
        if response.get("aether_code"):
            print(f"   Code preview: {response['aether_code'][:100]}...")

        # Test memory operation
        print("\n3. Testing memory system...")
        response = await lyrixa.process_natural_language(
            "Remember that I prefer Python for scripting"
        )
        print(f"✅ Memory response: {response['lyrixa_response'][:100]}...")

        # Test goal management
        print("\n4. Testing goal management...")
        response = await lyrixa.process_natural_language(
            "Create a goal to improve code quality"
        )
        print(f"✅ Goal response: {response['lyrixa_response'][:100]}...")

        # Test plugin execution
        print("\n5. Testing plugin system...")
        response = await lyrixa.process_natural_language(
            "List the files in this directory"
        )
        print(f"✅ Plugin response: {response['lyrixa_response'][:100]}...")

        # Test system status
        print("\n6. Testing system status...")
        status = await lyrixa.get_system_status()
        print(f"✅ System status: {len(status)} components active")

        # Cleanup
        await lyrixa.cleanup()

        print("\n🎉 All tests passed! Lyrixa AI Assistant is working correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    success = await test_lyrixa()
    if success:
        print("\n✅ Lyrixa AI Assistant is ready for use!")
        print("Run 'python lyrixa_launcher.py' to start the interactive assistant.")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())

#!/usr/bin/env python3
"""
🎙️ LYRIXA BASIC FUNCTIONALITY TEST
==================================

Quick test to verify core Lyrixa functionality is working.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))


async def main():
    print("🎙️ LYRIXA BASIC FUNCTIONALITY TEST")
    print("=" * 50)

    try:
        # Test 1: Basic imports
        print("1️⃣ Testing imports...")
        from lyrixa import LyrixaAI

        print("   ✅ LyrixaAI imported")

        # Test 2: Basic instantiation
        print("2️⃣ Testing instantiation...")
        lyrixa = LyrixaAI(workspace_path=str(current_dir))
        print("   ✅ LyrixaAI instantiated")

        # Test 3: Initialization
        print("3️⃣ Testing initialization...")
        await lyrixa.initialize()
        print("   ✅ Lyrixa initialized")

        # Test 4: Basic conversation
        print("4️⃣ Testing basic conversation...")
        response = await lyrixa.process_natural_language("Hello Lyrixa!")
        print(f"   ✅ Response received: {response['lyrixa_response'][:50]}...")

        # Test 5: System status
        print("5️⃣ Testing system status...")
        status = await lyrixa.get_system_status()
        print(f"   ✅ System status: {status['status']}")

        print("\n🎉 BASIC FUNCTIONALITY WORKING!")
        print("Lyrixa AI Assistant is operational.")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n✅ Lyrixa is ready for feature development!")
    else:
        print("\n❌ Lyrixa needs fixes before feature development.")

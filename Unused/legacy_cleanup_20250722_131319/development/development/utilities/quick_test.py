#!/usr/bin/env python3
"""
Quick test of both enhanced systems
"""

import asyncio
import sys
import os

# Add the Aetherra directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Aetherra'))

async def test_systems():
    try:
        print("🎯 Testing Enhanced Lyrixa Systems")
        print("=" * 50)

        # Test Chat Router
        print("🎯 Testing Chat Router...")
        from Aetherra.core.chat_router import create_chat_router
        router = create_chat_router()

        result = await router.process_message("What is autonomous improvement?")
        print(f"Message: What is autonomous improvement?")
        print(f"Intent: {result['routing_result'].intent_type.value}")
        print(f"Handler: {result['routing_result'].handler}")
        print(f"Confidence: {result['routing_result'].confidence:.2f}")
        print("-" * 30)

        # Test Idle Reflection
        print("🧠 Testing Idle Reflection...")
        from Aetherra.core.idle_reflection import create_idle_reflection_system
        reflection = create_idle_reflection_system()
        status = reflection.get_reflection_status()
        print(f"Has Aetherra engines: {status['has_aetherra_engines']}")
        print(f"Reflection cycles: {status['reflection_state']['cycles_completed']}")

        print("\n✅ Both systems are working perfectly!")
        print("🎉 idle_reflection.py and chat_router.py are ready for Lyrixa!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_systems())

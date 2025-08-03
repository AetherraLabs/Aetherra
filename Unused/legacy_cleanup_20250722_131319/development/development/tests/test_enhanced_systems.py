#!/usr/bin/env python3
"""
Test script for the enhanced idle_reflection.py and chat_router.py implementations
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the Aetherra directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_idle_reflection():
    """Test the idle reflection system"""
    print("🧠 Testing Idle Reflection System...")

    try:
        from Aetherra.core.idle_reflection import IdleReflectionSystem, create_idle_reflection_system

        # Test system creation
        reflection_system = create_idle_reflection_system()
        print(f"✅ Idle reflection system created: {type(reflection_system)}")

        # Test status
        status = reflection_system.get_reflection_status()
        print(f"📊 System status: {status['is_running']}")
        print(f"[TOOL] Has Aetherra engines: {status['has_aetherra_engines']}")

        # Test starting the system
        reflection_system.start()
        print("🚀 Reflection system started")

        # Wait a moment
        import time
        time.sleep(2)

        # Test stopping
        reflection_system.stop()
        print("⏹️ Reflection system stopped")

        print("✅ Idle Reflection System test passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Idle Reflection System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chat_router():
    """Test the chat router system"""
    print("\n🎯 Testing Chat Router System...")

    try:
        from Aetherra.core.chat_router import ChatRouter, create_chat_router, ChatMessage

        # Test router creation
        router = create_chat_router()
        print(f"✅ Chat router created: {type(router)}")

        # Test status
        status = router.get_router_status()
        print(f"📊 Router status: {status['routes_count']} routes, {status['handlers_count']} handlers")
        print(f"[TOOL] Has Aetherra engines: {status['has_aetherra_engines']}")

        # Test message processing
        test_messages = [
            "What is the meaning of life?",
            "Please help me with this problem",
            "Can you analyze this situation?",
            "How does autonomous improvement work?",
            "Hello there!"
        ]

        print("\n📤 Testing message routing...")
        for msg in test_messages:
            result = await router.process_message(msg)
            print(f"Message: '{msg}' -> Intent: {result['routing_result'].intent_type.value} (confidence: {result['routing_result'].confidence:.2f})")

        print("✅ Chat Router System test passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Chat Router System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration():
    """Test integration between systems"""
    print("\n🔗 Testing System Integration...")

    try:
        from Aetherra.core.idle_reflection import create_idle_reflection_system
        from Aetherra.core.chat_router import create_chat_router

        # Create both systems
        reflection_system = create_idle_reflection_system()
        router = create_chat_router()

        # Test that they can coexist
        reflection_system.start()

        # Test a message about reflection
        result = await router.process_message("I want to reflect on my recent experiences")
        print(f"Reflection message routed to: {result['routing_result'].handler}")

        # Test a message about autonomous improvement
        result = await router.process_message("Can you help me optimize my autonomous capabilities?")
        print(f"Autonomous message routed to: {result['routing_result'].handler}")

        reflection_system.stop()

        print("✅ System Integration test passed!")
        return True

    except Exception as e:
        print(f"[ERROR] System Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Lyrixa Systems Test Suite")
    print("=" * 60)

    # Test individual systems
    reflection_test = test_idle_reflection()

    # Test chat router (async)
    router_test = asyncio.run(test_chat_router())

    # Test integration (async)
    integration_test = asyncio.run(test_integration())

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"🧠 Idle Reflection: {'✅ PASS' if reflection_test else '[ERROR] FAIL'}")
    print(f"🎯 Chat Router: {'✅ PASS' if router_test else '[ERROR] FAIL'}")
    print(f"🔗 Integration: {'✅ PASS' if integration_test else '[ERROR] FAIL'}")

    overall_success = reflection_test and router_test and integration_test
    print(f"\n🎉 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '[ERROR] SOME TESTS FAILED'}")

    if overall_success:
        print("\n✨ Both idle_reflection.py and chat_router.py are successfully implemented!")
        print("🎯 The systems are ready for integration with Lyrixa!")
    else:
        print("\n[WARN] Some issues detected - please review the error messages above.")

if __name__ == "__main__":
    main()

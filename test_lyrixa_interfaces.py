#!/usr/bin/env python3
"""
🧪 LYRIXA INTERFACES TEST SUITE
==============================

Comprehensive test suite for all Lyrixa interface files.
Tests imports, initialization, and basic functionality.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test all interface imports"""
    print("🔍 Testing interface imports...")

    try:
        from lyrixa.interfaces.lyrixa import (
            LyrixaCore,
            get_lyrixa_instance,
            initialize_lyrixa,
        )

        print("✅ lyrixa.py imports successful")
    except Exception as e:
        print(f"❌ lyrixa.py import failed: {e}")
        return False

    try:
        from lyrixa.interfaces.lyrixa_agent_integration import LyrixaAgentInterface

        print("✅ lyrixa_agent_integration.py imports successful")
    except Exception as e:
        print(f"❌ lyrixa_agent_integration.py import failed: {e}")
        return False

    try:
        from lyrixa.interfaces.lyrixa_assistant import (
            LyrixaAssistant,
            create_assistant,
            quick_chat,
        )

        print("✅ lyrixa_assistant.py imports successful")
    except Exception as e:
        print(f"❌ lyrixa_assistant.py import failed: {e}")
        return False

    try:
        from lyrixa.interfaces.lyrixa_assistant_console import LyrixaConsole

        print("✅ lyrixa_assistant_console.py imports successful")
    except Exception as e:
        print(f"❌ lyrixa_assistant_console.py import failed: {e}")
        return False

    print("✅ All interface imports successful!")
    return True


async def test_lyrixa_core():
    """Test LyrixaCore functionality"""
    print("\n🧠 Testing LyrixaCore...")

    try:
        from lyrixa.interfaces.lyrixa import LyrixaCore

        # Test initialization
        core = LyrixaCore()
        print(f"✅ LyrixaCore created: {core}")

        # Test basic methods
        status = await core.get_system_status()
        print(f"✅ System status retrieved: {status['session_id']}")

        # Test chat (should work even without full initialization)
        response = await core.chat("Hello, test message")
        print(f"✅ Chat response: {response[:50]}...")

        # Test shutdown
        await core.shutdown()
        print("✅ LyrixaCore shutdown complete")

        return True

    except Exception as e:
        print(f"❌ LyrixaCore test failed: {e}")
        logger.error(f"LyrixaCore test error: {e}")
        return False


async def test_agent_interface():
    """Test LyrixaAgentInterface functionality"""
    print("\n🤖 Testing LyrixaAgentInterface...")

    try:
        from lyrixa.interfaces.lyrixa_agent_integration import LyrixaAgentInterface

        # Test initialization
        agent = LyrixaAgentInterface(str(Path.cwd()))
        print(f"✅ LyrixaAgentInterface created: {agent}")

        # Test basic methods
        status = await agent.get_agent_status()
        print(f"✅ Agent status retrieved: {status['agent_id']}")

        # Test task execution
        task = {"id": "test_task", "type": "test", "description": "Test task execution"}
        result = await agent.execute_task(task)
        print(f"✅ Task executed: {result}")

        # Test communication
        comm_result = await agent.communicate_with_agent(
            "test_agent", {"message": "test"}
        )
        print(f"✅ Communication test: {comm_result}")

        return True

    except Exception as e:
        print(f"❌ LyrixaAgentInterface test failed: {e}")
        logger.error(f"LyrixaAgentInterface test error: {e}")
        return False


async def test_assistant():
    """Test LyrixaAssistant functionality"""
    print("\n🎙️ Testing LyrixaAssistant...")

    try:
        from lyrixa.interfaces.lyrixa_assistant import LyrixaAssistant

        # Test initialization
        assistant = LyrixaAssistant()
        print(f"✅ LyrixaAssistant created: {assistant}")

        # Test basic methods
        capabilities = await assistant.get_capabilities()
        print(f"✅ Capabilities retrieved: {len(capabilities)} capabilities")

        # Test chat
        response = await assistant.chat("Hello, this is a test")
        print(f"✅ Chat response: {response[:50]}...")

        # Test task execution
        task_result = await assistant.execute_task("Test task", "test")
        print(f"✅ Task executed: {task_result}")

        # Test status
        status = await assistant.get_status()
        print(f"✅ Status retrieved: {status['session_id']}")

        # Test shutdown
        await assistant.shutdown()
        print("✅ LyrixaAssistant shutdown complete")

        return True

    except Exception as e:
        print(f"❌ LyrixaAssistant test failed: {e}")
        logger.error(f"LyrixaAssistant test error: {e}")
        return False


async def test_console():
    """Test LyrixaConsole functionality"""
    print("\n🖥️ Testing LyrixaConsole...")

    try:
        from lyrixa.interfaces.lyrixa_assistant_console import LyrixaConsole

        # Test initialization
        console = LyrixaConsole()
        print("✅ LyrixaConsole created")

        # Test batch command
        result = await console.run_batch_command("status", [])
        print(f"✅ Batch command executed: {result}")

        return True

    except Exception as e:
        print(f"❌ LyrixaConsole test failed: {e}")
        logger.error(f"LyrixaConsole test error: {e}")
        return False


async def test_convenience_functions():
    """Test convenience functions"""
    print("\n🛠️ Testing convenience functions...")

    try:
        from lyrixa.interfaces.lyrixa import get_lyrixa_instance
        from lyrixa.interfaces.lyrixa_assistant import quick_chat

        # Test global instance
        instance = get_lyrixa_instance()
        print(f"✅ Global instance retrieved: {instance}")

        # Test quick chat (this might take a moment)
        response = await quick_chat("Hello from quick chat test")
        print(f"✅ Quick chat response: {response[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        logger.error(f"Convenience functions test error: {e}")
        return False


async def run_all_tests():
    """Run all interface tests"""
    print("🧪 LYRIXA INTERFACES TEST SUITE")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("LyrixaCore Tests", test_lyrixa_core),
        ("Agent Interface Tests", test_agent_interface),
        ("Assistant Tests", test_assistant),
        ("Console Tests", test_console),
        ("Convenience Functions Tests", test_convenience_functions),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🏃 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Lyrixa interfaces are working correctly.")
        return True
    else:
        print(f"\n⚠️ {failed} tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    asyncio.run(run_all_tests())

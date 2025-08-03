#!/usr/bin/env python3
"""
Autonomous Agents Integration Test
=================================

This script tests the integration of the new AWAKENING autonomous agents
into the main Lyrixa system.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_agent_imports():
    """Test that all agents can be imported"""
    print("🧪 Testing agent imports...")

    try:
        from Aetherra.lyrixa.agents import (
            AutonomousGrowthAgent,
            LyrixaAI,
            ProjectScannerAgent,
            SelfIncorporatorAgent,
        )

        print("✅ All agents imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False


def test_core_agent_autonomous():
    """Test autonomous agent integration in core agent"""
    print("🧪 Testing core agent autonomous integration...")

    try:
        from Aetherra.lyrixa.agents.core_agent import LyrixaAI

        # Create minimal core agent for testing
        agent = LyrixaAI(
            runtime=None, memory=None, prompt_engine=None, llm_manager=None
        )

        print(
            f"✅ Core agent created with {len(agent.autonomous_agents)} autonomous agents"
        )

        # List available autonomous agents
        for name, autonomous_agent in agent.autonomous_agents.items():
            print(f"   🧠 {name}: {type(autonomous_agent).__name__}")

        return len(agent.autonomous_agents) > 0

    except Exception as e:
        print(f"[ERROR] Core agent test failed: {e}")
        return False


def test_autonomous_capabilities():
    """Test autonomous capabilities method"""
    print("🧪 Testing autonomous capabilities...")

    try:
        import asyncio

        from Aetherra.lyrixa.agents.core_agent import LyrixaAI

        agent = LyrixaAI(
            runtime=None, memory=None, prompt_engine=None, llm_manager=None
        )

        # Test async capabilities method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        capabilities = loop.run_until_complete(agent.get_autonomous_capabilities())

        print(f"✅ Autonomous capabilities: {capabilities['available']}")
        if capabilities["available"]:
            for name, info in capabilities["agents"].items():
                print(f"   🧠 {info['name']}: {info['description']}")

        return capabilities["available"]

    except Exception as e:
        print(f"[ERROR] Capabilities test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("🌟 LYRIXA AWAKENING INTEGRATION TEST")
    print("=" * 50)

    tests = [
        ("Agent Imports", test_agent_imports),
        ("Core Agent Integration", test_core_agent_autonomous),
        ("Autonomous Capabilities", test_autonomous_capabilities),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        print()

    print("📊 TEST RESULTS")
    print("=" * 50)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "[ERROR] FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 ALL TESTS PASSED - Autonomous agents are integrated!")
        print("🧠 The AWAKENING agents are now available in Lyrixa!")
    else:
        print("[WARN] Some tests failed - check integration")

    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

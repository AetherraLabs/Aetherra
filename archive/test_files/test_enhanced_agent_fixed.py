#!/usr/bin/env python3
"""
Test script to verify the enhanced agent works correctly after fixes
"""

import sys
import time

sys.path.append(".")

from core.enhanced_agent import create_enhanced_agent


def test_enhanced_agent():
    """Test basic functionality of the enhanced agent"""
    print("🧪 Testing Enhanced Agent Functionality")
    print("=" * 50)

    # Test 1: Agent Creation
    print("Test 1: Creating enhanced agent...")
    try:
        agent = create_enhanced_agent()
        print("✅ Agent created successfully")
        print(f"   Initial state: {agent.get_state()}")
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

    # Test 2: Agent State Management
    print("\nTest 2: Testing state management...")
    try:
        original_state = agent.get_state()
        agent.set_state("reflecting")
        new_state = agent.get_state()
        print(f"✅ State changed from {original_state} to {new_state}")
        agent.set_state(original_state)  # Reset
    except Exception as e:
        print(f"❌ State management failed: {e}")
        return False

    # Test 3: Goal Management
    print("\nTest 3: Testing goal management...")
    try:
        initial_goals = agent.get_goals()
        test_goal = {"id": "test_goal", "text": "Test goal", "priority": "high"}
        agent.add_goal(test_goal)
        new_goals = agent.get_goals()
        print(f"✅ Goals: {len(initial_goals)} -> {len(new_goals)}")
        assert len(new_goals) == len(initial_goals) + 1
    except Exception as e:
        print(f"❌ Goal management failed: {e}")
        return False

    # Test 4: Agent Status
    print("\nTest 4: Testing agent status...")
    try:
        status = agent.get_agent_status()
        print(f"✅ Agent status retrieved: {status['state']}")
        assert "state" in status
        assert "stats" in status
    except Exception as e:
        print(f"❌ Status retrieval failed: {e}")
        return False

    # Test 5: Event Notification
    print("\nTest 5: Testing event notification...")
    try:
        agent.notify_event("test_event", {"test": "data"})
        print("✅ Event notification successful")
    except Exception as e:
        print(f"❌ Event notification failed: {e}")
        return False

    # Test 6: Agent Start/Stop
    print("\nTest 6: Testing agent start/stop...")
    try:
        start_result = agent.start()
        print(f"✅ Agent started: {start_result['status']}")

        # Let it run briefly
        time.sleep(2)

        stop_result = agent.stop()
        print(f"✅ Agent stopped: {stop_result['status']}")
    except Exception as e:
        print(f"❌ Agent start/stop failed: {e}")
        return False

    print("\n🎉 All tests passed! Enhanced agent is working correctly.")
    return True


if __name__ == "__main__":
    success = test_enhanced_agent()
    if success:
        print("\n✅ Enhanced agent is fixed and fully functional!")
    else:
        print("\n❌ Some tests failed - further investigation needed")
    sys.exit(0 if success else 1)

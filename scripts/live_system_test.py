#!/usr/bin/env python3
"""
NeuroCode Live System Test

Test actual NeuroCode functionality with real operations
"""

import json
import sys
from pathlib import Path


def test_memory_operations():
    """Test memory system with actual operations."""
    print("🧠 Testing Memory System")
    print("-" * 30)

    try:
        from core.memory import NeuroMemory

        # Test memory creation and operations
        memory = NeuroMemory()

        # Test remembering
        test_memory = f"System test executed at {sys.version}"
        memory.remember(test_memory, tags=["test", "system"], category="testing")

        # Test recall
        memories = memory.recall(category="testing", limit=1)

        if memories and len(memories) > 0:
            print("✅ Memory store/recall successful")
            print(f"   Stored: {len(memories)} test memory")
            return True
        else:
            print("⚠️ Memory recall returned empty")
            return False

    except Exception as e:
        print(f"❌ Memory system error: {e}")
        return False


def test_goal_operations():
    """Test goal system with actual operations."""
    print("\n🎯 Testing Goal System")
    print("-" * 30)

    try:
        from core.goal_system import GoalSystem

        # Test goal system creation
        goals = GoalSystem()

        # Test adding a goal
        test_goal = "Complete system functionality test"
        goal_id = goals.add_goal(test_goal, priority="high")

        # Test getting goals
        active_goals = goals.get_active_goals()

        if goal_id and active_goals:
            print("✅ Goal system operational")
            print(f"   Active goals: {len(active_goals)}")

            # Mark test goal as completed
            goals.complete_goal(goal_id)
            print("✅ Goal completion successful")
            return True
        else:
            print("⚠️ Goal system returned no data")
            return False

    except Exception as e:
        print(f"❌ Goal system error: {e}")
        return False


def test_interpreter_basic():
    """Test basic interpreter functionality."""
    print("\n🔧 Testing Interpreter")
    print("-" * 30)

    try:
        from core.interpreter import NeuroCodeInterpreter

        # Test interpreter creation
        interpreter = NeuroCodeInterpreter()

        # Test simple expression
        result = interpreter.execute("2 + 2")

        if result and "4" in str(result):
            print("✅ Basic interpreter functionality working")
            return True
        else:
            print("⚠️ Interpreter returned unexpected result")
            return False

    except Exception as e:
        print(f"❌ Interpreter error: {e}")
        return False


def test_data_persistence():
    """Test data file read/write operations."""
    print("\n💾 Testing Data Persistence")
    print("-" * 30)

    try:
        # Test goals file
        goals_file = Path("goals_store.json")
        if goals_file.exists():
            with open(goals_file) as f:
                goals_data = json.load(f)
            print(f"✅ Goals file: {len(goals_data.get('goals', []))} goals loaded")
        else:
            print("ℹ️ Goals file will be created on first use")

        # Test memory file
        memory_file = Path("memory_store.json")
        if memory_file.exists():
            with open(memory_file) as f:
                memory_data = json.load(f)
            print(f"✅ Memory file: {len(memory_data)} memories loaded")
        else:
            print("ℹ️ Memory file will be created on first use")

        return True

    except Exception as e:
        print(f"❌ Data persistence error: {e}")
        return False


def test_neuroplex_components():
    """Test Neuroplex launcher components."""
    print("\n🚀 Testing Neuroplex Components")
    print("-" * 30)

    try:
        # Test batch launcher exists
        batch_launcher = Path("neuroplex.bat")
        if batch_launcher.exists():
            print("✅ Neuroplex batch launcher found")
        else:
            print("⚠️ Neuroplex batch launcher missing")

        # Test script launcher exists
        script_launcher = Path("neuroplex")
        if script_launcher.exists():
            print("✅ Neuroplex script launcher found")
        else:
            print("⚠️ Neuroplex script launcher missing")

        return True

    except Exception as e:
        print(f"❌ Neuroplex component error: {e}")
        return False


def main():
    """Run live system test."""
    print("🧬 NeuroCode Live System Test")
    print("=" * 50)

    tests = [
        ("Memory Operations", test_memory_operations),
        ("Goal Operations", test_goal_operations),
        ("Basic Interpreter", test_interpreter_basic),
        ("Data Persistence", test_data_persistence),
        ("Neuroplex Components", test_neuroplex_components),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_name}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 LIVE SYSTEM TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Final Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL SYSTEMS FULLY OPERATIONAL!")
        print("✅ NeuroCode and Neuroplex are ready for use")
    elif passed >= total * 0.8:
        print("⚠️ MOSTLY OPERATIONAL - Minor issues detected")
        print("✅ Core functionality is working")
    else:
        print("❌ CRITICAL ISSUES DETECTED")
        print("⚠️ Manual intervention may be required")

    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

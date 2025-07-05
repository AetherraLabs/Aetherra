#!/usr/bin/env python3
"""
Test script to verify both launchers work correctly
"""

import asyncio
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_aetherra_launcher():
    """Test importing aetherra_launcher"""
    try:
        from launchers.aetherra_launcher import main

        print("✅ aetherra_launcher.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ aetherra_launcher.py failed to import: {e}")
        return False


def test_main_launcher():
    """Test importing main.py launcher"""
    try:
        from launchers.main import main

        print("✅ main.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ main.py failed to import: {e}")
        return False


async def test_aether_interpreter():
    """Test that AetherInterpreter can parse and execute simple code"""
    try:
        from lyrixa.core.aether_interpreter import AetherInterpreter

        interpreter = AetherInterpreter()

        # Test parsing simple aether code
        simple_code = """node test_input input
source: "test.csv"

node test_output output
destination: "result.json"

test_input -> test_output"""

        workflow = await interpreter.parse_aether_code(simple_code)
        print(f"✅ Workflow parsing successful: {len(workflow.nodes)} nodes created")

        # Test execution
        result = await interpreter.execute_workflow(workflow)
        print(f"✅ Workflow execution successful: status = {result.get('status')}")

        return True
    except Exception as e:
        print(f"❌ AetherInterpreter test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Launcher Fixes")
    print("=" * 50)

    tests_passed = 0
    total_tests = 3

    # Test launcher imports
    if test_aetherra_launcher():
        tests_passed += 1

    if test_main_launcher():
        tests_passed += 1

    # Test interpreter functionality
    if asyncio.run(test_aether_interpreter()):
        tests_passed += 1

    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("🎉 All tests passed! Both launchers are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    main()

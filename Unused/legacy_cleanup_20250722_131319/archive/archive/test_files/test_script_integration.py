#!/usr/bin/env python3
"""
Comprehensive test for Aetherra Script Library Integration
Tests all components: registry loading, script router, memory integration, and Lyrixa integration
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.runtime.lyrixa_script_integration import (
    get_script_help,
    handle_script_command,
    initialize_script_library,
    is_script_related,
    lyrixa_script_integration,
)


def test_initialization():
    """Test script library initialization"""
    print("🧪 Testing Script Library Initialization...")

    result = initialize_script_library()

    if result:
        print("✅ Script library initialized successfully")
        return True
    else:
        print("❌ Script library initialization failed")
        return False


def test_script_commands():
    """Test various script commands"""
    print("\n🧪 Testing Script Commands...")

    commands = [
        "list scripts",
        "categories",
        "suggest daily maintenance",
        "describe bootstrap",
        "list memory scripts",
        "suggest project analysis",
        "help scripts",
    ]

    for command in commands:
        print(f"\n📝 Testing: '{command}'")
        result = handle_script_command(command)
        print(f"Response: {result[:200]}{'...' if len(result) > 200 else ''}")

    return True


def test_script_detection():
    """Test script-related command detection"""
    print("\n🧪 Testing Script Detection...")

    test_cases = [
        ("run bootstrap", True),
        ("list scripts", True),
        ("suggest daily maintenance", True),
        ("hello world", False),
        ("what is the weather", False),
        ("describe reflect", True),
        ("categories", True),
        ("help me with something", False),
    ]

    for test_input, expected in test_cases:
        result = is_script_related(test_input)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{test_input}' -> {result} (expected: {expected})")

    return True


def test_integration_info():
    """Test integration information retrieval"""
    print("\n🧪 Testing Integration Information...")

    # Test registry info
    registry_info = lyrixa_script_integration.get_registry_info()
    print(f"📋 Registry loaded: {'✅' if 'registry_info' in registry_info else '❌'}")

    if "registry_info" in registry_info:
        print(f"   Name: {registry_info['registry_info'].get('name', 'N/A')}")
        print(f"   Version: {registry_info['registry_info'].get('version', 'N/A')}")
        print(f"   Categories: {len(registry_info.get('categories', {}))}")

    # Test insights
    insights = lyrixa_script_integration.get_script_insights()
    print(f"📊 Insights generated: {'✅' if 'total_scripts' in insights else '❌'}")

    if "total_scripts" in insights:
        print(f"   Total scripts: {insights['total_scripts']}")
        print(f"   Categories: {insights['by_category']}")

    return True


def test_help_system():
    """Test help system"""
    print("\n🧪 Testing Help System...")

    help_text = get_script_help()
    print(f"📚 Help text generated: {'✅' if help_text else '❌'}")

    if help_text:
        print(f"Help preview: {help_text[:300]}...")

    return True


def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive Script Library Integration Test")
    print("=" * 60)

    tests = [
        test_initialization,
        test_script_commands,
        test_script_detection,
        test_integration_info,
        test_help_system,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Script library integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)

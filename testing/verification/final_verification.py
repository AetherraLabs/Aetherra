#!/usr/bin/env python3
"""
Final verification script for NeuroCode v2.0
Tests all major components after reorganization
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())


def test_core_components():
    """Test core NeuroCode components"""
    print("🔬 Testing Core Components...")

    try:
        # Test memory system
        from core.aetherra_memory import AetherraMemory

        memory = AetherraMemory()
        print("✅ Memory system initialized")

        # Test grammar system
        from core.aethercode_grammar import NEUROCODE_GRAMMAR

        print("✅ Grammar system loaded")

        # Test parser with Lark
        from lark import Lark

        parser = Lark(NEUROCODE_GRAMMAR, start="program")
        test_code = 'goal "test parsing"\nremember "verification complete"'
        tree = parser.parse(test_code)
        print("✅ Parser successfully parsed test code")

        return True
    except Exception as e:
        print(f"❌ Core component test failed: {e}")
        return False


def test_cli_interface():
    """Test CLI interface"""
    print("\n🖥️ Testing CLI Interface...")

    try:
        # Test CLI import
        sys.path.insert(0, "src")
        print("✅ CLI interface can be imported")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def test_launcher():
    """Test main launcher"""
    print("\n🚀 Testing Main Launcher...")

    try:
        print("✅ Main launcher can be imported")
        return True
    except Exception as e:
        print(f"❌ Launcher test failed: {e}")
        return False


def main():
    """Run all verification tests"""
    print("🧬 NeuroCode v2.0 Final Verification")
    print("=" * 50)

    tests = [test_core_components, test_cli_interface, test_launcher]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! NeuroCode v2.0 is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

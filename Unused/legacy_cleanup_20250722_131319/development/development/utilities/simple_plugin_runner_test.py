#!/usr/bin/env python3
"""
Simple Clean Plugin Runner Integration Test
==========================================

This script tests the integration without creating Qt widgets.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_method_existence():
    """Test that the hybrid window has the required methods"""
    try:
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow

        # Get the class methods without instantiating
        methods = dir(LyrixaWindow)

        required_methods = [
            'create_execute_plugin_tab',
            'create_basic_execute_tab',
            'execute_selected_plugin',
            'clear_exec_output'
        ]

        for method in required_methods:
            if method in methods:
                print(f"✅ {method} method exists")
            else:
                print(f"[ERROR] {method} method missing")
                return False

        print("✅ All required methods exist in LyrixaWindow")
        return True

    except Exception as e:
        print(f"[ERROR] Error checking methods: {e}")
        return False

def test_plugin_runner_functionality():
    """Test that the plugin runner core functionality works"""
    try:
        from clean_plugin_runner import CleanPluginRunner, PluginDiscovery

        # Test plugin discovery
        discovery = PluginDiscovery()
        plugins = discovery.discover_plugins()

        if plugins is None:
            plugins = []

        print(f"✅ Plugin discovery found {len(plugins)} plugins")

        # Test some core functionality without GUI
        runner = CleanPluginRunner(plugin_manager=None)

        # Check that basic methods exist
        if hasattr(runner, 'discover_plugins'):
            print("✅ discover_plugins method exists")
        else:
            print("[ERROR] discover_plugins method missing")
            return False

        if hasattr(runner, 'execute_plugin'):
            print("✅ execute_plugin method exists")
        else:
            print("[ERROR] execute_plugin method missing")
            return False

        return True

    except Exception as e:
        print(f"[ERROR] Plugin runner functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run integration tests"""
    print("🧪 Simple Clean Plugin Runner Integration Test")
    print("=" * 50)

    tests = [
        test_method_existence,
        test_plugin_runner_functionality
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n📋 Running: {test.__name__}")
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"[ERROR] {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {test.__name__} FAILED with exception: {e}")

    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 Integration tests passed! Clean Plugin Runner is properly integrated.")
        return 0
    else:
        print("[WARN]  Some tests failed. Please check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

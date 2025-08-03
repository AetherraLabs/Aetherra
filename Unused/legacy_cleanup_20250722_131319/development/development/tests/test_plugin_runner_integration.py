#!/usr/bin/env python3
"""
Test Clean Plugin Runner Integration
===================================

This script tests the integration of the Clean Plugin Runner with the Hybrid Window
to verify that the execute tab properly loads and functions as expected.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_runner_import():
    """Test that the Clean Plugin Runner can be imported successfully"""
    try:
        from clean_plugin_runner import CleanPluginRunner
        print("✅ Clean Plugin Runner imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import Clean Plugin Runner: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing Clean Plugin Runner: {e}")
        return False

def test_enhanced_plugin_manager():
    """Test that the enhanced plugin manager can be imported"""
    try:
        from Aetherra.lyrixa.plugins.enhanced_plugin_manager import PluginManager
        print("✅ Enhanced Plugin Manager imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import Enhanced Plugin Manager: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing Enhanced Plugin Manager: {e}")
        return False

def test_hybrid_window_integration():
    """Test that the hybrid window can load the plugin runner"""
    try:
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow
        print("✅ Hybrid Window imported successfully")

        # Test that the methods exist
        window = LyrixaWindow()
        if hasattr(window, 'create_execute_plugin_tab'):
            print("✅ create_execute_plugin_tab method exists")
        else:
            print("[ERROR] create_execute_plugin_tab method missing")
            return False

        if hasattr(window, 'create_basic_execute_tab'):
            print("✅ create_basic_execute_tab method exists")
        else:
            print("[ERROR] create_basic_execute_tab method missing")
            return False

        if hasattr(window, 'execute_selected_plugin'):
            print("✅ execute_selected_plugin method exists")
        else:
            print("[ERROR] execute_selected_plugin method missing")
            return False

        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import Hybrid Window: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error with Hybrid Window: {e}")
        return False

def test_plugin_discovery():
    """Test that plugins can be discovered"""
    try:
        from clean_plugin_runner import PluginDiscovery

        discovery = PluginDiscovery()
        plugins = discovery.discover_plugins()

        if plugins is None:
            plugins = []

        print(f"✅ Plugin discovery successful - found {len(plugins)} plugins")
        for plugin in plugins[:5]:  # Show first 5 plugins
            print(f"  - {plugin.get('name', 'Unknown')}: {plugin.get('description', 'No description')}")

        return True
    except Exception as e:
        print(f"[ERROR] Plugin discovery failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 Testing Clean Plugin Runner Integration")
    print("=" * 50)

    tests = [
        test_plugin_runner_import,
        test_enhanced_plugin_manager,
        test_hybrid_window_integration,
        test_plugin_discovery
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
        print("🎉 All tests passed! Clean Plugin Runner integration is working correctly.")
        return 0
    else:
        print("[WARN]  Some tests failed. Please check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

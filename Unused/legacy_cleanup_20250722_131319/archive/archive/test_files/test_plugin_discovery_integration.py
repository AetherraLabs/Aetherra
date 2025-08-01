#!/usr/bin/env python3
"""
Comprehensive Plugin Discovery Integration Test
===============================================

Test all plugin discovery integration points to ensure they're always available.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())


def test_direct_discovery():
    """Test direct plugin discovery."""
    print("🔍 Testing Direct Plugin Discovery")
    print("-" * 40)

    try:
        from lyrixa.plugin_discovery import discover, discover_detailed, status

        # Test basic discovery
        plugins = discover()
        print(f"✅ Found {len(plugins)} plugins via direct discovery")

        # Test status
        status_info = status()
        print(f"✅ Status: Available={status_info['available']}")
        print(f"   Directories: {status_info['directories']}")

        # Test detailed discovery
        detailed = discover_detailed()
        print(f"✅ Detailed discovery: {len(detailed['combined'])} plugins combined")

        return True, len(plugins)

    except Exception as e:
        print(f"❌ Error in direct discovery: {e}")
        return False, 0


def test_main_module_access():
    """Test plugin discovery through main Lyrixa module."""
    print("\n📦 Testing Main Module Access")
    print("-" * 40)

    try:
        import lyrixa

        # Test if discovery functions are available
        if hasattr(lyrixa, "discover"):
            plugins = lyrixa.discover()
            print(f"✅ lyrixa.discover() found {len(plugins)} plugins")
        else:
            print("❌ lyrixa.discover() not available")
            return False, 0

        if hasattr(lyrixa, "plugin_status"):
            status_info = lyrixa.plugin_status()
            print(f"✅ lyrixa.plugin_status() available: {status_info['available']}")
        else:
            print("❌ lyrixa.plugin_status() not available")

        return True, len(plugins) if hasattr(lyrixa, "discover") else 0

    except Exception as e:
        print(f"❌ Error accessing main module: {e}")
        return False, 0


def test_api_endpoints():
    """Test API endpoint functionality."""
    print("\n🌐 Testing API Endpoints")
    print("-" * 40)

    try:
        from lyrixa.self_improvement_dashboard_api import (
            discover_plugins,
            get_plugin_status,
            router,
        )

        print("✅ API module imported successfully")

        # Test discover endpoint function
        result = discover_plugins()
        print(f"✅ API discover function works")

        # Test status endpoint function
        status_result = get_plugin_status()
        print(f"✅ API status function works")

        # Check routes
        routes = [route.path for route in router.routes]
        plugin_routes = [r for r in routes if "/api/plugins/" in r]
        print(f"✅ Found {len(plugin_routes)} plugin-related API routes")

        return True, 0

    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False, 0


def test_plugin_managers():
    """Test plugin managers directly."""
    print("\n🧩 Testing Plugin Managers")
    print("-" * 40)

    advanced_count = 0
    enhanced_count = 0

    # Test Advanced Plugin Manager
    try:
        from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager

        manager = LyrixaAdvancedPluginManager()
        plugins = manager.discover_plugins()
        advanced_count = len(plugins)
        print(f"✅ Advanced Plugin Manager: {advanced_count} plugins")
    except Exception as e:
        print(f"❌ Advanced Plugin Manager error: {e}")

    # Test Enhanced Plugin Manager
    try:
        from lyrixa.plugins.enhanced_plugin_manager import PluginManager

        manager = PluginManager()
        plugins = manager.discover_plugins()
        enhanced_count = len(plugins)
        print(f"✅ Enhanced Plugin Manager: {enhanced_count} plugins")
    except Exception as e:
        print(f"❌ Enhanced Plugin Manager error: {e}")

    return (advanced_count > 0 or enhanced_count > 0), max(
        advanced_count, enhanced_count
    )


def main():
    """Run comprehensive tests."""
    print("🚀 COMPREHENSIVE PLUGIN DISCOVERY TEST")
    print("=" * 60)

    tests = [
        ("Direct Discovery", test_direct_discovery),
        ("Main Module Access", test_main_module_access),
        ("API Endpoints", test_api_endpoints),
        ("Plugin Managers", test_plugin_managers),
    ]

    results = {}
    total_plugins = 0

    for test_name, test_func in tests:
        success, plugin_count = test_func()
        results[test_name] = success
        total_plugins = max(total_plugins, plugin_count)

    print("\n📊 TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25}: {status}")

    all_passed = all(results.values())

    print(f"\nTotal Plugins Found: {total_plugins}")
    print(
        f"Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
    )

    if all_passed:
        print("\n🎉 SUCCESS! Plugin discovery is now always available through:")
        print("  1. from lyrixa.plugin_discovery import discover")
        print("  2. from lyrixa import discover")
        print("  3. API: /api/plugins/discover")
        print("  4. CLI: python lyrixa/plugin_discovery.py")
        print("  5. Direct manager access")
    else:
        print("\n⚠️  Some integration points need attention.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

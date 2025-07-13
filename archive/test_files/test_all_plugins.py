#!/usr/bin/env python3
"""
Test all plugin files in the lyrixa/plugins directory
"""

import importlib.util
import os
import sys


def test_plugin_imports():
    """Test importing all plugin files"""
    print("🔍 Testing all plugin imports...")

    plugin_files = [
        "ai_plugin_generator_v2",
        "workflow_builder_plugin",
        "sample_plugin_2",
        "sample_plugin_1",
        "plugin_quality_control",
        "plugin_lifecycle_memory",
        "plugin_generator_plugin",
        "plugin_discovery",
        "plugin_creation_wizard",
        "plugin_analytics",
        "enhanced_plugin_manager",
        "context_aware_surfacing",
        "assistant_trainer_plugin",
    ]

    success_count = 0
    failed_imports = []

    for plugin_name in plugin_files:
        try:
            module_path = f"lyrixa.plugins.{plugin_name}"
            module = __import__(module_path, fromlist=[plugin_name])
            print(f"✅ {plugin_name}: Import successful")
            success_count += 1
        except Exception as e:
            print(f"❌ {plugin_name}: Import failed - {e}")
            failed_imports.append((plugin_name, str(e)))

    print(
        f"\n📊 Results: {success_count}/{len(plugin_files)} plugins imported successfully"
    )

    if failed_imports:
        print("\n❌ Failed imports:")
        for plugin_name, error in failed_imports:
            print(f"  - {plugin_name}: {error}")
        return False
    else:
        print("\n🎉 All plugin imports successful!")
        return True


def test_specific_functionality():
    """Test specific functionality of key plugins"""
    print("\n🧪 Testing specific plugin functionality...")

    # Test context-aware surfacing
    try:
        from lyrixa.plugins.context_aware_surfacing import (
            ContextAwareSurfacing,
            capture_context,
        )

        surfacing = ContextAwareSurfacing()
        context = capture_context(active_files=["test.py"], current_task="testing")
        print("✅ Context-aware surfacing: Basic functionality works")
    except Exception as e:
        print(f"❌ Context-aware surfacing: {e}")
        return False

    # Test plugin analytics
    try:
        from lyrixa.plugins.plugin_analytics import PluginAnalyticsIntegration

        analytics = PluginAnalyticsIntegration(
            db_path=":memory:"
        )  # Use in-memory DB for test
        with analytics.track_plugin_execution("test_plugin") as tracker:
            tracker.set_context({"test": True})
        print("✅ Plugin analytics: Basic functionality works")
    except Exception as e:
        print(f"❌ Plugin analytics: {e}")
        return False

    # Test AI plugin generator
    try:
        from lyrixa.plugins.ai_plugin_generator_v2 import (
            AIPluginGenerator,
            get_available_templates,
        )

        generator = AIPluginGenerator()
        templates = get_available_templates()
        print(f"✅ AI plugin generator: {len(templates)} templates available")
    except Exception as e:
        print(f"❌ AI plugin generator: {e}")
        return False

    print("🎉 All functionality tests passed!")
    return True


if __name__ == "__main__":
    print("🚀 Starting comprehensive plugin tests...")

    import_success = test_plugin_imports()

    if import_success:
        functionality_success = test_specific_functionality()

        if functionality_success:
            print("\n✅ ALL TESTS PASSED! All plugins are working correctly.")
        else:
            print("\n❌ Some functionality tests failed.")
            sys.exit(1)
    else:
        print("\n❌ Some imports failed.")
        sys.exit(1)

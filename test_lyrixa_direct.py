#!/usr/bin/env python3
"""
Direct test runner for Lyrixa Plugin UI - bypasses launcher interception
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_plugin_ui_components():
    """Test Lyrixa Plugin UI components directly"""
    print("🎙️ LYRIXA PLUGIN UI DIRECT TEST")
    print("=" * 50)

    # Test 1: PluginUIManager
    try:
        from lyrixa.gui.plugin_ui_loader import PluginUIManager

        manager = PluginUIManager()
        print("✅ PluginUIManager imported and created")

        # Test plugin registration
        test_plugin = {"name": "test", "version": "1.0"}
        manager.register_plugin(test_plugin)
        print("✅ Plugin registration working")

        # Test zone management
        manager.set_zone("suggestion_panel", test_plugin)
        print("✅ Zone assignment working")

        # Test mode switching
        manager.switch_mode("Developer")
        print("✅ Mode switching working")

    except Exception as e:
        print(f"❌ PluginUIManager test failed: {e}")
        return False

    # Test 2: Configuration Manager
    try:
        from lyrixa.gui.simple_configuration_manager import SimpleConfigurationManager

        config = SimpleConfigurationManager()
        print("✅ SimpleConfigurationManager created")

        # Test preferences
        prefs = config.get_preferences()
        print(f"✅ User preferences loaded: theme={prefs.theme}")

    except Exception as e:
        print(f"❌ Configuration Manager test failed: {e}")
        return False

    # Test 3: Sample Plugins
    try:
        from lyrixa.plugins import sample_plugin_1, sample_plugin_2

        plugin1 = sample_plugin_1.plugin_data
        plugin2 = sample_plugin_2.plugin_data
        print(f"✅ Sample plugins loaded: {plugin1['name']}, {plugin2['name']}")

    except Exception as e:
        print(f"❌ Sample plugins test failed: {e}")
        return False

    print("\n🎉 ALL TESTS PASSED! Lyrixa Plugin UI system is working!")
    return True


if __name__ == "__main__":
    success = test_plugin_ui_components()
    if success:
        print("\n✅ LYRIXA PLUGIN UI SYSTEM VERIFIED")
    else:
        print("\n❌ SOME TESTS FAILED")

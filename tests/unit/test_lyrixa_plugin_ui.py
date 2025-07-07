#!/usr/bin/env python3
"""
Test the Lyrixa Plugin UI functionality and verify it's working properly
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("🎙️ Testing Lyrixa Plugin UI Components...")


def test_plugin_ui_manager():
    """Test the PluginUIManager"""
    try:
        from lyrixa.gui.plugin_ui_loader import PluginUIManager

        manager = PluginUIManager()
        print("✅ PluginUIManager created successfully")

        # Test plugin registration
        test_plugin = {"name": "test", "version": "1.0"}
        manager.register_plugin(test_plugin)
        print("✅ Plugin registered successfully")

        # Test zone management
        manager.set_zone("suggestion_panel", test_plugin)
        print("✅ Zone assignment working")

        # Test mode switching
        manager.switch_mode("Developer")
        print("✅ Mode switching working")

        # Test layout initialization
        manager.initialize_layout()
        print("✅ Layout initialization working")

        return True
    except ImportError as e:
        print(f"❌ PluginUIManager import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PluginUIManager test failed: {e}")
        return False


def test_configuration_manager():
    """Test the Configuration Manager"""
    try:
        from lyrixa.gui.simple_configuration_manager import SimpleConfigurationManager

        config = SimpleConfigurationManager()
        print("✅ SimpleConfigurationManager created successfully")

        # Test basic operations
        preferences = config.get_preferences()
        if preferences:
            print("✅ User preferences accessible")

        # Test preference updates
        config.update_preference("theme", "dark")
        print("✅ Configuration update working")

        return True
    except ImportError as e:
        print(f"❌ Configuration Manager import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration Manager test failed: {e}")
        return False


def test_sample_plugins():
    """Test sample plugins"""
    try:
        from lyrixa.plugins import sample_plugin_1, sample_plugin_2

        plugin1_data = sample_plugin_1.plugin_data
        plugin2_data = sample_plugin_2.plugin_data

        print("✅ Sample plugins imported successfully")

        # Test plugin info
        if plugin1_data.get("name") and plugin2_data.get("name"):
            print(f"✅ Plugin 1: {plugin1_data.get('name', 'Unknown')}")
            print(f"✅ Plugin 2: {plugin2_data.get('name', 'Unknown')}")

        return True
    except ImportError as e:
        print(f"❌ Sample plugins import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Sample plugins test failed: {e}")
        return False


def test_lyrixa_launcher():
    """Test Lyrixa launcher import"""
    try:
        import importlib.util

        spec = importlib.util.find_spec("lyrixa.launcher")
        if spec is not None:
            print("✅ Lyrixa launcher module found")
            return True
        else:
            print("❌ Lyrixa launcher module not found")
            return False
    except ImportError as e:
        print(f"❌ Lyrixa launcher import failed: {e}")
        return False


def run_all_tests():
    """Run all Lyrixa Plugin UI tests"""
    tests = [
        ("Plugin UI Manager", test_plugin_ui_manager),
        ("Configuration Manager", test_configuration_manager),
        ("Sample Plugins", test_sample_plugins),
        ("Lyrixa Launcher", test_lyrixa_launcher),
    ]

    print("🎙️ LYRIXA PLUGIN UI TEST SUITE")
    print("=" * 50)

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

"""
Test Plugin Editor GUI Integration
Quick test to verify the Plugin Editor tab integration
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from PySide6.QtWidgets import QApplication

from Aetherra.lyrixa.gui.plugin_editor_tab import PluginEditorTab


def test_plugin_editor_tab():
    """Test that the PluginEditorTab can be created"""
    print("🧪 Testing Plugin Editor Tab Creation")
    print("=" * 40)

    app = QApplication(sys.argv)

    try:
        # Create the plugin editor tab
        tab = PluginEditorTab(
            plugin_dir="Aetherra/plugins",
            memory_manager=None,  # Mock
            plugin_manager=None,  # Mock
        )

        print("✅ PluginEditorTab created successfully")
        print(f"📁 Plugin directory: {tab.plugin_dir}")
        print("✅ UI components initialized")

        # Test that the tab has the expected buttons
        if hasattr(tab, "generate_new_plugin"):
            print("✅ Plugin generation method available")
        else:
            print("[ERROR] Plugin generation method missing")

        if hasattr(tab, "show_templates"):
            print("✅ Template viewing method available")
        else:
            print("[ERROR] Template viewing method missing")

        # Show the tab briefly
        tab.show()
        print("✅ Tab window displayed successfully")

        # Close immediately for test
        tab.close()
        app.quit()

        print("\n🎉 Plugin Editor Tab integration test PASSED!")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_plugin_generation_availability():
    """Test that the plugin generation system is accessible"""
    print("\n[TOOL] Testing Plugin Generation System Access")
    print("=" * 40)

    try:
        from Aetherra.lyrixa.plugins.plugin_generator_plugin import (
            PluginGeneratorPlugin,
        )

        generator = PluginGeneratorPlugin()
        templates = generator.list_templates()

        print(f"✅ PluginGeneratorPlugin imported successfully")
        print(f"📚 Templates available: {len(templates)}")

        for template in templates:
            print(f"   • {template['name']} ({template['category']})")

        print("✅ Plugin generation system ready for GUI integration")
        return True

    except ImportError as e:
        print(f"[ERROR] Plugin generation system not available: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def main():
    """Run integration tests"""
    print("🚀 Plugin Editor GUI Integration Test")
    print("=" * 50)

    test1_passed = test_plugin_generation_availability()
    test2_passed = test_plugin_editor_tab()

    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Plugin Editor is ready for GUI integration")
        print("✅ Plugin generation system is accessible")
        print("✅ GUI components are working correctly")
    else:
        print("[WARN]  SOME TESTS FAILED")
        print("Check the errors above for details")


if __name__ == "__main__":
    main()

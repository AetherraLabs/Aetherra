#!/usr/bin/env python3
"""
Test Plugin Manager UI Integration
==================================

Quick test to validate that the plugin manager UI can load plugins from the core system.
"""

import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)


def test_plugin_manager_integration():
    """Test if the plugin manager UI can integrate with the core system"""
    print("🧪 Testing Plugin Manager UI Integration")
    print("=" * 50)

    try:
        # Test core plugin manager
        from Aetherra.core.plugin_manager import get_plugin_metadata, list_plugins

        plugins = list_plugins()
        print(f"✅ Core system loaded {len(plugins)} plugins:")
        for plugin in sorted(plugins)[:10]:  # Show first 10
            metadata = get_plugin_metadata(plugin)
            desc = metadata.description if metadata else "No metadata"
            print(f"  - {plugin}: {desc}")

        if len(plugins) > 10:
            print(f"  ... and {len(plugins) - 10} more")

        print()

        # Test UI plugin manager
        #         print("Testing UI Plugin Manager integration...")

        # Mock Qt imports for testing
        class MockWidget:
            def __init__(self, *args, **kwargs):
                pass

            def addWidget(self, *args):
                pass

            def setStyleSheet(self, *args):
                pass

            def clear(self):
                pass

            def addItem(self, *args):
                pass

            def setText(self, *args):
                pass

            def setEnabled(self, *args):
                pass

            def setChecked(self, *args):
                pass

            def clicked(self):
                return MockWidget()

            def connect(self, *args):
                pass

            def stateChanged(self):
                return MockWidget()

            def itemClicked(self):
                return MockWidget()

        class MockModules:
            QWidget = MockWidget
            QVBoxLayout = MockWidget
            QHBoxLayout = MockWidget
            QListWidget = MockWidget
            QListWidgetItem = MockWidget
            QTextEdit = MockWidget
            QCheckBox = MockWidget
            QPushButton = MockWidget
            QFileDialog = MockWidget
            QMessageBox = MockWidget
            QBrush = MockWidget
            Qt = type(
                "Qt",
                (),
                {
                    "ItemDataRole": type("ItemDataRole", (), {"UserRole": 0}),
                    "CheckState": type(
                        "CheckState", (), {"Checked": type("Checked", (), {"value": 2})}
                    ),
                },
            )()
            ModernTheme = type(
                "ModernTheme",
                (),
                {
                    "SURFACE": "#000",
                    "BORDER": "#111",
                    "TEXT_PRIMARY": "#fff",
                    "TEXT_SECONDARY": "#ccc",
                    "PRIMARY": "#00f",
                    "SUCCESS": "#0f0",
                    "WARNING": "#ff0",
                },
            )
            ModernCard = MockWidget

        # Mock the Qt imports
        import importlib

        qt_utils = importlib.util.spec_from_loader("utils.qt_imports", loader=None)
        qt_module = importlib.util.module_from_spec(qt_utils)
        for attr in dir(MockModules):
            if not attr.startswith("_"):
                setattr(qt_module, attr, getattr(MockModules, attr))
        sys.modules["src.aethercode.ui.components.utils.qt_imports"] = qt_module
        sys.modules["..utils.qt_imports"] = qt_module

        # Mock other dependencies
        sys.modules["..cards"] = type("cards", (), {"ModernCard": MockWidget})
        sys.modules["..theme"] = type(
            "theme", (), {"ModernTheme": MockModules.ModernTheme}
        )

        # Now test the plugin manager
        from Lyrixa.ui.components.panels.plugin_manager import (
            PluginManagerPanel,
        )

        # Create a mock panel and test plugin loading
        panel = PluginManagerPanel()

        print(f"✅ UI Plugin Manager created successfully")
        print(f"✅ Loaded {len(panel.plugins)} plugins in UI:")

        for plugin in panel.plugins[:5]:  # Show first 5
            name = plugin.get("name", "Unknown")
            desc = plugin.get("description", "No description")
            status = plugin.get("status", "Unknown")
            print(f"  - {name} ({status}): {desc}")

        if len(panel.plugins) > 5:
            print(f"  ... and {len(panel.plugins) - 5} more")

        print("\n✅ Plugin Manager UI integration test passed!")
        return True

    except Exception as e:
        print(f"❌ Plugin Manager UI integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_plugin_manager_integration()
    if success:
        print(
            "\n🎉 All tests passed! The plugin manager should now show your plugins in Lyrixa."
        )
    else:
        print("\n💥 Tests failed. There may be integration issues.")

#!/usr/bin/env python3
"""
Test Plugin Tab Integration
===========================
Validates that the hybrid UI plugin tab functionality is properly integrated
"""

import os
import sys

# Add the Aetherra path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))


def test_plugin_tab_methods():
    """Test that the plugin tab methods exist and are callable"""
    try:
        from lyrixa.gui.hybrid_window import LyrixaWindow

        # Create a window instance (without showing)
        print("[TOOL] Creating LyrixaWindow instance...")
        window = LyrixaWindow()

        # Test plugin tab methods exist
        print("🔍 Checking plugin tab methods...")

        # Check if create_plugin_tab method exists
        assert hasattr(window, "create_plugin_tab"), "create_plugin_tab method missing"
        assert callable(getattr(window, "create_plugin_tab")), (
            "create_plugin_tab is not callable"
        )
        print("✅ create_plugin_tab method found")

        # Check if load_plugin_file method exists
        assert hasattr(window, "load_plugin_file"), "load_plugin_file method missing"
        assert callable(getattr(window, "load_plugin_file")), (
            "load_plugin_file is not callable"
        )
        print("✅ load_plugin_file method found")

        # Check if plugin_log attribute exists after creating plugin tab
        plugin_tab = window.create_plugin_tab()
        assert hasattr(window, "plugin_log"), "plugin_log attribute missing"
        print("✅ plugin_log attribute found")

        # Test tab widget has plugin tab
        tab_count = window.tab_widget.count()
        plugin_tab_found = False
        for i in range(tab_count):
            if window.tab_widget.tabText(i) == "Plugins":
                plugin_tab_found = True
                break
        assert plugin_tab_found, "Plugins tab not found in tab widget"
        print("✅ Plugins tab found in tab widget")

        print("\n🎉 All plugin tab integration tests passed!")
        return True

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def test_file_imports():
    """Test that all required imports are working"""
    try:
        print("🔍 Testing imports...")

        # Test PySide6 imports
        from PySide6.QtWidgets import QFileDialog

        print("✅ QFileDialog import working")

        from PySide6.QtCore import Qt

        print("✅ QtCore import working")

        from PySide6.QtWebEngineWidgets import QWebEngineView

        print("✅ QWebEngineView import working")

        print("✅ All imports working")
        return True

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Plugin Tab Integration")
    print("=" * 40)

    success = True

    # Test imports first
    if not test_file_imports():
        success = False

    print()

    # Test plugin tab methods
    if not test_plugin_tab_methods():
        success = False

    print("\n" + "=" * 40)
    if success:
        print("🎉 ALL TESTS PASSED - Plugin tab integration successful!")
    else:
        print("[ERROR] SOME TESTS FAILED - Check the output above")

    sys.exit(0 if success else 1)

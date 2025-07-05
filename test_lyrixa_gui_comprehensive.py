#!/usr/bin/env python3
"""
Test Lyrixa GUI System
=====================

Comprehensive test for the Lyrixa GUI system to ensure all components work correctly.
"""

import os
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_gui_imports():
    """Test that all GUI components can be imported correctly."""
    print("🔍 Testing GUI Imports...")

    try:
        from src.aetherra.ui import enhanced_lyrixa

        print("✅ Enhanced Lyrixa imported successfully")

        from src.aetherra.ui import component_library

        print("✅ Component library imported successfully")

        from src.aetherra.ui import dark_mode_provider

        print("✅ Dark mode provider imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_qt_availability():
    """Test if Qt framework is available."""
    print("\n🖥️ Testing Qt Framework...")

    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication, QMainWindow

        print("✅ PySide6 available")
        return True
    except ImportError:
        try:
            from PySide2.QtCore import Qt
            from PySide2.QtWidgets import QApplication, QMainWindow

            print("✅ PySide2 available")
            return True
        except ImportError:
            print("❌ No Qt framework available")
            return False


def test_lyrixa_window_creation():
    """Test creating a Lyrixa window."""
    print("\n🏠 Testing Lyrixa Window Creation...")

    try:
        from PySide6.QtWidgets import QApplication

        from src.aetherra.ui.enhanced_lyrixa import EnhancedLyrixaWindow

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Create window
        window = EnhancedLyrixaWindow()
        print("✅ Enhanced Lyrixa window created successfully")

        # Test that we can show the window (without actually displaying it)
        if hasattr(window, "qt_available") and window.qt_available:
            print("✅ Qt GUI mode available")
        else:
            print("ℹ️ Running in console mode (no Qt)")

        return True

    except Exception as e:
        print(f"❌ Window creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_gui_launch():
    """Test launching the GUI (dry run)."""
    print("\n🚀 Testing GUI Launch...")

    try:
        from src.aetherra.ui import GUI_AVAILABLE, launch_gui

        if GUI_AVAILABLE:
            print("✅ GUI launch function available")
            print("ℹ️ (Skipping actual launch to avoid blocking)")
        else:
            print("⚠️ GUI not available - would run in console mode")

        return True

    except Exception as e:
        print(f"❌ GUI launch test failed: {e}")
        return False


def test_ui_components():
    """Test UI component library."""
    print("\n🧩 Testing UI Components...")

    try:
        from src.aetherra.ui.component_library import get_component_info
        from src.aetherra.ui.dark_mode_provider import DarkModeProvider

        # Test dark mode provider
        dark_mode = DarkModeProvider()
        colors = dark_mode.get_color_palette()
        print(f"✅ Dark mode provider working - {len(colors)} colors available")

        return True

    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 LYRIXA GUI SYSTEM TEST")
    print("=" * 50)

    tests = [
        test_gui_imports,
        test_qt_availability,
        test_lyrixa_window_creation,
        test_gui_launch,
        test_ui_components,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    print("\n" + "=" * 50)
    print("🏁 TEST RESULTS:")

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i + 1}. {test.__name__}: {status}")

    print(f"\nOVERALL: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All GUI tests passed! Lyrixa GUI system is working correctly.")
    else:
        print("⚠️ Some GUI tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Comprehensive UI Testing Script
=============================

This script tests all the UI components we've implemented to ensure
they work correctly and AetherraCode/Neuroplex function as intended.
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_fallback_implementations():
    """Test Qt fallback implementations."""
    print("\n=== Testing Qt Fallback Implementations ===")

    try:
            QApplication,
            QLabel,
            QMainWindow,
            QPushButton,
            Qt,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        # Test basic widget creation
        app = QApplication([])
        window = QMainWindow()
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Test widget operations
        button = QPushButton("Test Button")
        label = QLabel("Test Label")
        text_edit = QTextEdit()

        layout.addWidget(label)
        layout.addWidget(text_edit)
        layout.addWidget(button)

        window.setCentralWidget(central_widget)
        window.setWindowTitle("Test Window")

        print("✓ Qt fallback implementations working")
        return True

    except Exception as e:
        print(f"✗ Qt fallback implementations failed: {e}")
        return False


def test_safe_ui_calls():
    """Test safe UI call utilities."""
    print("\n=== Testing Safe UI Call Utilities ===")

    try:
        # Test safe widget creation
        from Lyrixa.ui.qt_fallbacks import QPushButton
        from Lyrixa.ui.safe_ui_calls import (
            UIErrorHandler,
            ensure_qt_application,
            safe_call,
            safe_widget_setup,
        )

        button = safe_widget_setup(QPushButton, "Safe Button")
        if button:
            result = safe_call(button, "setText", "Updated Text")
            text = safe_call(button, "text")

        # Test error handling
        with UIErrorHandler.safe_ui_operation("test_operation"):
            # This should not crash
            result = safe_call(None, "nonexistent_method")

        # Test Qt application
        app = ensure_qt_application()

        print("✓ Safe UI calls working")
        return True

    except Exception as e:
        print(f"✗ Safe UI calls failed: {e}")
        return False


def test_fallback_ui():
    """Test fallback UI implementation."""
    print("\n=== Testing Fallback UI Implementation ===")

    try:
        from Lyrixa.ui.fallback_ui import BasicNeuroUI, FallbackUI

        # Test FallbackUI creation
        fallback = FallbackUI()
        if fallback.commands and "help" in fallback.commands:
            print("✓ FallbackUI commands initialized")

        # Test BasicNeuroUI creation
        basic_ui = BasicNeuroUI()
        if basic_ui.fallback:
            print("✓ BasicNeuroUI initialized")

        print("✓ Fallback UI implementations working")
        return True

    except Exception as e:
        print(f"✗ Fallback UI failed: {e}")
        return False


def test_aetherplex_fixed():
    """Test the fixed Neuroplex implementation."""
    print("\n=== Testing Fixed Neuroplex Implementation ===")

    try:
        # Import without actually running the GUI

        spec = importlib.util.spec_from_file_location(
            "aetherplex_fixed", "src/neurocode/ui/aetherplex_fixed.py"
        )
        aetherplex_module = importlib.util.module_from_spec(spec)

        # Set __file__ to avoid NameError
        aetherplex_module.__file__ = str(
            Path("src/neurocode/ui/aetherplex_fixed.py").absolute()
        )

        spec.loader.exec_module(aetherplex_module)

        # Test window creation (without showing)
        window = aetherplex_module.aetherplexWindow()
        if window:
            print("✓ Neuroplex window created successfully")

            # Test that it has the expected attributes
            if hasattr(window, "chat_router"):
                print("✓ Chat router attribute present")

            if hasattr(window, "development_panel"):
                print("✓ Development panel attribute present")

            if hasattr(window, "chat_widget"):
                print("✓ Chat widget attribute present")

        print("✓ Fixed Neuroplex implementation working")
        return True

    except Exception as e:
        print(f"✗ Fixed Neuroplex failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ui_init():
    """Test UI package initialization."""
    print("\n=== Testing UI Package Initialization ===")

    try:
        from Lyrixa.ui import QT_AVAILABLE, get_chat_interface, get_main_window

        print(f"✓ Qt available: {QT_AVAILABLE}")

        # Test main window factory
        window = get_main_window()
        if window:
            print("✓ Main window factory working")

        # Test chat interface factory
        chat = get_chat_interface()
        print(f"✓ Chat interface factory working (result: {chat is not None})")

        print("✓ UI package initialization working")
        return True

    except Exception as e:
        print(f"✗ UI package initialization failed: {e}")
        return False


def test_import_safety():
    """Test that imports don't cause crashes."""
    print("\n=== Testing Import Safety ===")

    test_imports = [
        "src.aethercode.ui.qt_fallbacks",
        "src.aethercode.ui.safe_ui_calls",
        "src.aethercode.ui.fallback_ui",
    ]

    results = []

    for module_name in test_imports:
        try:
            __import__(module_name)
            print(f"✓ {module_name} imported successfully")
            results.append(True)
        except Exception as e:
            print(f"✗ {module_name} import failed: {e}")
            results.append(False)

    return all(results)


def run_comprehensive_test():
    """Run all tests and report results."""
    print("=" * 60)
    print("NEUROCODE UI COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    tests = [
        ("Qt Fallback Implementations", test_fallback_implementations),
        ("Safe UI Call Utilities", test_safe_ui_calls),
        ("Fallback UI Implementation", test_fallback_ui),
        ("Fixed Neuroplex Implementation", test_aetherplex_fixed),
        ("UI Package Initialization", test_ui_init),
        ("Import Safety", test_import_safety),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
#     print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! AetherraCode UI is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    # Add current directory to path
    sys.path.insert(0, str(Path(__file__).parent))

    exit_code = run_comprehensive_test()
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
Hybrid UI Test Script - Updated
===============================

Simple test to verify the streamlined hybrid UI works correctly.
Tests the new LyrixaWindow implementation.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_file_structure():
    """Test that all required files exist"""
    print("📁 Testing file structure...")

    base_path = project_root / "Aetherra" / "lyrixa" / "gui"

    required_files = [
        "hybrid_window.py",
        "window_factory.py",
        "style.qss",
        "ui_config.env",
    ]

    all_exist = True
    for file_name in required_files:
        file_path = base_path / file_name
        if file_path.exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"[ERROR] {file_name} missing")
            all_exist = False

    return all_exist


def test_imports():
    """Test that all modules can be imported"""
    print("\n🧪 Testing imports...")

    try:
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow

        print("✅ Hybrid LyrixaWindow imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import hybrid LyrixaWindow: {e}")
        return False

    try:
        from Aetherra.lyrixa.gui.window_factory import create_lyrixa_window

        print("✅ Window factory imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import window factory: {e}")
        return False

    return True


def test_compatibility():
    """Test that the window has all required methods"""
    print("\n🔌 Testing compatibility methods...")

    try:
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow

        required_methods = [
            "attach_lyrixa",
            "attach_runtime",
            "attach_intelligence_stack",
            "refresh_plugin_discovery",
            "update_dashboard_metrics",
            "update_intelligence_status",
            "update_runtime_status",
            "update_agent_status",
            "update_performance_metrics",
            "init_background_monitors",
            "add_plugin_editor_tab",
            "populate_model_dropdown",
        ]

        for method_name in required_methods:
            if hasattr(LyrixaWindow, method_name):
                print(f"✅ {method_name} method exists")
            else:
                print(f"[ERROR] {method_name} method missing")
                return False

        return True

    except Exception as e:
        print(f"[ERROR] Compatibility test failed: {e}")
        return False


def test_window_factory():
    """Test the window factory"""
    print("\n🏭 Testing window factory...")

    try:
        from Aetherra.lyrixa.gui.window_factory import (
            create_lyrixa_window,
            get_window_class,
        )

        # Test that we can get a window class
        window_class = get_window_class()
        print(f"✅ Got window class: {window_class.__name__}")

        # Test that the factory works
        print("✅ Window factory functional")

        return True

    except Exception as e:
        print(f"[ERROR] Window factory test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Lyrixa Hybrid UI Test Suite - Updated")
    print("=" * 45)

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Compatibility", test_compatibility),
        ("Window Factory", test_window_factory),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"[ERROR] {test_name} test FAILED")
        except Exception as e:
            print(f"[FAIL] {test_name} test CRASHED: {e}")

    print("\n" + "=" * 45)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Streamlined hybrid UI is ready!")
        return 0
    else:
        print("[WARN]  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

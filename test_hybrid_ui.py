#!/usr/bin/env python3
"""
Hybrid UI Test Script
=====================

Simple test to verify the hybrid UI components work correctly.
Tests the window factory and basic functionality.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all hybrid UI modules can be imported"""
    print("🧪 Testing imports...")

    try:
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow as LyrixaHybridWindow

        print("✅ LyrixaHybridWindow imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LyrixaHybridWindow: {e}")
        return False

    try:
        from Aetherra.lyrixa.gui.window_factory import (
            create_lyrixa_window,
            get_window_class,
        )

        print("✅ Window factory imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import window factory: {e}")
        return False

    return True


def test_window_factory():
    """Test the window factory selection logic"""
    print("\n🏭 Testing window factory...")

    try:
        from Aetherra.lyrixa.gui.gui_window import LyrixaWindow
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaHybridWindow
        from Aetherra.lyrixa.gui.window_factory import get_window_class

        # Test classic mode
        os.environ["LYRIXA_UI_MODE"] = "classic"
        window_class = get_window_class()
        assert window_class == LyrixaWindow, (
            "Should return LyrixaWindow for classic mode"
        )
        print("✅ Classic mode selection works")

        # Test hybrid mode
        os.environ["LYRIXA_UI_MODE"] = "hybrid"
        window_class = get_window_class()
        assert window_class == LyrixaHybridWindow, (
            "Should return LyrixaHybridWindow for hybrid mode"
        )
        print("✅ Hybrid mode selection works")

        return True

    except Exception as e:
        print(f"❌ Window factory test failed: {e}")
        return False


def test_compatibility_methods():
    """Test that hybrid window has all required compatibility methods"""
    print("\n🔌 Testing compatibility methods...")

    try:
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaHybridWindow

        # Create window instance (without Qt app for testing)
        # This will fail at Qt initialization but we can check methods exist
        window_class = LyrixaHybridWindow

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
        ]

        for method_name in required_methods:
            if hasattr(window_class, method_name):
                print(f"✅ {method_name} method exists")
            else:
                print(f"❌ {method_name} method missing")
                return False

        return True

    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")

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
            print(f"❌ {file_name} missing")
            all_exist = False

    return all_exist


def main():
    """Run all tests"""
    print("🚀 Lyrixa Hybrid UI Test Suite")
    print("=" * 40)

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Window Factory", test_window_factory),
        ("Compatibility Methods", test_compatibility_methods),
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
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"💥 {test_name} test CRASHED: {e}")

    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Hybrid UI is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

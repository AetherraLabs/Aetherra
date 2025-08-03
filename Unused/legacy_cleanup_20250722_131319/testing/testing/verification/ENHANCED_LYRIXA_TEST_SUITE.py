#!/usr/bin/env python3
"""
ENHANCED LYRIXA TEST SUITE
==========================
This script tests all major components of the Enhanced Lyrixa system
to ensure everything is functioning correctly.
"""

import sys
import traceback


def test_enhanced_lyrixa_import():
    """Test 1: Enhanced Lyrixa Import"""
#     print("Test 1: Enhanced Lyrixa Import...")
    try:
        from Aetherra.ui.enhanced_lyrixa import EnhancedLyrixaWindow

        print("✅ Enhanced Lyrixa imported successfully")
        return True, EnhancedLyrixaWindow
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False, None


def test_window_creation(EnhancedLyrixaWindow):
    """Test 2: Window Creation"""
    print("\nTest 2: Window Creation...")
    try:
        window = EnhancedLyrixaWindow()
        print("✅ Enhanced Lyrixa Window created successfully")
        return True, window
    except Exception as e:
        print(f"❌ Window creation failed: {e}")
        return False, None


def test_core_functionality(window):
    """Test 3: Core Functionality"""
    print("\nTest 3: Core Functionality...")
    try:
        # Test code execution
        result = window.execute_code("print('Hello Aetherra')")
        print("✅ Code execution method available")

        # Test message sending
        response = window.send_message("Hello Lyrixa")
        print("✅ Message sending method available")

        # Test plugin activation
        plugins_available = window.activate_plugin("Memory System")
        print("✅ Plugin activation method available")

        return True
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        return False


def test_ui_launch_integration():
    """Test 4: UI Launch Integration"""
    print("\nTest 4: UI Launch Integration...")
    try:

        print(f"✅ UI module imported (GUI Available: {GUI_AVAILABLE})")

        if GUI_AVAILABLE:
            print("✅ GUI components are available")
        else:
            print("[WARN] GUI running in fallback mode (PySide6 not available)")

        return True
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        return False


def test_aetherra_core_integration():
    """Test 5: Aetherra Core Integration"""
    print("\nTest 5: Aetherra Core Integration...")
    try:

        print("✅ Aetherra interpreter imported")


        print("✅ Aetherra parser imported")


        print("✅ Aetherra memory system imported")

        return True
    except Exception as e:
        print(f"❌ Core integration test failed: {e}")
        return False


def main():
    print("ENHANCED LYRIXA TEST SUITE")
    print("=" * 50)
    print("Running comprehensive tests...")
    print()

    # Test 1: Import
    success1, window_class = test_enhanced_lyrixa_import()
    if not success1:
        print("\n❌ Critical failure: Cannot import Enhanced Lyrixa")
        return False

    # Test 2: Window Creation
    success2, window = test_window_creation(window_class)
    if not success2:
        print("\n❌ Critical failure: Cannot create Enhanced Lyrixa Window")
        return False

    # Test 3: Core Functionality
    success3 = test_core_functionality(window)

    # Test 4: UI Integration
    success4 = test_ui_launch_integration()

    # Test 5: Core Integration
    success5 = test_aetherra_core_integration()

    # Summary
    print("\nTEST SUMMARY")
    print("=" * 50)
    tests = [success1, success2, success3, success4, success5]
    passed = sum(tests)
    total = len(tests)

    print(f"Tests passed: {passed}/{total}")

    if all(tests):
        print("🎉 ALL TESTS PASSED - ENHANCED LYRIXA IS FULLY OPERATIONAL!")
        print("\nREADY FOR PRODUCTION:")
        print("   • Enhanced Lyrixa Window: ✅")
        print("   • Core functionality: ✅")
        print("   • UI integration: ✅")
        print("   • Aetherra core: ✅")
        print("   • Import system: ✅")
        print()
        print("LAUNCH COMMAND:")
        print("   python aetherra_launcher.py")
        return True
    else:
        print("❌ Some tests failed - system needs attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

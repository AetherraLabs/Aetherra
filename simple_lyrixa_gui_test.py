#!/usr/bin/env python3
"""
Simple Lyrixa GUI Test - Windows Compatible
===========================================

A minimal test to verify the Lyrixa GUI system is working correctly.
This uses ASCII characters for Windows compatibility.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_gui_imports():
    """Test that GUI components can be imported."""
    print("[*] Testing GUI imports...")

    try:
        from PySide6.QtWidgets import QApplication

        print("   [+] PySide6 available")
        return True
    except ImportError as e:
        print(f"   [-] PySide6 not available: {e}")
        return False


def test_modern_gui():
    """Test the modern GUI can be imported."""
    print("[*] Testing Modern GUI...")

    try:
        from modern_lyrixa_gui import ModernLyrixaGUI

        print("   [+] Modern GUI class available")
        return True
    except ImportError as e:
        print(f"   [-] Modern GUI not available: {e}")
        return False


def test_unified_gui():
    """Test the unified GUI can be imported."""
    print("[*] Testing Unified GUI...")

    try:
        from unified_aetherra_lyrixa_gui import UnifiedAetherraLyrixaGUI

        print("   [+] Unified GUI class available")
        return True
    except ImportError as e:
        print(f"   [-] Unified GUI not available: {e}")
        return False


def test_enhanced_gui():
    """Test the enhanced GUI can be imported."""
    print("[*] Testing Enhanced GUI...")

    try:
        from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

        print("   [+] Enhanced GUI class available")
        return True
    except ImportError as e:
        print(f"   [-] Enhanced GUI not available: {e}")
        return False


def test_gui_creation():
    """Test that we can actually create a GUI instance."""
    print("[*] Testing GUI creation...")

    try:
        from PySide6.QtWidgets import QApplication

        # Create QApplication
        app = QApplication.instance() or QApplication(sys.argv)

        # Try to create Modern GUI
        try:
            from modern_lyrixa_gui import ModernLyrixaGUI

            gui = ModernLyrixaGUI()
            print("   [+] Modern GUI created successfully")
            return True
        except Exception as e:
            print(f"   [!] Modern GUI creation failed: {e}")

            # Try Enhanced GUI as fallback
            try:
                from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

                gui = EnhancedLyrixaWindow()
                print("   [+] Enhanced GUI created successfully")
                return True
            except Exception as e:
                print(f"   [-] Enhanced GUI creation failed: {e}")
                return False

    except ImportError as e:
        print(f"   [-] GUI creation failed: {e}")
        return False


def main():
    """Run all GUI tests."""
    print("SIMPLE LYRIXA GUI TEST")
    print("=" * 30)
    print("Testing GUI components for Windows compatibility...")
    print()

    tests = [
        test_gui_imports,
        test_modern_gui,
        test_unified_gui,
        test_enhanced_gui,
        test_gui_creation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   [-] Test error: {e}")
            failed += 1
        print()

    print("=" * 30)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")

    if failed == 0:
        print("[+] All GUI tests passed!")
        print("[*] Lyrixa GUI system is ready for use.")
        print("[*] Run: python lyrixa_unified_launcher_win.py")
    else:
        print(f"[!] {failed} test(s) failed")
        print("[*] Check dependencies and installation")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
🔍 LAUNCHER UI VERIFICATION
🎯 Verify launcher is using new 11-tab hybrid UI
⚡ Quick validation test

This script verifies that the main launcher is properly
configured to use the new hybrid window with all 11 tabs.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_launcher_hybrid_ui():
    """Test that launcher uses the new hybrid UI"""
    print("🔍 LAUNCHER HYBRID UI VERIFICATION")
    print("=" * 40)

    try:
        # Test launcher import
        print("📋 Testing launcher configuration...")

        # Read launcher file to verify import
        launcher_path = "Aetherra/lyrixa/launcher.py"
        with open(launcher_path, "r", encoding="utf-8") as f:
            launcher_content = f.read()

        # Check for hybrid window import
        if (
            "from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow"
            in launcher_content
        ):
            print("✅ Launcher imports new hybrid_window.LyrixaWindow")
        else:
            print("[ERROR] Launcher still using old gui_window import")
            return False

        # Check for old import (should not be present)
        if (
            "from Aetherra.lyrixa.gui.gui_window import LyrixaWindow"
            in launcher_content
        ):
            print("[WARN] WARNING: Launcher still has old gui_window import")
            return False
        else:
            print("✅ Old gui_window import removed")

        # Check for header comment about hybrid UI
        if "HYBRID UI" in launcher_content and "11-Tab" in launcher_content:
            print("✅ Launcher header updated for hybrid UI")
        else:
            print("[WARN] Launcher header not updated")

        # Test that we can import the hybrid window from launcher path
        sys.path.insert(
            0, os.path.join(os.path.dirname(__file__), "Aetherra", "lyrixa")
        )
        from gui.hybrid_window import LyrixaWindow

        print("✅ Hybrid window imports successfully from launcher path")

        # Test window creation
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = LyrixaWindow()
        print("✅ Hybrid window creates successfully")

        # Verify it has all 11 tabs
        tab_count = window.tab_widget.count()
        if tab_count == 11:
            print(f"✅ Hybrid window has all {tab_count} tabs")
        else:
            print(f"[ERROR] Hybrid window has {tab_count} tabs, expected 11")
            return False

        # Check for Agent Collab tab specifically
        last_tab_name = window.tab_widget.tabText(10)  # 11th tab (index 10)
        if last_tab_name == "Agent Collab":
            print("✅ Agent Collaboration tab present (newest feature)")
        else:
            print(f"[ERROR] Expected 'Agent Collab' tab, found '{last_tab_name}'")
            return False

        print("\n🎉 LAUNCHER VERIFICATION PASSED!")
        print("🚀 Main launcher now uses new 11-tab hybrid UI!")

        return True

    except Exception as e:
        print(f"[ERROR] Launcher verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_launcher_execution():
    """Test launcher execution (dry run)"""
    print("\n🔍 LAUNCHER EXECUTION TEST")
    print("=" * 30)

    try:
        print("📋 Testing launcher can be imported...")

        # Test launcher import
        sys.path.insert(
            0, os.path.join(os.path.dirname(__file__), "Aetherra", "lyrixa")
        )
        import launcher

        print("✅ Launcher module imports successfully")

        # Check launcher has launch_gui function
        if hasattr(launcher, "launch_gui"):
            print("✅ Launcher has launch_gui function")
        else:
            print("[ERROR] Launcher missing launch_gui function")
            return False

        print("✅ Launcher execution test passed")
        return True

    except Exception as e:
        print(f"[ERROR] Launcher execution test failed: {e}")
        return False


def main():
    """Main verification function"""
    print("🌟 AETHERRA LYRIXA LAUNCHER")
    print("🔍 HYBRID UI VERIFICATION TEST")
    print("🎯 Confirming 11-Tab Interface Integration")
    print("\n" + "=" * 50)

    # Run tests
    ui_test = test_launcher_hybrid_ui()
    exec_test = test_launcher_execution()

    print("\n" + "=" * 50)
    print("🏆 VERIFICATION RESULTS:")
    print("=" * 25)

    print(f"   {'✅ PASSED' if ui_test else '[ERROR] FAILED'} Hybrid UI Integration")
    print(f"   {'✅ PASSED' if exec_test else '[ERROR] FAILED'} Launcher Execution")

    if ui_test and exec_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Launcher successfully updated to use hybrid UI")
        print("✅ All 11 tabs including Agent Collaboration")
        print("✅ Ready for production use")
        print("\n🚀 TO RUN THE NEW UI:")
        print("   python Aetherra/lyrixa/launcher.py")
        print("\n🌟 Enjoy your revolutionary 11-tab AI interface!")
    else:
        print("\n[ERROR] SOME TESTS FAILED!")
        print("[TOOL] Please review failed tests above")

    print("=" * 50)


if __name__ == "__main__":
    main()

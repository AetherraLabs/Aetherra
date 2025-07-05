#!/usr/bin/env python3
"""
Simple test to check if GUI can be launched
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "lyrixa"))
sys.path.insert(0, str(project_root / "src"))


def test_gui_import():
    """Test if GUI can be imported."""
    print("🔍 Testing GUI imports...")

    try:
        from PySide6.QtWidgets import QApplication

        print("✅ PySide6 import successful")
    except ImportError as e:
        print(f"❌ PySide6 import failed: {e}")
        return False

    try:
        from unified_aetherra_lyrixa_gui import UnifiedAetherraLyrixaGUI

        print("✅ Unified GUI import successful")
        return True
    except ImportError as e:
        print(f"❌ Unified GUI import failed: {e}")
        try:
            from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

            print("✅ Enhanced Lyrixa fallback import successful")
            return True
        except ImportError as e2:
            print(f"❌ Enhanced Lyrixa fallback import failed: {e2}")
            return False


def test_gui_creation():
    """Test if GUI can be created and shown."""
    print("\n🖥️ Testing GUI creation...")

    try:
        from PySide6.QtWidgets import QApplication

        # Create QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("Lyrixa Test")

        try:
            from unified_aetherra_lyrixa_gui import UnifiedAetherraLyrixaGUI

            print("🚀 Creating Unified GUI window...")
            main_window = UnifiedAetherraLyrixaGUI()
            main_window.show()
            print("✅ Unified GUI window created and shown")

        except ImportError:
            print("⚠️ Unified GUI not available, trying Enhanced Lyrixa...")
            from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

            main_window = EnhancedLyrixaWindow()
            main_window.show()
            print("✅ Enhanced Lyrixa window created and shown")

        print("🎯 GUI should now be visible!")
        print("   (If not visible, there may be a display issue)")

        # Don't run the event loop in test mode
        # return app.exec()
        return True

    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 LYRIXA GUI LAUNCH TEST")
    print("=" * 40)

    if not test_gui_import():
        print("❌ GUI imports failed")
        sys.exit(1)

    if not test_gui_creation():
        print("❌ GUI creation failed")
        sys.exit(1)

    print("\n✅ GUI TEST COMPLETED SUCCESSFULLY")
    print("   The GUI should be able to launch properly")

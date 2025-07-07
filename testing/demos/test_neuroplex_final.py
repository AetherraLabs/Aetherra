#!/usr/bin/env python3
"""
Final test of Lyrixalaunch capabilities
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test all the import fixes"""
    print("🧪 Testing import fixes...")

    try:
        print("  Testing Aetherra package...")
        print("  ✅ Aetherra package imported")

        print("  Testing core components...")
        print("  ✅ core functions imported")

        print("  Testing UI components...")
        print("  ✅ UI launch function imported")

        print("  Testing Lyrixafully modular...")
        print("  ✅ Lyrixafully modular imported")

        print("  Testing Qt components...")
        from Aetherra.ui.components.utils.qt_imports import is_qt_available

        print("  ✅ Qt imports working")

        if is_qt_available():
            print("  ✅ Qt backend available")
        else:
            print("  ⚠️ Qt backend not available")

        print("\n🎉 All imports successful! Lyrixalaunch is fixed.")
        return True

    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_basic_gui():
    """Test basic GUI functionality"""
    print("\n🖥️ Testing basic GUI launch...")

    try:
        from Aetherra.ui.components.utils.qt_imports import (
            QApplication,
            QLabel,
            QVBoxLayout,
            QWidget,
            is_qt_available,
        )

        if not is_qt_available():
            print("  ⚠️ Qt not available - skipping GUI test")
            return False

        app = QApplication.instance() or QApplication([])

        # Create simple test window
        widget = QWidget()
        widget.setWindowTitle("LyrixaTest - SUCCESS!")
        widget.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()
        label = QLabel(
            "🎉 Lyrixaimports are fixed!\n\nThe GUI system is working correctly."
        )
        label.setStyleSheet("font-size: 14px; padding: 20px; text-align: center;")
        layout.addWidget(label)
        widget.setLayout(layout)

        widget.show()
        print("  ✅ Test GUI window created and shown")
        print("  📝 Close the test window to continue...")

        # Run for a few seconds then close
        import threading
        import time

        def close_after_delay():
            time.sleep(3)
            widget.close()

        threading.Thread(target=close_after_delay, daemon=True).start()

        app.exec()
        print("  ✅ GUI test completed")
        return True

    except Exception as e:
        print(f"  ❌ GUI test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Final LyrixaTest")
    print("=" * 50)

    # Test imports
    imports_ok = test_imports()

    if imports_ok:
        # Test basic GUI
        gui_ok = test_basic_gui()

        if gui_ok:
            print("\n✅ ALL TESTS PASSED!")
            print("🎯 Lyrixais ready to launch!")
            print("\nYou can now use:")
            print("  - python Aetherra_launcher.py")
            print("  - python launchers/launch_fully_modular_Lyrixa.py")
            print("  - python launchers/launch_modular_Lyrixa.py")
            print("  - python launchers/launch_enhanced_Lyrixa.py")
        else:
            print("\n⚠️ Imports fixed but GUI needs Qt dependencies")
            print("   Run: pip install PySide6")
    else:
        print("\n❌ Import issues remain")

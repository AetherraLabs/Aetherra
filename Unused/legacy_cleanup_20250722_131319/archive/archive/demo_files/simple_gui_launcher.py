#!/usr/bin/env python3
"""
Simple Lyrixa GUI Launcher - Minimal Version
Just launches the Enhanced Lyrixa GUI without complex phase initialization
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "lyrixa"))
sys.path.insert(0, str(project_root / "src"))


def launch_simple_gui():
    """Launch the Enhanced Lyrixa GUI directly."""
    try:
        print("🚀 LYRIXA SIMPLE GUI LAUNCHER")
        print("=" * 40)

        # Import PySide6
        from PySide6.QtWidgets import QApplication

        print("✅ PySide6 imported successfully")

        # Create application
        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("Lyrixa AI Assistant")
        app.setApplicationVersion("2.0")
        print("✅ QApplication created")

        # Import and create Enhanced Lyrixa window
        from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

        print("✅ Enhanced Lyrixa imported successfully")

        # Create main window
        main_window = EnhancedLyrixaWindow()
        print("✅ Enhanced Lyrixa window created")

        # Show window
        main_window.show()
        print("✅ Window shown - GUI should now be visible!")

        # Run application
        print("🎯 Starting GUI event loop...")
        return app.exec()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = launch_simple_gui()
    sys.exit(exit_code)

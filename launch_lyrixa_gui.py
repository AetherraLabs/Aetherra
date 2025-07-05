#!/usr/bin/env python3
"""
Lyrixa GUI Launcher
==================

Simple launcher for the Lyrixa GUI system.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def launch_lyrixa_gui():
    """Launch the Lyrixa GUI."""
    print("🎙️ Launching Lyrixa GUI...")

    try:
        # Check Qt availability
        from PySide6.QtWidgets import QApplication

        print("✅ PySide6 available")

        # Import Lyrixa window
        from src.aetherra.ui.enhanced_lyrixa import EnhancedLyrixaWindow

        print("✅ Lyrixa GUI components loaded")

        # Create application
        app = QApplication(sys.argv)

        # Create and show window
        window = EnhancedLyrixaWindow()
        print("✅ Lyrixa window created")

        # Show the window
        result = window.show()
        print("✅ Lyrixa GUI launched successfully!")

        # Run the application
        if hasattr(window, "qt_available") and window.qt_available:
            print("🚀 Starting Qt application loop...")
            sys.exit(app.exec())
        else:
            print("ℹ️ Running in console mode")
            return window

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("To use the GUI, install PySide6: pip install PySide6")
        return None
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    print("🎙️ LYRIXA GUI LAUNCHER")
    print("=" * 30)

    result = launch_lyrixa_gui()

    if result is None:
        print("\n❌ Failed to launch Lyrixa GUI")
        sys.exit(1)
    else:
        print("\n✅ Lyrixa GUI session completed")


if __name__ == "__main__":
    main()

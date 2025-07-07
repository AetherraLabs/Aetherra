#!/usr/bin/env python3
"""
🌙 LYRIXA MODERN GUI LAUNCHER
============================

Simple launcher specifically for the modern dark mode Lyrixa GUI.
This launcher focuses on providing a clean, stable interface.

Usage:
    python launch_modern_lyrixa.py
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Launch the modern Lyrixa GUI."""
    print("🌙 LYRIXA MODERN GUI LAUNCHER")
    print("=" * 35)

    # Check dependencies
    try:
        from PySide6.QtWidgets import QApplication

        print("✅ PySide6 GUI framework available")
    except ImportError:
        print("❌ PySide6 not installed")
        print("💡 Install with: pip install PySide6")
        return 1

    try:
        from modern_lyrixa_gui import ModernLyrixaGUI

        print("✅ Modern Lyrixa GUI available")
    except ImportError as e:
        print(f"❌ Modern GUI import failed: {e}")
        return 1

    # Launch GUI
    print("\n🚀 Launching Modern Lyrixa GUI...")

    # Create QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Lyrixa AI Assistant")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Aetherra")

    # Create and show main window
    window = ModernLyrixaGUI()
    window.show()

    print("🎯 Modern Lyrixa GUI launched successfully!")
    print("🌙 Enjoy the beautiful dark mode interface!")

    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

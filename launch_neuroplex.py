#!/usr/bin/env python3
"""
🚀 Neuroplex Launcher
Quick launcher for the Neuroplex GUI with PySide6 support
"""

import sys
from pathlib import Path

# Add UI path
ui_path = Path(__file__).parent / "ui"
sys.path.insert(0, str(ui_path))

# Check for Qt availability - prioritize PySide6
QT_AVAILABLE = False
QApplication = None

try:
    # Try PySide6 first (our standard)
    from PySide6.QtWidgets import QApplication

    QT_AVAILABLE = True
    QT_BACKEND = "PySide6"
    print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI")
except ImportError:
    try:
        # Fallback to PyQt6
        from PyQt6.QtWidgets import QApplication

        QT_AVAILABLE = True
        QT_BACKEND = "PyQt6"
        print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI")
    except ImportError:
        try:
            # Last resort: PyQt5
            from PyQt5.QtWidgets import QApplication

            QT_AVAILABLE = True
            QT_BACKEND = "PyQt5"
            print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI")
        except ImportError:
            print("❌ No Qt library available!")
            print("💡 Install one of: pip install PySide6 (recommended)")
            print("💡 Alternative: pip install PyQt6")
            print("💡 Legacy: pip install PyQt5")
            sys.exit(1)

# Import and run Neuroplex
try:
    from neuroplex_gui import NeuroplexMainWindow

    print("🧬 Starting Neuroplex - The Future of AI-Native Programming!")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = NeuroplexMainWindow()
    window.show()

    if QT_BACKEND == "PySide6":
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())

except ImportError as e:
    print(f"❌ Missing dependencies for GUI: {e}")
    print(f"💡 Current Qt backend: {QT_BACKEND if QT_AVAILABLE else 'None'}")
    print("💡 Make sure Neuroplex GUI components are available")
    sys.exit(1)
except Exception as e:
    print(f"❌ Failed to launch Neuroplex: {e}")
    print("💡 Check that all UI dependencies are properly installed")
    sys.exit(1)

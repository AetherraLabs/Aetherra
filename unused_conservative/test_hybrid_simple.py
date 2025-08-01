#!/usr/bin/env python3
"""
Simple test launcher for the hybrid interface
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test all required imports"""
    try:
        print("Testing PySide6 imports...")
        from PySide6.QtWebChannel import QWebChannel
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWidgets import QApplication, QMainWindow

        print("✅ PySide6 imports successful")

        print("Testing Aetherra imports...")
        from Aetherra.lyrixa.gui.web_bridge import LyrixaWebBridge, LyrixaWebView

        print("✅ Web bridge imports successful")

        from Aetherra.lyrixa.gui.aetherra_main_window_hybrid import AetherraMainWindow

        print("✅ Hybrid main window import successful")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def create_simple_test():
    """Create a simple test window"""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QVBoxLayout,
        QWidget,
    )

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Lyrixa Hybrid Test")
    window.resize(800, 600)

    central = QWidget()
    layout = QVBoxLayout(central)

    label = QLabel("🧠 Lyrixa Hybrid Interface Test")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("""
        QLabel {
            color: #00ff88;
            font-size: 24px;
            font-weight: bold;
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
        }
    """)
    layout.addWidget(label)

    # Try to add web view
    try:
        from Aetherra.lyrixa.gui.web_bridge import LyrixaWebView

        web_view = LyrixaWebView()
        layout.addWidget(web_view)
        print("✅ Web view added successfully")
    except Exception as e:
        error_label = QLabel(f"Web view error: {e}")
        error_label.setStyleSheet("color: #ff6666; padding: 10px;")
        layout.addWidget(error_label)
        print(f"❌ Web view failed: {e}")

    window.setCentralWidget(central)
    window.setStyleSheet("""
        QMainWindow {
            background: #0a0a0a;
        }
    """)

    window.show()
    return app.exec()


def main():
    print("🚀 Testing Lyrixa Hybrid Interface...")

    if not test_imports():
        return 1

    print("\n🎮 Creating test window...")
    return create_simple_test()


if __name__ == "__main__":
    sys.exit(main())

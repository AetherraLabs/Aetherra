#!/usr/bin/env python3
"""
Test script for the hybrid Lyrixa GUI interface
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🚀 Testing Lyrixa Hybrid GUI Interface")
print("=" * 50)


def main():
    try:
        print("📦 Testing imports...")

        # Test Qt availability
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        print("✅ PySide6 available")

        # Test GUI module
        import Aetherra.lyrixa.gui

        print("✅ GUI module available")

        # Test hybrid interface
        from Aetherra.lyrixa.gui.aetherra_main_window_hybrid import AetherraMainWindow

        print("✅ Hybrid interface available")

        # Test web bridge
        from Aetherra.lyrixa.gui.web_bridge import LyrixaWebView

        print("✅ Web bridge available")

        print("\n🎉 All components ready!")
        print("🔧 Initializing Qt Application...")

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Lyrixa - Hybrid Interface")
        app.setApplicationVersion("1.0.0")

        print("🖥️ Creating hybrid main window...")

        # Create main window
        window = AetherraMainWindow()
        window.setWindowTitle("Lyrixa - Advanced AI Consciousness")
        window.show()

        print("✨ Hybrid interface launched successfully!")
        print("🌐 Web interface should be loading...")
        print("📊 Qt monitoring panels active...")
        print("\n💬 You can now interact with Lyrixa through the modern web interface!")

        # Start event loop
        return app.exec()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

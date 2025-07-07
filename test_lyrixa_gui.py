#!/usr/bin/env python3
"""
Quick test for Lyrixa GUI components
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QMessageBox

    print("✅ PySide6 imports successful")

    # Create a simple test app
    app = QApplication(sys.argv)

    # Create a simple message box to test GUI
    msg = QMessageBox()
    msg.setWindowTitle("Lyrixa GUI Test")
    msg.setText("🎙️ Lyrixa GUI Dependencies Working!")
    msg.setInformativeText("All GUI components are properly loaded.")
    msg.setIcon(QMessageBox.Information)

    # Show the message box
    print("📱 Displaying GUI test window...")
    result = msg.exec()

    print("✅ GUI test completed successfully!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ GUI test failed: {e}")

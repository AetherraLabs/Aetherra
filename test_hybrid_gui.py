#!/usr/bin/env python3
"""
Test script for the Lyrixa Hybrid GUI
"""
import sys
from pathlib import Path

# Add the Aetherra path
project_root = Path(__file__).parent
aetherra_path = project_root / "Aetherra"
sys.path.insert(0, str(aetherra_path))

try:
    print("🔍 Testing Lyrixa Hybrid GUI...")

    # Import required modules
    from PySide6.QtWidgets import QApplication
    from lyrixa_core.gui.main_window import LyrixaHybridWindow

    print("[OK] Imports successful")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa Hybrid GUI Test")

    print("[OK] Qt Application created")

    # Create main window
    window = LyrixaHybridWindow()
    print("[OK] Hybrid window created")

    # Show window
    window.show()
    print("🚀 Hybrid GUI launched successfully!")
    print("🎨 Web panels with Aetherra styling should be visible")
    print("📡 WebChannel bridge is active")

    # Run event loop
    sys.exit(app.exec())

except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("💡 Make sure PySide6 is installed: pip install PySide6")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

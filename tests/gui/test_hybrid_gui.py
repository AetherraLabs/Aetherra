#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Test script for the Lyrixa Hybrid GUI
"""

# Standard library imports
import sys
from pathlib import Path

# Add the Aetherra path
project_root = Path(__file__).parent
aetherra_path = project_root / "Aetherra"
sys.path.insert(0, str(aetherra_path))

try:
    print("🔍 Testing Lyrixa Hybrid GUI...")

    # Import required modules
    # Third party imports
    from lyrixa.gui.main_window import LyrixaHybridWindow
    from PySide6.QtWidgets import QApplication

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
    sys.exit(app.exec()  # nosec B102: Qt application execution)

except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("💡 Make sure PySide6 is installed: pip install PySide6")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    # Standard library imports
    import traceback

    traceback.print_exc()

#!/usr/bin/env python3
"""
Simplified GUI launcher to test import fixes
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧬 Starting NeuroCode GUI...")

# Test Qt separately
print("1. Testing Qt availability...")
try:
    from PySide6.QtWidgets import QApplication
    print("   ✅ PySide6 available")
    qt_backend = "PySide6"
except ImportError:
    try:
        from PyQt6.QtWidgets import QApplication
        print("   ✅ PyQt6 available")  
        qt_backend = "PyQt6"
    except ImportError:
        print("   ❌ No Qt library available")
        sys.exit(1)

# Test core modules separately
print("2. Testing core module availability...")
core_available = True

try:
    sys.path.insert(0, str(project_root / "core"))
    import interpreter
    print("   ✅ Interpreter module available")
except Exception as e:
    print(f"   ⚠️ Interpreter issue: {e}")
    core_available = False

try:
    import memory
    print("   ✅ Memory module available")
except Exception as e:
    print(f"   ⚠️ Memory issue: {e}")
    core_available = False

try:
    import chat_router
    print("   ✅ Chat router available")
except Exception as e:
    print(f"   ⚠️ Chat router issue: {e}")
    core_available = False

print(f"3. Core modules status: {'✅ Available' if core_available else '⚠️ Demo mode'}")

# Now try to import and run the GUI
print("4. Launching GUI...")
try:
    if qt_backend == "PySide6":
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QApplication,
            QLabel,
            QMainWindow,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )
    else:
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import (
            QApplication,
            QLabel,
            QMainWindow,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

    class SimpleNeuroplexGUI(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🧬 Neuroplex - Simple Launcher")
            self.setMinimumSize(800, 600)
            
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Status label
            status = "✅ All systems operational" if core_available else "⚠️ Running in demo mode"
            status_label = QLabel(f"Status: {status}")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(status_label)
            
            # Welcome message
            welcome = QLabel("🧬 Welcome to NeuroCode!\nThe first AI-native programming language.")
            welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(welcome)
            
            # Launch button
            launch_btn = QPushButton("Launch Full Neuroplex")
            launch_btn.clicked.connect(self.launch_full_gui)
            layout.addWidget(launch_btn)
            
        def launch_full_gui(self):
            try:
                # Import the full GUI
                from ui.neuroplex_gui import NeuroplexMainWindow
                self.full_window = NeuroplexMainWindow()
                self.full_window.show()
                self.hide()
            except Exception as e:
                print(f"❌ Failed to launch full GUI: {e}")
    
    app = QApplication(sys.argv)
    window = SimpleNeuroplexGUI()
    window.show()
    
    print("✅ GUI launched successfully!")
    sys.exit(app.exec())

except Exception as e:
    print(f"❌ GUI launch failed: {e}")
    import traceback
    traceback.print_exc()

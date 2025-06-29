#!/usr/bin/env python3
"""
🚀 Neuroplex Launcher
Quick launcher for the Neuroplex GUI
"""

import sys
from pathlib import Path

# Add UI path
ui_path = Path(__file__).parent / "ui"
sys.path.insert(0, str(ui_path))

# Import and run Neuroplex
try:
    import sys
    from PyQt5.QtWidgets import QApplication
    from neuroplex_gui import NeuroplexMainWindow

    print("🧬 Starting Neuroplex - The Future of AI-Native Programming!")
    
    app = QApplication(sys.argv)
    window = NeuroplexMainWindow()
    window.show()
    sys.exit(app.exec_())
    
except ImportError as e:
    print(f"❌ Missing dependencies for GUI: {e}")
    print("💡 Try: pip install PyQt5")
    sys.exit(1)
except Exception as e:
    print(f"❌ Failed to launch Neuroplex: {e}")
    sys.exit(1)

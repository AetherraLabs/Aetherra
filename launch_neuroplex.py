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
    from neuroplex_gui import main
    print("🧬 Starting Neuroplex - The Future of AI-Native Programming!")
    main()
except Exception as e:
    print(f"❌ Failed to launch Neuroplex: {e}")
    sys.exit(1)

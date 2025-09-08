#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌌 Aetherra OS Enhanced Neural Dashboard Launcher
===============================================

Launch the unified Aetherra OS with all requested visual enhancements:

🌌 High-Impact Visual Features:
✅ Pulsating Neural Web (Background Layer)
✅ Animated Quantum Core (Centerpiece)
✅ Live Memory Graph Integration
✅ Consciousness Timeline
✅ Introspective Diagnostics
✅ Plugin Aura Viewer
✅ Fractal-Inspired UI Elements
✅ Synthetic Soul Metrics
✅ Real-time Neural Activity
✅ Quantum Observer Effects

This creates a single, unified Aetherra OS window that represents
the complete neural processing dashboard experience.
"""


import sys
from pathlib import Path

# Add the GUI directory to the Python path
GUI_DIR = Path(__file__).parent
sys.path.insert(0, str(GUI_DIR))

try:
    # Compatibility wrapper: delegate to the new minimal OS monitor GUI
    from aetherra_os_gui import main as main

    if __name__ == "__main__":
        print("🚀 Launching Aetherra OS Monitor GUI (compat launcher)")
        sys.exit(main())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure PySide6 is installed: pip install PySide6")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error launching Aetherra OS: {e}")
    sys.exit(1)

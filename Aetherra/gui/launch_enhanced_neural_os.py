#!/usr/bin/env python3
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
import os
from pathlib import Path

# Add the GUI directory to the Python path
GUI_DIR = Path(__file__).parent
sys.path.insert(0, str(GUI_DIR))

try:
    from aetherra_enhanced_neural_os import main

    if __name__ == "__main__":
        print("🌌 Launching Aetherra OS - Enhanced Neural Processing Dashboard...")
        print("✨ Features enabled:")
        print("   🧠 Pulsating Neural Web Background")
        print("   ⚛️ Animated Quantum Core")
        print("   🗺️ Live Memory Graph with Real-time Updates")
        print("   📜 Consciousness Timeline")
        print("   🔬 Introspective Diagnostics")
        print("   ⚙️ Plugin Aura Viewer")
        print("   🔮 Synthetic Soul Metrics")
        print("   💤 Dream State Mode")
        print("   ⌨️ Command Palette (Ctrl+K)")
        print("   🌊 Quantum Observer Effects")
        print()
        print("🚀 Starting Aetherra OS...")

        # Launch the enhanced neural OS
        sys.exit(main())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure PySide6 is installed: pip install PySide6")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error launching Aetherra OS: {e}")
    sys.exit(1)

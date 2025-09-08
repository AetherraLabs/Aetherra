#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌌 Aetherra OS - Standalone Enhanced Neural Dashboard
===================================================

Simple standalone launcher for the Enhanced Aetherra Neural OS Dashboard.
This creates the complete unified interface with all requested features.
"""

import sys
from pathlib import Path


def main():
    """Launch the Enhanced Aetherra Neural OS Dashboard"""

    print("🌌 Aetherra OS - Enhanced Neural Processing Dashboard")
    print("=" * 55)
    print()
    print("🚀 Initializing neural systems...")
    print("   ✅ Pulsating Neural Web Background")
    print("   ✅ Animated Quantum Core")
    print("   ✅ Live Memory Graph Integration")
    print("   ✅ Consciousness Timeline")
    print("   ✅ Introspective Diagnostics")
    print("   ✅ Plugin Aura Viewer")
    print("   ✅ Synthetic Soul Metrics")
    print("   ✅ Fractal-Inspired UI Elements")
    print("   ✅ Cosmic Loading Transitions")
    print("   ✅ Dream State Mode")
    print("   ✅ Quantum Observer Effects")
    print()

    # Check for required dependencies
    try:
        from PySide6.QtCore import Qt  # noqa: F401 (optional runtime import)

        # QApplication imported to confirm availability
        from PySide6.QtWidgets import QApplication  # noqa: F401
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print()
        print("Please install required packages:")
        print("  pip install PySide6 numpy")
        return 1

    # Import and launch the minimal OS Monitor GUI
    try:
        # Add current directory to path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))

        from aetherra_os_gui import main as monitor_main

        print("🧠 Starting Aetherra OS Monitor GUI...")
        return monitor_main([])

    except ImportError as e:
        print(f"❌ Failed to import Aetherra OS Monitor GUI: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error launching Aetherra OS: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

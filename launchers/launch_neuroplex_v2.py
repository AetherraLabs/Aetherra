#!/usr/bin/env python3
"""
🚀 Neuroplex v2.0 Launcher
==========================

Launch the modern Neuroplex GUI with dark mode and enhanced features.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Launch Neuroplex v2.0"""
    try:
        # Try to launch the new modern GUI
        from ui.neuroplex_gui_v2 import main as launch_neuroplex_v2

        print("🧬 Launching Neuroplex v2.0 - Modern Dark Mode Interface")
        launch_neuroplex_v2()

    except ImportError as e:
        print(f"❌ Could not launch Neuroplex v2.0: {e}")
        print("📋 Please ensure you have either PySide6 or PyQt6 installed:")
        print("   pip install PySide6")
        print("   or")
        print("   pip install PyQt6")

        # Fallback to original GUI if available
        try:
            from ui.neuroplex_gui import main as launch_neuroplex_v1

            print("\n🔄 Falling back to Neuroplex v1.0...")
            launch_neuroplex_v1()
        except ImportError:
            print("❌ No GUI available. Please install Qt dependencies.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error launching Neuroplex: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

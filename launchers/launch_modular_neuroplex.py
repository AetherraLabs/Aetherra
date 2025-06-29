#!/usr/bin/env python3
"""
🚀 Modular Neuroplex Launcher
=============================

Launch the modular version of Neuroplex with separated components.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Launch Modular Neuroplex"""
    try:
        # Try to launch the modular GUI
        from ui.neuroplex_modular import main as launch_modular_neuroplex

        print("🧬 Launching Modular Neuroplex v2.0")
        print("📦 Using separated component architecture")
        launch_modular_neuroplex()

    except ImportError as e:
        print(f"❌ Could not launch Modular Neuroplex: {e}")
        print("📋 Please ensure you have either PySide6 or PyQt6 installed:")
        print("   pip install PySide6")

        # Fallback to original monolithic GUI
        try:
            from ui.neuroplex_gui_v2 import main as launch_neuroplex_v2

            print("\n🔄 Falling back to original Neuroplex v2.0...")
            launch_neuroplex_v2()
        except ImportError:
            print("❌ No GUI available. Please install Qt dependencies.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error launching Modular Neuroplex: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

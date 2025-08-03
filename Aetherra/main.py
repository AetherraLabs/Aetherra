"""
Aetherra Legacy Bootstrapper (DEPRECATED)
==========================================

This file is deprecated. Use the new unified launcher instead:

    python launcher.py        # Launch with GUI
    python launcher.py --cli  # Launch CLI mode

The new launcher provides:
- Unified Aetherra OS Backend (services, memory, plugins, agents)
- Single Lyrixa GUI Frontend (no conflicts, no multiple interfaces)
- Complete system integration and control
"""

import sys
from pathlib import Path

def main():
    print("\n" + "=" * 60)
    print("[WARN]  DEPRECATED BOOTSTRAPPER")
    print("=" * 60)
    print("This file is deprecated. Use the new unified launcher:")
    print()
    print("  python lyrixa/launcher.py        # Launch with GUI")
    print("  python lyrixa/launcher.py --cli  # Launch CLI mode")
    print()
    print("The new launcher provides complete system integration")
    print("with a single unified interface as designed.")
    print("=" * 60)

    # Auto-redirect to new launcher
    choice = input("\nLaunch new unified system? (y/n): ").strip().lower()
    if choice in ['y', 'yes', '']:
        print("🚀 Launching Lyrixa AI Operating System...")
        import subprocess
        subprocess.run([sys.executable, "lyrixa/launcher.py"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🚀 AETHERRA AI OPERATING SYSTEM - MAIN ENTRY POINT
==================================================

Primary entry point for launching the Aetherra AI Operating System.
This script provides a clean interface to start various OS components.

Usage:
    python aetherra_os.py                    # Launch main OS interface
    python aetherra_os.py --interface gui    # Launch GUI interface
    python aetherra_os.py --interface web    # Launch web interface only
    python aetherra_os.py --interface hybrid # Launch hybrid interface (default)
    python aetherra_os.py --help            # Show help

The Aetherra OS provides:
- Hybrid PySide6 + Web dashboard interface
- Real-time AI system monitoring
- Quantum memory visualization
- Agent ecosystem management
- Consciousness state monitoring
"""

import sys
import argparse
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def launch_hybrid_interface():
    """Launch the hybrid PySide6 + Web interface with full OS"""
    print("🚀 Starting Aetherra AI Operating System with Hybrid Interface...")
    print("🖥️ This will:")
    print("   • Start the Aetherra OS kernel and core systems")
    print("   • Launch Lyrixa intelligence engine")
    print("   • Open hybrid desktop + web dashboard")
    print("   • Provide real-time monitoring and control")
    print()

    try:
        from Aetherra.interface.launch_aetherra_os import main as launch_main
        return launch_main()
    except ImportError as e:
        print(f"❌ Failed to import hybrid interface: {e}")
        print("[TOOL] Make sure PySide6 is installed: pip install PySide6")
        return 1


def launch_web_interface():
    """Launch web interface only"""
    try:
        from Aetherra.gui.web_interface_server import main as web_main
        return web_main()
    except ImportError as e:
        print(f"❌ Failed to import web interface: {e}")
        return 1


def launch_gui_interface():
    """Launch GUI interface (alias for hybrid)"""
    return launch_hybrid_interface()


def show_system_info():
    """Show system information and available interfaces"""
    print("🤖 AETHERRA AI OPERATING SYSTEM")
    print("=" * 40)
    print("🖥️ Available Interfaces:")
    print("  • hybrid - PySide6 + Web hybrid interface (recommended)")
    print("  • web    - Web-only interface")
    print("  • gui    - GUI interface (alias for hybrid)")
    print()
    print("🧠 Core Features:")
    print("  • Real-time AI system monitoring")
    print("  • Quantum memory visualization")
    print("  • Agent ecosystem management")
    print("  • Consciousness state tracking")
    print("  • Live cognitive metrics")
    print()
    print("📁 Project Structure:")
    print("  • Aetherra/interface/ - Hybrid interface components")
    print("  • Aetherra/gui/      - Web interface server")
    print("  • Aetherra/lyrixa/   - AI consciousness core")
    print()


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Aetherra AI Operating System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aetherra_os.py                    # Launch hybrid interface
  python aetherra_os.py --interface web    # Web interface only
  python aetherra_os.py --info            # Show system information
        """
    )

    parser.add_argument(
        '--interface', '-i',
        choices=['hybrid', 'web', 'gui'],
        default='hybrid',
        help='Interface type to launch (default: hybrid)'
    )

    parser.add_argument(
        '--info',
        action='store_true',
        help='Show system information and exit'
    )

    args = parser.parse_args()

    if args.info:
        show_system_info()
        return 0

    print("🤖 AETHERRA AI OPERATING SYSTEM")
    print(f"🚀 Launching {args.interface} interface...")
    print("=" * 40)

    if args.interface == 'hybrid':
        return launch_hybrid_interface()
    elif args.interface == 'web':
        return launch_web_interface()
    elif args.interface == 'gui':
        return launch_gui_interface()
    else:
        print(f"❌ Unknown interface type: {args.interface}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: GPL-3.0-or-later
SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

[LAUNCH] AETHERRA AI OPERATING SYSTEM - MAIN ENTRY POINT
==================================================

Licensed under GNU General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

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

import argparse
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def launch_hybrid_interface():
    """Launch the designated Aetherra GUI interface and start OS backend"""
    print("[LAUNCH] Starting Aetherra AI Operating System with Designated GUI...")
    print("[DESKTOP] This will:")
    print("   * Start the Aetherra OS kernel and core systems")
    print("   * Launch the official Aetherra/gui interface")
    print("   * Connect to real-time OS data")
    print("   * Provide neural OS monitoring and control")
    print()

    # First, start the OS backend systems
    try:
        print("[TOOL] Starting Aetherra OS backend services...")
        import asyncio
        import threading

        from aetherra_os_launcher import AetherraOSLauncher

        async def start_os_backend():
            launcher = AetherraOSLauncher()
            await launcher.launch_full_os({"gui_enabled": False})  # Backend only

        def run_os():
            asyncio.run(start_os_backend())

        os_thread = threading.Thread(target=run_os, daemon=True)
        os_thread.start()

        # Give OS time to start
        import time

        time.sleep(3)
        print("[OK] Aetherra OS backend started")

    except Exception as e:
        print(f"[WARN] OS backend start warning: {e}")
        print("Continuing with GUI launch...")

    # Now launch the designated GUI
    try:
        # Add GUI path to system path
        gui_path = PROJECT_ROOT / "Aetherra" / "gui"
        if str(gui_path) not in sys.path:
            sys.path.insert(0, str(gui_path))

        # Import and run the official Aetherra GUI
        from aetherra_enhanced_neural_os import main as gui_main

        return gui_main()
    except ImportError as e:
        print(f"[ERROR] Failed to import official Aetherra GUI: {e}")
        print("📁 Make sure Aetherra/gui/aetherra_enhanced_neural_os.py exists")
        print("[TOOL] Make sure PySide6 is installed: pip install PySide6")
        return 1


def launch_web_interface():
    """Launch web interface only"""
    try:
        from Aetherra.gui.web_interface_server import start_web_interface

        return start_web_interface()
    except ImportError as e:
        print(f"[ERROR] Failed to import web interface: {e}")
        return 1


def launch_gui_interface():
    """Launch GUI interface (alias for hybrid)"""
    return launch_hybrid_interface()


def show_system_info():
    """Show system information and available interfaces"""
    print("[BOT] AETHERRA AI OPERATING SYSTEM")
    print("=" * 40)
    print("[DESKTOP] Available Interfaces:")
    print("  * hybrid - PySide6 + Web hybrid interface (recommended)")
    print("  * web    - Web-only interface")
    print("  * gui    - GUI interface (alias for hybrid)")
    print()
    print("[BRAIN] Core Features:")
    print("  * Real-time AI system monitoring")
    print("  * Quantum memory visualization")
    print("  * Agent ecosystem management")
    print("  * Consciousness state tracking")
    print("  * Live cognitive metrics")
    print()
    print("📁 Project Structure:")
    print("  * Aetherra/GUI/           - Official Aetherra OS GUI interface")
    print("  * Aetherra/aetherra_core/ - Core Aetherra memory & processing engines")
    print("  * Aetherra/gui/          - Web interface server")
    print("  * Aetherra/plugins/      - Plugin ecosystem & management")
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
        """,
    )

    parser.add_argument(
        "--interface",
        "-i",
        choices=["hybrid", "web", "gui"],
        default="hybrid",
        help="Interface type to launch (default: hybrid)",
    )

    parser.add_argument(
        "--info", action="store_true", help="Show system information and exit"
    )

    args = parser.parse_args()

    if args.info:
        show_system_info()
        return 0

    print("[BOT] AETHERRA AI OPERATING SYSTEM")
    print(f"[LAUNCH] Launching {args.interface} interface...")
    print("=" * 40)

    if args.interface == "hybrid":
        return launch_hybrid_interface()
    elif args.interface == "web":
        return launch_web_interface()
    elif args.interface == "gui":
        return launch_gui_interface()
    else:
        print(f"[ERROR] Unknown interface type: {args.interface}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
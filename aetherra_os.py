#!/usr/bin/env python3
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

# Standard library imports
import argparse
import asyncio
import sys
import threading
import time
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _print_presence(interface_name: str) -> None:
    print("[AETHERRA] Aetherra online.")
    print(f"[AETHERRA] Preparing {interface_name} interface and startup diagnostics...")
    print()


def _start_backend_thread(gui_enabled: bool) -> bool:
    try:
        print("[AETHERRA] Starting core systems...")
        from aetherra_os_launcher import AetherraOSLauncher

        async def start_os_backend() -> None:
            launcher = AetherraOSLauncher()
            await launcher.launch_full_os(
                {"gui_enabled": gui_enabled, "interface": "hybrid"}
            )

        def run_os():
            asyncio.run(start_os_backend())

        os_thread = threading.Thread(target=run_os, daemon=True)
        os_thread.start()
        time.sleep(3)
        print("[AETHERRA] Core systems initialized. Continuing to interface handoff.")
        return True
    except Exception as e:
        print(f"[WARN] Backend start warning: {e}")
        print("[AETHERRA] Continuing with interface launch path.")
        return False


def launch_hybrid_interface():
    """Launch the designated Aetherra GUI interface and start OS backend"""
    _print_presence("hybrid")
    print(
        "[LAUNCH] Starting Aetherra AI Operating System with transitional monitor GUI..."
    )
    print("[DESKTOP] This will:")
    print("   * Start the Aetherra OS kernel and core systems")
    print("   * Launch the supported Aetherra monitor GUI")
    print("   * Connect to real-time OS data")
    print("   * Provide startup diagnostics and control visibility")
    print()

    _start_backend_thread(gui_enabled=False)

    try:
        gui_path = PROJECT_ROOT / "Aetherra" / "gui"
        if str(gui_path) not in sys.path:
            sys.path.insert(0, str(gui_path))

        from Aetherra.gui.aetherra_os_gui import main as gui_main

        print("[AETHERRA] Handing over to the Aetherra monitor GUI.")
        return gui_main([])
    except ImportError as e:
        print(f"[ERROR] Failed to import supported Aetherra GUI: {e}")
        print("[TOOL] Make sure PySide6 is installed: pip install PySide6")
        return 1


def launch_web_interface():
    """Launch web interface only"""
    try:
        _print_presence("web")
        _start_backend_thread(gui_enabled=False)

        import uvicorn

        from aetherra_os_web.server import app

        print("[AETHERRA] Launching web interface at http://localhost:8888")
        uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info", reload=False)
        return 0
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
    print("  * hybrid - Backend startup + transitional monitor GUI (recommended)")
    print("  * web    - FastAPI web interface")
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
    print("  * frontend/              - Canonical Aetherra frontend target")
    print("  * Aetherra/aetherra_core/ - Core Aetherra memory & processing engines")
    print("  * Aetherra/gui/          - Transitional native monitor GUI")
    print("  * aetherra_os_web/       - FastAPI web interface")
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
    if args.interface == "web":
        return launch_web_interface()
    if args.interface == "gui":
        return launch_gui_interface()
    print(f"[ERROR] Unknown interface type: {args.interface}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

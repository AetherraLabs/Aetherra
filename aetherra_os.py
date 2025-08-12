#!/usr/bin/env python3
"""
🚀 AETHERRA AI OPERATING SYSTEM - MAIN ENTRY POINT
==================================================

Copyright (C) 2025 AetherraLabs
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
    python aetherra_os.py                      # Backend-only smoke boot (default)
    python aetherra_os.py --interface backend  # Backend-only smoke boot
    python aetherra_os.py --help               # Show help

Notes:
- GUI launch is no longer handled by this file.
- Use Lyrixa or aetherra_os_launcher.py for GUI experiences.
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _deprecated_gui_entry(which: str) -> int:
    print("❌ GUI launching was removed from aetherra_os.py")
    print(f"Requested interface: {which}")
    print("➡️ Use one of the following instead:")
    print("   • Lyrixa launcher: Aetherra/lyrixa/launcher.py")
    print("   • OS launcher with GUI: aetherra_os_launcher.py (if applicable)")
    return 2


def launch_web_interface():
    return _deprecated_gui_entry("web")


def launch_gui_interface():
    return _deprecated_gui_entry("gui")


def launch_backend_only(duration_seconds: int = 3):
    """Launch only the OS backend for a short smoke boot and exit.

    Args:
        duration_seconds: How long to keep the backend running before shutdown.
    """
    import asyncio

    from aetherra_os_launcher import AetherraOSLauncher

    async def run_backend():
        launcher = AetherraOSLauncher()
        # Start in the background and let it settle
        asyncio.create_task(
            launcher.launch_full_os({"gui_enabled": False, "quiet": True})
        )
        try:
            await asyncio.sleep(max(1, duration_seconds))
        finally:
            # Request shutdown cleanly
            launcher.running = False
            try:
                await launcher._graceful_shutdown()
            except Exception:
                pass
        return 0

    return asyncio.run(run_backend())


def show_system_info():
    """Show system information and available interfaces"""
    print("🤖 AETHERRA AI OPERATING SYSTEM")
    print("=" * 40)
    print("🖥️ Available Interfaces:")
    print("  • backend - Backend-only smoke boot (no GUI)")
    print()
    print("🧠 Core Features:")
    print("  • Real-time AI system monitoring")
    print("  • Quantum memory visualization")
    print("  • Agent ecosystem management")
    print("  • Consciousness state tracking")
    print("  • Live cognitive metrics")
    print()
    print("📁 Project Structure:")
    print("  • Aetherra/lyrixa/       - Lyrixa GUI launcher and UI")
    print("  • Aetherra/aetherra_core/- Core Aetherra memory & processing engines")
    print("  • Aetherra/plugins/      - Plugin ecosystem & management")
    print()


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Aetherra AI Operating System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aetherra_os.py                    # Backend-only smoke boot
  python aetherra_os.py --interface backend# Backend-only smoke boot
  python aetherra_os.py --info             # Show system information
    """,
    )

    parser.add_argument(
        "--interface",
        "-i",
        choices=["backend", "hybrid", "web", "gui"],
        default="backend",
        help="Interface type to launch (default: backend)",
    )

    parser.add_argument(
        "--info", action="store_true", help="Show system information and exit"
    )

    args = parser.parse_args()

    if args.info:
        show_system_info()
        return 0

    print("🤖 AETHERRA AI OPERATING SYSTEM")
    print(f"🚀 Launching {args.interface} interface...")
    print("=" * 40)

    if args.interface == "backend":
        # Short backend-only smoke boot
        return launch_backend_only()
    elif args.interface in ("hybrid", "web", "gui"):
        # Deprecated here
        return _deprecated_gui_entry(args.interface)
    else:
        print(f"❌ Unknown interface type: {args.interface}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌌 Quantum Dashboard Launcher
============================

Launch the quantum memory monitoring web dashboard as part of the Aetherra ecosystem.
This script integrates with existing Aetherra components and provides a unified
interface for monitoring quantum-enhanced memory operations.

Usage:
    python quantum_dashboard_launcher.py [--port 8080] [--mode web]
"""

# Standard library imports
import argparse
import asyncio
import sys
from pathlib import Path

# Add Aetherra to path
aetherra_path = Path(__file__).parent / "Aetherra"
sys.path.insert(0, str(aetherra_path))

# Quantum UI components removed; provide feature flags and stubs
QUANTUM_AVAILABLE = False
WEB_AVAILABLE = False
QFAC_AVAILABLE = False


async def launch_quantum_dashboard(port: int = 8080, mode: str = "web"):
    """Launch the quantum dashboard in specified mode"""

    print("🌌 Aetherra Quantum Dashboard Launcher")
    print("=" * 50)

    if mode == "web" and not WEB_AVAILABLE:
        print("❌ Web mode not available - missing aiohttp dependency")
        print("💡 Install with: pip install aiohttp")
        mode = "text"

    if mode == "web":
        print("🚀 Starting Quantum Web Dashboard...")
        print("⚠️ Web UI has been disabled in this build.")
        print("� To enable, add a web dashboard implementation and set WEB_AVAILABLE=True.")
        return False

    elif mode == "integrated" and QFAC_AVAILABLE:
        print("🎯 Starting Integrated QFAC Dashboard with Quantum Support...")
        print("⚠️ QFAC components are not present in this build.")
        return False

    else:
        print("📟 Text mode dashboard not implemented in this launcher")
        print("💡 Use the full QFAC dashboard for text mode")
        return False

    return True


def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="Launch Aetherra Quantum Memory Dashboard"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for web dashboard (default: 8080)"
    )
    parser.add_argument(
        "--mode",
        choices=["web", "integrated", "text"],
        default="web",
        help="Dashboard mode (default: web)",
    )
    parser.add_argument(
        "--test-data",
        action="store_true",
        help="Add additional test data for demonstration",
    )

    args = parser.parse_args()

    # Check dependencies
    missing_deps = []
    if args.mode == "web" and not WEB_AVAILABLE:
        missing_deps.append("aiohttp (for web interface)")
    if not QUANTUM_AVAILABLE:
        missing_deps.append("quantum components")

    if missing_deps:
        print("⚠️ Missing dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n💡 Dashboard will run in compatibility mode")

    # Run dashboard
    try:
        success = asyncio.run(launch_quantum_dashboard(args.port, args.mode))
        if success:
            print("🎉 Dashboard session completed successfully")
        else:
            print("❌ Dashboard failed to start")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard launcher interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

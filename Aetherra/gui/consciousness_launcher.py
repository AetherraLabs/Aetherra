#!/usr/bin/env python3
"""
🚀 Quick Consciousness Dashboard Launcher
========================================

Simple launcher that bypasses Lyrixa components and goes directly to consciousness dashboards.
"""

import argparse
import sys


def main():
    """Quick launcher for consciousness dashboards."""
    parser = argparse.ArgumentParser(
        description="Aetherra Consciousness Dashboard Launcher"
    )
    parser.add_argument(
        "--consciousness", action="store_true", help="Launch Qt Consciousness Dashboard"
    )
    parser.add_argument(
        "--web", action="store_true", help="Launch Web Consciousness Dashboard"
    )
    args = parser.parse_args()

    if args.consciousness:
        print("🧠 Launching Qt Consciousness Evolution Dashboard...")
        try:
            from consciousness_evolution_dashboard import main as consciousness_main

            return consciousness_main()
        except ImportError as e:
            print(f"❌ Qt dashboard not available: {e}")
            return 1

    elif args.web:
        print("🌐 Launching Web Consciousness Dashboard...")
        try:
            from consciousness_web_viewer import main as web_main

            return web_main()
        except ImportError as e:
            print(f"❌ Web dashboard not available: {e}")
            return 1

    else:
        print("🎯 AETHERRA CONSCIOUSNESS DASHBOARD LAUNCHER")
        print("=" * 50)
        print("Available options:")
        print("  --consciousness    Launch Qt-based consciousness dashboard")
        print("  --web             Launch web-based consciousness dashboard")
        print("")
        print("Examples:")
        print("  python consciousness_launcher.py --consciousness")
        print("  python consciousness_launcher.py --web")
        return 0


if __name__ == "__main__":
    sys.exit(main())

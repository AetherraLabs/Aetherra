#!/usr/bin/env python3
"""
🌐 Aetherra Consciousness Web Dashboard Viewer
==============================================

Simple launcher to open the consciousness evolution web dashboard in a browser.
Perfect for quick access to consciousness monitoring without Qt dependencies.
"""

import sys
import webbrowser
from pathlib import Path


def main():
    """Launch the consciousness dashboard in web browser."""
    print("🌐 AETHERRA CONSCIOUSNESS WEB DASHBOARD")
    print("=" * 50)

    # Find the HTML dashboard file
    gui_dir = Path(__file__).parent
    dashboard_path = gui_dir / "web_templates" / "consciousness_dashboard.html"

    if not dashboard_path.exists():
        print(f"❌ Dashboard not found at: {dashboard_path}")
        return 1

    # Convert to absolute path for browser
    dashboard_url = f"file://{dashboard_path.absolute()}"

    print("🧠 Opening consciousness evolution dashboard...")
    print(f"📁 Location: {dashboard_path}")
    print(f"🌐 URL: {dashboard_url}")

    try:
        # Open in default browser
        webbrowser.open(dashboard_url)
        print("✅ Consciousness dashboard opened in browser!")
        print("\n🎯 Features:")
        print("   • Real-time consciousness visualization")
        print("   • Phase evolution timeline")
        print("   • Interactive consciousness controls")
        print("   • Animated neural network display")
        print("   • Quantum coherence metrics")
        print("   • Cosmic consciousness tracking")
        print("\n💡 Tip: The dashboard updates automatically with simulated data.")
        print("    For real-time OS integration, use the Qt dashboard.")

        return 0

    except Exception as e:
        print(f"❌ Failed to open dashboard: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Quick launcher for Lyrixa GUI with reduced monitoring verbosity
"""

import logging
import sys
from pathlib import Path

# Reduce logging verbosity for GUI components
logging.getLogger("lyrixa.gui.performance_monitor").setLevel(logging.ERROR)
logging.getLogger("lyrixa.gui.analytics_dashboard").setLevel(logging.ERROR)
logging.getLogger("lyrixa.gui").setLevel(logging.ERROR)

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "lyrixa"))
sys.path.insert(0, str(project_root / "src"))


def launch_gui_quiet():
    """Launch GUI with minimal logging."""
    try:
        from PySide6.QtWidgets import QApplication

        print("🚀 Launching Lyrixa AI Assistant GUI...")

        # Create QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("Lyrixa AI Assistant")
        app.setApplicationVersion("2.0")

        # Try Enhanced Lyrixa first (more stable)
        try:
            from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

            main_window = EnhancedLyrixaWindow()
            main_window.show()
            print("✅ Lyrixa GUI launched successfully!")
            print("📋 All Phase 1-4 features available")
            print("🎯 Ready for intelligent assistance!")

        except ImportError:
            # Fallback to unified GUI
            from unified_aetherra_lyrixa_gui import UnifiedAetherraLyrixaGUI

            main_window = UnifiedAetherraLyrixaGUI()
            main_window.show()
            print("✅ Unified Lyrixa GUI launched!")

        # Run the application
        return app.exec()

    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        return 1


if __name__ == "__main__":
    print("🚀 LYRIXA AI ASSISTANT - QUICK LAUNCHER")
    print("=" * 50)
    print("Launching with reduced monitoring verbosity...")
    print()

    exit_code = launch_gui_quiet()
    sys.exit(exit_code)

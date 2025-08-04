#!/usr/bin/env python3
"""
🌌 Aetherra OS Enhanced Launcher
================================

Launch the enhanced Aetherra OS GUI with real-time engine integration.

Features:
- Real-time Aetherra Engine monitoring and interaction
- Enhanced Aetherra Labs branding
- Live conversation interface with AI
- Quantum consciousness visualization
- Plugin ecosystem monitoring
- System health dashboards

Usage:
    python launch_enhanced_aetherra_os.py

Keyboard Shortcuts:
    F1 - About Aetherra Labs
    Ctrl+E - Focus Engine Monitor
    Ctrl+K - System Command Palette
    Ctrl+D - Field Diagnostics
    Ctrl+Q - Quantum Pulse
"""

import sys
import os
import asyncio
from pathlib import Path

# Ensure we can import from the right paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Aetherra"))

def main():
    """Launch the enhanced Aetherra OS"""
    print("🌌 Launching Aetherra OS Enhanced...")
    print("🏢 Aetherra Labs - Advancing AI Consciousness")
    print("=" * 60)

    try:
        # Import Qt application framework
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon

        # Import the enhanced Aetherra OS
        from gui.aetherra_enhanced_neural_os import AetherraOS

        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Aetherra OS Enhanced")
        app.setApplicationVersion("2.1")
        app.setOrganizationName("Aetherra Labs")
        app.setOrganizationDomain("aetherra.ai")

        # Set application properties
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

        print("✅ Qt Application initialized")

        # Create and show the main window
        main_window = AetherraOS()
        main_window.show()

        print("✅ Aetherra OS Enhanced launched successfully")
        print("🔗 Engine integration: Active")
        print("💬 Conversation interface: Ready")
        print("📊 Real-time monitoring: Enabled")
        print("=" * 60)
        print("🚀 Welcome to the future of AI consciousness!")

        # Run the application
        sys.exit(app.exec())

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure PySide6 is installed: pip install PySide6")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Failed to launch Aetherra OS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

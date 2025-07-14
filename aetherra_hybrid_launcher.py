#!/usr/bin/env python3
"""
Lyrixa Hybrid UI Launcher Demo
==============================

This script demonstrates how to launch Lyrixa with the hybrid UI.
It's designed as a drop-in replacement for the existing launcher
with minimal changes required.

Usage:
    python aetherra_hybrid_launcher.py

Environment Variables:
    LYRIXA_UI_MODE=hybrid    # Enable hybrid UI
    LYRIXA_UI_MODE=classic   # Use original UI (default)
"""

import asyncio
import os
import sys
from pathlib import Path

# Set environment for hybrid UI
os.environ["LYRIXA_UI_MODE"] = "hybrid"

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the existing launcher but with hybrid UI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(project_root / "Aetherra" / "lyrixa" / "gui" / "ui_config.env")

# Import and modify the launcher
try:
    # Import from the original launcher
    from PySide6.QtWidgets import QApplication

    from Aetherra.lyrixa.gui.window_factory import create_lyrixa_window
    from Aetherra.lyrixa.launcher import initialize_system

    def main():
        """Main function for hybrid UI launcher"""
        print("🌟 Lyrixa Hybrid UI Launcher Starting...")
        print(f"UI Mode: {os.getenv('LYRIXA_UI_MODE', 'classic')}")

        # Create Qt application
        app = QApplication(sys.argv)

        # Create window using factory (will auto-select hybrid mode)
        window = create_lyrixa_window()

        # Show window first for immediate feedback
        window.show()

        try:
            # Create event loop for async initialization
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run initialization with GUI window reference
            loop.run_until_complete(initialize_system(window))

            # Import the global variables from launcher
            from Aetherra.lyrixa.launcher import intelligence_stack, lyrixa, runtime

            print("🔗 Attaching components to GUI...")

            # Attach components to GUI using modular methods
            print(f"🔧 DEBUG: intelligence_stack = {intelligence_stack}")
            print(f"🔧 DEBUG: runtime = {runtime}")
            print(f"🔧 DEBUG: lyrixa = {lyrixa}")

            if intelligence_stack:
                window.attach_intelligence_stack(intelligence_stack)
                print("✅ Intelligence stack attached to GUI")

            if runtime:
                window.attach_runtime(runtime)
                print("✅ Runtime attached to GUI")

            if lyrixa:
                print(f"🔧 DEBUG: About to call attach_lyrixa with {type(lyrixa)}")
                window.attach_lyrixa(lyrixa)
                # Set GUI interface reference
                lyrixa.gui_interface = window
                print("✅ Lyrixa agent attached to GUI with auto-population enabled")
            else:
                print("❌ DEBUG: lyrixa is None or undefined!")

            print("✅ Hybrid UI initialized successfully!")
            print("🎉 Lyrixa is ready with modern hybrid interface!")

        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            import traceback

            traceback.print_exc()

        # Start Qt event loop
        return app.exec()

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure PySide6 is installed: py -m pip install PySide6")
    print("💡 Or run: python aetherra_launcher.py (for classic UI)")
    sys.exit(1)

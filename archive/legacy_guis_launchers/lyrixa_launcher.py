#!/usr/bin/env python3
"""
🎙️ LYRIXA AI ASSISTANT LAUNCHER
===============================

Main launcher for the Lyrixa AI Assistant.
This is the primary entry point that delegates to the modularized system.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Import from the modularized lyrixa package
    import asyncio

    from lyrixa.launcher import main as lyrixa_main

    if __name__ == "__main__":
        print("🎙️ Launching Lyrixa AI Assistant for Aetherra...")
        asyncio.run(lyrixa_main())

except ImportError as e:
    print(f"❌ Failed to import modularized Lyrixa: {e}")
    print("The Lyrixa system may need to be rebuilt.")
    print("Please check the lyrixa/ directory structure.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error launching Lyrixa: {e}")
    sys.exit(1)

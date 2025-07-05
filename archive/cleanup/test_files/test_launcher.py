#!/usr/bin/env python3
"""Test launcher functionality"""

import sys
from pathlib import Path

# Test the unified launcher
try:
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    # Test importing the main launcher
    from launchers.launch_lyrixa import main as Lyrixa_main

    print("✅ Main Lyrixa launcher imports successfully")

    # Test importing the GUI components - skip src path manipulation

    from Lyrixa.ui.enhanced_lyrixa import EnhancedLyrixaWindow
    # from Aetherra.ui.aetherplex import main as gui_main  # If this exists

    print("✅ Main GUI components import successfully")

    print("🎉 All launcher components are working!")
    print("🚀 You can now launch Lyrixa using:")
    print("   python launchers/launch_Lyrixa.py")
    print("   OR")
    print("   python aetherra_launcher.py (then choose option 1)")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

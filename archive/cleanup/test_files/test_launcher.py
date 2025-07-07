#!/usr/bin/env python3
"""Test launcher functionality"""

import sys
from pathlib import Path

# Test the unified launcher
try:
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    # Test importing the main launcher
    from launchers.launch_Aetherra import main as Aetherra_main

    print("✅ Main Aetherra launcher imports successfully")

    # Test importing the GUI components
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))

    from aetherra.ui.aetherplex import AetherraWindow
    from aetherra.ui.aetherplex import main as gui_main

    print("✅ Main GUI components import successfully")

    print("🎉 All launcher components are working!")
    print("🚀 You can now launch Aetherra using:")
    print("   python launchers/launch_Aetherra.py")
    print("   OR")
    print("   python aetherra_launcher.py (then choose option 1)")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

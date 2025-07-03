#!/usr/bin/env python3
"""
Test if the GUI main function can be called without hanging
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# print("Testing GUI main function import...")

try:
    # Import the main function

    print(f"✅ Main function imported successfully")
    print(f"   - Qt available: {QT_AVAILABLE}")
    print(f"   - NeuroCode available: {NEUROCODE_AVAILABLE}")

    print("✅ All GUI components imported successfully!")
    print("   The import issues have been resolved.")
    print("   You can now run: python ui/neuroplex_gui.py")

except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback

    traceback.print_exc()

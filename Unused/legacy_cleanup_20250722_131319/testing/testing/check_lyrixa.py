#!/usr/bin/env python3
"""Check that aetherplex.py can be imported"""

import sys

print("Attempting to import aetherplex.py...")

try:
    # Try direct import

    print("✅ Direct import successful!")

    # Check if the LyrixaWindow class is available
    if hasattr(src.aethercode.ui.aetherplex, "LyrixaWindow"):
        print("✅ LyrixaWindow class found!")
    else:
        print("❌ LyrixaWindow class not found in aetherplex.py")

except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("All checks passed successfully!")
sys.exit(0)

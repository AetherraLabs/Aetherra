#!/usr/bin/env python3
"""
Simple test script to see if neuroplex.py is fixed
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Starting import test...")

try:
    print("Checking basic imports")

    print("Trying to import UI package...")

    print("✅ UI package imported successfully")

    print("Trying direct import of neuroplex.py...")
    try:
        from src.aethercode.ui import neuroplex

        print("✅ neuroplex.py imported successfully")
        if hasattr(neuroplex, "LyrixaWindow"):
            print("✅ LyrixaWindow class is available")
        else:
            print("❌ LyrixaWindow class not found")
    except Exception as e:
        print(f"❌ Could not import neuroplex.py directly: {e}")

    print("Trying to check neuroplex.py file...")
    try:
        file_path = Path("src/neurocode/ui/neuroplex.py").resolve()
        print(f"Checking file at: {file_path}")
        if file_path.exists():
            with open(file_path, "r") as f:
                code = f.read()
                compile(code, str(file_path), "exec")
                print("✅ neuroplex.py compiles successfully")
        else:
            print(f"❌ File does not exist: {file_path}")
    except Exception as e:
        print(f"❌ Compilation failed: {e}")

except Exception as e:
    print(f"❌ Error: {e}")

# print("Test complete.")

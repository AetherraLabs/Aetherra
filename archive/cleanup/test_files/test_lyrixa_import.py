#!/usr/bin/env python3
"""
Simple test script to see if Aetherra.py is fixed
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Starting import test...")

try:
    print("Checking basic imports")
    from importlib import util

    print("Trying to import UI package...")
    import src.aethercode.ui

    print("✅ UI package imported successfully")

    print("Trying direct import of Aetherra.py...")
    try:
        from src.aethercode.ui import Aetherra

        print("✅ Aetherra.py imported successfully")
        if hasattr(Aetherra, "AetherraWindow"):
            print("✅ AetherraWindow class is available")
        else:
            print("❌ AetherraWindow class not found")
    except Exception as e:
        print(f"❌ Could not import Aetherra.py directly: {e}")

    print("Trying to check Aetherra.py file...")
    try:
        file_path = Path("src/aetherra/ui/Aetherra.py").resolve()
        print(f"Checking file at: {file_path}")
        if file_path.exists():
            with open(file_path, "r") as f:
                code = f.read()
                compile(code, str(file_path), "exec")
                print("✅ Aetherra.py compiles successfully")
        else:
            print(f"❌ File does not exist: {file_path}")
    except Exception as e:
        print(f"❌ Compilation failed: {e}")

except Exception as e:
    print(f"❌ Error: {e}")

print("Test complete.")

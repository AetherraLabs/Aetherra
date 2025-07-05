#!/usr/bin/env python3
"""
Simple test script to see if Lyrixa.py is fixed
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

    print("Trying to import Lyrixa package...")
    import Lyrixa

    print("✅ Lyrixa package imported successfully")

    print("Trying to import models...")
    try:
        from Lyrixa.models.local_model import LocalModel

        print("✅ LocalModel imported successfully")

        # Test basic functionality
        model = LocalModel()
        print(f"✅ LocalModel instance created: {type(model)}")

    except Exception as e:
        print(f"❌ LocalModel error: {e}")

except Exception as e:
    print(f"❌ Error: {e}")

print("Test complete.")

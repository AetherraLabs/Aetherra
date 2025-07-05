#!/usr/bin/env python3
"""Test Lyrixa imports"""

import os
import sys

# Add current directory to path so we can import local packages
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import Lyrixa

    print("✅ Lyrixa package imported successfully")
    print(f"   Version: {Lyrixa.__version__}")

    # Test main components
    try:
        from Lyrixa import LyrixaAI

        print("✅ LyrixaAI imported")
    except Exception as e:
        print(f"❌ LyrixaAI import failed: {e}")

    try:
        from Lyrixa import ModelRouter

        print("✅ ModelRouter imported")
    except Exception as e:
        print(f"❌ ModelRouter import failed: {e}")

    try:
        from Lyrixa import LocalModel

        print("✅ LocalModel imported")
    except Exception as e:
        print(f"❌ LocalModel import failed: {e}")

except Exception as e:
    print(f"❌ Lyrixa package import failed: {e}")

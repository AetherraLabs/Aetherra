#!/usr/bin/env python3
"""Basic test to check if Aetherra.py compiles"""

import sys
from pathlib import Path

file_path = Path("src/aetherra/ui/Aetherra.py").resolve()
print(f"Testing file: {file_path}")

try:
    # Just check if it compiles
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
        compile(code, str(file_path), "exec")
    print("✅ SUCCESS: Aetherra.py compiles without syntax errors")
    sys.exit(0)
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

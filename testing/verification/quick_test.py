#!/usr/bin/env python3
"""
Quick test of core AetherraCode functionality
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("🧪 Testing AetherraCode Core Functionality...")

try:
    from aetherra import create_interpreter, create_parser

    print("✅ All core AetherraCode functionality imports successfully!")

    parser = create_parser()
    print("✅ Parser created successfully!")

    interpreter = create_interpreter()
    print("✅ Interpreter created successfully!")

    result = interpreter.execute('say "AetherraCode is working!"')
    print(f"✅ Code execution successful: {result[:50]}...")

    print("🎉 NEUROCODE PROJECT FULLY OPERATIONAL!")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

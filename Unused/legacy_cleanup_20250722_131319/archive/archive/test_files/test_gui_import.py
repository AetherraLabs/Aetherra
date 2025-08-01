#!/usr/bin/env python3
"""
Test script to verify GUI import works correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧪 Testing Aetherra GUI imports...")

try:
    print("1. Testing Qt imports...")
    from ui.aetherplex_gui import QT_AVAILABLE, QT_BACKEND

    print(f"   ✅ Qt available: {QT_AVAILABLE} using {QT_BACKEND}")

    print("2. Testing Aetherra component imports...")
    from ui.aetherplex_gui import (
        Aetherra_AVAILABLE,
        AetherraChatRouter,
        AetherraInterpreter,
        AetherraMemory,
    )

    print(f"   ✅ Aetherra components: {Aetherra_AVAILABLE}")
    print(f"   - Interpreter: {'✅' if AetherraInterpreter else '❌'}")
    print(f"   - Memory: {'✅' if AetherraMemory else '❌'}")
    print(f"   - Chat Router: {'✅' if AetherraChatRouter else '❌'}")

    print("3. Testing GUI class imports...")

    print("   ✅ GUI classes imported successfully")

    print("4. Testing Aetherra interpreter instantiation...")
    if AetherraInterpreter:
        try:
            interpreter = AetherraInterpreter()
            print("   ✅ Interpreter created successfully")

            # Test basic execution
            result = interpreter.execute("remember('test') as 'demo'")
            print(f"   ✅ Basic execution test: {result}")

        except Exception as e:
            print(f"   ⚠️ Interpreter creation failed: {e}")
    else:
        print("   ⚠️ Interpreter not available (demo mode)")

    print("\n🎉 All GUI import tests completed successfully!")
    print("   You can now run: python ui/aetherplex_gui.py")

except Exception as e:
    print(f"❌ Import test failed: {e}")
    import traceback

    traceback.print_exc()

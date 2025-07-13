#!/usr/bin/env python3
"""
Test script to verify Aetherra core modules are working correctly
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

print("🧬 Testing Aetherra Core Module Imports")
print("=" * 50)

# Test direct imports
success_count = 0
total_tests = 3

try:
    from Aetherra.core.aetherra_memory import AetherraMemory

    memory = AetherraMemory()
    memory.remember("Test memory", ["test"])
    memories = memory.recall(["test"])
    print("✅ AetherraMemory: Import and basic functionality working")
    success_count += 1
except Exception as e:
    print(f"❌ AetherraMemory: {e}")

try:
    from Aetherra.core.interpreter import AetherraInterpreter

    interpreter = AetherraInterpreter()
    result = interpreter.execute('remember("Hello Aetherra") as "greeting"')
    print("✅ AetherraInterpreter: Import and basic functionality working")
    success_count += 1
except Exception as e:
    print(f"❌ AetherraInterpreter: {e}")

try:
    from Aetherra.core.chat_router import AetherraChatRouter

    chat_router = AetherraChatRouter()
    response = chat_router.process_message("Hello")
    print("✅ AetherraChatRouter: Import and basic functionality working")
    success_count += 1
except Exception as e:
    print(f"❌ AetherraChatRouter: {e}")

print()
print(f"📊 Results: {success_count}/{total_tests} core modules working correctly")

if success_count == total_tests:
    print("🎉 All core modules working perfectly!")
    print("The import issues have been resolved.")
else:
    print("⚠️ Some modules still have issues, but progress made.")

print("\n🎨 Testing GUI Import System")
print("-" * 30)

try:
    # Test the GUI's import system
    import ui.aetherplex_gui as gui_module

    print("✅ GUI module imports successfully")

    if hasattr(gui_module, "AetherraInterpreter") and gui_module.aetherCodeInterpreter:
        print("✅ GUI has access to AetherraInterpreter")
    else:
        print("⚠️ GUI does not have AetherraInterpreter")

    if hasattr(gui_module, "AetherraMemory") and gui_module.aetherMemory:
        print("✅ GUI has access to AetherraMemory")
    else:
        print("⚠️ GUI does not have AetherraMemory")

    if hasattr(gui_module, "AetherraChatRouter") and gui_module.aetherCodeChatRouter:
        print("✅ GUI has access to AetherraChatRouter")
    else:
        print("⚠️ GUI does not have AetherraChatRouter")

    if hasattr(gui_module, "Aetherra_AVAILABLE") and gui_module.aetherCODE_AVAILABLE:
        print("🎉 GUI reports: All Aetherra components available!")
    else:
        print("⚠️ GUI reports: Some Aetherra components not available")

except Exception as e:
    print(f"❌ GUI import test failed: {e}")

print("\n" + "=" * 50)
print("✅ Import fix verification complete!")

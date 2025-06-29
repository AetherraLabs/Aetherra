#!/usr/bin/env python3
"""
Test script to verify NeuroCode core modules are working correctly
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

print("🧬 Testing NeuroCode Core Module Imports")
print("=" * 50)

# Test direct imports
success_count = 0
total_tests = 3

try:
    from core.memory import NeuroMemory
    memory = NeuroMemory()
    memory.remember("Test memory", ["test"])
    memories = memory.recall(["test"])
    print("✅ NeuroMemory: Import and basic functionality working")
    success_count += 1
except Exception as e:
    print(f"❌ NeuroMemory: {e}")

try:
    from core.interpreter import NeuroCodeInterpreter
    interpreter = NeuroCodeInterpreter()
    result = interpreter.execute('remember("Hello NeuroCode") as "greeting"')
    print("✅ NeuroCodeInterpreter: Import and basic functionality working")
    success_count += 1
except Exception as e:
    print(f"❌ NeuroCodeInterpreter: {e}")

try:
    from core.chat_router import NeuroCodeChatRouter
    chat_router = NeuroCodeChatRouter()
    response = chat_router.process_message("Hello")
    print("✅ NeuroCodeChatRouter: Import and basic functionality working")
    success_count += 1
except Exception as e:
    print(f"❌ NeuroCodeChatRouter: {e}")

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
    import ui.neuroplex_gui as gui_module
    print("✅ GUI module imports successfully")
    
    if hasattr(gui_module, 'NeuroCodeInterpreter') and gui_module.NeuroCodeInterpreter:
        print("✅ GUI has access to NeuroCodeInterpreter")
    else:
        print("⚠️ GUI does not have NeuroCodeInterpreter")
        
    if hasattr(gui_module, 'NeuroMemory') and gui_module.NeuroMemory:
        print("✅ GUI has access to NeuroMemory")
    else:
        print("⚠️ GUI does not have NeuroMemory")
        
    if hasattr(gui_module, 'NeuroCodeChatRouter') and gui_module.NeuroCodeChatRouter:
        print("✅ GUI has access to NeuroCodeChatRouter")
    else:
        print("⚠️ GUI does not have NeuroCodeChatRouter")
        
    if hasattr(gui_module, 'NEUROCODE_AVAILABLE') and gui_module.NEUROCODE_AVAILABLE:
        print("🎉 GUI reports: All NeuroCode components available!")
    else:
        print("⚠️ GUI reports: Some NeuroCode components not available")
        
except Exception as e:
    print(f"❌ GUI import test failed: {e}")

print("\n" + "=" * 50)
print("✅ Import fix verification complete!")

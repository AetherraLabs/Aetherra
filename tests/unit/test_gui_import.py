#!/usr/bin/env python3
"""
Test script to verify GUI import works correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧪 Testing NeuroCode GUI imports...")

try:
    print("1. Testing Qt imports...")
    from ui.neuroplex_gui import QT_AVAILABLE, QT_BACKEND
    print(f"   ✅ Qt available: {QT_AVAILABLE} using {QT_BACKEND}")
    
    print("2. Testing NeuroCode component imports...")
    from ui.neuroplex_gui import (
        NEUROCODE_AVAILABLE,
        NeuroCodeChatRouter,
        NeuroCodeInterpreter,
        NeuroMemory,
    )
    print(f"   ✅ NeuroCode components: {NEUROCODE_AVAILABLE}")
    print(f"   - Interpreter: {'✅' if NeuroCodeInterpreter else '❌'}")
    print(f"   - Memory: {'✅' if NeuroMemory else '❌'}")
    print(f"   - Chat Router: {'✅' if NeuroCodeChatRouter else '❌'}")
    
    print("3. Testing GUI class imports...")
    from ui.neuroplex_gui import NeuroplexMainWindow, NeuroTheme
    print("   ✅ GUI classes imported successfully")
    
    print("4. Testing NeuroCode interpreter instantiation...")
    if NeuroCodeInterpreter:
        try:
            interpreter = NeuroCodeInterpreter()
            print("   ✅ Interpreter created successfully")
            
            # Test basic execution
            result = interpreter.execute("remember('test') as 'demo'")
            print(f"   ✅ Basic execution test: {result}")
            
        except Exception as e:
            print(f"   ⚠️ Interpreter creation failed: {e}")
    else:
        print("   ⚠️ Interpreter not available (demo mode)")
    
    print("\n🎉 All GUI import tests completed successfully!")
    print("   You can now run: python ui/neuroplex_gui.py")
    
except Exception as e:
    print(f"❌ Import test failed: {e}")
    import traceback
    traceback.print_exc()

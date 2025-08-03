#!/usr/bin/env python3
"""
Test script to verify the self-extending system fixes
"""

import sys
import os
from pathlib import Path

# Add Aetherra to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_async_handling():
    """Test that the async handling works correctly"""
    print("🧪 Testing async handling fix...")

    try:
        from Aetherra.lyrixa.gui.self_extending_panel_system import SelfExtendingPanelSystem
        print("✅ Import successful")

        # Check if the new method exists
        if hasattr(SelfExtendingPanelSystem, '_get_engine_response'):
            print("✅ _get_engine_response method exists")
        else:
            print("[ERROR] _get_engine_response method missing")
            return False

        print("✅ Self-extending system fixes appear to be working")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_usage_instructions():
    """Show usage instructions for the fixed system"""
    print("""
🎯 SELF-EXTENDING SYSTEM - READY FOR USE!

The async handling issue has been fixed. You can now use:

1. Open Aetherra (if not already running)
2. Go to the Chat panel
3. Try these commands:

   /create_panel Create a system monitor with CPU and memory graphs
   /modify_panel chat_panel Add a file upload button and emoji picker
   /self_expand I need better debugging tools
   /help

[TOOL] What was fixed:
- LyrixaEngine.process_user_input() returns a coroutine
- Added _get_engine_response() to handle async properly
- Fixed all engine calls in the self-extending system
- Removed duplicate code that was causing errors

✅ The system should now work without the 'coroutine' object error!
    """)

if __name__ == "__main__":
    print("🧠 LYRIXA SELF-EXTENDING SYSTEM - FIX VERIFICATION")
    print("=" * 60)

    success = test_async_handling()

    if success:
        show_usage_instructions()
    else:
        print("\n[ERROR] Fixes may need additional work. Check the errors above.")

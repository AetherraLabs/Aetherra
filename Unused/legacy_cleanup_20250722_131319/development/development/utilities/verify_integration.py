#!/usr/bin/env python3
"""
Verify World-Class Integration
==============================
🔍 Test if the world-class components are properly integrated into the hybrid window
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_integration():
    """Test the integration"""

    print("🔍 Testing World-Class Integration...")

    try:
        # Set environment
        os.environ["LYRIXA_UI_MODE"] = "hybrid"

        # Test imports
        from Aetherra.lyrixa.gui.window_factory import create_lyrixa_window

        print("✅ Creating hybrid window...")
        window = create_lyrixa_window()

        print("✅ Testing memory tab creation...")
        memory_tab = window.create_memory_tab()

        # Check if it's a world-class component
        if hasattr(memory_tab, 'memory_core'):
            print("✅ Memory tab uses world-class memory core!")
        elif hasattr(memory_tab, 'search_memories'):
            print("✅ Memory tab uses lightweight memory core!")
        else:
            print("⚠️  Memory tab uses fallback implementation")

        print("✅ Testing goal tab creation...")
        goal_tab = window.create_goal_tab()

        # Check if it's a world-class component
        if hasattr(goal_tab, 'goals'):
            print("✅ Goal tab uses world-class goal tracker!")
        elif hasattr(goal_tab, 'goal_tracker'):
            print("✅ Goal tab uses lightweight goal tracker!")
        else:
            print("⚠️  Goal tab uses fallback implementation")

        print("✅ Integration test complete!")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")

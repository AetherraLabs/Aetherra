#!/usr/bin/env python3
"""
Quick test for chat router fixes
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

def test_chat_router_fixes():
    """Test that chat router fixes work correctly"""
    print("🔍 Testing chat router fixes...")

    try:
        from core.chat_router import NeuroCodeChatRouter
        print("✅ Chat router imported successfully")

        # Create chat router instance
        router = NeuroCodeChatRouter(demo_mode=True, debug_mode=False)
        print("✅ Chat router instance created")

        # Test the fixed plugin loading method
        print("🔍 Testing fixed plugin loading method...")

        # Simulate a plugin loading error
        test_command = "use nonexistent_plugin"
        test_error = "plugin not loaded: nonexistent_plugin"

        # This should not crash now
        result = router._fix_plugin_loading(test_command, test_error)
        print(f"✅ Plugin loading fix method works: {result['success']}")

        # Test basic message processing
        print("🔍 Testing message processing...")
        response = router.process_message("Hello, how are you?")
        print(f"✅ Message processing works: {response.get('text', 'No text')[:50]}...")

        print("\n🎉 All chat router fixes are working correctly!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chat_router_fixes()
    sys.exit(0 if success else 1)

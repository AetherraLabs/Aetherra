#!/usr/bin/env python3
"""
Test all core Lyrixa imports to ensure everything works correctly
"""


def test_imports():
    """Test all imports and basic functionality"""
    print("🔍 Testing all Lyrixa imports...")

    # Test 1: Basic imports
    try:
        from lyrixa.conversation_manager import LyrixaConversationManager

        print("✅ ConversationManager imported successfully")
    except Exception as e:
        print(f"❌ ConversationManager import failed: {e}")
        return False

    try:
        from lyrixa.intelligence_integration import LyrixaIntelligenceStack

        print("✅ IntelligenceStack imported successfully")
    except Exception as e:
        print(f"❌ IntelligenceStack import failed: {e}")
        return False

    try:
        from lyrixa.launcher import LyrixaLauncherGUI

        print("✅ LauncherGUI imported successfully")
    except Exception as e:
        print(f"❌ LauncherGUI import failed: {e}")
        return False

    # Test 2: Basic instantiation
    try:
        conversation_manager = LyrixaConversationManager(workspace_path=".")
        print("✅ ConversationManager instantiated successfully")
    except Exception as e:
        print(f"❌ ConversationManager instantiation failed: {e}")
        return False

    try:
        intelligence_stack = LyrixaIntelligenceStack(workspace_path=".")
        print("✅ IntelligenceStack instantiated successfully")
    except Exception as e:
        print(f"❌ IntelligenceStack instantiation failed: {e}")
        return False

    # Test 3: Test basic methods
    try:
        # Test conversation manager
        test_response = conversation_manager.generate_response_sync(
            "Hello, test message"
        )
        print(f"✅ ConversationManager response: {test_response[:50]}...")
    except Exception as e:
        print(f"❌ ConversationManager response failed: {e}")
        return False

    print("✅ All core imports and basic functionality tests passed!")
    return True


if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 All tests passed! Lyrixa is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

#!/usr/bin/env python3
"""
Debug Chat Function
===================

Test the chat functionality in Lyrixa to identify the issue.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_intelligence_stack():
    """Test the intelligence stack initialization and chat response"""
    print("🧪 Testing Lyrixa Intelligence Stack Chat Function")
    print("=" * 55)

    try:
        from lyrixa.intelligence_integration import LyrixaIntelligenceStack

        print("✅ Successfully imported LyrixaIntelligenceStack")

        # Initialize intelligence stack
        workspace_path = os.path.dirname(__file__)
        intelligence_stack = LyrixaIntelligenceStack(workspace_path)

        print("✅ Successfully initialized intelligence stack")

        # Test conversation manager
        if intelligence_stack.conversation_manager:
            print("✅ Conversation manager available")
        else:
            print("⚠️  Conversation manager not available")

        # Test generate_response
        test_messages = [
            "Hello Lyrixa!",
            "What can you help me with?",
            "Tell me about the system status",
            "How are you doing?",
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. Testing message: '{message}'")
            try:
                response = intelligence_stack.generate_response(message)
                print(
                    f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}"
                )
                print("   ✅ Chat function working")
            except Exception as e:
                print(f"   ❌ Chat function error: {e}")
                import traceback

                print(f"   📋 Traceback: {traceback.format_exc()}")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback

        print(f"📋 Traceback: {traceback.format_exc()}")


def test_conversation_manager():
    """Test the conversation manager separately"""
    print("\n🗣️ Testing Conversation Manager")
    print("=" * 35)

    try:
        from lyrixa.conversation_manager import LyrixaConversationManager

        print("✅ Successfully imported LyrixaConversationManager")

        workspace_path = os.path.dirname(__file__)
        conv_manager = LyrixaConversationManager(workspace_path)

        print("✅ Successfully initialized conversation manager")

        if hasattr(conv_manager, "generate_response"):
            print("✅ generate_response method exists")
        else:
            print("❌ generate_response method missing")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
    except Exception as e:
        print(f"❌ Test Error: {e}")


def main():
    """Run all chat tests"""
    print("🚀 Lyrixa Chat Function Debug Suite")
    print("=" * 50)

    test_intelligence_stack()
    test_conversation_manager()

    print("\n" + "=" * 50)
    print("✅ Chat debug tests completed!")


if __name__ == "__main__":
    main()

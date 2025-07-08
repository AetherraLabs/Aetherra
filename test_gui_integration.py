#!/usr/bin/env python3
"""
🎙️ Test Lyrixa GUI Integration
=============================

Test the integration between the conversation manager and GUI.
"""

import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lyrixa.conversation_manager import LyrixaConversationManager
from lyrixa.intelligence_integration import LyrixaIntelligenceStack


def test_gui_integration():
    """Test GUI integration with conversation manager"""
    print("🎙️ Testing GUI Integration...")

    workspace_path = os.path.dirname(os.path.abspath(__file__))

    # Initialize conversation manager
    conversation_manager = LyrixaConversationManager(workspace_path)
    print(
        f"✅ Conversation manager initialized (Model: {conversation_manager.current_model})"
    )

    # Initialize intelligence stack
    intelligence_stack = LyrixaIntelligenceStack(workspace_path)
    print("✅ Intelligence stack initialized")

    # Test typical GUI interactions
    test_interactions = [
        "Hello Lyrixa!",
        "What can you do?",
        "Tell me about Aetherra",
        "How many plugins are active?",
    ]

    print("\n🔄 Testing GUI-style interactions...")
    for i, user_input in enumerate(test_interactions, 1):
        print(f"\n💬 User {i}: {user_input}")

        # Test sync response (like GUI would use)
        try:
            response = conversation_manager.generate_response_sync(user_input)
            print(f"🎙️ Lyrixa: {response[:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n📊 Final Status:")
    summary = conversation_manager.get_conversation_summary()
    print(f"• Conversations: {summary['conversation_count']}")
    print(f"• History: {summary['history_length']} messages")
    print(f"• Model: {summary['current_model']}")
    print(f"• LLM Enabled: {conversation_manager.llm_enabled}")

    print("\n✅ GUI integration test completed!")


if __name__ == "__main__":
    test_gui_integration()

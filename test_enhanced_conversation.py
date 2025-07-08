#!/usr/bin/env python3
"""
🧠 Test Enhanced Lyrixa Conversation Manager
==========================================

Test the enhanced conversation manager with smart fallback responses.
"""

import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lyrixa.conversation_manager import LyrixaConversationManager


def test_enhanced_conversation_manager():
    """Test the enhanced conversation manager"""
    print("🔄 Testing Enhanced Lyrixa Conversation Manager...")

    # Initialize the conversation manager
    print("🎙️ Initializing LyrixaConversationManager...")
    conversation_manager = LyrixaConversationManager(".")

    # Test queries with different patterns
    test_queries = [
        "Hello!",
        "What's the current system status?",
        "Can you help me with plugins?",
        "Tell me about Aetherra",
        "How's the memory system working?",
        "I need help with something complex",
        "What are your capabilities?",
    ]

    print("\n✅ System initialized! Testing enhanced responses...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"💬 Query {i}: {query}")

        try:
            # Test the sync response (which should use smart fallback)
            response = conversation_manager.generate_response_sync(query)
            print(f"🎙️ Enhanced Response: {response}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 80)

    # Test conversation summary
    print("\n📊 Conversation Summary:")
    summary = conversation_manager.get_conversation_summary()
    for key, value in summary.items():
        if key != "system_context":  # Skip detailed system context
            print(f"• {key}: {value}")

    print("\n✅ Enhanced conversation manager test complete!")


if __name__ == "__main__":
    test_enhanced_conversation_manager()

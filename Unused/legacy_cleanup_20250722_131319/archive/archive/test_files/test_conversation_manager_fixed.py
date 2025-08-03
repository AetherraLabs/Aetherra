#!/usr/bin/env python3
"""
🧠 Test Fixed Lyrixa Conversation Manager
========================================

Test the conversation manager with improved error handling and sync support.
"""

import asyncio
import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lyrixa.conversation_manager import LyrixaConversationManager


async def test_conversation_manager():
    """Test the conversation manager with various scenarios"""
    print("🧠 Testing Lyrixa Conversation Manager...")

    # Initialize the conversation manager
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    conversation_manager = LyrixaConversationManager(workspace_path)

    print(f"✅ Conversation manager initialized")
    print(f"🎯 Current model: {conversation_manager.current_model}")
    print(f"[TOOL] LLM enabled: {conversation_manager.llm_enabled}")

    # Test queries
    test_queries = [
        "Hello Lyrixa!",
        "What is Aetherra?",
        "Can you help me?",
        "Tell me about the system status",
    ]

    print("\n🔄 Testing async responses...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n💬 Query {i}: {query}")
        try:
            response = await conversation_manager.generate_response(query)
            print(f"🎙️ Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n🔄 Testing sync responses...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n💬 Query {i}: {query}")
        try:
            response = conversation_manager.generate_response_sync(query)
            print(f"🎙️ Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Test conversation summary
    print("\n📊 Conversation Summary:")
    summary = conversation_manager.get_conversation_summary()
    print(f"Session ID: {summary['session_id']}")
    print(f"Conversation count: {summary['conversation_count']}")
    print(f"History length: {summary['history_length']}")

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_conversation_manager())

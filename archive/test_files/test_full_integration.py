#!/usr/bin/env python3
"""
🧠 Test Full Lyrixa LLM Integration
==================================

Test the complete LLM-powered conversation system with all components.
"""

import asyncio
import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lyrixa.conversation_manager import LyrixaConversationManager
from lyrixa.intelligence_integration import LyrixaIntelligenceStack


async def test_full_system():
    """Test the complete system with real LLM integration"""
    print("🔄 Testing full LLM integration...")

    # Initialize the conversation manager
    print("🎙️ Initializing LyrixaConversationManager...")
    _ = LyrixaConversationManager(
        workspace_path="."
    )  # Initialize but use intelligence stack

    # Initialize the intelligence stack
    print("🧠 Initializing LyrixaIntelligenceStack...")
    intelligence_stack = LyrixaIntelligenceStack(workspace_path=".")

    # Test queries
    test_queries = [
        "Hello, what is Aetherra?",
        "Can you help me understand what plugins are available?",
        "What's the current system status?",
        "How does the memory system work?",
        "Can you explain your capabilities?",
    ]

    print("\n✅ System initialized! Testing queries...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"💬 Query {i}: {query}")

        # Test both sync and async
        try:
            # Async test
            async_response = await intelligence_stack.generate_response_async(query)
            print(f"🎙️ Async Response: {async_response}")

            # Sync test
            sync_response = intelligence_stack.generate_response(query)
            print(f"🎙️ Sync Response: {sync_response}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 80)

    print("✅ Full integration test complete!")


if __name__ == "__main__":
    asyncio.run(test_full_system())

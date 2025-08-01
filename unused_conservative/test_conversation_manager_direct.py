#!/usr/bin/env python3
"""
Direct Conversation Manager Test
Test the conversation manager directly without web interface
"""

import sys
import asyncio
from pathlib import Path

# Add the Aetherra directory to the Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_conversation_manager():
    print("🧪 Testing Conversation Manager Directly")
    print("=" * 50)

    try:
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

        # Initialize conversation manager
        print("📋 Initializing conversation manager...")
        conversation_manager = LyrixaConversationManager(
            workspace_path=str(project_root),
            gui_interface=None
        )

        # Test messages
        test_messages = [
            "hello",
            "how are you?",
            "tell me about yourself",
            "what are your capabilities?"
        ]

        for message in test_messages:
            print(f"\n🔹 Sending: {message}")
            try:
                response = conversation_manager.generate_response_sync(message)
                print(f"🤖 Response: {response[:200]}...")
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Failed to initialize conversation manager: {e}")

if __name__ == "__main__":
    test_conversation_manager()

#!/usr/bin/env python3
"""
Test Web Conversation Manager
Direct test of the conversation manager used by the web interface
"""

import sys
from pathlib import Path

# Add the Aetherra directory to the Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

    print("🧪 Testing Enhanced Conversation Manager")
    print("=" * 50)

    # Initialize the conversation manager (same as web interface)
    conversation_manager = LyrixaConversationManager(workspace_path=".")

    print("✅ Conversation manager initialized")

    # Test the exact same call the web interface makes
    test_messages = [
        "hello",
        "how are you?",
        "tell me about Aetherra",
        "what are your capabilities?"
    ]

    for message in test_messages:
        print(f"\n🔹 User: {message}")
        response = conversation_manager.generate_response_sync(message)
        print(f"🤖 Lyrixa: {response}")
        print("-" * 50)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

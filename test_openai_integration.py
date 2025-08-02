#!/usr/bin/env python3
"""
🧪 Test OpenAI Integration
==========================

Quick test to verify OpenAI API integration is working properly.
"""

import os
import sys

sys.path.append(".")


# Load environment variables from .env file manually
def load_env_file():
    """Load environment variables from .env file."""
    try:
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ .env file loaded successfully")
        else:
            print("❌ .env file not found")
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")


# Load environment variables
load_env_file()

from Aetherra.lyrixa.agents.lyrixa_ai import LyrixaAI
from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager


async def test_openai_integration():
    """Test OpenAI API integration."""

    print("🧪 Testing Aetherra AI Integration...")
    print("=" * 50)

    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API Key: Found (starts with {api_key[:8]}...)")
    else:
        print("❌ OpenAI API Key: Not found in environment")
        print("   Please set OPENAI_API_KEY in your .env file")
        return

    print("\n🤖 Testing LyrixaAI Agent...")

    # Create LyrixaAI agent
    lyrixa_agent = LyrixaAI()
    print(f"   Agent Status: {lyrixa_agent.get_status()}")

    # Test agent conversation
    test_request = {
        "type": "chat",
        "message": "Hello! Can you tell me about the Aetherra AI OS?",
        "context": {"test_mode": True},
    }

    print(f"\n📤 Sending test message: {test_request['message']}")

    try:
        response = await lyrixa_agent.process_request(test_request)
        print(f"📥 Response received:")
        print(f"   Success: {response.get('success', False)}")
        if response.get("success"):
            print(f"   AI Response: {response.get('response', 'No response')}")
            print(f"   Model: {response.get('model', 'Unknown')}")
        else:
            print(f"   Error: {response.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error during test: {e}")

    print("\n💬 Testing Conversation Manager...")

    # Test conversation manager
    conv_manager = LyrixaConversationManager()

    try:
        conv_response = conv_manager.process_message(
            "What capabilities does Aetherra have?", user_id="test_user"
        )

        print(f"📥 Conversation Manager Response:")
        print(f"   Success: {conv_response.get('success', False)}")
        print(f"   Response: {conv_response.get('response', 'No response')}")

    except Exception as e:
        print(f"❌ Error in conversation manager: {e}")

    print("\n🎉 OpenAI Integration Test Complete!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_openai_integration())

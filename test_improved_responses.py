#!/usr/bin/env python3
"""
Test the improved basic response system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def generate_basic_response(user_message):
    """Generate intelligent basic responses without full AI stack"""
    message_lower = user_message.lower()

    # Greeting responses
    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm Lyrixa, your AI assistant. How can I help you today? (Basic mode - full capabilities loading...)"

    # Question responses
    elif "?" in user_message:
        return f"That's an interesting question about '{user_message}'. I'm currently in basic mode while my full intelligence stack initializes. I'll be able to provide more detailed answers soon!"

    # Help requests
    elif any(word in message_lower for word in ["help", "assist", "support"]):
        return "I'm here to help! I'm currently in basic mode while loading my full capabilities. You can ask me anything, and I'll do my best to assist you."

    # Status requests
    elif any(word in message_lower for word in ["status", "ready", "working"]):
        return "I'm partially online! My basic chat functions are working, and I'm currently loading my advanced intelligence modules. Full capabilities will be available shortly."

    # Aetherra/Project questions
    elif any(word in message_lower for word in ["aetherra", "project", "what are you"]):
        return "I'm Lyrixa, an AI assistant that's part of the Aetherra project - an AI-native operating system. I'm currently starting up my full intelligence stack!"

    # Default intelligent response
    else:
        return f"I understand you're saying '{user_message}'. I'm processing this in basic mode while my full AI capabilities initialize. Thank you for your patience!"


def test_openai_basic():
    """Test OpenAI basic responses"""
    try:
        import os

        import openai
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Lyrixa, an AI assistant from the Aetherra project. Be helpful, friendly, and concise. You are currently in basic mode while the full intelligence stack initializes.",
                    },
                    {"role": "user", "content": "Hello, how are you?"},
                ],
                max_tokens=150,
                temperature=0.7,
            )
            ai_response = response.choices[0].message.content
            return f"{ai_response} (Basic AI mode)"
    except Exception as e:
        return f"OpenAI error: {e}"


def main():
    print("🧪 Testing Improved Basic Responses")
    print("=" * 50)

    # Test messages
    test_messages = [
        "Hello",
        "What is Aetherra?",
        "Can you help me?",
        "What's your status?",
        "How does this work?",
        "Test message",
    ]

    print("\n📝 Testing basic response patterns:")
    for message in test_messages:
        response = generate_basic_response(message)
        print(f"\nUser: {message}")
        print(f"Lyrixa: {response}")

    print("\n🤖 Testing OpenAI basic mode:")
    openai_response = test_openai_basic()
    print(f"OpenAI Response: {openai_response}")


if __name__ == "__main__":
    main()

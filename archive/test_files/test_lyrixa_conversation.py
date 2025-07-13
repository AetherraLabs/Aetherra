#!/usr/bin/env python3
"""
🎙️ TEST LYRIXA CONVERSATION
===========================

Test script to verify Lyrixa's conversational capabilities and AI response generation.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from lyrixa import LyrixaAI
except ImportError as e:
    print(f"❌ Failed to import LyrixaAI: {e}")
    sys.exit(1)


async def test_lyrixa_conversation():
    """Test Lyrixa's basic conversation functionality"""
    print("🧪 Testing Lyrixa Conversation Capabilities")
    print("=" * 50)

    try:
        # Initialize Lyrixa
        print("🎙️ Initializing Lyrixa...")
        lyrixa = LyrixaAI(workspace_path=str(project_root))
        await lyrixa.initialize()
        print("✅ Lyrixa initialized successfully")

        # Test cases
        test_inputs = [
            "hello",
            "status_report",
            "What is Aetherra?",
            "How can you help me?",
            "I'm having trouble with my code",
        ]

        print("\n🗣️ Testing Conversation:")
        print("-" * 30)

        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n{i}. User: {user_input}")

            try:
                # Use brain_loop method for complete response generation
                response = await lyrixa.brain_loop(user_input)

                lyrixa_response = response.get(
                    "lyrixa_response", "No response generated"
                )
                confidence = response.get("confidence", 0.0)
                actions = response.get("actions_taken", [])

                print(f"   🎙️ Lyrixa: {lyrixa_response}")
                print(f"   📊 Confidence: {confidence:.2f}")
                if actions:
                    print(f"   🎯 Actions: {', '.join(actions)}")

                # Check if response looks like AI-generated content
                if len(lyrixa_response) > 10 and "I" in lyrixa_response:
                    print("   ✅ Response appears to be AI-generated")
                else:
                    print("   ❌ Response appears to be template/fallback")

            except Exception as e:
                print(f"   ❌ Error generating response: {e}")

        print("\n" + "=" * 50)
        print("🎯 Conversation Test Complete")

        # Test the conversation engine directly
        print("\n🧠 Testing Conversation Engine Directly:")
        print("-" * 40)

        try:
            conv_response = await lyrixa.conversation.process_conversation_turn(
                "Tell me about yourself", {"session_id": "test_session"}
            )

            print(
                f"Direct conversation response: {conv_response.get('text', 'No text')}"
            )

            if conv_response.get("text"):
                print("✅ Conversation engine is working")
            else:
                print("❌ Conversation engine not responding correctly")

        except Exception as e:
            print(f"❌ Conversation engine error: {e}")

    except Exception as e:
        print(f"❌ Failed to initialize Lyrixa: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_lyrixa_conversation())

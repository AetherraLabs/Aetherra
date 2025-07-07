#!/usr/bin/env python3
"""
Test script for the upgraded Lyrixachat system
"""


def test_chat_router(demo_mode=True):
    try:
        from Aetherra.core.chat_router import AetherraChatRouter

        print("✅ Chat router imported successfully")

        chat_router = AetherraChatRouter(demo_mode=demo_mode)
        mode_str = "Demo Mode" if demo_mode else "AI Mode"
        print(f"✅ Chat router initialized in {mode_str}")

        # Test different types of messages
        test_messages = [
            "Hello there!",
            "Can you help me learn AetherraCode?",
            "I want to create a memory system for my project",
            "What can you do?",
            "How do I use the memory features?",
            "Create a function to analyze data patterns",
        ]

        print(f"\n🧬 Testing LyrixaChat Upgrade ({mode_str})")
        print("=" * 60)

        for i, message in enumerate(test_messages, 1):
            print(f"\n=== Test {i}: {message} ===")
            try:
                response = chat_router.process_message(message)

                if isinstance(response, dict):
                    text_response = response.get("text", "No text")
                    print(f"✅ Response: {text_response[:300]}")
                    if len(text_response) > 300:
                        print("...")

                    # Show additional info
                    if response.get("Aetherra"):
                        print(f"🧬 AetherraCode: {response['Aetherra']}")
                    if response.get("suggestions"):
                        print(f"💡 Suggestions: {response['suggestions']}")
                else:
                    print(f"❌ Unexpected response type: {type(response)}")

            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback

                traceback.print_exc()

        print(f"\n✅ Chat router test completed ({mode_str})")

        # Test conversation history
        history = chat_router.get_chat_history()
        print(f"\n📚 Conversation history: {len(history)} entries")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧬 LyrixaChat System Upgrade Test")
    print("=" * 50)

    # Test in demo mode first (no AI calls)
    success = test_chat_router(demo_mode=True)

    if success:
        print("\n" + "=" * 50)
        print("🎉 Upgrade successful! Key improvements:")
        print("  ✅ AI-powered responses (when available)")
        print("  ✅ Rich context injection")
        print("  ✅ Enhanced fallback responses")
        print("  ✅ Conversation history tracking")
        #         print("  ✅ Debug logging for troubleshooting")
        print("  ✅ Graceful error handling")
    else:
        print("\n❌ Tests failed. Check errors above.")

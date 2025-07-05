#!/usr/bin/env python3
"""
Advanced test script for the tuned Neuroplex chat system
"""

def test_advanced_features():
    try:
        from Aetherra.core.chat_router import AetherraChatRouter
        print('🧬 Testing Advanced Neuroplex Features')
        print('=' * 50)

        # Test with different personalities
        personalities = ["default", "mentor", "sassy", "dev_focused"]

        for personality in personalities:
            print(f'\n🎭 Testing {personality.upper()} personality:')

            chat_router = AetherraChatRouter(demo_mode=True, debug_mode=True)
            chat_router.set_personality(personality)

            # Test message
            test_message = "How do I write a plugin?"
            response = chat_router.process_message(test_message)

            print(f'Response: {response.get("text", "No response")[:150]}...')

            # Check proactive suggestions
            if response.get("proactive_suggestions"):
                print(f'Suggestions: {response["proactive_suggestions"]}')

            print('-' * 30)

        print('\n🚀 Testing Smart Intent Routing:')

        # Test ambiguous messages that should route to open-ended
        ambiguous_messages = [
            "I'm thinking about programming",
            "Tell me something interesting",
            "What do you think about AI?",
            "Random question"
        ]

        chat_router = AetherraChatRouter(demo_mode=True, debug_mode=True)

        for msg in ambiguous_messages:
            print(f'\nTesting: "{msg}"')
            response = chat_router.process_message(msg)
            print(f'Route taken: {response.get("intent", {}).get("type", "unknown")}')

        print('\n✅ Advanced features test completed!')
        return True

    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_advanced_features()

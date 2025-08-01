#!/usr/bin/env python3
"""
Final demonstration of advanced Lyrixacapabilities
"""

from core.chat_router import AetherraChatRouter


def demonstrate_advanced_Lyrixa():
    print("🧬 LyrixaADVANCED CAPABILITIES DEMONSTRATION")
    print("=" * 60)

    # Initialize with debug mode for full visibility
    Lyrixa = AetherraChatRouter(demo_mode=True, debug_mode=False)  # Clean output

    print("\n🎭 Demonstrating Personality Switching:")

    # Test different personalities with the same question
    test_question = "How do I optimize my Aetherra?"

    personalities = ["default", "mentor", "sassy", "dev_focused"]

    for personality in personalities:
        Lyrixa.set_personality(personality)
        print(f"\n🎭 {personality.upper()} Personality:")

        response = Lyrixa.process_message(test_question)
        print(f"Response: {response['text'][:150]}...")

        if response.get("proactive_suggestions"):
            print(f"Suggestions: {response['proactive_suggestions']}")

    print("\n🧠 Demonstrating Smart Context Awareness:")

    # Reset to default personality
    Lyrixa.set_personality("default")

    # Simulate conversation flow
    conversation_flow = [
        "Hello, I'm new to Aetherra",
        "I want to build a memory system",
        "How do I track my progress?",
        "What should I do next?",
    ]

    for i, message in enumerate(conversation_flow, 1):
        print(f"\n💬 Exchange {i}: {message}")
        response = Lyrixa.process_message(message)
        print(f"Response: {response['text'][:200]}...")

        if response.get("proactive_suggestions"):
            print(f"Proactive: {response['proactive_suggestions']}")

    print(f"\n📚 Conversation History: {len(Lyrixa.chat_history)} exchanges")

    print("\n🚀 Testing Smart Intent Routing:")

    # Test messages that should trigger different routing
    routing_tests = [
        ("What is Aetherra?", "Should route to help"),
        ("Hmm, interesting thought...", "Should route to open-ended AI"),
        ("Create a data analyzer", "Should route to programming"),
        ("Random philosophical question", "Should route to open-ended AI"),
    ]

    for message, expected in routing_tests:
        print(f"\n🔍 Testing: '{message}' ({expected})")
        # Use debug mode temporarily to see routing
        Lyrixa.debug_mode = True
        response = Lyrixa.process_message(message)
        Lyrixa.debug_mode = False
        print(f"Result: {response['text'][:100]}...")

    print("\n✅ DEMONSTRATION COMPLETE")
    print("🎉 Lyrixais now a true AI Assistant with:")
    print("   🧠 Contextual Intelligence")
    print("   🎭 Swappable Personalities")
    print("   🚀 Proactive Suggestions")
    print("   🔮 Smart Intent Routing")
    print("   💾 Conversation Memory")
    print("   🛠️ Advanced Context Injection")


if __name__ == "__main__":
    demonstrate_advanced_Lyrixa()

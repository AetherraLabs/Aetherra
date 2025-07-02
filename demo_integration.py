#!/usr/bin/env python3
"""
🚀 Integration Demonstration
===========================

Quick demo showing the Enhanced Neuroplex with integrated chat router in action.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "core"))

def demo_integration():
    """Demonstrate the integrated features"""
    print("🚀 NEUROPLEX INTEGRATION DEMONSTRATION")
    print("=" * 50)

    # Import and initialize
    from chat_router import NeuroCodeChatRouter

    print("✅ Importing enhanced chat router...")
    chat_router = NeuroCodeChatRouter(demo_mode=True, debug_mode=False)

    print("✅ Chat router initialized successfully!")
    print("\n🎭 Testing personality switching:")

    personalities = ["default", "mentor", "sassy", "dev_focused"]
    test_message = "How do I optimize my NeuroCode?"

    for personality in personalities:
        print(f"\n--- {personality.upper()} Personality ---")
        chat_router.set_personality(personality)

        response = chat_router.process_message(test_message)
        print(f"Response: {response['text'][:100]}...")

        if response.get('proactive_suggestions'):
            print(f"Suggestions: {response['proactive_suggestions']}")

    print("\n🧠 Testing context awareness:")

    conversation = [
        "I'm new to NeuroCode",
        "I want to build a memory system",
        "How do I track my progress?",
        "What should I do next?"
    ]

    for msg in conversation:
        print(f"\nUser: {msg}")
        response = chat_router.process_message(msg)
        print(f"AI: {response['text'][:80]}...")

    print(f"\n📚 Conversation history: {len(chat_router.chat_history)} exchanges")

    print("\n🎉 INTEGRATION DEMO COMPLETE!")
    print("🚀 Enhanced Neuroplex features:")
    print("   ✅ AI-powered responses")
    print("   ✅ Swappable personalities")
    print("   ✅ Context-aware conversations")
    print("   ✅ Proactive suggestions")
    print("   ✅ Smart intent routing")
    print("   ✅ Memory integration")

    print("\n🎯 Ready for GUI launch!")
    print("Run: python neurocode_launcher.py → Option 1")

if __name__ == "__main__":
    demo_integration()

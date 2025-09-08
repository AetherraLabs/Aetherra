#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Enhanced Conversational AI Demo (#7)
========================================

Demonstration of Lyrixa's Enhanced Conversational AI capabilities
with multi-turn memory, intent translation, and advanced context management.
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_conversation_manager_7 import LyrixaEnhancedConversationManager


class MockMemoryEngine:
    """Mock memory engine for demonstration"""

    def __init__(self):
        self.stored_conversations = []
        self.memories = []

    async def recall(self, query, user_id, context=None, limit=5):
        """Mock memory recall"""
        # Simple keyword matching for demo
        relevant_memories = []
        for memory in self.memories[-limit:]:
            if any(
                word in memory.get("content", "").lower()
                for word in query.lower().split()
            ):
                relevant_memories.append(
                    {
                        "content": memory["content"],
                        "confidence": 0.8,
                        "timestamp": memory["timestamp"],
                    }
                )
        return relevant_memories

    async def store_conversation(
        self, user_input, assistant_response, context, intent_analysis, timestamp
    ):
        """Mock conversation storage"""
        self.memories.append(
            {
                "content": f"{user_input} -> {assistant_response}",
                "context": context,
                "intent": intent_analysis,
                "timestamp": timestamp.isoformat(),
            }
        )


class MockAnalyticsEngine:
    """Mock analytics engine for demonstration"""

    def __init__(self):
        self.metrics = []

    async def collect_metrics(self, metrics):
        """Mock metrics collection"""
        self.metrics.append(metrics)
        print(f"📊 Analytics: {metrics}")


async def demo_enhanced_conversation():
    """Demonstrate Enhanced Conversational AI capabilities"""

    print("🧠 LYRIXA ENHANCED CONVERSATIONAL AI DEMO (#7)")
    print("=" * 50)
    print("Enhanced features:")
    print("• Multi-Turn Conversation Memory")
    print("• Intent-to-Code Translation")
    print("• Context-Aware Dialogue Management")
    print("• Thread-Aware Session Continuity")
    print("• Personality Persistence & Auto-Selection")
    print()

    # Initialize enhanced conversation manager
    memory_engine = MockMemoryEngine()
    analytics_engine = MockAnalyticsEngine()

    conversation_manager = LyrixaEnhancedConversationManager(
        memory_engine=memory_engine, analytics_engine=analytics_engine
    )

    # Demo conversation scenarios
    test_messages = [
        {
            "message": "Hello! I'm working on a new Python project and need help.",
            "user_id": "demo_user",
            "context": {"session_id": "session_1", "project_context": "Python web app"},
        },
        {
            "message": "Can you create a function to calculate fibonacci numbers?",
            "user_id": "demo_user",
            "context": {"session_id": "session_1", "thread_id": "thread_1"},
        },
        {
            "message": "Now explain how the fibonacci algorithm works",
            "user_id": "demo_user",
            "context": {"session_id": "session_1", "thread_id": "thread_1"},
        },
        {
            "message": "What did we discuss earlier about fibonacci?",
            "user_id": "demo_user",
            "context": {"session_id": "session_1", "thread_id": "thread_2"},
        },
        {
            "message": "URGENT: Fix a bug in my API endpoint code",
            "user_id": "demo_user",
            "context": {"session_id": "session_1", "thread_id": "thread_3"},
        },
    ]

    print("🎯 ENHANCED CONVERSATION DEMONSTRATION")
    print("-" * 40)

    for i, test_case in enumerate(test_messages, 1):
        print(f"\n📝 Test Case {i}: {test_case['message'][:50]}...")
        print("-" * 30)

        # Process message with enhanced conversation manager
        result = await conversation_manager.process_enhanced_message(
            message=test_case["message"],
            user_id=test_case["user_id"],
            context=test_case["context"],
        )

        # Display results
        print(f"🤖 Response: {result['response'][:200]}...")
        print(f"🎯 Intent: {result.get('intent', 'None')}")
        print(f"💬 Type: {result['conversation_type']}")
        print(f"📊 Confidence: {result['confidence']:.2f}")
        print(f"⚡ Processing Time: {result['processing_time']:.3f}s")

        if result.get("generated_code"):
            print(f"💻 Code Generated: Yes ({len(result['generated_code'])} chars)")

        if result.get("requires_followup"):
            print("🔄 Requires Followup: Yes")

        # Small delay for demonstration
        await asyncio.sleep(0.5)

    print("\n" + "=" * 50)
    print("📊 ENHANCED CONVERSATION STATISTICS")
    print("-" * 30)

    stats = conversation_manager.get_enhanced_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

    print(f"\n🧠 Memory Engine: {len(memory_engine.memories)} stored memories")
    print(f"📈 Analytics Engine: {len(analytics_engine.metrics)} metric events")

    # Demo thread summary
    print("\n🧵 THREAD SUMMARY DEMO")
    print("-" * 20)

    thread_summary = conversation_manager.get_thread_summary("session_1", "thread_1")
    print("Thread 1 Summary:")
    for key, value in thread_summary.items():
        print(f"  {key}: {value}")

    print("\n[OK] Enhanced Conversational AI Demo Complete!")
    print("🚀 Ready for production integration with:")
    print("   • Real memory engine integration")
    print("   • OpenAI API for enhanced responses")
    print("   • Production analytics collection")
    print("   • Multi-user session management")


async def interactive_demo():
    """Interactive demo for testing Enhanced Conversational AI"""

    print("\n🎮 INTERACTIVE ENHANCED CONVERSATION MODE")
    print("=" * 45)
    print("Type messages to test Enhanced Conversational AI")
    print("Special commands:")
    print("  /stats - Show conversation statistics")
    print("  /personality [mode] - Set personality mode")
    print("  /exit - Exit interactive mode")
    print()

    # Initialize
    memory_engine = MockMemoryEngine()
    analytics_engine = MockAnalyticsEngine()

    conversation_manager = LyrixaEnhancedConversationManager(
        memory_engine=memory_engine, analytics_engine=analytics_engine
    )

    user_id = "interactive_user"
    session_id = "interactive_session"
    thread_counter = 1

    while True:
        try:
            user_input = input("\n💬 You: ").strip()

            if user_input.lower() in ["/exit", "quit", "exit"]:
                print("👋 Goodbye! Enhanced Conversational AI session ended.")
                break

            if user_input.lower() == "/stats":
                stats = conversation_manager.get_enhanced_stats()
                print("\n📊 Current Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                continue

            if user_input.lower().startswith("/personality "):
                personality = user_input.split(" ", 1)[1]
                conversation_manager.set_user_personality(user_id, personality)
                print(f"🎭 Personality set to: {personality}")
                continue

            if not user_input:
                continue

            # Process with enhanced conversation manager
            result = await conversation_manager.process_enhanced_message(
                message=user_input,
                user_id=user_id,
                context={
                    "session_id": session_id,
                    "thread_id": f"thread_{thread_counter}",
                    "project_context": "Interactive Demo",
                },
            )

            # Display response
            print(
                f"\n🧠 Lyrixa ({result.get('intent', 'general')}): {result['response']}"
            )

            # Show metadata if interesting
            if result["confidence"] > 0.8:
                print(f"   🎯 High confidence: {result['confidence']:.2f}")

            if result.get("generated_code"):
                print("   💻 Code generated - see response above")

            # Increment thread for topic changes
            if result.get("requires_followup"):
                thread_counter += 1

        except KeyboardInterrupt:
            print("\n\n👋 Enhanced Conversational AI session interrupted.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("🧠 LYRIXA ENHANCED CONVERSATIONAL AI (#7)")
    print("Roadmap Item #7: Enhanced Conversational AI Implementation")
    print()

    # Run demo
    asyncio.run(demo_enhanced_conversation())

    # Offer interactive mode
    try:
        choice = (
            input("\n🎮 Would you like to try interactive mode? (y/n): ").strip().lower()
        )
        if choice in ["y", "yes"]:
            asyncio.run(interactive_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo session ended.")

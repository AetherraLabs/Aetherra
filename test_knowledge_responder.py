"""
Test Knowledge Responder Integration
===================================

Tests the Knowledge Responder with the Lyrixa memory system and context bridge.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_knowledge_responder():
    """Test the Knowledge Responder system."""
    print("🎯 TESTING KNOWLEDGE RESPONDER")
    print("=" * 50)

    try:
        # Import components
        from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
        from lyrixa.core.conversation import PersonalityType, ToneMode
        from lyrixa.core.knowledge_responder import (
            KnowledgeResponder,
            create_knowledge_responder,
        )
        from lyrixa.gui.unified.context_bridge import ContextBridge

        print("✅ Imports successful")

        # Initialize memory system
        print("\n🧠 Initializing memory system...")
        memory = AdvancedMemorySystem()

        # Initialize context bridge
        print("🔗 Initializing context bridge...")
        context_bridge = ContextBridge()

        # Create knowledge responder
        print("🎯 Creating Knowledge Responder...")
        responder = await create_knowledge_responder(memory, context_bridge)

        # Test basic response
        print("\n📝 Testing basic response...")
        result = await responder.answer_question(
            "What is Python programming?",
            context={"personality": "mentor", "tone_mode": "encouraging"},
        )

        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Quality: {result['quality']}")

        # Test different personalities
        personalities = [
            ("mentor", "How do I learn machine learning?"),
            ("dev_focused", "Explain REST API architecture"),
            ("creative", "Tell me about digital art techniques"),
            ("analytical", "What are the performance implications of async/await?"),
        ]

        print("\n🎭 Testing different personalities...")
        for personality, query in personalities:
            print(f"\n{personality.upper()}: {query}")
            result = await responder.quick_answer(query, personality)
            print(f"Response: {result[:100]}...")

        # Test conversation context
        print("\n💬 Testing conversational context...")
        from lyrixa.core.conversation import ConversationState

        conv_state = ConversationState(
            session_id="test_123",
            turn_count=1,
            user_mood="curious",
            user_expertise_level="beginner",
            current_topic="programming",
            context_history=[],
            emotional_state="engaged",
            relationship_stage="new",
        )

        conv_result = await responder.conversational_answer(
            "Can you explain more about that?", conv_state, PersonalityType.FRIENDLY
        )

        print(f"Conversational response: {conv_result['response']}")

        # Test memory integration (if memories exist)
        print("\n🔍 Testing memory search integration...")
        memories = await responder._search_memories("Python programming", limit=3)
        print(f"Found {len(memories)} relevant memories")

        print("\n✅ Knowledge Responder test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_knowledge_responder())
    print(
        f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Knowledge Responder integration test"
    )

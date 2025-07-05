#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
from lyrixa.core.conversation import LyrixaConversationalEngine


async def test_knowledge_routing():
    print("🧪 TESTING KNOWLEDGE RESPONDER ROUTING")

    # Initialize memory system
    memory = AdvancedMemorySystem()

    # Store test memory
    await memory.store_memory(
        content="Aetherra is an advanced AI coding platform for smart contracts.",
        memory_type="project_info",
        tags=["aetherra", "platform"],
    )

    # Initialize conversation engine WITHOUT calling initialize_conversation
    # This will test the auto-initialization in process_conversation_turn
    engine = LyrixaConversationalEngine(memory_system=memory)

    print("✅ Engine created, testing knowledge responder...")

    # Check if knowledge responder is available
    if engine.knowledge_responder:
        print("✅ Knowledge Responder is available")

        # Test detection
        test_query = "What is Aetherra?"
        is_factual = engine.knowledge_responder.is_factual_or_project_query(test_query)
        print(f"Query '{test_query}' detected as factual: {is_factual}")

        # Test answer generation directly
        try:
            answer = await engine.knowledge_responder.answer_question(test_query)
            print(f"Direct answer: {answer}")
        except Exception as e:
            print(f"Error in direct answer: {e}")
    else:
        print("⚠️ Knowledge Responder not available")

    # Test conversation turn (this will auto-initialize)
    try:
        print("\n🔄 Testing conversation turn...")
        response = await engine.process_conversation_turn("What is Aetherra?")
        print(f"Full response: {response}")
    except Exception as e:
        print(f"Error in conversation turn: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_knowledge_routing())

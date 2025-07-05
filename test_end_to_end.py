#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
from lyrixa.core.conversation import LyrixaConversationalEngine


async def test_end_to_end():
    print("🧪 END-TO-END KNOWLEDGE TEST")
    print("=" * 50)

    # Step 1: Load knowledge fresh
    print("1. Loading knowledge into memory...")
    from load_project_knowledge import ProjectKnowledgeLoader

    memory = AdvancedMemorySystem()
    loader = ProjectKnowledgeLoader(memory_system=memory)

    # Load a small subset first to test
    test_knowledge = [
        {
            "id": "test_aetherra",
            "content": "Aetherra is an advanced AI coding platform that uses .aether files for smart contracts and decentralized applications.",
            "summary": "Aetherra is an AI coding platform for smart contracts.",
            "tags": ["aetherra", "platform", "coding"],
        },
        {
            "id": "test_lyrixa",
            "content": "Lyrixa is the conversational AI assistant integrated into Aetherra that helps with coding, debugging, and project management.",
            "summary": "Lyrixa is Aetherra's AI assistant for coding help.",
            "tags": ["lyrixa", "assistant", "ai"],
        },
    ]

    print("   Loading test knowledge items...")
    for item in test_knowledge:
        await loader._process_knowledge_item(item)

    print(f"   Memory system now has {len(memory.memories)} items in memory")

    # Step 2: Test direct search
    print("\n2. Testing direct memory search...")
    results = await memory.semantic_search("What is Aetherra?", top_k=2)
    print(f"   Search results: {len(results) if results else 0}")

    if results:
        for result in results:
            print(f"   -> {result.get('content', 'No content')[:80]}...")

    # Step 3: Test with conversation engine
    print("\n3. Testing with conversation engine...")
    engine = LyrixaConversationalEngine(memory_system=memory)

    if engine.knowledge_responder:
        print("   ✅ Knowledge responder available")

        # Test query detection
        query = "What is Aetherra?"
        is_factual = engine.knowledge_responder.is_factual_or_project_query(query)
        print(f"   Query '{query}' detected as factual: {is_factual}")

        # Test direct knowledge response
        if is_factual:
            answer = await engine.knowledge_responder.answer_question(query)
            print(f"   Direct answer: {answer}")

        # Test full conversation
        response = await engine.process_conversation_turn(query)
        print(f"   Full response: {response['text']}")
        print(
            f"   Used knowledge responder: {'Used Project Knowledge Responder' in response.get('adaptation_notes', [])}"
        )
    else:
        print("   ❌ Knowledge responder not available")


if __name__ == "__main__":
    asyncio.run(test_end_to_end())

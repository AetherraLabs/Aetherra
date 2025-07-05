#!/usr/bin/env python3
"""
🧪 TEST LYRIXA WITH PROJECT KNOWLEDGE
====================================

Test Lyrixa's conversational engine with loaded project knowledge.
Verifies that the Knowledge Responder can answer questions about
Aetherra, Lyrixa, and the platform using the loaded knowledge.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from load_project_knowledge import load_project_knowledge
from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
from lyrixa.core.conversation import LyrixaConversationalEngine


async def test_lyrixa_with_knowledge():
    """Test Lyrixa with loaded project knowledge."""

    print("🧠 TESTING LYRIXA WITH PROJECT KNOWLEDGE")
    print("=" * 60)

    # Step 1: Load project knowledge
    print("\n1. Loading project knowledge...")
    try:
        stats = await load_project_knowledge(
            "lyrixa_project_knowledge_seed.json", verbose=False
        )
        print(f"   ✅ Loaded {stats['loaded']} knowledge items")
    except Exception as e:
        print(f"   ❌ Error loading knowledge: {e}")
        return

    # Step 2: Initialize Lyrixa with memory
    print("\n2. Initializing Lyrixa with memory system...")
    memory = AdvancedMemorySystem()
    engine = LyrixaConversationalEngine(memory_system=memory)

    if engine.knowledge_responder:
        print("   ✅ Knowledge Responder ready")
    else:
        print("   ❌ Knowledge Responder not available")
        return

    # Step 3: Test knowledge-based queries
    print("\n3. Testing knowledge-based conversations...")

    knowledge_queries = [
        "What is Aetherra?",
        "Who is Lyrixa?",
        "How does .aether work?",
        "What makes this platform unique?",
        "Tell me about the Aetherra language",
        "What are the key features of Aetherra?",
        "How do I get started with Aetherra?",
        "What is the philosophy behind Aetherra?",
    ]

    for i, query in enumerate(knowledge_queries, 1):
        print(f"\n--- Test {i}: {query} ---")

        try:
            # Test direct knowledge responder
            is_factual = engine.knowledge_responder.is_factual_or_project_query(query)
            print(f"Detected as factual: {is_factual}")

            if is_factual:
                direct_answer = await engine.knowledge_responder.answer_question(query)
                print(f"Direct answer: {direct_answer[:200]}...")

            # Test full conversation
            response = await engine.process_conversation_turn(query)
            print(f"Lyrixa says: {response['text'][:300]}...")

            # Check if knowledge responder was used
            used_knowledge = any(
                "Knowledge Responder" in note
                for note in response.get("adaptation_notes", [])
            )
            print(f"Used Knowledge Responder: {'✅' if used_knowledge else '❌'}")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Step 4: Test conversational queries (should NOT use knowledge responder)
    print(f"\n4. Testing conversational queries...")

    conversational_queries = [
        "Hello! How are you today?",
        "I'm feeling excited about this project!",
        "What's your favorite color?",
        "Can you help me with debugging?",
    ]

    for query in conversational_queries:
        print(f"\n--- Conversational Test: {query} ---")

        try:
            response = await engine.process_conversation_turn(query)
            print(f"Lyrixa says: {response['text'][:200]}...")

            used_knowledge = any(
                "Knowledge Responder" in note
                for note in response.get("adaptation_notes", [])
            )
            print(
                f"Used Knowledge Responder: {'❌' if not used_knowledge else '⚠️ (unexpected)'}"
            )

        except Exception as e:
            print(f"❌ Error: {e}")

    print(f"\n" + "=" * 60)
    print("🎯 LYRIXA KNOWLEDGE INTEGRATION TEST COMPLETE")

    # Summary
    summary = await engine.get_conversation_summary()
    print(f"📊 Total conversation turns: {summary.get('turn_count', 0)}")


if __name__ == "__main__":
    asyncio.run(test_lyrixa_with_knowledge())

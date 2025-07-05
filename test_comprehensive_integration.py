#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
from lyrixa.core.conversation import LyrixaConversationalEngine


async def comprehensive_test():
    print("🧪 COMPREHENSIVE KNOWLEDGE RESPONDER INTEGRATION TEST")
    print("=" * 60)

    # Initialize memory system
    print("\n1. Creating fresh memory system...")
    memory = AdvancedMemorySystem()

    # Store specific test knowledge
    print("2. Storing test knowledge...")

    await memory.store_memory(
        content="Aetherra is an advanced AI coding platform that uses .aether files for smart contracts and decentralized applications. It provides intelligent development tools and automated assistance.",
        memory_type="project_info",
        tags=["aetherra", "platform", "coding", "smart_contracts"],
    )

    await memory.store_memory(
        content="Lyrixa is the conversational AI assistant built into Aetherra. She helps developers with coding, debugging, project management, and provides intelligent assistance for .aether development.",
        memory_type="project_info",
        tags=["lyrixa", "assistant", "ai", "helper"],
    )

    await memory.store_memory(
        content="The ProjectKnowledgeResponder is a specialized module that handles factual and project-related queries by searching the memory system and synthesizing intelligent responses.",
        memory_type="technical_info",
        tags=["knowledge", "responder", "queries", "memory"],
    )

    print("✅ Test knowledge stored")

    # Initialize conversation engine
    print("\n3. Creating conversation engine...")
    engine = LyrixaConversationalEngine(memory_system=memory)

    if engine.knowledge_responder:
        print("✅ Knowledge Responder initialized successfully")
    else:
        print("❌ Knowledge Responder failed to initialize")
        return

    # Test direct responder functionality
    print("\n4. Testing Knowledge Responder directly...")

    test_queries = [
        "What is Aetherra?",
        "Tell me about Lyrixa",
        "How does the ProjectKnowledgeResponder work?",
        "What are .aether files?",
    ]

    for query in test_queries:
        print(f"\n--- Testing: '{query}' ---")

        # Test detection
        is_factual = engine.knowledge_responder.is_factual_or_project_query(query)
        print(f"Detected as factual: {is_factual}")

        if is_factual:
            try:
                answer = await engine.knowledge_responder.answer_question(query)
                print(f"Direct answer: {answer}")
            except Exception as e:
                print(f"❌ Error getting direct answer: {e}")
                import traceback

                traceback.print_exc()

    # Test full conversation integration
    print("\n" + "=" * 60)
    print("5. Testing full conversation integration...")

    conversation_tests = [
        ("What is Aetherra?", "Should use Knowledge Responder"),
        ("I'm feeling happy today!", "Should use normal conversation"),
        ("Tell me about Lyrixa", "Should use Knowledge Responder"),
        ("What's your favorite color?", "Should use normal conversation"),
        ("How does the knowledge system work?", "Should use Knowledge Responder"),
    ]

    for query, expectation in conversation_tests:
        print(f"\n--- Full Conversation Test: '{query}' ---")
        print(f"Expected: {expectation}")

        try:
            response = await engine.process_conversation_turn(query)
            print(f"Response: {response['text']}")

            if "adaptation_notes" in response and response["adaptation_notes"]:
                print(f"Notes: {response['adaptation_notes']}")
                used_knowledge = any(
                    "Knowledge Responder" in note
                    for note in response["adaptation_notes"]
                )
                print(f"Used Knowledge Responder: {used_knowledge}")
            else:
                print("Used Knowledge Responder: False")

        except Exception as e:
            print(f"❌ Error in conversation turn: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST COMPLETE")

    # Summary
    summary = await engine.get_conversation_summary()
    if "turn_count" in summary:
        print(f"\n📊 Conversation Summary: {summary['turn_count']} turns completed")
    else:
        print(f"\n📊 Conversation Summary: {summary}")


if __name__ == "__main__":
    asyncio.run(comprehensive_test())

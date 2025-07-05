#!/usr/bin/env python3
"""
🧪 TEST KNOWLEDGE RESPONDER INTEGRATION
======================================

Test the integration of ProjectKnowledgeResponder into the conversational engine.
Verifies that factual/project queries are properly routed to the knowledge responder.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
from lyrixa.core.conversation import LyrixaConversationalEngine


async def test_knowledge_integration():
    """Test the integration of knowledge responder with conversation engine."""

    print("🧪 TESTING KNOWLEDGE RESPONDER INTEGRATION")
    print("=" * 50)

    # Initialize memory system
    print("\n1. Initializing memory system...")
    memory = AdvancedMemorySystem()

    # Store some test knowledge
    print("\n2. Storing test knowledge...")
    await memory.store_memory(
        content="Aetherra is an advanced AI coding platform that uses .aether files for smart contracts and decentralized applications.",
        memory_type="project_info",
        tags=["aetherra", "platform", "coding"],
        confidence=0.8,
        context={"type": "project_info", "component": "platform"},
    )

    await memory.store_memory(
        content="Lyrixa is the conversational AI assistant integrated into Aetherra that helps with coding, debugging, and project management.",
        memory_type="project_info",
        tags=["lyrixa", "assistant", "ai"],
        confidence=0.8,
        context={"type": "project_info", "component": "assistant"},
    )

    await memory.store_memory(
        content="The ProjectKnowledgeResponder class handles factual queries by searching memory and synthesizing responses from stored knowledge.",
        memory_type="technical_info",
        tags=["knowledge", "responder", "technical"],
        confidence=0.7,
        context={"type": "technical_info", "component": "knowledge_system"},
    )

    # Initialize conversation engine
    print("\n3. Initializing conversational engine with memory...")
    engine = LyrixaConversationalEngine(memory_system=memory)

    await engine.initialize_conversation("test_session_knowledge")

    # Test queries
    test_queries = [
        ("What is Aetherra?", "factual/project"),
        ("Tell me about Lyrixa", "factual/project"),
        ("How does the ProjectKnowledgeResponder work?", "factual/project"),
        ("I'm feeling great today!", "conversational"),
        ("Help me understand the knowledge system", "factual/project"),
        ("What's your favorite color?", "conversational"),
    ]

    print("\n4. Testing query routing...")
    for i, (query, expected_type) in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {expected_type.upper()} QUERY ---")
        print(f"Query: '{query}'")

        # Check if responder detects it as factual
        if engine.knowledge_responder:
            is_factual = engine.knowledge_responder.is_factual_or_project_query(query)
            print(f"Detected as factual: {is_factual}")
        else:
            print("⚠️ Knowledge responder not available")
            is_factual = False

        # Process the conversation turn
        response = await engine.process_conversation_turn(query)

        print(f"Response: {response['text']}")

        if "adaptation_notes" in response and response["adaptation_notes"]:
            print(f"Notes: {response['adaptation_notes']}")

        # Verify routing worked as expected
        used_knowledge = any(
            "Knowledge Responder" in note
            for note in response.get("adaptation_notes", [])
        )

        if expected_type == "factual/project" and is_factual:
            if used_knowledge:
                print("✅ Correctly routed to Knowledge Responder")
            else:
                print("⚠️ Detected as factual but didn't use Knowledge Responder")
        elif expected_type == "conversational" and not is_factual:
            if not used_knowledge:
                print("✅ Correctly used normal conversation flow")
            else:
                print("⚠️ Used Knowledge Responder for conversational query")
        else:
            print(f"🔍 Edge case: detected={is_factual}, expected={expected_type}")

    print("\n" + "=" * 50)
    print("🎯 KNOWLEDGE INTEGRATION TEST COMPLETE")

    # Test conversation state persistence
    print("\n5. Testing conversation state...")
    summary = await engine.get_conversation_summary()
    print(f"Conversation turns: {summary.get('turn_count', 0)}")
    print(f"Current topic: {summary.get('current_topic', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(test_knowledge_integration())

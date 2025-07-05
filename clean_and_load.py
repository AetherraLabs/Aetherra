#!/usr/bin/env python3

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from load_project_knowledge import ProjectKnowledgeLoader
from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem


async def clean_and_load_knowledge():
    print("🧹 CLEAN KNOWLEDGE LOADING")
    print("=" * 50)

    # Step 1: Remove existing database to start fresh
    db_file = "lyrixa_advanced_memory.db"
    if os.path.exists(db_file):
        print(f"🗑️ Removing existing database: {db_file}")
        os.remove(db_file)
    else:
        print("📂 No existing database found")

    # Step 2: Create fresh memory system
    print("🆕 Creating fresh memory system...")
    memory = AdvancedMemorySystem()

    # Step 3: Load only project knowledge
    print("📚 Loading project knowledge...")
    loader = ProjectKnowledgeLoader(memory_system=memory)
    stats = await loader.load_from_json(
        "lyrixa_project_knowledge_seed.json", verbose=True
    )

    print(f"\n✅ CLEAN LOADING COMPLETE")
    print(f"   Loaded: {stats['loaded']} items")
    print(f"   Success rate: {(stats['loaded'] / stats['total_items'] * 100):.1f}%")

    # Step 4: Test the cleaned memory
    print(f"\n🔍 Testing cleaned memory...")
    test_queries = ["What is Aetherra?", "Who is Lyrixa?", "How does .aether work?"]

    for query in test_queries:
        results = await memory.semantic_search(query, top_k=1)
        print(f"\n'{query}':")
        if results:
            print(f"  ✅ Found: {results[0].get('content', 'No content')[:100]}...")
        else:
            print(f"  ❌ No results")

    # Step 5: Test with conversation engine
    print(f"\n💬 Testing with conversation engine...")
    from lyrixa.core.conversation import LyrixaConversationalEngine

    engine = LyrixaConversationalEngine(memory_system=memory)
    response = await engine.process_conversation_turn("What is Aetherra?")

    print(f"Response: {response['text']}")
    used_knowledge = any(
        "Knowledge Responder" in note for note in response.get("adaptation_notes", [])
    )
    print(f"Used Knowledge Responder: {used_knowledge}")


if __name__ == "__main__":
    asyncio.run(clean_and_load_knowledge())

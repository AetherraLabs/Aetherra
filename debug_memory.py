#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem


async def debug_memory():
    print("🔍 DEBUGGING MEMORY SYSTEM")

    # Create single memory system instance
    memory = AdvancedMemorySystem()

    # Load knowledge using the same memory instance
    print("Loading knowledge...")
    from load_project_knowledge import ProjectKnowledgeLoader

    loader = ProjectKnowledgeLoader(memory_system=memory)
    await loader.load_from_json("lyrixa_project_knowledge_seed.json", verbose=False)

    # Get memory stats
    stats = await memory.get_memory_statistics()
    print(f"Memory stats: {stats}")

    # Try basic search
    print("\nTesting search...")
    results = await memory.semantic_search("Aetherra", top_k=3)
    print(f"Search results for 'Aetherra': {len(results) if results else 0}")

    if results:
        for i, result in enumerate(results[:2]):
            print(f"Result {i + 1}: {result.get('content', 'No content')[:100]}...")
    else:
        print("No results found")

    # Check what's in the memories list
    print(f"\nMemories in system: {len(memory.memories)}")
    if memory.memories:
        print(f"First memory sample: {memory.memories[0][:100]}...")

        # Try searching within the memories directly
        print("\nDirect memory search test:")
        for i, mem in enumerate(memory.memories[:3]):
            if "aetherra" in mem.lower():
                print(f"  Found 'aetherra' in memory {i}: {mem[:100]}...")
                break
        else:
            print("  No 'aetherra' found in first 3 memories")

    # Test multiple search terms
    test_queries = ["Aetherra", "Lyrixa", "platform", "AI coding"]
    print("\nTesting multiple search queries...")
    for query in test_queries:
        results = await memory.semantic_search(query, top_k=1)
        print(f"  '{query}': {len(results) if results else 0} results")
        if results:
            print(f"    -> {results[0].get('content', 'No content')[:80]}...")


if __name__ == "__main__":
    asyncio.run(debug_memory())

#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem


async def test_search_debug():
    print("🔍 DEBUGGING SEARCH FUNCTIONALITY")

    memory = AdvancedMemorySystem()

    # Test the search with debug info
    print("\nTesting semantic search...")

    query = "Aetherra"
    print(f"Query: '{query}'")

    # Check if vector support is enabled
    print(
        f"Vector support: {hasattr(memory, 'embedding_model') and memory.embedding_model is not None}"
    )
    print(f"FAISS index: {hasattr(memory, 'index') and memory.index is not None}")

    try:
        results = await memory.semantic_search(query, top_k=5)
        print(f"Results: {len(results) if results else 0}")

        if results:
            for i, result in enumerate(results):
                print(f"  {i + 1}. Score: {result.get('similarity_score', 'N/A'):.3f}")
                print(f"      Content: {result.get('content', 'No content')[:100]}...")
                print()
        else:
            print("No results found")

            # Try fallback search
            print("\nTrying fallback search...")
            fallback_results = await memory._fallback_search(query, 5, None)
            print(
                f"Fallback results: {len(fallback_results) if fallback_results else 0}"
            )

            if fallback_results:
                for i, result in enumerate(fallback_results[:2]):
                    print(f"  {i + 1}. {result.get('content', 'No content')[:100]}...")

    except Exception as e:
        print(f"Error during search: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_search_debug())

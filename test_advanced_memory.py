#!/usr/bin/env python3
"""
Test the Advanced Vector Memory System
"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def main():
    try:
        from lyrixa.core.advanced_vector_memory import (
            AdvancedMemorySystem,
            ReflexiveAnalysisEngine,
        )

        print("🧪 Testing Advanced Vector Memory System")
        print("=" * 50)

        # Initialize systems
        memory = AdvancedMemorySystem()
        reflection_engine = ReflexiveAnalysisEngine(memory)

        # Test storing a memory
        print("\n1. Storing test memory...")
        memory_id = await memory.store_memory(
            "User prefers Python for scripting tasks",
            "preference",
            ["python", "scripting"],
        )
        print(f"   ✅ Stored memory: {memory_id[:8]}...")

        # Test semantic search
        print("\n2. Testing semantic search...")
        results = await memory.semantic_search("python programming", top_k=3)
        print(f"   Found {len(results)} relevant memories")

        # Test confidence analysis
        print("\n3. Testing confidence analysis...")
        response = "I think this might work, but I'm not entirely sure"
        confidence_analysis = await memory.analyze_confidence(response, {})
        print(f"   Confidence score: {confidence_analysis['confidence_score']:.3f}")
        print(f"   Needs clarification: {confidence_analysis['needs_clarification']}")

        # Get statistics
        print("\n4. Getting memory statistics...")
        stats = await memory.get_memory_statistics()
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Vector support: {stats['vector_support_enabled']}")

        print("\n✅ Advanced Memory System test successful!")

    except Exception as e:
        print(f"❌ Error testing memory system: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

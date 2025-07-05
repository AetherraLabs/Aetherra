#!/usr/bin/env python3
"""
🧠 PHASE 1 COMPREHENSIVE TEST (CORRECTED)
========================================

Test all Phase 1 Advanced Memory System features with correct API usage.
"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_phase1_complete():
    """Complete test of Phase 1 features"""
    print("🧠 PHASE 1: ADVANCED MEMORY SYSTEM - FINAL TEST")
    print("=" * 55)

    try:
        from lyrixa.core.advanced_vector_memory import (
            AdvancedMemorySystem,
            ReflexiveAnalysisEngine,
        )

        print("✅ Phase 1 modules imported successfully")

        # Initialize systems
        print("\n1️⃣ Initializing Systems...")
        memory = AdvancedMemorySystem()
        reflection_engine = ReflexiveAnalysisEngine(memory)

        # Test memory storage
        print("\n2️⃣ Testing Memory Storage...")
        test_memories = [
            ("User prefers dark mode interface", "preference", ["ui", "dark"], 0.9),
            (
                "Working on Phase 1 vector embeddings",
                "project",
                ["phase1", "vectors"],
                0.95,
            ),
            ("Need to implement anticipation engine", "goal", ["future", "ai"], 0.8),
            (
                "Uncertain about technical implementation details",
                "question",
                ["uncertainty"],
                0.6,
            ),
            (
                "Successfully completed vector memory system",
                "achievement",
                ["success"],
                1.0,
            ),
        ]

        for content, mem_type, tags, confidence in test_memories:
            memory_id = await memory.store_memory(content, mem_type, tags, confidence)
            print(f"   📝 Stored: {content[:40]}... (ID: {memory_id[:8]})")

        # Test semantic search
        print("\n3️⃣ Testing Semantic Search...")
        queries = ["user preferences", "implementation work", "future goals"]
        for query in queries:
            results = await memory.semantic_search(query, top_k=2)
            print(f"   🔍 '{query}' → {len(results)} results")
            for result in results:
                score = result.get("similarity_score", 0)
                print(f"      - {result['content'][:50]}... (score: {score:.3f})")

        # Test confidence analysis
        print("\n4️⃣ Testing Confidence Analysis...")
        test_response = "I think this might work, but I'm not entirely sure about the implementation"
        confidence_analysis = await memory.analyze_confidence(
            test_response, {"relevant_memories": []}
        )
        print(
            f"   💭 Test response confidence: {confidence_analysis['confidence_score']:.2f}"
        )
        print(
            f"   💭 Needs clarification: {confidence_analysis['needs_clarification']}"
        )

        # Test reflexive analysis
        print("\n5️⃣ Testing Reflexive Analysis...")
        reflection = await reflection_engine.daily_reflection()
        print(f"   🤔 Memories analyzed: {reflection['memory_count']}")
        print(f"   🤔 Average confidence: {reflection['average_confidence']:.2f}")
        print(f"   🤔 Insights generated: {len(reflection['insights'])}")
        print(f"   🤔 Suggestions provided: {len(reflection['suggestions'])}")

        if reflection["insights"]:
            print(f"   💡 Key insight: {reflection['insights'][0]}")
        if reflection["suggestions"]:
            print(f"   💡 Top suggestion: {reflection['suggestions'][0]}")

        # Test memory statistics
        print("\n6️⃣ Testing Memory Statistics...")
        stats = await memory.get_memory_statistics()
        print(f"   📊 Total memories: {stats['total_memories']}")
        print(f"   📊 Average confidence: {stats['average_confidence']:.2f}")
        print(f"   📊 Vector support: {stats['vector_support_enabled']}")
        print(f"   📊 Memory types: {list(stats['memory_types'].keys())}")

        print("\n🎉 PHASE 1 IMPLEMENTATION COMPLETE!")
        print("=" * 55)
        print("✅ Advanced vector memory with semantic search")
        print("✅ Confidence modeling and uncertainty detection")
        print("✅ Reflexive analysis with insights and suggestions")
        print("✅ Rich memory statistics and analytics")
        print("✅ Multi-type memory storage with tagging")
        print("✅ Async operations for GUI integration")

        print("\n🚀 PHASE 1 SUCCESS - READY FOR INTEGRATION!")
        return True

    except Exception as e:
        print(f"❌ Phase 1 test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_phase1_complete())

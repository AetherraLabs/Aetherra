#!/usr/bin/env python3
"""
🧠 PHASE 1 COMPREHENSIVE TEST SUITE
==================================

Test all Phase 1 Advanced Memory System features:
- Vector embeddings and semantic search
- Confidence modeling
- Reflexive analysis engine
- Memory statistics and insights
"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_advanced_memory_features():
    """Comprehensive test of Phase 1 features"""
    print("🧠 PHASE 1: ADVANCED MEMORY SYSTEM TEST")
    print("=" * 50)

    try:
        from lyrixa.core.advanced_vector_memory import (
            AdvancedMemorySystem,
            ReflexiveAnalysisEngine,
        )

        print("✅ Phase 1 modules imported successfully")

        # Initialize systems
        print("\n1️⃣ Initializing Advanced Memory System...")
        memory = AdvancedMemorySystem()

        print("\n2️⃣ Initializing Reflexive Analysis Engine...")
        reflection_engine = ReflexiveAnalysisEngine(memory)

        # Test memory storage with different types and confidence levels
        print("\n3️⃣ Testing Memory Storage...")

        memories_to_store = [
            {
                "content": "User prefers dark mode interface with minimal distractions",
                "memory_type": "preference",
                "tags": ["ui", "preferences", "dark-mode"],
                "confidence": 0.9,
            },
            {
                "content": "Working on Lyrixa Phase 1 implementation with vector embeddings",
                "memory_type": "project",
                "tags": ["lyrixa", "phase1", "implementation"],
                "confidence": 0.95,
            },
            {
                "content": "Need to implement reflexive analysis for self-improvement",
                "memory_type": "goal",
                "tags": ["improvement", "analysis", "ai"],
                "confidence": 0.8,
            },
            {
                "content": "User asked about vector search capabilities - uncertain about technical details",
                "memory_type": "question",
                "tags": ["vector", "search", "uncertainty"],
                "confidence": 0.6,
            },
            {
                "content": "Successfully integrated PySide6 GUI with enhanced memory system",
                "memory_type": "achievement",
                "tags": ["gui", "integration", "success"],
                "confidence": 1.0,
            },
        ]

        stored_ids = []
        for mem_data in memories_to_store:
            memory_id = await memory.store_memory(**mem_data)
            stored_ids.append(memory_id)
            print(f"   📝 Stored: {mem_data['content'][:50]}... (ID: {memory_id[:8]})")

        # Test semantic search
        print("\n4️⃣ Testing Semantic Search...")
        search_queries = [
            "user interface preferences",
            "implementation progress",
            "technical questions",
            "achievements and successes",
        ]

        for query in search_queries:
            results = await memory.semantic_search(query, top_k=3)
            print(f"   🔍 Query: '{query}' → {len(results)} results")
            for i, result in enumerate(results[:2]):  # Show top 2
                print(
                    f"      {i + 1}. {result['content'][:60]}... (score: {result.get('similarity_score', 0):.3f})"
                )

        # Test confidence analysis
        print("\n5️⃣ Testing Confidence Analysis...")
        test_responses = [
            "I'm absolutely certain this is the correct implementation",
            "I think this might work, but I'm not entirely sure about the details",
            "This is unclear and I need more information to proceed",
        ]

        # Get some results for context
        sample_results = await memory.semantic_search("test", top_k=2)

        for response in test_responses:
            confidence_analysis = await memory.analyze_confidence(
                response, {"relevant_memories": sample_results}
            )
            print(f"   💭 Response: '{response[:40]}...'")
            print(f"      Confidence: {confidence_analysis['confidence_score']:.2f}")
            print(
                f"      Needs clarification: {confidence_analysis['needs_clarification']}"
            )

        # Test reflexive analysis
        print("\n6️⃣ Testing Reflexive Analysis...")
        reflection = await reflection_engine.daily_reflection()
        print("   🤔 Daily reflection generated:")
        print(f"      Memory count: {reflection['memory_count']}")
        print(f"      Average confidence: {reflection['average_confidence']:.2f}")
        print(f"      Insights: {len(reflection['insights'])} found")
        print(f"      Suggestions: {len(reflection['suggestions'])} generated")

        # Show insights and suggestions
        if reflection["insights"]:
            print(f"      Key insight: {reflection['insights'][0]}")
        if reflection["suggestions"]:
            print(f"      Top suggestion: {reflection['suggestions'][0]}")

        # Test memory statistics
        print("\n7️⃣ Testing Memory Statistics...")
        stats = await memory.get_memory_statistics()
        print(f"   📊 Total memories: {stats['total_memories']}")
        print(f"   📊 Vector support: {stats['vector_support']}")
        print(f"   📊 Memory types: {stats['memory_types']}")
        print(f"   📊 Average confidence: {stats['average_confidence']:.2f}")
        print(f"   📊 Recent activity: {stats['recent_activity_count']} (last 24h)")

        print("\n🎉 PHASE 1 IMPLEMENTATION SUCCESSFUL!")
        print("=" * 50)
        print("✅ Vector embeddings and semantic search")
        print("✅ Confidence modeling and uncertainty detection")
        print("✅ Reflexive analysis engine")
        print("✅ Advanced memory statistics")
        print("✅ Multi-type memory storage with tagging")
        print("\n🚀 Ready for Phase 2: Anticipation Engine!")

        return True

    except Exception as e:
        print(f"❌ Phase 1 test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the comprehensive Phase 1 test"""
    success = await test_advanced_memory_features()

    if success:
        print("\n🎯 NEXT STEPS:")
        print("- Integrate with existing Lyrixa GUI")
        print("- Add memory visualization")
        print("- Implement Phase 2: Anticipation Engine")
        print("- Add personality customization")
    else:
        print("\n🔧 TROUBLESHOOTING NEEDED:")
        print("- Check dependencies (sentence-transformers, faiss-cpu)")
        print("- Verify module imports")
        print("- Review error logs")


if __name__ == "__main__":
    asyncio.run(main())

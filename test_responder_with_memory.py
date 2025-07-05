"""
Test Knowledge Responder with Memory Storage
===========================================
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_with_stored_memories():
    """Test Knowledge Responder with actual stored memories."""
    print("🧪 Testing Knowledge Responder with stored memories...")

    try:
        from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
        from lyrixa.core.knowledge_responder import KnowledgeResponder

        # Create memory system
        memory = AdvancedMemorySystem()
        print("✅ Memory system created")

        # Store some test memories
        test_memories = [
            {
                "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
                "memory_type": "knowledge",
                "tags": ["python", "programming", "language"],
                "confidence": 0.9,
            },
            {
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
                "memory_type": "knowledge",
                "tags": ["machine learning", "AI", "data"],
                "confidence": 0.85,
            },
            {
                "content": "REST APIs (Representational State Transfer) are architectural style for designing networked applications, using standard HTTP methods like GET, POST, PUT, DELETE.",
                "memory_type": "knowledge",
                "tags": ["REST", "API", "web development"],
                "confidence": 0.8,
            },
        ]

        # Store memories
        for i, mem in enumerate(test_memories):
            try:
                memory_id = await memory.store_memory(
                    content=mem["content"],
                    memory_type=mem["memory_type"],
                    tags=mem["tags"],
                    confidence=mem["confidence"],
                )
                print(f"✅ Stored memory {i + 1}: {memory_id}")
            except Exception as e:
                print(f"⚠️ Error storing memory {i + 1}: {e}")

        # Create responder
        responder = KnowledgeResponder(memory)
        print("✅ Knowledge Responder created")

        # Test queries
        test_queries = [
            "What is Python?",
            "Tell me about machine learning",
            "How do REST APIs work?",
            "What is quantum computing?",  # Should have no results
        ]

        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            result = await responder.answer_question(
                query, context={"personality": "mentor", "tone_mode": "encouraging"}
            )

            print(f"📝 Response: {result['response'][:100]}...")
            print(f"📊 Confidence: {result['confidence']:.2f}")
            print(f"🎯 Quality: {result['quality']}")
            print(f"📚 Sources: {result['sources_count']}")

        print("\n✅ Full Knowledge Responder test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_with_stored_memories())
    print(
        f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Knowledge Responder with memory storage test"
    )

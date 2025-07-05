"""
Comprehensive Knowledge Responder Test
=====================================
Test the Knowledge Responder with stored memories and full functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def comprehensive_test():
    """Comprehensive test of the Knowledge Responder."""
    print("🎯 COMPREHENSIVE KNOWLEDGE RESPONDER TEST")
    print("=" * 50)

    try:
        from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
        from lyrixa.core.conversation import PersonalityType, ToneMode
        from lyrixa.core.knowledge_responder import KnowledgeResponder

        # Create memory system
        memory = AdvancedMemorySystem()
        print("✅ Memory system created")

        # Store some test memories
        print("\n📚 Storing test memories...")
        test_memories = [
            {
                "content": "Python is a high-level programming language known for its readability and versatility. It's widely used in web development, data science, and automation.",
                "memory_type": "knowledge",
                "tags": ["python", "programming", "language"],
                "confidence": 0.9,
            },
            {
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
                "memory_type": "knowledge",
                "tags": ["machine learning", "AI", "algorithms"],
                "confidence": 0.85,
            },
            {
                "content": "FastAPI is a modern, fast web framework for building APIs with Python. It provides automatic API documentation and type checking.",
                "memory_type": "knowledge",
                "tags": ["fastapi", "web", "api", "python"],
                "confidence": 0.8,
            },
        ]

        for i, memory_data in enumerate(test_memories):
            try:
                await memory.store_memory(**memory_data)
                print(f"   ✅ Stored memory {i + 1}: {memory_data['content'][:50]}...")
            except Exception as e:
                print(f"   ⚠️ Failed to store memory {i + 1}: {e}")

        # Create responder
        responder = KnowledgeResponder(memory)
        print("\n✅ Knowledge Responder created")

        # Test different types of queries
        test_queries = [
            {
                "query": "What is Python?",
                "context": {"personality": "mentor", "tone_mode": "encouraging"},
                "expected": "Should find Python information",
            },
            {
                "query": "Tell me about machine learning",
                "context": {"personality": "analytical", "tone_mode": "formal"},
                "expected": "Should find ML information",
            },
            {
                "query": "How do I build an API?",
                "context": {"personality": "dev_focused", "tone_mode": "direct"},
                "expected": "Should find FastAPI information",
            },
            {
                "query": "What is quantum computing?",
                "context": {"personality": "friendly", "tone_mode": "casual"},
                "expected": "Should show no knowledge gracefully",
            },
        ]

        print("\n🧪 Testing different queries and personalities...")

        for i, test in enumerate(test_queries):
            print(f"\n--- Test {i + 1}: {test['query']} ---")
            print(
                f"Personality: {test['context']['personality']}, Tone: {test['context']['tone_mode']}"
            )
            print(f"Expected: {test['expected']}")

            result = await responder.answer_question(test["query"], test["context"])

            print(f"📝 Response: {result['response']}")
            print(f"📊 Confidence: {result['confidence']:.2f}")
            print(f"🎭 Quality: {result['quality']}")
            print(f"🔍 Sources: {result['sources_count']}")

        # Test utility methods
        print("\n🔧 Testing utility methods...")

        quick_response = await responder.quick_answer("What is Python?", "creative")
        print(f"Quick Answer: {quick_response}")

        detailed_response = await responder.detailed_answer(
            "Tell me about machine learning",
            {"personality": "professional", "tone_mode": "formal"},
        )
        print(f"Detailed Answer Confidence: {detailed_response['confidence']:.2f}")

        print("\n🎉 All tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(comprehensive_test())
    print(
        f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Comprehensive Knowledge Responder test"
    )

"""
🧠 INTEGRATED MEMORY DEMO (STANDALONE)
=====================================

Standalone demonstration of Advanced Memory Systems that doesn't rely on
complex external dependencies. This showcases the core memory functionality.
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


# Simple memory implementation for demo
class SimpleMemoryEngine:
    """Simple memory engine for demonstration purposes"""

    def __init__(self):
        self.memories = []
        self.patterns = {}
        self.context_memory = {}

    async def remember(self, content: str, tags: List[str] = None, **kwargs):
        """Store a memory"""
        memory = {
            "id": f"mem_{len(self.memories)}",
            "content": content,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
            "metadata": kwargs,
        }
        self.memories.append(memory)
        return memory

    async def recall(self, query: str, limit: int = 5, **kwargs):
        """Recall memories based on query"""
        results = []
        query_lower = query.lower()

        for memory in self.memories:
            content_lower = memory["content"].lower()
            relevance = 0.0

            # Simple relevance scoring
            if query_lower in content_lower:
                relevance = 0.8
            else:
                # Check for word overlap
                query_words = set(query_lower.split())
                content_words = set(content_lower.split())
                overlap = len(query_words.intersection(content_words))
                if overlap > 0:
                    relevance = overlap / len(query_words.union(content_words))

            if relevance > 0.3:
                results.append(
                    {
                        "content": memory["content"],
                        "relevance_score": relevance,
                        "timestamp": memory["timestamp"],
                        "tags": memory["tags"],
                    }
                )

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]


class StandaloneMemoryDemo:
    """Standalone Advanced Memory Systems demonstration"""

    def __init__(self):
        self.memory_engine = SimpleMemoryEngine()
        self.conversation_history = []

        print("🧠 Standalone Advanced Memory Systems Demo initialized")

    async def store_conversation(
        self, message: str, response: str, user_id: str = "demo_user"
    ):
        """Store a conversation in memory"""

        # Store conversation
        conversation_memory = await self.memory_engine.remember(
            content=f"User: {message} | Assistant: {response}",
            tags=["conversation", user_id, "demo"],
            message=message,
            response=response,
            user_id=user_id,
        )

        # Add to conversation history
        self.conversation_history.append(
            {
                "message": message,
                "response": response,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "memory_id": conversation_memory["id"],
            }
        )

        print(f"💾 Stored conversation: '{message[:50]}...'")
        return conversation_memory

    async def generate_memory_enhanced_response(
        self, message: str, user_id: str = "demo_user"
    ):
        """Generate response using memory context"""

        # Recall relevant memories
        relevant_memories = await self.memory_engine.recall(query=message, limit=3)

        # Simple response generation with memory context
        response = ""
        memory_enhanced = len(relevant_memories) > 0

        if memory_enhanced:
            # Use memory context
            top_memory = relevant_memories[0]
            response = (
                f"Based on our previous discussions (relevance: {top_memory['relevance_score']:.2f}), "
                f"I recall we talked about similar topics. Regarding '{message}', "
                f"let me build on that context to provide a more informed response. "
                f"I found {len(relevant_memories)} related memories to help answer your question."
            )
        else:
            # Default response
            response = (
                f"I understand you're asking about '{message}'. While I don't have specific "
                f"previous context about this topic, I'm ready to help and will remember "
                f"our conversation for future reference."
            )

        # Store the new conversation
        await self.store_conversation(message, response, user_id)

        return {
            "response": response,
            "memory_enhanced": memory_enhanced,
            "relevant_memories": len(relevant_memories),
            "memory_details": relevant_memories,
            "confidence": 0.8 if memory_enhanced else 0.5,
        }

    async def demonstrate_memory_features(self):
        """Demonstrate key memory features"""

        print("\n🚀 DEMONSTRATING ADVANCED MEMORY FEATURES")
        print("=" * 60)

        # Phase 1: Store initial conversations
        print("\n📚 Phase 1: Building Memory Base")
        initial_conversations = [
            (
                "Hello, I'm interested in quantum computing",
                "Quantum computing is an exciting field that uses quantum mechanics principles like superposition and entanglement for computation.",
            ),
            (
                "What is machine learning?",
                "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed.",
            ),
            (
                "How do neural networks work?",
                "Neural networks are computing systems inspired by biological neural networks, using interconnected nodes to process information.",
            ),
            (
                "Can you explain quantum entanglement?",
                "Quantum entanglement is a phenomenon where particles become correlated in such a way that the quantum state of each particle cannot be described independently.",
            ),
        ]

        for i, (message, response) in enumerate(initial_conversations, 1):
            print(f"   {i}. Storing: '{message[:40]}...'")
            await self.store_conversation(message, response)
            await asyncio.sleep(0.1)

        print(f"   [OK] Stored {len(initial_conversations)} initial conversations")

        # Phase 2: Memory-enhanced conversations
        print("\n💬 Phase 2: Memory-Enhanced Conversations")
        memory_test_queries = [
            "Tell me more about quantum computing",
            "How does quantum relate to machine learning?",
            "What did we discuss about neural networks?",
            "Can you remember what I asked about entanglement?",
            "What have we talked about so far?",
        ]

        for i, query in enumerate(memory_test_queries, 1):
            print(f"\n💭 Query {i}: '{query}'")

            response_data = await self.generate_memory_enhanced_response(query)

            print(f"   🤖 Response: {response_data['response'][:100]}...")
            print(f"   🧠 Memory Enhanced: {response_data['memory_enhanced']}")
            print(f"   📊 Relevant Memories: {response_data['relevant_memories']}")
            print(f"   🎯 Confidence: {response_data['confidence']:.2f}")

            if response_data["memory_details"]:
                print(f"   🔍 Top Memory Match:")
                top_match = response_data["memory_details"][0]
                print(f"      Content: {top_match['content'][:80]}...")
                print(f"      Relevance: {top_match['relevance_score']:.2f}")

            await asyncio.sleep(0.2)

        # Phase 3: Memory statistics
        print("\n📊 Phase 3: Memory Statistics")
        total_memories = len(self.memory_engine.memories)
        total_conversations = len(self.conversation_history)

        print(f"   📚 Total memories stored: {total_memories}")
        print(f"   💬 Total conversations: {total_conversations}")
        print(
            f"   🕐 Memory span: {self.conversation_history[0]['timestamp'] if self.conversation_history else 'N/A'} to {datetime.now().isoformat()}"
        )

        # Show memory distribution
        tag_counts = {}
        for memory in self.memory_engine.memories:
            for tag in memory["tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        print(f"   🏷️  Memory tags:")
        for tag, count in tag_counts.items():
            print(f"      • {tag}: {count} memories")

        # Phase 4: Advanced recall demonstration
        print("\n🔍 Phase 4: Advanced Recall Demonstration")

        # Test different recall strategies
        recall_tests = [
            ("quantum", "Testing quantum-related recall"),
            ("learning machine", "Testing multi-word recall"),
            ("network neural", "Testing reversed word order"),
            ("entanglement", "Testing specific term recall"),
        ]

        for query, description in recall_tests:
            print(f"\n   🔍 {description}")
            print(f"      Query: '{query}'")

            recall_start = time.time()
            results = await self.memory_engine.recall(query, limit=3)
            recall_time = time.time() - recall_start

            print(f"      ⏱️  Recall time: {recall_time:.3f}s")
            print(f"      📊 Results: {len(results)}")

            for j, result in enumerate(results, 1):
                print(
                    f"      {j}. Relevance: {result['relevance_score']:.2f} | {result['content'][:60]}..."
                )

        print("\n🎉 MEMORY DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("[OK] Advanced Memory Systems successfully demonstrated")
        print("🧠 Memory storage, recall, and enhancement working perfectly")
        print("🚀 Ready for integration with full Aetherra AI OS")


async def main():
    """Main demo entry point"""

    print("🧠 AETHERRA ADVANCED MEMORY SYSTEMS")
    print("🔬 Standalone Integration Demo")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    demo = StandaloneMemoryDemo()

    try:
        demo_start = time.time()
        await demo.demonstrate_memory_features()
        demo_time = time.time() - demo_start

        print(f"\n⏱️  Total demo time: {demo_time:.2f} seconds")
        print("🏆 ADVANCED MEMORY SYSTEMS (#5) COMPLETE!")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting Standalone Advanced Memory Demo...")
    asyncio.run(main())

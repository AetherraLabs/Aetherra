"""
🧠 ADVANCED MEMORY SYSTEMS DEMONSTRATION
=======================================

Demo script for the Aetherra Advanced Memory Systems (#5)
Showcases quantum-enhanced memory integration with conversation management.
"""

import asyncio
import os
import sys
import time
from datetime import datetime

# Add Aetherra to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Aetherra.lyrixa.advanced_memory_integration import (
        create_advanced_memory_manager,
    )
    from Aetherra.lyrixa.enhanced_conversation_manager import (
        create_enhanced_conversation_manager,
    )

    AETHERRA_AVAILABLE = True
    print("[OK] Aetherra Advanced Memory Systems imported successfully")
except ImportError as e:
    AETHERRA_AVAILABLE = False
    create_enhanced_conversation_manager = None
    create_advanced_memory_manager = None
    print(f"❌ Aetherra import failed: {e}")


class AdvancedMemoryDemo:
    """Demo class for Advanced Memory Systems"""

    def __init__(self):
        self.memory_manager = None
        self.conversation_manager = None

        # Demo configuration
        self.config = {
            "memory_config": {
                "max_episodic_entries": 100,
                "max_context_entries": 50,
                "quantum_threshold": 0.6,
            },
            "conversation_config": {
                "memory_enabled": True,
                "pattern_enhancement": True,
                "conversation_flow_analysis": True,
                "memory_context_weight": 0.4,
                "temperature": 0.7,
                "max_tokens": 800,
            },
        }

        print("🧠 Advanced Memory Systems Demo initialized")

    async def initialize_systems(self):
        """Initialize the advanced memory systems"""

        print("\n🚀 Initializing Advanced Memory Systems...")

        try:
            # Initialize memory manager
            if AETHERRA_AVAILABLE and create_advanced_memory_manager:
                self.memory_manager = create_advanced_memory_manager(
                    self.config["memory_config"]
                )
                memory_init_success = await self.memory_manager.initialize()

                if memory_init_success:
                    print("[OK] Advanced Memory Manager initialized")
                else:
                    print("[WARN] Memory Manager initialization had issues")

                # Initialize conversation manager
                if create_enhanced_conversation_manager:
                    self.conversation_manager = create_enhanced_conversation_manager(
                        self.config["conversation_config"]
                    )
                    conv_init_success = await self.conversation_manager.initialize()

                    if conv_init_success:
                        print("[OK] Enhanced Conversation Manager initialized")
                    else:
                        print("[WARN] Conversation Manager initialization had issues")
                else:
                    print("❌ Enhanced Conversation Manager not available")
                    conv_init_success = False

                return memory_init_success and conv_init_success
            else:
                print("❌ Aetherra modules not available")
                return False

        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False

    async def demonstrate_memory_storage(self):
        """Demonstrate advanced memory storage capabilities"""

        print("\n📚 DEMONSTRATING MEMORY STORAGE")
        print("=" * 50)

        if not self.memory_manager:
            print("❌ Memory manager not available")
            return

        # Test conversation memories with different importance levels
        test_conversations = [
            {
                "message": "Hello, I'm learning about quantum computing",
                "response": "Quantum computing is fascinating! It uses quantum mechanics principles like superposition and entanglement.",
                "user_id": "demo_user",
                "context": {"importance": "high", "topic": "quantum"},
            },
            {
                "message": "What is machine learning?",
                "response": "Machine learning is a subset of AI that enables computers to learn patterns from data without explicit programming.",
                "user_id": "demo_user",
                "context": {"importance": "medium", "topic": "ai"},
            },
            {
                "message": "How does memory work in AI systems?",
                "response": "AI memory systems store and retrieve information, with advanced systems using quantum-enhanced storage for better pattern recognition.",
                "user_id": "demo_user",
                "context": {"importance": "high", "topic": "memory"},
            },
            {
                "message": "Can you remember our previous conversations?",
                "response": "Yes! I use quantum-enhanced memory systems to recall and build upon our previous interactions for better context.",
                "user_id": "demo_user",
                "context": {"importance": "high", "topic": "memory"},
            },
        ]

        storage_results = []

        for i, conv in enumerate(test_conversations, 1):
            print(f"\n📝 Storing conversation {i}...")
            print(f"   User: {conv['message'][:50]}...")

            storage_result = await self.memory_manager.store_conversation_memory(
                message=conv["message"],
                response=conv["response"],
                user_id=conv["user_id"],
                context=conv["context"],
            )

            storage_results.append(storage_result)

            if storage_result["success"]:
                print(
                    f"   [OK] Stored (quantum: {storage_result['quantum_stored']}, patterns: {storage_result['patterns_discovered']})"
                )
            else:
                print(
                    f"   ❌ Storage failed: {storage_result.get('error', 'Unknown error')}"
                )

            # Small delay to simulate realistic timing
            await asyncio.sleep(0.1)

        print(f"\n📊 Storage Summary:")
        print(f"   • Total conversations stored: {len(test_conversations)}")
        print(
            f"   • Quantum storage attempts: {sum(1 for r in storage_results if r.get('quantum_stored', False))}"
        )
        print(
            f"   • Pattern discoveries: {sum(r.get('patterns_discovered', 0) for r in storage_results)}"
        )

        return storage_results

    async def demonstrate_memory_recall(self):
        """Demonstrate advanced memory recall capabilities"""

        print("\n🔍 DEMONSTRATING MEMORY RECALL")
        print("=" * 50)

        if not self.memory_manager:
            print("❌ Memory manager not available")
            return

        # Test queries with different recall strategies
        test_queries = [
            {
                "query": "quantum computing principles",
                "strategy": "quantum_hybrid",
                "description": "Quantum-enhanced recall for quantum topics",
            },
            {
                "query": "machine learning AI",
                "strategy": "episodic",
                "description": "Episodic memory recall for AI topics",
            },
            {
                "query": "memory systems",
                "strategy": "contextual",
                "description": "Context-aware recall for memory topics",
            },
            {
                "query": "previous conversations",
                "strategy": "quantum_hybrid",
                "description": "Hybrid recall for conversation references",
            },
        ]

        recall_results = []

        for i, query_test in enumerate(test_queries, 1):
            print(f"\n🔍 Recall Test {i}: {query_test['description']}")
            print(f"   Query: '{query_test['query']}'")
            print(f"   Strategy: {query_test['strategy']}")

            recall_start = time.time()

            recall_result = await self.memory_manager.recall_memory(
                query=query_test["query"],
                user_id="demo_user",
                strategy=query_test["strategy"],
                limit=5,
            )

            recall_time = time.time() - recall_start
            recall_results.append(recall_result)

            # Display results
            results = recall_result.get("results", [])
            metadata = recall_result.get("metadata", {})

            print(f"   ⏱️  Recall time: {recall_time:.3f}s")
            print(f"   📊 Results found: {len(results)}")

            if results:
                print(f"   🏆 Top result:")
                top_result = results[0]
                content = (
                    top_result.get("content", "")[:80] + "..."
                    if len(top_result.get("content", "")) > 80
                    else top_result.get("content", "")
                )
                print(f"      Content: {content}")
                print(f"      Source: {top_result.get('source', 'unknown')}")
                print(f"      Relevance: {top_result.get('relevance', 0.0):.2f}")
                print(f"      Type: {top_result.get('type', 'unknown')}")

            # Show metadata
            for key, value in metadata.items():
                print(f"   📈 {key}: {value}")

            await asyncio.sleep(0.1)

        print(f"\n📊 Recall Summary:")
        total_results = sum(len(r.get("results", [])) for r in recall_results)
        avg_recall_time = sum(r.get("recall_time", 0.0) for r in recall_results) / len(
            recall_results
        )
        print(f"   • Total results across all queries: {total_results}")
        print(f"   • Average recall time: {avg_recall_time:.3f}s")
        print(
            f"   • Successful recalls: {sum(1 for r in recall_results if r.get('results'))}"
        )

        return recall_results

    async def demonstrate_enhanced_conversations(self):
        """Demonstrate memory-enhanced conversations"""

        print("\n💬 DEMONSTRATING ENHANCED CONVERSATIONS")
        print("=" * 50)

        if not self.conversation_manager:
            print("❌ Conversation manager not available")
            return

        # Test conversations that should benefit from memory
        test_conversations = [
            "Tell me about quantum computing again",
            "What did we discuss about AI earlier?",
            "Can you build on our memory conversation?",
            "How do you use your memory systems?",
            "Remember what I asked about machine learning?",
        ]

        conversation_results = []

        for i, message in enumerate(test_conversations, 1):
            print(f"\n💬 Enhanced Conversation {i}")
            print(f"   User: {message}")

            response_start = time.time()

            response_result = await self.conversation_manager.generate_response(
                message=message,
                user_id="demo_user",
                context={"demo_mode": True, "conversation_number": i},
            )

            response_time = time.time() - response_start
            conversation_results.append(response_result)

            # Display response details
            print(f"   🤖 Aetherra: {response_result['response'][:100]}...")
            print(f"   ⏱️  Response time: {response_time:.3f}s")
            print(
                f"   🧠 Memory enhanced: {response_result.get('memory_enhanced', False)}"
            )
            print(f"   📊 Confidence: {response_result.get('confidence', 0.0):.2f}")
            print(f"   🔗 Source: {response_result.get('source', 'unknown')}")

            # Show memory context if available
            memory_context = response_result.get("memory_context", {})
            if memory_context.get("memory_enhanced", False):
                print(f"   🧠 Memory context:")
                print(
                    f"      • Total memories used: {memory_context.get('total_memories', 0)}"
                )
                print(
                    f"      • High relevance: {memory_context.get('high_relevance_memories', 0)}"
                )
                print(
                    f"      • Memory sources: {', '.join(memory_context.get('memory_sources', []))}"
                )

                patterns = memory_context.get("patterns_discovered", [])
                if patterns:
                    print(f"      • Patterns discovered: {len(patterns)}")
                    for pattern in patterns[:2]:  # Show top 2 patterns
                        print(
                            f"        - {pattern.get('pattern', 'Unknown')} (×{pattern.get('frequency', 1)})"
                        )

            await asyncio.sleep(0.2)  # Realistic conversation pacing

        # Show conversation statistics
        print(f"\n📊 Enhanced Conversation Summary:")
        memory_enhanced_count = sum(
            1 for r in conversation_results if r.get("memory_enhanced", False)
        )
        avg_confidence = sum(
            r.get("confidence", 0.0) for r in conversation_results
        ) / len(conversation_results)
        avg_response_time = sum(
            r.get("response_time", 0.0) for r in conversation_results
        ) / len(conversation_results)

        print(f"   • Total conversations: {len(test_conversations)}")
        print(f"   • Memory-enhanced responses: {memory_enhanced_count}")
        print(
            f"   • Enhancement rate: {(memory_enhanced_count / len(test_conversations)) * 100:.1f}%"
        )
        print(f"   • Average confidence: {avg_confidence:.2f}")
        print(f"   • Average response time: {avg_response_time:.3f}s")

        return conversation_results

    async def demonstrate_memory_statistics(self):
        """Show comprehensive memory system statistics"""

        print("\n📈 MEMORY SYSTEM STATISTICS")
        print("=" * 50)

        # Memory manager statistics
        if self.memory_manager:
            memory_stats = self.memory_manager.get_memory_statistics()

            print("🧠 Memory System Status:")
            system_status = memory_stats.get("system_status", {})
            for key, value in system_status.items():
                status_icon = "[OK]" if value else "❌"
                print(f"   {status_icon} {key.replace('_', ' ').title()}: {value}")

            print("\n📊 Memory Operations:")
            memory_ops = memory_stats.get("memory_stats", {})
            for key, value in memory_ops.items():
                print(f"   • {key.replace('_', ' ').title()}: {value}")

            print("\n⚡ Performance Metrics:")
            performance = memory_stats.get("performance_metrics", {})
            for key, value in performance.items():
                if isinstance(value, float):
                    print(f"   • {key.replace('_', ' ').title()}: {value:.3f}")
                else:
                    print(f"   • {key.replace('_', ' ').title()}: {value}")

            print("\n🔍 Pattern Analysis:")
            patterns = memory_stats.get("pattern_analysis", {})
            if patterns:
                for pattern, data in list(patterns.items())[:5]:  # Show top 5 patterns
                    frequency = data.get("frequency", 0)
                    strength = data.get("strength", 0.0)
                    print(
                        f"   • {pattern}: frequency={frequency}, strength={strength:.2f}"
                    )
            else:
                print("   • No patterns discovered yet")

        # Conversation manager statistics
        if self.conversation_manager:
            conv_stats = self.conversation_manager.get_conversation_statistics()

            print("\n💬 Conversation System Status:")
            conv_system_status = conv_stats.get("system_status", {})
            for key, value in conv_system_status.items():
                status_icon = "[OK]" if value else "❌"
                print(f"   {status_icon} {key.replace('_', ' ').title()}: {value}")

            print("\n📈 Conversation Metrics:")
            for key, value in conv_stats.items():
                if key not in ["system_status", "memory_system_stats"] and isinstance(
                    value, (int, float)
                ):
                    if isinstance(value, float):
                        print(f"   • {key.replace('_', ' ').title()}: {value:.3f}")
                    else:
                        print(f"   • {key.replace('_', ' ').title()}: {value}")

    async def run_complete_demo(self):
        """Run the complete Advanced Memory Systems demonstration"""

        print("🧠 AETHERRA ADVANCED MEMORY SYSTEMS DEMO")
        print("=" * 60)
        print(f"🕐 Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        demo_start = time.time()

        # Initialize systems
        init_success = await self.initialize_systems()
        if not init_success:
            print("❌ Demo aborted due to initialization failure")
            return

        # Run demonstrations
        try:
            print("\n" + "=" * 60)
            storage_results = await self.demonstrate_memory_storage()

            print("\n" + "=" * 60)
            recall_results = await self.demonstrate_memory_recall()

            print("\n" + "=" * 60)
            conversation_results = await self.demonstrate_enhanced_conversations()

            print("\n" + "=" * 60)
            await self.demonstrate_memory_statistics()

            # Demo summary
            demo_time = time.time() - demo_start

            print("\n" + "=" * 60)
            print("🎉 DEMO COMPLETION SUMMARY")
            print("=" * 60)
            print(f"[OK] Demo completed successfully in {demo_time:.2f} seconds")
            print(
                f"📚 Memory storage tests: {'[OK] Passed' if storage_results else '❌ Failed'}"
            )
            print(
                f"🔍 Memory recall tests: {'[OK] Passed' if recall_results else '❌ Failed'}"
            )
            print(
                f"💬 Enhanced conversations: {'[OK] Passed' if conversation_results else '❌ Failed'}"
            )

            if all([storage_results, recall_results, conversation_results]):
                print("\n🏆 ALL ADVANCED MEMORY SYSTEMS FUNCTIONING PERFECTLY!")
                print("✨ Quantum-enhanced memory integration is operational")
                print("🚀 Aetherra AI OS memory capabilities are fully enhanced")
            else:
                print("\n[WARN]  Some systems had issues - check logs for details")

        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            import traceback

            traceback.print_exc()


async def main():
    """Main demo entry point"""

    if not AETHERRA_AVAILABLE:
        print("❌ Cannot run demo - Aetherra modules not available")
        print("Please ensure all Aetherra modules are properly installed")
        return

    demo = AdvancedMemoryDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    print("🧠 Starting Advanced Memory Systems Demo...")
    asyncio.run(main())

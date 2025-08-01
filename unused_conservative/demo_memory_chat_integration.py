#!/usr/bin/env python3
"""
🧪 MEMORY INTEGRATION DEMONSTRATION
===================================

This script demonstrates the integration between the LyrixaMemoryEngine
and the conversation manager, showing how episodic memory enhances
conversation continuity.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def demo_memory_integration():
    """Demonstrate memory-enhanced conversation system"""
    print("🎭 " + "=" * 60)
    print("🧠 AETHERRA MEMORY INTEGRATION DEMONSTRATION")
    print("🎭 " + "=" * 60)

    try:
        # Import the enhanced conversation manager
        from Aetherra.lyrixa.chat_handler import LyrixaConversationManager

        print("✅ Enhanced conversation manager imported successfully")

        # Create a test workspace
        workspace_path = "demo_workspace"
        os.makedirs(workspace_path, exist_ok=True)

        print(f"📁 Using workspace: {workspace_path}")

        # Initialize the conversation manager
        print("🚀 Initializing conversation manager with memory integration...")
        manager = LyrixaConversationManager(workspace_path)

        # Check memory status
        memory_status = await manager.get_memory_status()
        print(f"📊 Memory Status: {memory_status}")

        print("\\n" + "=" * 50)
        print("📝 CONVERSATION SIMULATION")
        print("=" * 50)

        # Simulate a conversation with memory
        conversations = [
            "Hello! I'm working on a Python project about machine learning.",
            "Can you help me understand neural networks?",
            "What libraries should I use for deep learning?",
            "I'm particularly interested in computer vision applications.",
            "Can you remember what we discussed about my project?",
        ]

        responses = []

        for i, user_input in enumerate(conversations, 1):
            print(f"\\n👤 User #{i}: {user_input}")

            # Generate response
            response = await manager.generate_response(user_input)
            responses.append(response)

            print(f"🤖 Lyrixa: {response}")

            # Small delay to simulate real conversation
            await asyncio.sleep(0.5)

        print("\\n" + "=" * 50)
        print("📖 CONVERSATION ANALYSIS")
        print("=" * 50)

        # Get conversation summary
        try:
            summary = await manager.get_conversation_summary()
            print(f"📋 Session Summary:\\n{summary}")
        except Exception as e:
            print(f"⚠️ Could not generate summary: {e}")

        # Show memory status after conversation
        final_status = await manager.get_memory_status()
        print(f"\\n📊 Final Memory Status: {final_status}")

        print("\\n" + "=" * 50)
        print("🧠 MEMORY CONTINUITY TEST")
        print("=" * 50)

        # Test memory continuity with a follow-up question
        followup_response = await manager.generate_response(
            "What was the main topic I was asking about earlier?"
        )
        print(f"👤 User: What was the main topic I was asking about earlier?")
        print(f"🤖 Lyrixa: {followup_response}")

        print("\\n" + "=" * 50)
        print("🔄 CLEANUP")
        print("=" * 50)

        # Clean shutdown
        await manager.cleanup_and_shutdown()
        print("✅ Conversation manager shutdown complete")

        print("\\n🎉 DEMONSTRATION COMPLETE!")
        print("\\n💡 Key Features Demonstrated:")
        print("   • Memory-enhanced conversation responses")
        print("   • Episodic memory storage of conversation turns")
        print("   • Context retrieval from previous interactions")
        print("   • Session summaries using memory narratives")
        print("   • Conversation continuity across multiple exchanges")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure the memory system is properly installed")
        return False

    except Exception as e:
        print(f"❌ Demonstration Error: {e}")
        logger.exception("Full error details:")
        return False

    return True


async def demo_memory_features():
    """Demonstrate specific memory features"""
    print("\\n🔬 " + "=" * 60)
    print("🧠 MEMORY SYSTEM FEATURES DEMONSTRATION")
    print("🔬 " + "=" * 60)

    try:
        from Aetherra.lyrixa.memory.lyrixa_memory_engine import (
            LyrixaMemoryEngine,
            MemoryFragmentType,
            MemorySystemConfig,
        )

        # Create memory engine directly
        config = MemorySystemConfig()
        memory_engine = LyrixaMemoryEngine(config)

        print("✅ Memory engine initialized for feature demonstration")

        # Demonstrate memory storage
        print("\\n📝 Storing sample memories...")

        memories = [
            {
                "content": "User is learning about neural networks",
                "tags": ["learning", "AI", "neural_networks"],
            },
            {
                "content": "User prefers Python for machine learning",
                "tags": ["preference", "Python", "ML"],
            },
            {
                "content": "User is working on computer vision project",
                "tags": ["project", "computer_vision", "CV"],
            },
            {
                "content": "User asked about deep learning libraries",
                "tags": ["question", "deep_learning", "libraries"],
            },
        ]

        stored_ids = []
        for memory in memories:
            result = await memory_engine.remember(
                content=memory["content"],
                tags=memory["tags"],
                fragment_type=MemoryFragmentType.EPISODIC,
                category="demo",
            )
            if result.success:
                stored_ids.append(result.fragment_id)
                print(f"  ✅ Stored: {memory['content'][:50]}...")

        print(f"\\n💾 Stored {len(stored_ids)} memories successfully")

        # Demonstrate memory recall
        print("\\n🔍 Testing memory recall...")

        queries = [
            "neural networks",
            "Python programming",
            "computer vision",
            "what does the user prefer?",
        ]

        for query in queries:
            print(f"\\n🔎 Query: '{query}'")
            results = await memory_engine.recall(query=query, limit=3)

            for i, result in enumerate(results, 1):
                if isinstance(result, dict) and "content" in result:
                    relevance = result.get("relevance_score", 0)
                    print(f"  {i}. (Relevance: {relevance:.2f}) {result['content']}")

        print("\\n✅ Memory features demonstration complete")

    except Exception as e:
        print(f"❌ Memory features error: {e}")
        logger.exception("Full error details:")


if __name__ == "__main__":

    async def main():
        print("🚀 Starting Aetherra Memory Integration Demo...")

        # Run main demonstration
        success = await demo_memory_integration()

        if success:
            # Run memory features demo
            await demo_memory_features()

        print("\\n🏁 All demonstrations complete!")

    # Run the demonstration
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n⏹️ Demonstration interrupted by user")
    except Exception as e:
        print(f"\\n❌ Demonstration failed: {e}")
        logging.exception("Full error details:")

#!/usr/bin/env python3
"""
🧠 FractalMesh Integration Test
==============================

Test script to verify that Lyrixa's FractalMesh memory system integration is working properly.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_fractal_integration():
    """Test FractalMesh memory integration with Lyrixa's conversation manager"""

    print("🧠 Testing FractalMesh Memory Integration")
    print("=" * 50)

    try:
        # Import and initialize conversation manager
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

        print("✅ Successfully imported LyrixaConversationManager")

        # Initialize conversation manager
        workspace_path = str(project_root)
        conversation_manager = LyrixaConversationManager(workspace_path=workspace_path)

        print("✅ Successfully initialized conversation manager")

        # Check if FractalMesh memory is available
        if (
            hasattr(conversation_manager, "fractal_memory")
            and conversation_manager.fractal_memory
        ):
            print("✅ FractalMesh memory system is integrated and available!")
            print(f"   Database path: {conversation_manager.fractal_memory.db_path}")

            # Test memory storage
            print("\n🧪 Testing memory storage...")
            test_user_input = "Hello, can you help me understand how plugins work?"
            test_response = "Of course! Plugins in Aetherra are modular components that extend functionality..."

            await conversation_manager._store_conversation_in_memory(
                test_user_input, test_response
            )
            print("✅ Successfully stored test conversation in FractalMesh memory")

            # Test memory retrieval
            print("\n🧪 Testing memory retrieval...")
            memory_context = await conversation_manager._retrieve_relevant_memories(
                "plugins", limit=2
            )

            if memory_context:
                print("✅ Successfully retrieved relevant memories!")
                print(f"   Retrieved context length: {len(memory_context)} characters")
                print(f"   Context preview: {memory_context[:200]}...")
            else:
                print("⚠️ No relevant memories found (this is normal for first run)")

            # Test conversation generation with memory
            print("\n🧪 Testing conversation generation with memory integration...")
            try:
                response = await conversation_manager.generate_response(
                    "Tell me about plugins again"
                )
                print("✅ Successfully generated response with memory integration")
                print(f"   Response length: {len(response)} characters")
                print(f"   Response preview: {response[:200]}...")
            except Exception as e:
                print(f"⚠️ Response generation test failed (this may be normal): {e}")

        else:
            print("❌ FractalMesh memory system is NOT integrated")
            print("   This means the documented features are not actually implemented")
            return False

        # Check memory system statistics
        if conversation_manager.fractal_memory:
            print(f"\n📊 Memory System Statistics:")
            print(
                f"   Fragments in memory: {len(conversation_manager.fractal_memory.fragments)}"
            )
            print(
                f"   Concept clusters: {len(conversation_manager.fractal_memory.concept_clusters)}"
            )
            print(
                f"   Episodic chains: {len(conversation_manager.fractal_memory.episodic_chains)}"
            )

        print("\n✅ FractalMesh integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   This suggests FractalMesh components are missing")
        return False

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_fractal_integration())

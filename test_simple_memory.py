#!/usr/bin/env python3
"""
Simple test for Advanced Memory System
"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def main():
    """Test the advanced memory system"""
    print("🧠 Testing Advanced Memory System (Async)...")

    try:
        print("📁 Adding project path:", str(project_root))
        print("🔍 Checking if lyrixa module exists...")

        # Try to import step by step
        import lyrixa

        print("✅ lyrixa imported successfully")

        from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem

        print("✅ AdvancedMemorySystem imported successfully")

        # Test creating an instance
        memory = AdvancedMemorySystem()
        print("✅ AdvancedMemorySystem instantiated successfully")

        # Test storing a memory
        memory_id = await memory.store_memory(
            content="This is a test memory for Phase 1 implementation",
            memory_type="test",
            tags=["phase1", "testing"],
            confidence=0.9,
        )
        print(f"✅ Memory stored with ID: {memory_id}")

        # Test searching (async)
        results = await memory.semantic_search("test memory phase")
        print(f"✅ Semantic search returned {len(results)} results")

        # Test getting statistics
        stats = await memory.get_memory_statistics()
        print(f"✅ Memory statistics: {stats}")

        print("\n🎉 Phase 1 Advanced Memory System is working!")

    except Exception as e:
        print(f"❌ Error testing memory system: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Detailed memory system test to find the exact issue
"""

import asyncio
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lyrixa"))


async def test_memory_system_detailed():
    """Test memory system with detailed debugging"""
    print("🧠 Testing memory system with detailed output...")

    try:
        from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem

        print("   [DISC] Imported LyrixaEnhancedMemorySystem successfully")

        # Create memory system
        memory_system = LyrixaEnhancedMemorySystem(
            memory_db_path="test_memory_detailed.db"
        )
        print("   🏗️ Created memory system instance")

        # Test basic functionality
        print("   💾 Storing test memory...")
        await memory_system.store_enhanced_memory(
            content={"test": "memory"},
            context={"test_session": True},
            tags=["test", "plugin_chain"],
            importance=0.5,
        )
        print("   ✅ Memory stored successfully")

        # Test get_memories_by_tags (this was failing before)
        print("   🔍 Testing get_memories_by_tags...")
        memories = await memory_system.get_memories_by_tags(["test"], limit=5)
        print(f"   ✅ Retrieved {len(memories)} memories by tags")

        # Test search memories
        print("   🔍 Testing search_memories...")
        search_results = await memory_system.search_memories("test", limit=5)
        print(f"   ✅ Found {len(search_results)} memories through search")

        # Clean up test database
        try:
            os.remove("test_memory_detailed.db")
            print("   🧹 Cleaned up test database")
        except Exception as e:
            print(f"   ⚠️ Could not clean up database: {e}")

        print("✅ Memory system test passed!")
        return True

    except Exception as e:
        print(f"❌ Memory system test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_memory_system_detailed())

#!/usr/bin/env python3
"""
[TOOL] SIMPLE MEMORY ENGINE TEST
============================

Direct test of the LyrixaMemoryEngine to isolate any issues.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


async def test_memory_engine():
    """Test the memory engine directly"""
    print("[TOOL] SIMPLE MEMORY ENGINE TEST")
    print("=" * 35)

    try:
        # Import and test the memory engine directly
        from Aetherra.lyrixa.memory.fractal_mesh.base import MemoryFragmentType
        from Aetherra.lyrixa.memory.lyrixa_memory_engine import (
            LyrixaMemoryEngine,
            MemorySystemConfig,
        )

        print("✅ Imports successful")

        # Initialize memory engine
        print("🔄 Initializing memory engine...")
        config = MemorySystemConfig()
        engine = LyrixaMemoryEngine(config)

        print("✅ Memory engine initialized")

        # Test storing a simple memory
        print("💾 Testing memory storage...")
        result = await engine.remember(
            content="This is a test memory from the migration test",
            tags=["test", "migration"],
            category="test",
            fragment_type=MemoryFragmentType.SEMANTIC,
            narrative_role="test_data",
        )

        print(f"📊 Memory storage result:")
        print(f"   Success: {result.success}")
        print(f"   Operation: {result.operation_type}")
        print(f"   Fragment ID: {result.fragment_id}")
        print(f"   Message: {result.message}")

        if result.success:
            print("✅ Memory storage test passed!")

            # Test retrieval
            print("🔍 Testing memory recall...")
            recalled = await engine.recall("test memory")
            print(f"   Recalled {len(recalled)} memories")

            return True
        else:
            print("[ERROR] Memory storage failed!")
            return False

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("💡 The memory system modules may not be available")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_memory_engine())
    if success:
        print("🎉 Memory engine is working!")
    else:
        print("[WARN] Memory engine needs fixing")

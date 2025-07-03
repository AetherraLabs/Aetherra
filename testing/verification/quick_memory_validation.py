#!/usr/bin/env python3
"""
Quick validation script for the modular memory system
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("🧪 Quick Memory System Validation")
    print("=" * 40)

    try:
        # Test 1: Basic memory import and operation
        print("1. Testing basic memory import...")
        from core.aetherra_memory import AetherraMemory

        memory = AetherraMemory()
        memory.remember("Validation test", ["test"], "validation")
        results = memory.recall()
        assert len(results) >= 1
        print("   ✅ Basic memory works")

        # Test 2: Modular interface
        print("2. Testing modular interface...")
        from core.memory import BasicMemory, UnifiedMemoryInterface

        basic = BasicMemory()
        basic.remember("Modular test", ["modular"], "test")
        assert len(basic.recall()) >= 1
        print("   ✅ Modular interface works")

        # Test 3: Unified interface
        print("3. Testing unified interface...")
        unified = UnifiedMemoryInterface()
        unified.remember("Unified test", ["unified"], "test")
        stats = unified.get_memory_stats()
        assert "basic_memory" in stats
        print("   ✅ Unified interface works")

        # Test 4: Vector memory (if available)
        print("4. Testing vector memory...")
        from core.memory import VectorMemory

        vector = VectorMemory()
        result = vector.remember("Vector test content", ["vector"], "test")
        assert result["status"] == "success"
        print("   ✅ Vector memory works")

        print()
        print("🎉 All validation tests passed!")
        print("✅ Memory modularization is complete and functional")
        return True

    except Exception as e:
        print(f"   ❌ Validation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

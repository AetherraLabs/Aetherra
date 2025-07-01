#!/usr/bin/env python3
"""
Simple validation script for the modular memory system
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("Memory System Validation")
    print("=" * 30)

    try:
        # Test 1: Basic memory import and operation
        print("1. Testing basic memory...")
        from core.memory import NeuroMemory

        memory = NeuroMemory()
        memory.remember("Validation test", ["test"], "validation")
        results = memory.recall()
        assert len(results) >= 1
        print("   PASS - Basic memory works")

        # Test 2: Modular interface
        print("2. Testing modular interface...")
        from core.memory import BasicMemory

        basic = BasicMemory()
        basic.remember("Modular test", ["modular"], "test")
        assert len(basic.recall()) >= 1
        print("   PASS - Modular interface works")

        # Test 3: Memory models
        print("3. Testing memory models...")
        from core.memory.models import MemoryEntry

        entry = MemoryEntry(text="Test", tags=["test"], category="validation")
        data = entry.to_dict()
        entry2 = MemoryEntry.from_dict(data)
        assert entry2.text == entry.text
        print("   PASS - Memory models work")

        print()
        print("SUCCESS: All validation tests passed!")
        print("Memory modularization is complete and functional")
        return True

    except Exception as e:
        print(f"   FAIL - Validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

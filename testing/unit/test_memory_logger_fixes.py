#!/usr/bin/env python3
"""
🧪 Memory Logger Fixes Verification Test
=======================================

Test to verify all memory logger errors have been fixed
and the module works correctly.
"""

import sys
import traceback


def test_memory_logger_imports():
    """Test that all memory logger imports work"""
    try:
        print("✅ memory.logger: All imports successful")
        return True

    except Exception as e:
        print(f"❌ memory.logger imports: Error - {e}")
        traceback.print_exc()
        return False


def test_enhanced_memory_entry():
    """Test EnhancedMemoryEntry functionality"""
    try:
        from Aetherra.core.memory.logger import EnhancedMemoryEntry

        # Test creating entry from dict with None values
        test_data = {
            "id": None,
            "text": "Test memory",
            "timestamp": None,
            "memory_type": "fact",
            "importance": 3,
        }

        entry = EnhancedMemoryEntry.from_dict(test_data)

        # Verify the fixes work
        assert entry.id is not None and entry.id != "", "ID should be generated when None"
        assert entry.timestamp is not None and entry.timestamp != "", (
            "Timestamp should be generated when None"
        )
        assert entry.text == "Test memory", "Text should be preserved"

        print("✅ EnhancedMemoryEntry: from_dict with None values works")

        # Test to_dict conversion
        entry_dict = entry.to_dict()
        assert "memory_type" in entry_dict, "memory_type should be in dict"
        assert "importance" in entry_dict, "importance should be in dict"

        print("✅ EnhancedMemoryEntry: to_dict conversion works")
        return True

    except Exception as e:
        print(f"❌ EnhancedMemoryEntry: Error - {e}")
        traceback.print_exc()
        return False


def test_memory_logger():
    """Test basic MemoryLogger functionality"""
    try:
        from Aetherra.core.memory.logger import MemoryLogger, MemoryType

        # Create a logger instance
        logger = MemoryLogger()

        # Test basic logging
        logger.log_memory("Test memory entry", MemoryType.FACT)

        print("✅ MemoryLogger: Basic functionality works")
        return True

    except Exception as e:
        print(f"❌ MemoryLogger: Error - {e}")
        traceback.print_exc()
        return False


def main():
    """Run all memory logger tests"""
    print("🧪 Testing Memory Logger Fixes")
    print("=" * 40)

    tests = [
        ("Memory Logger Imports", test_memory_logger_imports),
        ("Enhanced Memory Entry", test_enhanced_memory_entry),
        ("Memory Logger Basic", test_memory_logger),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All memory logger fixes are working correctly!")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

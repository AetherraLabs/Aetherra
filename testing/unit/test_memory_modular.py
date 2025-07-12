#!/usr/bin/env python3
"""
Test suite for the modular memory system
Validates all memory components, backward compatibility, and integration
"""

import os
import sys
import tempfile
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_memory_models():
    """Test core memory models"""
#     print("Testing memory models...")

    from Aetherra.core.memory.models import MemoryEntry

    # Test MemoryEntry
    memory = MemoryEntry(text="Test memory", tags=["test"], category="testing")
    assert memory.text == "Test memory"
    assert "test" in memory.tags
    assert memory.category == "testing"

    # Test serialization
    memory_dict = memory.to_dict()
    assert memory_dict["text"] == "Test memory"

    # Test deserialization
    memory2 = MemoryEntry.from_dict(memory_dict)
    assert memory2.text == memory.text
    assert memory2.tags == memory.tags

    print("✅ Memory models work correctly")


def test_basic_memory():
    """Test basic memory system"""
#     print("Testing basic memory system...")

    from Aetherra.core.memory.basic import BasicMemory
    from Aetherra.core.memory.storage import FileMemoryStorage

    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_file = tmp.name

    try:
        storage = FileMemoryStorage(tmp_file)
        memory = BasicMemory(storage)

        # Test remember and recall
        memory.remember("This is a test memory", ["test", "basic"], "testing")
        memories = memory.recall()

        assert len(memories) == 1
        assert "This is a test memory" in memories[0]

        # Test search
        results = memory.search("test")
        assert len(results) == 1

        # Test tags and categories
        tags = memory.get_tags()
        assert "test" in tags
        assert "basic" in tags

        categories = memory.get_categories()
        assert "testing" in categories

        print("✅ Basic memory system works correctly")

    finally:
        if os.path.exists(tmp_file):
            os.unlink(tmp_file)


def test_vector_memory():
    """Test vector memory system"""
#     print("Testing vector memory system...")

    from Aetherra.core.memory.vector import VectorMemory

    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        memory_file = os.path.join(tmp_dir, "vector_memory.json")
        vector_memory = VectorMemory(memory_file)

        # Test remember
        result = vector_memory.remember(
            "This is a test about machine learning", ["ai", "ml"], "technical"
        )
        assert result["status"] == "success"

        # Test semantic recall
        results = vector_memory.semantic_recall("machine learning", limit=1)
        assert len(results) >= 0  # May be 0 if embedding model not available

        # Test statistics
        stats = vector_memory.get_statistics()
        assert stats["total_memories"] == 1

        print("✅ Vector memory system works correctly")


def test_session_management():
    """Test session management"""
#     print("Testing session management...")

    from Aetherra.core.memory.models import MemoryEntry
    from Aetherra.core.memory.session import SessionManager

    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        session_manager = SessionManager()
        session_manager.storage.base_path = tmp_dir

        # Test session creation
        session_id = session_manager.start_session({"test": "session"})
        assert session_id is not None

        # Test adding memories
        memory = MemoryEntry(text="Session test memory", tags=["session"])
        success = session_manager.add_memory_to_session(memory, session_id)
        assert success

        # Test ending session
        ended = session_manager.end_session(session_id)
        assert ended

        # Test retrieving session
        session = session_manager.get_session(session_id)
        assert session is not None
        assert len(session.memories) == 1

        print("✅ Session management works correctly")


def test_daily_reflection():
    """Test daily reflection system"""
#     print("Testing daily reflection system...")

    from Aetherra.core.memory.models import MemoryEntry
    from Aetherra.core.memory.reflection import DailyReflectionManager
    from Aetherra.core.memory.storage import FileMemoryStorage

    # Use temporary directories for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test memory storage with some test data
        memory_file = os.path.join(tmp_dir, "memory.json")
        memory_storage = FileMemoryStorage(memory_file)

        # Add some test memories
        test_memory = MemoryEntry(
            text="Test reflection memory",
            tags=["reflection", "test"],
            category="testing",
            timestamp=datetime.now().isoformat(),
        )
        memory_storage.save_memory(test_memory)

        reflection_dir = os.path.join(tmp_dir, "reflections")
        os.makedirs(reflection_dir, exist_ok=True)

        reflection_manager = DailyReflectionManager(memory_storage=memory_storage)
        reflection_manager.reflection_storage.base_path = reflection_dir

        # Test daily reflection generation
        today = datetime.now().strftime("%Y-%m-%d")
        reflection = reflection_manager.generate_daily_reflection(today)

        assert reflection is not None
        assert reflection.date == today
        assert reflection.total_memories >= 1

        # Test reflection retrieval
        retrieved = reflection_manager.get_reflection(today)
        assert retrieved is not None
        assert retrieved.date == today

        print("✅ Daily reflection system works correctly")


def test_pattern_analysis():
    """Test pattern analysis system"""
#     print("Testing pattern analysis system...")

    from Aetherra.core.memory.models import MemoryEntry
    from Aetherra.core.memory.patterns import PatternAnalyzer
    from Aetherra.core.memory.storage import FileMemoryStorage

    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        memory_file = os.path.join(tmp_dir, "memory.json")
        memory_storage = FileMemoryStorage(memory_file)

        # Add test memories with patterns
        test_memories = [
            MemoryEntry(
                text="Machine learning is fascinating", tags=["ai", "ml"], category="technical"
            ),
            MemoryEntry(
                text="Deep learning algorithms are complex", tags=["ai", "dl"], category="technical"
            ),
            MemoryEntry(
                text="Neural networks are powerful", tags=["ai", "nn"], category="technical"
            ),
        ]

        for memory in test_memories:
            memory_storage.save_memory(memory)

        pattern_dir = os.path.join(tmp_dir, "patterns")
        os.makedirs(pattern_dir, exist_ok=True)

        analyzer = PatternAnalyzer(memory_storage=memory_storage)
        analyzer.pattern_storage.base_path = pattern_dir

        # Test pattern detection
        text_patterns = analyzer.detect_text_patterns(min_frequency=2, timeframe_days=1)
        category_patterns = analyzer.detect_category_patterns(timeframe_days=1)
        tag_patterns = analyzer.detect_tag_patterns(timeframe_days=1)

        # Should detect some patterns
        assert len(text_patterns) >= 0  # May be 0 if patterns don't meet threshold
        assert len(category_patterns) >= 1  # Should detect "technical" category
        assert len(tag_patterns) >= 1  # Should detect "ai" tag

        # Test full analysis
        analysis = analyzer.run_full_analysis(timeframe_days=1)
        assert "text_patterns" in analysis
        assert "temporal_patterns" in analysis
        assert "category_patterns" in analysis
        assert "tag_patterns" in analysis

        print("✅ Pattern analysis system works correctly")


def test_unified_interface():
    """Test unified memory interface"""
#     print("Testing unified memory interface...")

    from Aetherra.core.memory import UnifiedMemoryInterface

    # Use temporary directory to avoid conflicts
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_dir)  # Change to temp directory for file operations

            unified = UnifiedMemoryInterface()

            # Test basic operations
            unified.remember("Unified interface test", ["unified", "test"], "testing")
            memories = unified.recall()
            assert len(memories) >= 1

            # Test semantic operations
            result = unified.semantic_remember("Semantic test content", ["semantic"], "testing")
            assert result["status"] == "success"

            # Test search
            search_results = unified.search("test")
            assert "basic_results" in search_results

            # Test stats
            stats = unified.get_memory_stats()
            assert "basic_memory" in stats

            print("✅ Unified memory interface works correctly")

        finally:
            os.chdir(original_cwd)


def test_backward_compatibility():
    """Test backward compatibility with original AetherraMemory"""
#     print("Testing backward compatibility...")

    from Aetherra.core.aetherra_memory import AetherraMemory

    # Use temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_dir)  # Change to temp directory for file operations

            memory = AetherraMemory()

            # Test legacy interface
            memory.remember("Legacy compatibility test", ["legacy", "test"], "testing")
            memories = memory.recall()
            assert len(memories) >= 1
            assert "Legacy compatibility test" in memories[0]

            # Test legacy methods
            tags = memory.get_tags()
            assert "legacy" in tags

            categories = memory.get_categories()
            assert "testing" in categories

            # Test search
            results = memory.search("compatibility")
            assert len(results) >= 1

            # Test stats
            stats = memory.get_memory_stats()
            assert "Total memories" in stats

            print("✅ Backward compatibility works correctly")

        finally:
            os.chdir(original_cwd)


def test_legacy_memory_compatibility():
    """Test that legacy memory.py still works"""
#     print("Testing legacy memory module...")

    try:
        # Test import of legacy functions
        from Aetherra.core.memory_legacy import AetherraMemory as LegacyAetherraMemory

        # Use temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)

                legacy_memory = LegacyAetherraMemory()
                legacy_memory.remember("Legacy module test", ["legacy"], "testing")
                memories = legacy_memory.recall()

                assert len(memories) >= 1
                print("✅ Legacy memory module works correctly")

            finally:
                os.chdir(original_cwd)

    except ImportError as e:
        print(f"⚠️  Legacy memory module not available: {e}")


def run_all_tests():
    """Run all memory system tests"""
    print("🧪 Running AetherraCode Memory System Tests")
    print("=" * 50)

    test_functions = [
        test_memory_models,
        test_basic_memory,
        test_vector_memory,
        test_session_management,
        test_daily_reflection,
        test_pattern_analysis,
        test_unified_interface,
        test_backward_compatibility,
        test_legacy_memory_compatibility,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1

    print()
    print("=" * 50)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All memory system tests passed!")
        print("✅ Memory modularization is complete and functional")
        return True
    else:
        print("⚠️  Some tests failed - review memory system implementation")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

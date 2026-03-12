"""Standalone tests for Phase 4 memory-engine enhancement slice.

Run with:
    python test_phase4_memory_engine_enhancement_standalone.py
"""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timedelta
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngine


class _DummyBackend:
    def store(self, payload):
        return True

    def retrieve(self, query, context=None):
        return []


class TestMemoryEngineEnhancement(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = AetherraMemoryEngine()
        # Isolate tests from heavy backend behavior.
        engine_any: Any = self.engine
        engine_any.engine = _DummyBackend()

    def test_store_accepts_text_and_metadata(self):
        self.engine.store("alpha memory", metadata={"tag": "alpha"})
        rows = self.engine.retrieve("alpha")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["content"], "alpha memory")
        self.assertEqual(rows[0]["metadata"]["tag"], "alpha")

    def test_recall_prefers_better_semantic_match(self):
        self.engine.store({"content": "deploy service to production", "metadata": {}})
        self.engine.store({"content": "write docs for feature", "metadata": {}})
        ranked = self.engine.recall("deploy production", limit=2)
        self.assertEqual(ranked[0]["content"], "deploy service to production")
        self.assertGreaterEqual(ranked[0]["score"], ranked[1]["score"])

    def test_retrieve_honors_limit_from_context(self):
        for i in range(5):
            self.engine.store({"content": f"entry {i} build", "metadata": {}})
        rows = self.engine.retrieve("entry", context={"limit": 2})
        self.assertEqual(len(rows), 2)

    def test_consolidate_merges_similar_rows(self):
        self.engine.store({"content": "optimize query planner", "metadata": {"a": 1}})
        self.engine.store({"content": "optimize planner query", "metadata": {"b": 2}})
        before = len(self.engine._compat_mem)
        result = self.engine.consolidate(similarity_threshold=0.4)
        after = len(self.engine._compat_mem)

        self.assertEqual(before, 2)
        self.assertEqual(result["merged"], 1)
        self.assertEqual(after, 1)
        self.assertIn("consolidated_count", self.engine._compat_mem[0]["metadata"])

    def test_apply_decay_reduces_old_importance(self):
        old_ts = (datetime.utcnow() - timedelta(days=30)).isoformat()
        self.engine.store(
            {
                "content": "old memory",
                "importance": 0.9,
                "metadata": {"created_at": old_ts},
            }
        )
        before = self.engine._compat_mem[0]["importance"]
        updated = self.engine.apply_decay(half_life_hours=24 * 7)
        after = self.engine._compat_mem[0]["importance"]

        self.assertEqual(updated, 1)
        self.assertLess(after, before)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestMemoryEngineEnhancement
    )
    total = suite.countTestCases()
    print(f"Running {total} phase-4 memory-engine enhancement tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)

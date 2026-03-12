"""Standalone acceptance tests for Production Roadmap Phase 2a reflector gates.

Run with:
    python test_phase2a_reflector_acceptance_standalone.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from datetime import UTC, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.aetherra_core.kernel.reflector import MemoryReflector
from Aetherra.aetherra_core.memory.fractal_mesh.base import (
    ConceptCluster,
    MemoryFragment,
    MemoryFragmentType,
)
from Aetherra.plugins.reflector import ReflectorPlugin


class TestPhase2AReflectorAcceptance(unittest.TestCase):
    def _fragment(self, idx: int, concept: str, confidence: float, hour_offset: int = 0) -> MemoryFragment:
        created = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hour_offset)
        return MemoryFragment(
            fragment_id=f"frag-{idx}",
            content={"text": f"event {idx}", "idx": idx},
            fragment_type=MemoryFragmentType.SEMANTIC,
            temporal_tags={"hour": created.hour},
            symbolic_tags={concept, "phase2a"},
            associative_links=[],
            confidence_score=confidence,
            access_pattern={"count": 1},
            narrative_role="observation",
            created_at=created,
            last_evolved=created,
        )

    def _cluster(self, concept: str, members: set[str]) -> ConceptCluster:
        now = datetime.now(UTC).replace(tzinfo=None)
        return ConceptCluster(
            cluster_id=f"cluster-{concept}",
            central_concept=concept,
            related_concepts={"phase2a", "analysis"},
            member_fragments=members,
            cluster_strength=0.8,
            temporal_evolution=[(now, 0.8)],
            narrative_themes=["roadmap", "reflection"],
        )

    def test_kernel_reflector_time_range_analysis_returns_insights(self):
        with tempfile.TemporaryDirectory() as td:
            reflector = MemoryReflector(os.path.join(td, "phase2a_reflector.db"))
            fragments = [
                self._fragment(i, "governance", 0.45 + (i * 0.03), hour_offset=48 - i)
                for i in range(12)
            ]
            start = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=7)
            end = datetime.now(UTC).replace(tzinfo=None)

            insights = reflector.reflect_on_past_range(fragments, (start, end))

            self.assertIsInstance(insights, list)
            self.assertTrue(reflector.reflection_sessions)

    def test_kernel_reflector_compatibility_shims_work(self):
        with tempfile.TemporaryDirectory() as td:
            reflector = MemoryReflector(os.path.join(td, "phase2a_reflector_compat.db"))
            fragments = [self._fragment(i, "integration", 0.6, hour_offset=i) for i in range(5)]
            cluster = self._cluster("integration", {f.fragment_id for f in fragments})

            contradictions = reflector.analyze_contradictions(fragments, context=[cluster])
            connections = reflector.explore_concept_connections(fragments, None)

            self.assertIsInstance(contradictions, list)
            self.assertIsInstance(connections, list)

    def test_plugin_reflector_analysis_latency_under_100ms(self):
        plugin = ReflectorPlugin()
        for i in range(300):
            plugin.log_action(
                "analyze",
                {
                    "success": True,
                    "context": "repo",
                    "complexity": "medium",
                    "iteration": i,
                },
            )

        start = time.perf_counter()
        report = plugin.analyze_behavior("phase2a-acceptance")
        elapsed = time.perf_counter() - start

        self.assertIn("patterns", report)
        self.assertIn("efficiency_metrics", report)
        self.assertLess(elapsed, 0.1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase2AReflectorAcceptance)
    total = suite.countTestCases()
    print(f"Running {total} phase-2a reflector acceptance tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)

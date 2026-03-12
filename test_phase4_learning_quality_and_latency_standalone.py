"""Standalone tests for Phase 4 learning quality and latency checkpoints.

Run with:
    python test_phase4_learning_quality_and_latency_standalone.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngine
from Aetherra.consciousness.decision_engine import Decision
from Aetherra.consciousness.learning_loop import LearningLoop
from Aetherra.plugins.reflector import ReflectorPlugin


class _DummyBackend:
    def store(self, payload):
        return True

    def retrieve(self, query, context=None):
        return []


class _FakeEpisode:
    def __init__(self, payload):
        self.id = payload["id"]
        self.type = payload["type"]
        self.content = payload["content"]
        self.raw = payload.get("raw", {})
        self.ts = payload["ts"]


class _FakeStore:
    def __init__(self):
        self.events = []

    def new_event(self, **kwargs):
        payload = dict(kwargs)
        payload.setdefault("id", f"evt-{len(self.events) + 1}")
        payload.setdefault("ts", datetime.now(UTC).replace(tzinfo=None))
        evt = _FakeEpisode(payload)
        self.events.append(evt)
        return evt

    def list_recent(self, limit=100):
        return self.events[-limit:]


class _FakeMemory:
    def __init__(self):
        self.saved = []

    def store(self, payload):
        self.saved.append(payload)
        return True


class TestPhase4LearningQualityAndLatency(unittest.TestCase):
    def _decision(self, action="analyze"):
        return Decision(
            action=action,
            confidence=0.6,
            rationale="test",
            alternatives=["defer"],
            risk_level="medium",
            requires_approval=False,
        )

    def test_learning_improves_over_10_iterations(self):
        with tempfile.TemporaryDirectory() as td:
            loop = LearningLoop(
                episodic_store=_FakeStore(),
                memory_engine=_FakeMemory(),
                state_path=Path(td) / "learning_quality_state.json",
            )

            context = "benchmark"
            action = "analyze"

            for _ in range(12):
                loop.process_outcome(
                    self._decision(action=action),
                    {
                        "context": context,
                        "success": True,
                        "quality": 0.9,
                        "latency_ms": 25,
                    },
                )

            hints = loop.get_decision_hints(context, action=action)
            self.assertEqual(hints["source"], "learned")
            self.assertEqual(hints["attempts"], 12)
            self.assertGreaterEqual(hints["success_rate"], 0.9)
            self.assertGreaterEqual(hints["confidence_hint"], 0.85)
            self.assertEqual(hints["risk_hint"], "low")

    def test_memory_recall_latency_under_100ms(self):
        engine = AetherraMemoryEngine()
        engine.engine = _DummyBackend()  # Isolate from heavy backend behavior.

        for i in range(250):
            engine.store(
                {
                    "content": f"memory item {i} about deploy and testing",
                    "metadata": {"idx": i},
                    "importance": 0.7,
                }
            )

        start = time.perf_counter()
        rows = engine.recall("deploy testing", limit=20)
        elapsed = time.perf_counter() - start

        self.assertEqual(len(rows), 20)
        self.assertLess(elapsed, 0.1)

    def test_reflector_behavior_analysis_latency_under_100ms(self):
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
        analysis = plugin.analyze_behavior("latency-check")
        elapsed = time.perf_counter() - start

        self.assertIn("patterns", analysis)
        self.assertIn("efficiency_metrics", analysis)
        self.assertLess(elapsed, 0.1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestPhase4LearningQualityAndLatency
    )
    total = suite.countTestCases()
    print(f"Running {total} phase-4 quality/latency tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)

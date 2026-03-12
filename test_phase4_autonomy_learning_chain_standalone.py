"""Standalone integration tests for Decision -> Governor -> Learning chain.

Run with:
    python test_phase4_autonomy_learning_chain_standalone.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.consciousness.autonomy_governor import AutonomyGovernor
from Aetherra.consciousness.decision_engine import ConsciousnessDecisionEngine
from Aetherra.consciousness.learning_loop import LearningLoop


class FakeEpisode:
    def __init__(self, payload):
        self.id = payload["id"]
        self.type = payload["type"]
        self.content = payload["content"]
        self.raw = payload.get("raw", {})
        self.ts = payload["ts"]


class FakeStore:
    def __init__(self):
        self.events = []

    def new_event(self, **kwargs):
        payload = dict(kwargs)
        payload.setdefault("id", f"evt-{len(self.events) + 1}")
        payload.setdefault("ts", datetime.utcnow())
        evt = FakeEpisode(payload)
        self.events.append(evt)
        return evt

    def list_recent(self, limit=100):
        return self.events[-limit:]


class FakeMemory:
    def __init__(self):
        self.saved = []

    def store(self, payload):
        self.saved.append(payload)
        return True


class TestAutonomyLearningChain(unittest.TestCase):
    def setUp(self) -> None:
        self.decision_engine = ConsciousnessDecisionEngine()
        self.governor = AutonomyGovernor()
        self.store = FakeStore()
        self.memory = FakeMemory()

    def _loop(self, temp_dir: str) -> LearningLoop:
        return LearningLoop(
            episodic_store=self.store,
            memory_engine=self.memory,
            state_path=Path(temp_dir) / "chain_state.json",
        )

    def test_safe_flow_learns_positive_bias(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self._loop(td)
            decision = self.decision_engine.decide(
                {
                    "goal": "optimize docs",
                    "context": "repo",
                    "candidate_actions": ["analyze"],
                }
            )
            gate = self.governor.evaluate(
                {
                    "operation": decision.action,
                    "file_changes": 1,
                    "api_calls": 0,
                    "risk_score": 0.2,
                }
            )
            self.assertTrue(gate.allowed)

            adjustment = loop.process_outcome(
                decision,
                {"context": "repo", "success": True, "quality": 0.92, "latency_ms": 25},
            )
            self.assertEqual(adjustment.strategy_delta, "increase_autonomy")

            hints = loop.get_decision_hints("repo", action=decision.action)
            self.assertEqual(hints["source"], "learned")
            self.assertGreater(hints["confidence_hint"], 0.6)

    def test_denied_flow_learns_caution(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self._loop(td)
            decision = self.decision_engine.decide(
                {
                    "goal": "security lockdown",
                    "context": "production",
                    "risk_hint": "high",
                    "candidate_actions": ["execute"],
                    "confidence_hint": 0.9,
                }
            )
            gate = self.governor.evaluate(
                {
                    "operation": "git reset --hard",
                    "file_changes": 3,
                    "api_calls": 0,
                    "risk_score": 0.9,
                }
            )
            self.assertFalse(gate.allowed)

            adjustment = loop.process_outcome(
                decision,
                {
                    "context": "production",
                    "success": False,
                    "quality": 0.2,
                    "latency_ms": 1200,
                    "regression": True,
                },
            )
            self.assertEqual(adjustment.strategy_delta, "increase_caution")
            self.assertEqual(adjustment.recommended_risk_hint, "high")

    def test_chain_records_episodes_and_memory(self):
        with tempfile.TemporaryDirectory() as td:
            loop = self._loop(td)
            decision = self.decision_engine.decide(
                {"goal": "fix bug", "context": "repo"}
            )
            loop.process_outcome(
                decision, {"context": "repo", "success": True, "quality": 0.8}
            )
            rows = loop.recent_similar_episodes("repo", decision.action, limit=5)
            self.assertGreaterEqual(len(rows), 1)
            self.assertEqual(len(self.memory.saved), 1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAutonomyLearningChain)
    total = suite.countTestCases()
    print(f"Running {total} phase-4 autonomy-learning chain tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)

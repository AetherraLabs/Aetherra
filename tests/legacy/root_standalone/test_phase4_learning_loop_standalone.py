"""Standalone tests for Phase 4 learning loop.

Run with:
    python tests/legacy/root_standalone/test_phase4_learning_loop_standalone.py
"""

from __future__ import annotations

# Standard library imports
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Aetherra imports
from Aetherra.consciousness.decision_engine import Decision
from Aetherra.consciousness.learning_loop import LearningLoop


class FakeEpisode:
    def __init__(self, payload):
        self.id = payload.get("id", "evt")
        self.type = payload["type"]
        self.content = payload["content"]
        self.raw = payload.get("raw", {})
        self.ts = payload.get("ts")


class FakeEpisodicStore:
    def __init__(self):
        self.events = []

    def new_event(self, **kwargs):
        # Standard library imports
        from datetime import datetime

        payload = dict(kwargs)
        payload.setdefault("id", f"evt-{len(self.events) + 1}")
        payload.setdefault("ts", datetime.utcnow())
        self.events.append(FakeEpisode(payload))
        return self.events[-1]

    def list_recent(self, limit=100):
        return self.events[-limit:]


class FakeMemoryEngine:
    def __init__(self):
        self.stored = []

    def store(self, payload):
        self.stored.append(payload)
        return True


class TestLearningLoop(unittest.TestCase):
    def _decision(self, action="analyze", confidence=0.6, risk="medium"):
        return Decision(
            action=action,
            confidence=confidence,
            rationale="test",
            alternatives=["defer"],
            risk_level=risk,
            requires_approval=False,
        )

    def test_process_outcome_creates_adjustment(self):
        with tempfile.TemporaryDirectory() as td:
            loop = LearningLoop(
                episodic_store=FakeEpisodicStore(),
                memory_engine=FakeMemoryEngine(),
                state_path=Path(td) / "state.json",
            )
            adjustment = loop.process_outcome(
                self._decision(action="execute"),
                {"context": "repo", "success": True, "quality": 0.9, "latency_ms": 40},
            )
            assert adjustment.context == "repo"
            assert adjustment.action == "execute"
            assert adjustment.success
            assert adjustment.score >= 0.0

    def test_failure_outcome_moves_to_caution(self):
        with tempfile.TemporaryDirectory() as td:
            loop = LearningLoop(
                episodic_store=FakeEpisodicStore(),
                memory_engine=FakeMemoryEngine(),
                state_path=Path(td) / "state.json",
            )
            adjustment = loop.process_outcome(
                self._decision(action="execute"),
                {
                    "context": "prod",
                    "success": False,
                    "quality": 0.2,
                    "latency_ms": 3000,
                    "regression": True,
                },
            )
            assert adjustment.strategy_delta == "increase_caution"
            assert adjustment.recommended_risk_hint == "high"

    def test_get_decision_hints_defaults(self):
        with tempfile.TemporaryDirectory() as td:
            loop = LearningLoop(
                episodic_store=FakeEpisodicStore(),
                memory_engine=FakeMemoryEngine(),
                state_path=Path(td) / "state.json",
            )
            hints = loop.get_decision_hints("unknown")
            assert hints["source"] == "default"
            assert hints["risk_hint"] == "medium"

    def test_get_decision_hints_uses_learned_signal(self):
        with tempfile.TemporaryDirectory() as td:
            loop = LearningLoop(
                episodic_store=FakeEpisodicStore(),
                memory_engine=FakeMemoryEngine(),
                state_path=Path(td) / "state.json",
            )

            loop.process_outcome(
                self._decision(action="measure"),
                {"context": "repo", "success": True, "quality": 0.95, "latency_ms": 20},
            )
            loop.process_outcome(
                self._decision(action="measure"),
                {"context": "repo", "success": True, "quality": 0.9, "latency_ms": 30},
            )

            hints = loop.get_decision_hints("repo", action="measure")
            assert hints["source"] == "learned"
            assert hints["action"] == "measure"
            assert hints["confidence_hint"] > 0.6

    def test_recent_similar_episodes_filters(self):
        with tempfile.TemporaryDirectory() as td:
            store = FakeEpisodicStore()
            loop = LearningLoop(
                episodic_store=store,
                memory_engine=FakeMemoryEngine(),
                state_path=Path(td) / "state.json",
            )
            loop.process_outcome(
                self._decision(action="analyze"),
                {"context": "repo", "success": True, "quality": 0.8},
            )
            loop.process_outcome(
                self._decision(action="execute"),
                {"context": "repo", "success": False, "quality": 0.3},
            )

            rows = loop.recent_similar_episodes("repo", "analyze", limit=5)
            assert len(rows) == 1
            assert rows[0]["success"]

    def test_state_persists_between_instances(self):
        with tempfile.TemporaryDirectory() as td:
            state_path = Path(td) / "state.json"
            loop1 = LearningLoop(
                episodic_store=FakeEpisodicStore(),
                memory_engine=FakeMemoryEngine(),
                state_path=state_path,
            )
            loop1.process_outcome(
                self._decision(action="analyze"),
                {"context": "docs", "success": True, "quality": 0.8},
            )

            loop2 = LearningLoop(
                episodic_store=FakeEpisodicStore(),
                memory_engine=FakeMemoryEngine(),
                state_path=state_path,
            )
            hints = loop2.get_decision_hints("docs", action="analyze")
            assert hints["source"] == "learned"
            assert hints["attempts"] == 1

    def test_memory_engine_receives_learning_summary(self):
        with tempfile.TemporaryDirectory() as td:
            mem = FakeMemoryEngine()
            loop = LearningLoop(
                episodic_store=FakeEpisodicStore(),
                memory_engine=mem,
                state_path=Path(td) / "state.json",
            )
            loop.process_outcome(
                self._decision(action="plan"),
                {"context": "planning", "success": True, "quality": 0.9},
            )
            assert len(mem.stored) == 1
            assert "Learning update" in mem.stored[0]["content"]


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLearningLoop)
    total = suite.countTestCases()
    print(f"Running {total} phase-4 learning-loop tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)

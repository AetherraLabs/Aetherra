"""Standalone tests for Aetherra.plugins.reflector.ReflectorPlugin.

Run with:
    python test_plugins_reflector_standalone.py
"""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.plugins.reflector import ReflectorPlugin


class TestReflectorPluginStandalone(unittest.TestCase):
    def setUp(self) -> None:
        self.p = ReflectorPlugin()

    def _log(self, action_type: str, **data):
        self.p.log_action(action_type, data)

    def test_temporal_patterns_empty(self):
        r = self.p._analyze_temporal_patterns()
        self.assertEqual(r["total_actions"], 0)
        self.assertIsNone(r["peak_hour"])

    def test_temporal_patterns_non_empty(self):
        now = datetime.now().isoformat()
        self.p.behavior_log.append({"type": "x", "timestamp": now, "data": {}})
        self.p.behavior_log.append({"type": "y", "timestamp": now, "data": {}})
        r = self.p._analyze_temporal_patterns()
        self.assertEqual(r["total_actions"], 2)
        self.assertIsNotNone(r["peak_hour"])

    def test_contextual_patterns(self):
        self._log("analyze", context="dev")
        self._log("analyze", context="dev")
        self._log("run", context="qa")
        r = self.p._analyze_contextual_patterns()
        self.assertEqual(r["top_context"], "dev")

    def test_decision_patterns(self):
        self.p.decision_tracking(
            {"action": "x", "confidence": 0.9, "outcome": "success"}
        )
        self.p.decision_tracking(
            {"action": "y", "confidence": 0.5, "outcome": "failed"}
        )
        r = self.p._analyze_decision_patterns()
        self.assertEqual(r["decision_count"], 2)
        self.assertIn("success", r["outcomes"])

    def test_error_patterns(self):
        self._log("task", success=False)
        self._log("error", success=False)
        self._log("task", success=True)
        r = self.p._analyze_error_patterns()
        self.assertEqual(r["error_count"], 2)
        self.assertGreater(r["error_rate"], 0)

    def test_learning_patterns(self):
        self._log("learn", domain="math")
        self._log("adapt", domain="coding")
        r = self.p._analyze_learning_patterns()
        self.assertEqual(r["learning_events"], 2)

    def test_activity_times(self):
        self._log("x", context="a")
        r = self.p._analyze_activity_times()
        self.assertIn("business_hours_ratio", r)

    def test_identify_workflows(self):
        self._log("plan")
        self._log("build")
        self._log("test")
        self._log("build")
        wf = self.p._identify_workflows()
        self.assertTrue(any(x == "plan->build" for x in wf))

    def test_cognitive_load(self):
        for _ in range(5):
            self._log("task", complexity="high")
        r = self.p._analyze_cognitive_load()
        self.assertIn(r["cognitive_load"], {"low", "medium", "high"})

    def test_decision_quality(self):
        q = self.p._analyze_decision_quality({"confidence": 0.8, "outcome": "success"})
        self.assertGreaterEqual(q["quality_score"], 0.8)

    def test_improvement_rate(self):
        self._log("learn", topic="python", performance=0.5)
        self._log("learn", topic="python", performance=0.6)
        r = self.p._calculate_improvement_rate("python", 0.8)
        self.assertGreater(r, 0)

    def test_learning_curve(self):
        self._log("learn", topic="nlp", performance=0.2)
        self._log("learn", topic="nlp", performance=0.5)
        c = self.p._analyze_learning_curve("nlp")
        self.assertEqual(c["trend"], "improving")

    def test_goal_efficiency_and_recommendations(self):
        actions = [
            {
                "data": {
                    "duration_sec": 100,
                    "success": True,
                    "resource_usage": {"cpu": 0.7, "memory": 0.5},
                }
            },
            {
                "data": {
                    "duration_sec": 400,
                    "success": False,
                    "resource_usage": {"cpu": 0.9, "memory": 0.6},
                }
            },
        ]
        eff = self.p._analyze_goal_time_efficiency(actions)
        self.assertIn("efficiency", eff)
        rec = self.p._generate_goal_recommendations(actions)
        self.assertGreaterEqual(len(rec), 1)

    def test_goal_resource_usage(self):
        actions = [
            {"data": {"resource_usage": {"cpu": 0.8, "memory": 0.4}}},
            {"data": {"resource_usage": {"cpu": 0.6, "memory": 0.5}}},
        ]
        r = self.p._analyze_goal_resource_usage(actions)
        self.assertIn("resources", r)
        self.assertIsNotNone(r["resources"]["avg_cpu"])

    def test_goal_side_effects(self):
        actions = [
            {"data": {"side_effects": ["fatigue", "latency"]}},
            {"data": {"side_effects": ["fatigue"]}},
        ]
        r = self.p._identify_goal_side_effects(actions)
        self.assertIn("fatigue", r)

    def test_forgetting_patterns(self):
        mem = [
            {"type": "forget", "data": {}},
            {"type": "forget", "data": {}},
            {"type": "recall", "data": {}},
        ]
        r = self.p._analyze_forgetting_patterns(mem)
        self.assertEqual(r["patterns"]["forget_count"], 2)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestReflectorPluginStandalone
    )
    total = suite.countTestCases()
    print(f"Running {total} reflector tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)

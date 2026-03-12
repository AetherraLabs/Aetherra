"""Standalone tests for Phase 3 modules.

Covers:
- Aetherra.consciousness.decision_engine
- Aetherra.consciousness.autonomy_governor
- Aetherra.plugins.manager

Run with:
    python test_phase3_modules_standalone.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.consciousness.autonomy_governor import AutonomyGovernor
from Aetherra.consciousness.decision_engine import ConsciousnessDecisionEngine
from Aetherra.plugins.manager import PluginManager


class TestDecisionEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ConsciousnessDecisionEngine()

    def test_decision_has_required_fields(self):
        d = self.engine.decide({"goal": "fix bug", "context": "repo"})
        self.assertTrue(d.action)
        self.assertTrue(0.0 <= d.confidence <= 1.0)
        self.assertIn(d.risk_level, {"low", "medium", "high"})
        self.assertIsInstance(d.alternatives, list)

    def test_candidate_actions_from_goal(self):
        d = self.engine.decide({"goal": "fix critical bug", "context": "prod"})
        self.assertIn(d.action, {"analyze", "execute", "rollback", "defer"})

    def test_requires_approval_for_high_risk(self):
        d = self.engine.decide(
            {
                "goal": "security lockdown",
                "risk_hint": "high",
                "urgency": "critical",
                "candidate_actions": ["execute"],
                "confidence_hint": 0.9,
            }
        )
        self.assertTrue(d.requires_approval)

    def test_constraints_reduce_risky_actions(self):
        d = self.engine.decide(
            {
                "goal": "fix bug",
                "constraints": ["no_destructive_ops"],
                "candidate_actions": ["execute", "analyze"],
            }
        )
        self.assertEqual(d.action, "analyze")

    def test_custom_candidates_supported(self):
        d = self.engine.decide(
            {
                "goal": "optimize",
                "candidate_actions": ["measure", "execute", "defer"],
            }
        )
        self.assertIn(d.action, {"measure", "execute", "defer"})


class TestAutonomyGovernor(unittest.TestCase):
    def setUp(self) -> None:
        self.gov = AutonomyGovernor()

    def test_allows_safe_action(self):
        r = self.gov.evaluate(
            {
                "operation": "apply patch",
                "file_changes": 2,
                "api_calls": 1,
                "risk_score": 0.2,
                "breaking_change": False,
            }
        )
        self.assertTrue(r.allowed)

    def test_blocks_forbidden_operation(self):
        r = self.gov.evaluate({"operation": "git reset --hard", "risk_score": 0.1})
        self.assertFalse(r.allowed)
        self.assertIn("forbidden_operation", r.violations)

    def test_file_change_limit(self):
        r = self.gov.evaluate(
            {"operation": "bulk edit", "file_changes": 10_000, "risk_score": 0.1}
        )
        self.assertFalse(r.allowed)
        self.assertIn("file_change_limit_exceeded", r.violations)

    def test_risk_limit(self):
        r = self.gov.evaluate(
            {"operation": "apply", "file_changes": 1, "risk_score": 0.99}
        )
        self.assertFalse(r.allowed)
        self.assertIn("risk_limit_exceeded", r.violations)

    def test_breaking_change_requires_approval(self):
        r = self.gov.evaluate(
            {
                "operation": "public api update",
                "file_changes": 1,
                "risk_score": 0.3,
                "breaking_change": True,
            }
        )
        self.assertTrue(r.requires_approval)

    def test_api_rate_limit_violation(self):
        self.gov.max_api_calls_per_min = 3
        r = self.gov.evaluate(
            {
                "operation": "query external",
                "file_changes": 0,
                "api_calls": 5,
                "risk_score": 0.2,
            }
        )
        self.assertFalse(r.allowed)
        self.assertIn("api_rate_limit_exceeded", r.violations)


class TestPluginsManager(unittest.TestCase):
    def _write(self, root: Path, rel: str, content: str) -> Path:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_discover_file_plugin(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(
                root,
                "sample_plugin.py",
                "class PLUGIN_CLASS:\n    def __init__(self):\n        pass\n    def execute_action(self, action, **kwargs):\n        return action\n",
            )
            pm = PluginManager(plugins_dir=root)
            names = pm.discover_plugins()
            self.assertIn("sample_plugin", names)

    def test_load_file_plugin(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(
                root,
                "sample_plugin.py",
                "class PLUGIN_CLASS:\n    def __init__(self):\n        pass\n    def execute_action(self, action, **kwargs):\n        return {'action': action}\n",
            )
            pm = PluginManager(plugins_dir=root)
            pm.discover_plugins()
            ok = pm.load_plugin("sample_plugin")
            self.assertTrue(ok)

    def test_execute_capability_via_execute_action(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(
                root,
                "sample_plugin.py",
                "class PLUGIN_CLASS:\n    def execute_action(self, action, **kwargs):\n        return {'action': action, 'kwargs': kwargs}\n",
            )
            pm = PluginManager(plugins_dir=root)
            pm.discover_plugins()
            self.assertTrue(pm.load_plugin("sample_plugin"))
            out = pm.execute_capability("sample_plugin", "analyze", x=1)
            self.assertEqual(out["action"], "analyze")
            self.assertEqual(out["kwargs"]["x"], 1)

    def test_unload_plugin(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(
                root,
                "sample_plugin.py",
                "class PLUGIN_CLASS:\n    def execute_action(self, action, **kwargs):\n        return action\n",
            )
            pm = PluginManager(plugins_dir=root)
            pm.discover_plugins()
            self.assertTrue(pm.load_plugin("sample_plugin"))
            self.assertTrue(pm.unload_plugin("sample_plugin"))

    def test_manifest_directory_plugin_validation_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Missing required fields in manifest
            self._write(root, "badplug/plugin.json", json.dumps({"name": "badplug"}))
            self._write(root, "badplug/badplug.py", "class PLUGIN_CLASS:\n    pass\n")
            pm = PluginManager(plugins_dir=root)
            pm.discover_plugins()
            ok, errors = pm.validate_plugin("badplug")
            self.assertFalse(ok)
            self.assertGreater(len(errors), 0)

    def test_list_plugins(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(root, "sample_plugin.py", "class PLUGIN_CLASS:\n    pass\n")
            pm = PluginManager(plugins_dir=root)
            pm.discover_plugins()
            rows = pm.list_plugins(include_unloaded=True)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["name"], "sample_plugin")

    def test_plugin_load_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(
                root, "broken_plugin.py", "raise RuntimeError('boom on import')\n"
            )
            pm = PluginManager(plugins_dir=root)
            pm.discover_plugins()
            ok = pm.load_plugin("broken_plugin")
            self.assertFalse(ok)
            self.assertTrue(pm.registry["broken_plugin"].errors)

    def test_execute_unknown_capability_raises(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write(
                root,
                "sample_plugin.py",
                "class PLUGIN_CLASS:\n    def execute_action(self, action, **kwargs):\n        if action == 'known':\n            return {'ok': True}\n        raise AttributeError('unknown capability')\n",
            )
            pm = PluginManager(plugins_dir=root)
            pm.discover_plugins()
            self.assertTrue(pm.load_plugin("sample_plugin"))
            with self.assertRaises(AttributeError):
                pm.execute_capability("sample_plugin", "unknown")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for cls in [TestDecisionEngine, TestAutonomyGovernor, TestPluginsManager]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    total = suite.countTestCases()
    print(f"Running {total} phase-3 module tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"Result: {total - len(result.failures) - len(result.errors)}/{total} passed")
    sys.exit(0 if result.wasSuccessful() else 1)

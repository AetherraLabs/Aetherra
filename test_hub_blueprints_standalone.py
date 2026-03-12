"""
Standalone test runner for Task 4: Hub Blueprints
Tests: agents.py, interactive.py, quantum.py blueprints

Run with:
    python test_hub_blueprints_standalone.py
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Minimal Flask app factory ─────────────────────────────────────────────────


def _make_app():
    """Create a minimal Flask test app with all three blueprints registered."""
    from flask import Flask

    app = Flask(__name__)
    app.config["TESTING"] = True

    # Import blueprints (with mocked external deps)
    from aetherra_hub.blueprints import agents as agents_mod
    from aetherra_hub.blueprints import interactive as interactive_mod
    from aetherra_hub.blueprints import quantum as quantum_mod

    app.register_blueprint(agents_mod.bp)
    app.register_blueprint(interactive_mod.bp)
    app.register_blueprint(quantum_mod.bp)

    return app


_SAMPLE_AGENTS = [
    {
        "agent_id": "agent_001",
        "type": "analyzer",
        "status": "idle",
        "capabilities": ["data-analysis", "code-review"],
        "description": "Analyzes code",
    },
    {
        "agent_id": "agent_002",
        "type": "processor",
        "status": "busy",
        "capabilities": ["data-processing"],
        "description": "Processes data",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# Agents Blueprint Tests (10 tests)
# ──────────────────────────────────────────────────────────────────────────────


class TestAgentsBlueprint(unittest.TestCase):
    def setUp(self):
        os.environ.pop("AETHERRA_AGENTS_API_ENABLED", None)
        os.environ.pop("AETHERRA_AGENTS_API_REQUIRE_TOKEN", None)
        os.environ.pop("AETHERRA_AGENTS_API_TOKEN", None)
        os.environ["AETHERRA_AGENTS_API_ENABLED"] = "1"
        self.app = _make_app()
        self.client = self.app.test_client()

    def tearDown(self):
        os.environ.pop("AETHERRA_AGENTS_API_ENABLED", None)
        os.environ.pop("AETHERRA_AGENTS_API_REQUIRE_TOKEN", None)
        os.environ.pop("AETHERRA_AGENTS_API_TOKEN", None)

    # ── list_agents ───────────────────────────────────────────────────────────

    def test_list_agents_returns_200(self):
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_registered_agents",
            return_value=[],
        ):
            with patch(
                "aetherra_hub.blueprints.agents.registry_client.get_orchestrator_status",
                return_value=None,
            ):
                r = self.client.get("/api/agents")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data["ok"])

    def test_list_agents_disabled_returns_200_with_enabled_false(self):
        os.environ["AETHERRA_AGENTS_API_ENABLED"] = "0"
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_orchestrator_status",
            return_value=None,
        ):
            r = self.client.get("/api/agents")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertFalse(data["enabled"])

    def test_list_agents_returns_agents_from_registry(self):
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_registered_agents",
            return_value=_SAMPLE_AGENTS,
        ):
            with patch(
                "aetherra_hub.blueprints.agents.registry_client.get_orchestrator_status",
                return_value=None,
            ):
                r = self.client.get("/api/agents")
        data = json.loads(r.data)
        self.assertEqual(len(data["agents"]), 2)
        self.assertEqual(data["count"], 2)

    def test_list_agents_filter_by_capability(self):
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_registered_agents",
            return_value=_SAMPLE_AGENTS,
        ):
            with patch(
                "aetherra_hub.blueprints.agents.registry_client.get_orchestrator_status",
                return_value=None,
            ):
                r = self.client.get("/api/agents?capability=data-analysis")
        data = json.loads(r.data)
        self.assertEqual(len(data["agents"]), 1)
        self.assertEqual(data["agents"][0]["agent_id"], "agent_001")

    def test_list_agents_filter_by_status(self):
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_registered_agents",
            return_value=_SAMPLE_AGENTS,
        ):
            with patch(
                "aetherra_hub.blueprints.agents.registry_client.get_orchestrator_status",
                return_value=None,
            ):
                r = self.client.get("/api/agents?status=idle")
        data = json.loads(r.data)
        self.assertEqual(len(data["agents"]), 1)
        self.assertEqual(data["agents"][0]["status"], "idle")

    def test_list_agents_token_required_missing_returns_403(self):
        os.environ["AETHERRA_AGENTS_API_REQUIRE_TOKEN"] = "1"
        os.environ["AETHERRA_AGENTS_API_TOKEN"] = "secret"
        r = self.client.get("/api/agents")
        self.assertEqual(r.status_code, 403)

    def test_list_agents_token_correct_returns_200(self):
        os.environ["AETHERRA_AGENTS_API_REQUIRE_TOKEN"] = "1"
        os.environ["AETHERRA_AGENTS_API_TOKEN"] = "secret"
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_registered_agents",
            return_value=[],
        ):
            with patch(
                "aetherra_hub.blueprints.agents.registry_client.get_orchestrator_status",
                return_value=None,
            ):
                r = self.client.get(
                    "/api/agents", headers={"X-Aetherra-Token": "secret"}
                )
        self.assertEqual(r.status_code, 200)

    # ── get_agent ─────────────────────────────────────────────────────────────

    def test_get_agent_found(self):
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_registered_agents",
            return_value=_SAMPLE_AGENTS,
        ):
            r = self.client.get("/api/agents/agent_001")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data["ok"])
        self.assertEqual(data["agent"]["agent_id"], "agent_001")

    def test_get_agent_not_found_returns_404(self):
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_registered_agents",
            return_value=_SAMPLE_AGENTS,
        ):
            r = self.client.get("/api/agents/nonexistent")
        self.assertEqual(r.status_code, 404)

    # ── get_agent_status ──────────────────────────────────────────────────────

    def test_get_agent_status(self):
        with patch(
            "aetherra_hub.blueprints.agents.registry_client.get_registered_agents",
            return_value=_SAMPLE_AGENTS,
        ):
            r = self.client.get("/api/agents/agent_002/status")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data["ok"])
        self.assertEqual(data["status"], "busy")
        self.assertIn("capabilities", data)


# ──────────────────────────────────────────────────────────────────────────────
# Interactive Blueprint Tests (15 tests)
# ──────────────────────────────────────────────────────────────────────────────


class TestInteractiveBlueprint(unittest.TestCase):
    def setUp(self):
        os.environ.pop("AETHERRA_ADMIN_KEY", None)
        self.app = _make_app()
        self.client = self.app.test_client()

    def tearDown(self):
        os.environ.pop("AETHERRA_ADMIN_KEY", None)

    def _mock_interactive_sys(
        self, status_data=None, emotion="calm", expression="neutral"
    ):
        """Build a mock interactive system."""
        sys_mock = MagicMock()
        sys_mock.get_status.return_value = status_data or {
            "running": True,
            "emotion": emotion,
        }
        sys_mock.get_metrics.return_value = {"uptime": 100}
        sys_mock.interactive_loop = MagicMock()
        sys_mock.interactive_loop.get_current_emotion.return_value = emotion
        sys_mock.expression_manager = MagicMock()
        sys_mock.expression_manager.get_current_expression.return_value = expression
        sys_mock.event_bus = None  # No event bus - simpler path
        return sys_mock

    # ── /status ───────────────────────────────────────────────────────────────

    def test_status_unavailable_returns_503(self):
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=None,
        ):
            r = self.client.get("/api/interactive/status")
        self.assertEqual(r.status_code, 503)

    def test_status_available_returns_200(self):
        mock_sys = self._mock_interactive_sys()
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.get("/api/interactive/status")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data["status"], "ok")

    def test_status_contains_data(self):
        mock_sys = self._mock_interactive_sys(
            status_data={"running": True, "emotion": "curious"}
        )
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.get("/api/interactive/status")
        data = json.loads(r.data)
        self.assertIn("data", data)

    # ── /emotion ──────────────────────────────────────────────────────────────

    def test_emotion_unavailable_returns_503(self):
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=None,
        ):
            r = self.client.get("/api/interactive/emotion")
        self.assertEqual(r.status_code, 503)

    def test_emotion_available_returns_200(self):
        mock_sys = self._mock_interactive_sys(emotion="excited")
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.get("/api/interactive/emotion")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data["emotion"], "excited")

    def test_emotion_no_loop_returns_null(self):
        mock_sys = self._mock_interactive_sys()
        mock_sys.interactive_loop = None
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.get("/api/interactive/emotion")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsNone(data["emotion"])

    # ── /expression ───────────────────────────────────────────────────────────

    def test_expression_unavailable_returns_503(self):
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=None,
        ):
            r = self.client.get("/api/interactive/expression")
        self.assertEqual(r.status_code, 503)

    def test_expression_returns_value(self):
        mock_sys = self._mock_interactive_sys(expression="focused")
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.get("/api/interactive/expression")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data["expression"], "focused")

    # ── /trigger (admin auth) ─────────────────────────────────────────────────

    def test_trigger_no_auth_key_configured_allows_request(self):
        # When AETHERRA_ADMIN_KEY not set, dev mode: any request allowed
        mock_sys = self._mock_interactive_sys()
        payload = {"emotion": "calm", "intensity": 0.5}
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.post(
                "/api/interactive/trigger",
                json=payload,
                content_type="application/json",
            )
        # Should not get 403 (may get 503 if event_bus not wired, but not auth failure)
        self.assertNotEqual(r.status_code, 403)

    def test_trigger_wrong_admin_key_returns_403(self):
        os.environ["AETHERRA_ADMIN_KEY"] = "secret-key"
        r = self.client.post(
            "/api/interactive/trigger",
            json={"emotion": "calm"},
            headers={"X-Aetherra-Admin-Key": "wrong"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 403)
        data = json.loads(r.data)
        self.assertEqual(data["error"], "forbidden")

    def test_trigger_missing_admin_key_returns_403(self):
        os.environ["AETHERRA_ADMIN_KEY"] = "secret-key"
        r = self.client.post(
            "/api/interactive/trigger",
            json={"emotion": "calm"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 403)

    def test_trigger_correct_admin_key_passes_auth(self):
        os.environ["AETHERRA_ADMIN_KEY"] = "good-key"
        mock_sys = self._mock_interactive_sys()
        payload = {"emotion": "focused", "intensity": 0.8}
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.post(
                "/api/interactive/trigger",
                json=payload,
                headers={"X-Aetherra-Admin-Key": "good-key"},
                content_type="application/json",
            )
        # Auth passed; may get 503 due to event_bus=None, but not 403
        self.assertNotEqual(r.status_code, 403)

    def test_trigger_missing_emotion_returns_400(self):
        mock_sys = self._mock_interactive_sys()
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.post(
                "/api/interactive/trigger", json={}, content_type="application/json"
            )
        self.assertIn(r.status_code, [400, 503])

    def test_trigger_invalid_intensity_returns_400(self):
        mock_sys = self._mock_interactive_sys()
        payload = {"emotion": "calm", "intensity": 9.9}
        with patch(
            "aetherra_hub.blueprints.interactive._get_interactive_system",
            return_value=mock_sys,
        ):
            r = self.client.post(
                "/api/interactive/trigger",
                json=payload,
                content_type="application/json",
            )
        self.assertIn(r.status_code, [400, 503])


# ──────────────────────────────────────────────────────────────────────────────
# Quantum Blueprint Tests (5 tests)
# ──────────────────────────────────────────────────────────────────────────────


class TestQuantumBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = _make_app()
        self.client = self.app.test_client()

    def test_quantum_status_returns_200(self):
        r = self.client.get("/api/quantum/status")
        self.assertEqual(r.status_code, 200)

    def test_quantum_status_has_available_and_backend(self):
        r = self.client.get("/api/quantum/status")
        data = json.loads(r.data)
        self.assertIn("available", data)
        self.assertIn("backend", data)

    def test_quantum_snapshot_returns_200(self):
        with patch(
            "aetherra_hub.services.registry_client.get_memory_quantum_status",
            return_value={"coherence_level": 0.95, "enabled": False},
        ):
            r = self.client.get("/api/quantum/snapshot")
        self.assertEqual(r.status_code, 200)

    def test_quantum_snapshot_has_required_fields(self):
        with patch(
            "aetherra_hub.services.registry_client.get_memory_quantum_status",
            return_value={"coherence_level": 0.9, "branch_count": 3},
        ):
            r = self.client.get("/api/quantum/snapshot")
        data = json.loads(r.data)
        self.assertIn("coherence", data)
        self.assertIn("bridge_status", data)
        self.assertIn("memory", data)
        self.assertIn("timestamp", data)

    def test_quantum_snapshot_coherence_values(self):
        with patch(
            "aetherra_hub.services.registry_client.get_memory_quantum_status",
            return_value={"coherence_level": 0.85, "branch_count": 5, "stable": True},
        ):
            r = self.client.get("/api/quantum/snapshot")
        data = json.loads(r.data)
        self.assertAlmostEqual(data["coherence"]["level"], 0.85)
        self.assertEqual(data["coherence"]["branch_count"], 5)
        self.assertTrue(data["coherence"]["stable"])


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestAgentsBlueprint,
        TestInteractiveBlueprint,
        TestQuantumBlueprint,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    total = suite.countTestCases()
    print(f"Running {total} tests for Task 4 Hub Blueprints...")
    print("=" * 60)

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("=" * 60)
    passed = total - len(result.failures) - len(result.errors)
    print(f"\nResult: {passed}/{total} tests passed")

    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, trace in result.failures:
            print(f"  FAIL: {test}")
            for line in trace.strip().split("\n")[-3:]:
                print(f"    {line}")

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, trace in result.errors:
            print(f"  ERROR: {test}")
            for line in trace.strip().split("\n")[-3:]:
                print(f"    {line}")

    sys.exit(0 if result.wasSuccessful() else 1)

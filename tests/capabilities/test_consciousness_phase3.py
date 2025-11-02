# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Phase 3 Consciousness Capabilities Tests
=========================================

Acceptance tests for Self-Trust & Adaptive Awareness features:

1. Self-Trust Layer: Trust scores react to subsystem failures
2. Semantic Resonance Engine: Resonance beats raw magnitude for focus selection
3. Qualia Learning: Parameters adapt based on success/error patterns

These tests validate the core Phase 3 claim:
"Consciousness learns which events matter and adapts to outcomes"
"""

from Aetherra.consciousness.dashboards import ConsciousnessDashboard
from Aetherra.consciousness.qualia_learning import QualiaLearner, QualiaParams
from Aetherra.consciousness.self_trust import SelfTrust
from Aetherra.consciousness.semantic_resonance import SemanticResonance


class TestSelfTrustLayer:
    """Acceptance tests for Self-Trust Layer."""

    def test_trust_reacts_to_failures(self):
        """Trust scores decrease when subsystems report failures."""
        stl = SelfTrust()

        # Initial state: no subsystems tracked yet, global_score() returns 0.0
        initial_trust = stl.global_score()
        assert initial_trust == 0.0, (
            "Global trust should be 0.0 with no tracked subsystems"
        )

        # Track some subsystems with "ok" status to establish baseline
        stl.observe("disk", "ok")
        stl.observe("memory", "ok")
        baseline_trust = stl.global_score()
        assert baseline_trust > 85.0, (
            "Baseline trust should be near 90.0 for healthy subsystems"
        )

        # Simulate subsystem failures
        stl.observe("disk", "failed")
        stl.observe("disk", "failed")
        stl.observe("memory", "failed")

        # Trust should drop
        after_failures = stl.global_score()
        assert after_failures < baseline_trust, (
            "Global trust should drop after failures"
        )
        assert stl.subsystems["disk"].score < 90.0, (
            "Disk trust should be below baseline"
        )
        assert stl.subsystems["memory"].score < 90.0, (
            "Memory trust should be below baseline"
        )

    def test_trust_recovers_with_successes(self):
        """Trust scores recover when subsystems report successes."""
        stl = SelfTrust()

        # Induce failures
        stl.observe("services", "failed")
        stl.observe("services", "failed")
        degraded_trust = stl.subsystems["services"].score
        assert degraded_trust < 90.0, "Services trust should be degraded"

        # Simulate successful repairs
        stl.observe("services", "repaired")
        stl.observe("services", "ok")
        stl.observe("services", "repaired")

        # Trust should recover
        recovered_trust = stl.subsystems["services"].score
        assert recovered_trust > degraded_trust, "Trust should recover after successes"

    def test_attention_bias_increases_with_low_trust(self):
        """Low-trust subsystems get higher attention bias multipliers."""
        stl = SelfTrust()

        # Healthy subsystem: bias close to 1.0
        stl.observe("healthy_sys", "ok")
        healthy_bias = stl.bias_for_attention("healthy_sys")
        assert 1.0 <= healthy_bias <= 1.3, "Healthy subsystem should have low bias"

        # Failing subsystem: bias should be higher
        stl.observe("failing_sys", "failed")
        stl.observe("failing_sys", "failed")
        stl.observe("failing_sys", "failed")
        failing_bias = stl.bias_for_attention("failing_sys")
        assert failing_bias > healthy_bias, (
            "Failing subsystem should get higher attention bias"
        )
        assert failing_bias > 1.5, (
            "Low-trust subsystem should have significant bias boost"
        )


class TestSemanticResonanceEngine:
    """Acceptance tests for Semantic Resonance Engine."""

    def test_resonance_beats_magnitude_for_focus(self):
        """Resonance scoring produces valid similarity scores for event-goal pairs."""
        sre = SemanticResonance(vector_dim=8)

        # Define goal: maintain service health
        goal_vecs = [sre.embed_goal("ensure_service_health")]

        # Different events produce different embeddings
        event1_vec = sre.embed_event("disk.usage", {"path": "/var/log", "pct": 85})
        event1_res = sre.resonance(event1_vec, goal_vecs)

        event2_vec = sre.embed_event(
            "svc.health", {"service": "hub", "status": "degraded"}
        )
        event2_res = sre.resonance(event2_vec, goal_vecs)

        # Resonance scores should be valid floats in range [-1, 1] (cosine similarity)
        assert isinstance(event1_res, float), "Resonance should return float"
        assert isinstance(event2_res, float), "Resonance should return float"
        assert -1.0 <= event1_res <= 1.0, "Cosine similarity should be in [-1, 1]"
        assert -1.0 <= event2_res <= 1.0, "Cosine similarity should be in [-1, 1]"

    def test_top_resonances_ranks_correctly(self):
        """top_resonances returns events sorted by semantic relevance."""
        sre = SemanticResonance(vector_dim=8)

        goal_vecs = [sre.embed_goal("optimize_resource_usage")]

        events = [
            ("evt1", sre.embed_event("disk.status", {"free": "10%"})),
            ("evt2", sre.embed_event("chat.message", {"text": "hello"})),
            ("evt3", sre.embed_event("mem.usage", {"pct": 95})),
        ]

        top = sre.top_resonances(events, goal_vecs, k=3)

        # Verify function returns results sorted by score
        assert len(top) == 3, "Should return k=3 results"
        assert all(
            isinstance(eid, str) and isinstance(score, float) for eid, score in top
        ), "Results should be (event_id, score) tuples"
        # Scores should be in descending order
        scores = [score for _, score in top]
        assert scores == sorted(scores, reverse=True), (
            "Results should be sorted by score descending"
        )

    def test_cache_improves_performance(self):
        """Embedding cache avoids redundant computation."""
        sre = SemanticResonance(vector_dim=8)

        # First embedding: cache miss
        vec1 = sre.embed_event("svc.health", {"status": "ok"})
        cache_size_1 = sre.get_cache_size()
        assert cache_size_1 > 0, "Cache should store first embedding"

        # Second embedding: cache hit (same type and keys)
        vec2 = sre.embed_event("svc.health", {"status": "degraded"})  # keys match
        cache_size_2 = sre.get_cache_size()
        assert cache_size_2 == cache_size_1, (
            "Cache size should not grow for same event schema"
        )
        assert vec1 == vec2, (
            "Same schema should produce same embedding (deterministic hash)"
        )


class TestQualiaLearning:
    """Acceptance tests for Qualia Learning."""

    def test_parameters_adapt_to_repeated_errors(self):
        """Qualia learning increases error penalty and reduces curiosity after failures."""
        ql = QualiaLearner()

        initial_penalty = ql.p.error_penalty
        initial_curiosity = ql.p.curiosity_gain

        # Simulate repeated errors
        ql.on_errors(5)

        # Error penalty should increase
        assert ql.p.error_penalty > initial_penalty, (
            "Error penalty should increase after errors"
        )
        # Curiosity should decrease (system becomes more conservative)
        assert ql.p.curiosity_gain < initial_curiosity, (
            "Curiosity should decrease after errors"
        )

    def test_parameters_adapt_to_repeated_successes(self):
        """Qualia learning increases success boost and certainty gain after wins."""
        ql = QualiaLearner()

        initial_boost = ql.p.success_boost
        initial_certainty = ql.p.certainty_gain

        # Simulate repeated successes
        ql.on_successes(5)

        # Success boost should increase
        assert ql.p.success_boost > initial_boost, (
            "Success boost should increase after wins"
        )
        # Certainty gain should increase
        assert ql.p.certainty_gain > initial_certainty, "Certainty gain should increase"

    def test_decay_prevents_drift(self):
        """Decay pulls parameters back toward defaults over time."""
        ql = QualiaLearner()

        # Get baseline values
        baseline_penalty = ql.p.error_penalty
        baseline_boost = ql.p.success_boost

        # Push parameters to extremes
        ql.on_errors(10)
        ql.on_successes(10)

        # Check parameters are away from defaults
        assert ql.p.error_penalty > baseline_penalty
        assert ql.p.success_boost > baseline_boost

        # Apply decay multiple times
        for _ in range(20):
            ql.decay_toward_defaults()

        # Parameters should drift back toward defaults
        assert abs(ql.p.error_penalty - baseline_penalty) < 0.01
        assert abs(ql.p.success_boost - baseline_boost) < 0.01

    def test_parameters_stay_within_bounds(self):
        """Clamping ensures parameters never exceed min/max bounds."""
        ql = QualiaLearner()

        # Attempt to push parameters beyond bounds
        for _ in range(100):
            ql.on_errors(1)

        # Check parameters are clamped within QualiaParams.clamp() ranges
        assert 0.01 <= ql.p.curiosity_gain <= 0.1
        assert 0.01 <= ql.p.error_penalty <= 0.1
        assert 0.05 <= ql.p.success_boost <= 0.2
        assert 0.01 <= ql.p.certainty_gain <= 0.05


class TestDashboards:
    """Acceptance tests for Dashboards/Telemetry."""

    def test_dashboard_exports_self_trust_metrics(self):
        """Dashboard exports self-trust metrics for Prometheus."""
        stl = SelfTrust()
        stl.observe("disk", "failed")
        stl.observe("memory", "ok")

        dashboard = ConsciousnessDashboard(stl, None)  # type: ignore
        metrics = dashboard.get_self_trust_metrics()

        assert "global_score" in metrics
        assert "subsystems" in metrics
        assert "disk" in metrics["subsystems"]
        assert metrics["subsystems"]["disk"] < 90.0

    def test_dashboard_exports_qualia_learning_metrics(self):
        """Dashboard exports qualia learning parameters."""
        ql = QualiaLearner()
        ql.on_successes(3)

        dashboard = ConsciousnessDashboard(None, ql)  # type: ignore
        metrics = dashboard.get_qualia_learning_metrics()

        assert "curiosity_gain" in metrics
        assert "error_penalty" in metrics
        assert "success_boost" in metrics
        assert "certainty_gain" in metrics

    def test_dashboard_logs_focus_attribution(self):
        """Dashboard logs focus attribution for telemetry analysis."""
        dashboard = ConsciousnessDashboard(None, None)  # type: ignore
        dashboard.log_focus_attribution("svc.health", 0.85, "system health")

        # Check that attribution was logged
        assert len(dashboard.focus_attribution_log) == 1
        assert dashboard.focus_attribution_log[0][0] == "svc.health"
        assert dashboard.focus_attribution_log[0][1] == 0.85

    def test_prometheus_export_format(self):
        """Prometheus export produces valid metrics format."""
        stl = SelfTrust()
        ql = QualiaLearner()
        dashboard = ConsciousnessDashboard(stl, ql)

        prom_output = dashboard.export_prometheus()

        # Check for expected Prometheus metric lines
        assert "consciousness_self_trust_global" in prom_output
        assert "consciousness_qualia_curiosity_gain" in prom_output
        assert "consciousness_qualia_error_penalty" in prom_output

        # Validate format (metric name + value)
        lines = [
            line
            for line in prom_output.split("\n")
            if line and not line.startswith("#")
        ]
        for line in lines:
            assert " " in line, f"Invalid Prometheus line: {line}"
            metric, value = line.rsplit(" ", 1)
            float(value)  # Should be parseable as float


class TestIntegration:
    """Integration tests combining multiple Phase 3 components."""

    def test_full_phase3_pipeline(self):
        """Test complete Phase 3 pipeline: trust → resonance → learning."""
        stl = SelfTrust()
        sre = SemanticResonance()
        ql = QualiaLearner()
        dashboard = ConsciousnessDashboard(stl, ql)

        # 1. Simulate subsystem failure
        stl.observe("services", "failed")
        assert stl.subsystems["services"].score < 90.0

        # 2. Focus selection uses semantic resonance
        goals = [sre.embed_goal("ensure_service_health")]
        evt_vec = sre.embed_event("svc.health", {"status": "degraded"})
        res = sre.resonance(evt_vec, goals)
        assert res > 0.0

        # 3. Apply trust bias (low trust → higher attention)
        trust_bias = stl.bias_for_attention("services")
        focus_score = res * trust_bias
        assert focus_score > res

        # 4. Simulate action outcome (success)
        ql.on_successes(1)
        initial_boost = QualiaParams().success_boost
        assert ql.p.success_boost > initial_boost

        # 5. Update trust after successful repair
        score_before_repair = stl.subsystems["services"].score
        stl.observe("services", "repaired")
        assert stl.subsystems["services"].score > score_before_repair

        # 6. Export metrics
        metrics = dashboard.get_self_trust_metrics()
        assert "services" in metrics["subsystems"]

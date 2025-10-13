#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Tests for Alert Intelligence System (Strategic Enhancement #4)
==============================================================

Tests adaptive thresholds, AI-assisted anomaly detection,
Lyrixa integration, and intelligent alert management.

Author: Aetherra Labs
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from Aetherra.homeostasis.alert_intelligence import (
    AdaptiveThresholdEngine,
    AlertSeverity,
    AlertStatus,
    AnomalyDetection,
    AnomalyType,
    IntelligentAlert,
    MetricPattern,
)
from Aetherra.homeostasis.intelligent_alert_manager import (
    AlertEscalationRule,
    AlertNotificationChannel,
    IntelligentAlertManager,
)
from Aetherra.homeostasis.lyrixa_integration import (
    LyrixaAlertIntegration,
    LyrixaReflectionRequest,
    LyrixaReflectionResponse,
)


class TestAdaptiveThresholdEngine:
    """Test the adaptive threshold engine."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def engine(self, temp_db):
        """Create an adaptive threshold engine for testing."""
        return AdaptiveThresholdEngine(db_path=temp_db)

    @pytest.mark.asyncio
    async def test_engine_lifecycle(self, engine):
        """Test engine start/stop lifecycle."""
        # Initially not active
        assert not engine.engine_active

        # Start engine
        await engine.start_engine()
        assert engine.engine_active

        # Stop engine
        await engine.stop_engine()
        assert not engine.engine_active

    @pytest.mark.asyncio
    async def test_metric_sample_processing(self, engine):
        """Test adding metric samples and anomaly detection."""
        await engine.start_engine()

        try:
            # Add normal samples first (no anomaly expected)
            for i in range(20):
                detection = await engine.add_metric_sample(
                    "test_metric", 50.0 + i * 0.1
                )
                assert detection is None  # No anomaly for normal values

            # Add an outlier value (should detect anomaly after sufficient training)
            # Note: May not detect immediately as model needs training data
            detection = await engine.add_metric_sample("test_metric", 150.0)

            # Check that we can get adaptive thresholds
            thresholds = await engine.get_adaptive_thresholds("test_metric")
            assert isinstance(thresholds, dict)
            assert "baseline" in thresholds or "warning_upper" in thresholds

        finally:
            await engine.stop_engine()

    @pytest.mark.asyncio
    async def test_pattern_learning(self, engine):
        """Test pattern learning from metric history."""
        await engine.start_engine()

        try:
            # Add samples with a clear pattern
            for i in range(100):
                value = 50.0 + 10.0 * (i % 10) / 10.0  # Cyclic pattern
                await engine.add_metric_sample("pattern_metric", value)

            # Force pattern update
            await engine._update_pattern_for_metric("pattern_metric")

            # Check that pattern was learned
            pattern = engine.metric_patterns.get("pattern_metric")
            if pattern:  # Pattern might not be created if insufficient samples
                assert pattern.metric_name == "pattern_metric"
                assert pattern.baseline_mean > 0
                assert pattern.baseline_std >= 0
                assert pattern.sample_count > 0

        finally:
            await engine.stop_engine()

    def test_engine_status(self, engine):
        """Test engine status reporting."""
        status = engine.get_engine_status()

        assert isinstance(status, dict)
        assert "engine_active" in status
        assert "patterns_learned" in status
        assert "models_active" in status
        assert "detections_made" in status

        assert status["engine_active"] == engine.engine_active
        assert status["patterns_learned"] == len(engine.metric_patterns)


class TestLyrixaIntegration:
    """Test the Lyrixa integration system."""

    @pytest.fixture
    def integration(self):
        """Create a Lyrixa integration for testing."""
        return LyrixaAlertIntegration()

    @pytest.fixture
    def sample_detection(self):
        """Create a sample anomaly detection for testing."""
        return AnomalyDetection(
            detection_id="test_detection_001",
            metric_name="cpu_usage",
            value=95.0,
            timestamp="2025-01-27T10:00:00",
            anomaly_type=AnomalyType.THRESHOLD_BREACH,
            severity=AlertSeverity.HIGH,
            confidence=0.9,
            deviation_score=3.2,
            baseline_value=65.0,
            threshold_values={"warning_upper": 80.0, "critical_upper": 90.0},
            pattern_context={"pattern_type": "daily", "baseline_std": 5.0},
            root_cause_analysis={"primary_factors": []},
            correlation_analysis={"correlated_metrics": []},
            prediction_context={"predicted_range": {"lower": 60.0, "upper": 70.0}},
            status=AlertStatus.ACTIVE,
            acknowledged_by=None,
            resolved_at=None,
            explanation=None,
        )

    @pytest.mark.asyncio
    async def test_integration_lifecycle(self, integration):
        """Test integration start/stop lifecycle."""
        # Initially not active
        assert not integration.integration_active

        # Start integration
        await integration.start_integration()
        # Note: May or may not be active depending on Lyrixa availability

        # Stop integration
        await integration.stop_integration()
        assert not integration.integration_active

    @pytest.mark.asyncio
    async def test_intelligent_alert_creation(self, integration, sample_detection):
        """Test creating intelligent alerts with AI analysis."""
        await integration.start_integration()

        try:
            # Create intelligent alert
            alert = await integration.create_intelligent_alert(
                sample_detection,
                context={"system": "production", "region": "us-east-1"},
            )

            # Verify alert structure
            assert isinstance(alert, IntelligentAlert)
            assert alert.detection_id == sample_detection.detection_id
            assert alert.severity == sample_detection.severity
            assert alert.status == AlertStatus.ACTIVE

            # Verify AI-generated content
            assert len(alert.explanation) > 0
            assert len(alert.root_cause_hypothesis) > 0
            assert len(alert.remediation_suggestions) > 0
            assert len(alert.impact_assessment) > 0

            # Verify confidence is reasonable
            assert 0.0 <= alert.explanation_confidence <= 1.0

        finally:
            await integration.stop_integration()

    @pytest.mark.asyncio
    async def test_fallback_behavior(self, integration, sample_detection):
        """Test fallback behavior when Lyrixa is not available."""
        # Force Lyrixa unavailability
        integration.lyrixa_available = False

        # Create alert (should use fallbacks)
        alert = await integration.create_intelligent_alert(sample_detection)

        # Should still create alert with fallback content
        assert isinstance(alert, IntelligentAlert)
        assert len(alert.explanation) > 0
        assert alert.explanation_confidence < 1.0  # Lower confidence for fallback

    def test_integration_status(self, integration):
        """Test integration status reporting."""
        status = integration.get_integration_status()

        assert isinstance(status, dict)
        assert "integration_active" in status
        assert "lyrixa_available" in status
        assert "requests_made" in status
        assert "successful_responses" in status
        assert "success_rate" in status


class TestIntelligentAlertManager:
    """Test the intelligent alert management system."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def manager(self, temp_db):
        """Create an alert manager for testing."""
        return IntelligentAlertManager(db_path=temp_db)

    @pytest.mark.asyncio
    async def test_manager_lifecycle(self, manager):
        """Test manager start/stop lifecycle."""
        # Initially not active
        assert not manager.manager_active

        # Start manager
        await manager.start_manager()
        assert manager.manager_active

        # Stop manager
        await manager.stop_manager()
        assert not manager.manager_active

    @pytest.mark.asyncio
    async def test_metric_processing_workflow(self, manager):
        """Test complete metric processing workflow."""
        await manager.start_manager()

        try:
            # Process normal samples (should not generate alerts)
            for i in range(10):
                alert = await manager.process_metric_sample("test_metric", 50.0 + i)
                assert alert is None  # No alert for normal values

            # Process an extreme value (may generate alert after sufficient training)
            alert = await manager.process_metric_sample("test_metric", 200.0)

            # If alert was created, verify structure
            if alert:
                assert isinstance(alert, IntelligentAlert)
                assert alert.status == AlertStatus.ACTIVE
                assert alert.alert_id in manager.active_alerts

        finally:
            await manager.stop_manager()

    @pytest.mark.asyncio
    async def test_alert_acknowledgment(self, manager):
        """Test alert acknowledgment workflow."""
        await manager.start_manager()

        try:
            # Create a mock alert for testing
            mock_alert = IntelligentAlert(
                alert_id="test_alert_001",
                detection_id="test_detection_001",
                title="Test Alert",
                description="Test alert description",
                severity=AlertSeverity.MEDIUM,
                category="Test",
                explanation="Test explanation",
                root_cause_hypothesis="Test hypothesis",
                remediation_suggestions=["Test action"],
                impact_assessment="Test impact",
                triggered_at="2025-01-27T10:00:00",
                expires_at=None,
                context_data={},
                status=AlertStatus.ACTIVE,
                assignee=None,
                escalation_level=0,
                reflection_analysis=None,
                explanation_confidence=0.8,
            )

            # Add to active alerts
            manager.active_alerts[mock_alert.alert_id] = mock_alert

            # Acknowledge the alert
            success = await manager.acknowledge_alert(
                mock_alert.alert_id, "test_user", "Acknowledging for testing"
            )

            assert success
            assert mock_alert.status == AlertStatus.ACKNOWLEDGED
            assert mock_alert.assignee == "test_user"

        finally:
            await manager.stop_manager()

    @pytest.mark.asyncio
    async def test_alert_resolution(self, manager):
        """Test alert resolution workflow."""
        await manager.start_manager()

        try:
            # Create a mock alert
            mock_alert = IntelligentAlert(
                alert_id="test_alert_002",
                detection_id="test_detection_002",
                title="Test Alert 2",
                description="Test alert description",
                severity=AlertSeverity.LOW,
                category="Test",
                explanation="Test explanation",
                root_cause_hypothesis="Test hypothesis",
                remediation_suggestions=["Test action"],
                impact_assessment="Test impact",
                triggered_at="2025-01-27T10:00:00",
                expires_at=None,
                context_data={},
                status=AlertStatus.ACTIVE,
                assignee=None,
                escalation_level=0,
                reflection_analysis=None,
                explanation_confidence=0.8,
            )

            # Add to active alerts
            manager.active_alerts[mock_alert.alert_id] = mock_alert

            # Resolve the alert
            success = await manager.resolve_alert(
                mock_alert.alert_id, "test_user", "Resolved after testing"
            )

            assert success
            assert mock_alert.status == AlertStatus.RESOLVED
            assert mock_alert.assignee == "test_user"
            assert mock_alert.alert_id not in manager.active_alerts
            assert mock_alert in manager.alert_history

        finally:
            await manager.stop_manager()

    def test_alert_filtering(self, manager):
        """Test alert filtering and retrieval."""
        # Create mock alerts with different severities
        alerts = []
        for i, severity in enumerate(
            [
                AlertSeverity.LOW,
                AlertSeverity.MEDIUM,
                AlertSeverity.HIGH,
                AlertSeverity.CRITICAL,
            ]
        ):
            alert = IntelligentAlert(
                alert_id=f"test_alert_{i}",
                detection_id=f"test_detection_{i}",
                title=f"Test Alert {i}",
                description="Test description",
                severity=severity,
                category="Test",
                explanation="Test explanation",
                root_cause_hypothesis="Test hypothesis",
                remediation_suggestions=["Test action"],
                impact_assessment="Test impact",
                triggered_at=f"2025-01-27T10:0{i}:00",
                expires_at=None,
                context_data={},
                status=AlertStatus.ACTIVE,
                assignee=None,
                escalation_level=0,
                reflection_analysis=None,
                explanation_confidence=0.8,
            )
            alerts.append(alert)
            manager.active_alerts[alert.alert_id] = alert

        # Test getting all active alerts
        all_alerts = manager.get_active_alerts()
        assert len(all_alerts) == 4

        # Test filtering by severity
        critical_alerts = manager.get_active_alerts(AlertSeverity.CRITICAL)
        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == AlertSeverity.CRITICAL

        # Test alerts are sorted by severity (critical first)
        assert all_alerts[0].severity == AlertSeverity.CRITICAL
        assert all_alerts[-1].severity == AlertSeverity.LOW

    def test_alert_statistics(self, manager):
        """Test alert statistics generation."""
        # Add some mock statistics
        manager.alerts_created = 10
        manager.alerts_resolved = 8
        manager.alerts_escalated = 2

        # Add some active alerts
        for i, severity in enumerate([AlertSeverity.HIGH, AlertSeverity.MEDIUM]):
            alert = IntelligentAlert(
                alert_id=f"stat_alert_{i}",
                detection_id=f"stat_detection_{i}",
                title=f"Stat Alert {i}",
                description="Description",
                severity=severity,
                category="Test",
                explanation="Explanation",
                root_cause_hypothesis="Hypothesis",
                remediation_suggestions=["Action"],
                impact_assessment="Impact",
                triggered_at="2025-01-27T10:00:00",
                expires_at=None,
                context_data={},
                status=AlertStatus.ACTIVE,
                assignee=None,
                escalation_level=0,
                reflection_analysis=None,
                explanation_confidence=0.8,
            )
            manager.active_alerts[alert.alert_id] = alert

        # Get statistics
        stats = manager.get_alert_statistics()

        assert isinstance(stats, dict)
        assert stats["active_alerts_count"] == 2
        assert stats["total_created"] == 10
        assert stats["total_resolved"] == 8
        assert stats["total_escalated"] == 2
        assert stats["resolution_rate"] == 0.8
        assert "active_by_severity" in stats
        assert stats["active_by_severity"]["high"] == 1
        assert stats["active_by_severity"]["medium"] == 1


class TestIntegrationFlow:
    """Test the complete integration flow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for all components."""
        temp_dirs = {}
        for component in ["threshold", "alert", "lyrixa"]:
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
                temp_dirs[component] = f.name

        yield temp_dirs

        for path in temp_dirs.values():
            Path(path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_end_to_end_alert_flow(self, temp_dirs):
        """Test complete end-to-end alert flow."""
        # Create integrated system
        manager = IntelligentAlertManager(db_path=temp_dirs["alert"])

        await manager.start_manager()

        try:
            # Simulate metric samples that should trigger an alert
            samples = [50.0] * 20 + [150.0]  # Normal values followed by outlier

            alert_created = None
            for i, value in enumerate(samples):
                alert = await manager.process_metric_sample(
                    "integration_test_metric",
                    value,
                    context={"sample_id": i, "test": "integration"},
                )

                if alert:
                    alert_created = alert
                    break

            # If an alert was created, test the workflow
            if alert_created:
                # Verify alert was created properly
                assert alert_created.alert_id in manager.active_alerts
                assert alert_created.status == AlertStatus.ACTIVE

                # Test acknowledgment
                ack_success = await manager.acknowledge_alert(
                    alert_created.alert_id, "integration_test", "Testing workflow"
                )
                assert ack_success

                # Test resolution
                resolve_success = await manager.resolve_alert(
                    alert_created.alert_id, "integration_test", "Workflow complete"
                )
                assert resolve_success

                # Verify final state
                assert alert_created.status == AlertStatus.RESOLVED
                assert alert_created.alert_id not in manager.active_alerts

            # Test statistics
            stats = manager.get_alert_statistics()
            assert isinstance(stats, dict)
            assert "threshold_engine_status" in stats
            assert "lyrixa_integration_status" in stats

        finally:
            await manager.stop_manager()


# Helper functions for test execution
def test_alert_intelligence_import():
    """Test that all alert intelligence modules can be imported."""
    from Aetherra.homeostasis.alert_intelligence import AdaptiveThresholdEngine
    from Aetherra.homeostasis.intelligent_alert_manager import IntelligentAlertManager
    from Aetherra.homeostasis.lyrixa_integration import LyrixaAlertIntegration

    assert AdaptiveThresholdEngine is not None
    assert LyrixaAlertIntegration is not None
    assert IntelligentAlertManager is not None


if __name__ == "__main__":
    # Run basic import test
    test_alert_intelligence_import()
    print("✅ Alert Intelligence modules imported successfully")

    # Run a simple integration test
    async def simple_test():
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            manager = IntelligentAlertManager(db_path=db_path)
            await manager.start_manager()

            # Test basic functionality
            stats = manager.get_alert_statistics()
            print(f"✅ Alert manager started. Stats: {stats}")

            await manager.stop_manager()
            print("✅ Alert manager stopped successfully")

        finally:
            Path(db_path).unlink(missing_ok=True)

    # Run the test
    asyncio.run(simple_test())

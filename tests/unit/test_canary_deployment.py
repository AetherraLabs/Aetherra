#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Unit tests for canary deployment functionality.

Tests the integrate_with_canary() method in Self-Incorporation service.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)


@pytest.fixture
def temp_config():
    """Create a temporary configuration for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = SelfIncorporationConfig()
        config.hmr_enabled = True
        config.index_db_path = temp_path / "test_index.db"
        config.index_jsonl_path = temp_path / "test_index.jsonl"
        config.audit_db_path = temp_path / "test_audit.db"
        yield config


@pytest.fixture
def mock_service(temp_config):
    """Create a mock Self-Incorporation service."""
    service = SelfIncorporationService(temp_config)

    # Mock service registry with HMR controller
    mock_registry = MagicMock()
    mock_hmr_info = MagicMock()
    mock_hmr_info.instance = MagicMock()
    mock_registry.get_service_info.return_value = mock_hmr_info

    service.service_registry = mock_registry

    return service


@pytest.mark.asyncio
async def test_canary_deployment_hmr_disabled(mock_service):
    """Test canary deployment fails gracefully when HMR is disabled."""
    mock_service.config.hmr_enabled = False

    result = await mock_service.integrate_with_canary()

    assert result["ok"] is False
    assert result["status"] == "error"
    assert result["error"] == "hmr_disabled"


@pytest.mark.asyncio
async def test_canary_deployment_plan_not_ready(mock_service):
    """Test canary deployment fails when plan is not ready."""
    # Mock planning to return a non-ready plan
    mock_plan = {"plan_id": "test_plan_123", "status": "blocked", "actions": []}

    with patch.object(
        mock_service, "_run_integration_planning", return_value=mock_plan
    ):
        result = await mock_service.integrate_with_canary()

        assert result["ok"] is False
        assert result["status"] == "error"
        assert result["error"] == "plan_not_ready"
        assert result["plan_status"] == "blocked"


@pytest.mark.asyncio
async def test_canary_deployment_baseline_health_too_low(mock_service):
    """Test canary deployment fails when baseline health is too low."""
    # Mock planning to return a ready plan
    mock_plan = {
        "plan_id": "test_plan_123",
        "status": "ready",
        "actions": [{"action": "register_plugin", "target": {"file_id": "test_123"}}],
    }

    with (
        patch.object(mock_service, "_run_integration_planning", return_value=mock_plan),
        patch.object(
            mock_service,
            "_get_system_health_score",
            return_value=0.7,  # Below default threshold of 0.9
        ),
    ):
        result = await mock_service.integrate_with_canary()

        assert result["ok"] is False
        assert result["status"] == "error"
        assert result["error"] == "baseline_health_too_low"
        assert result["baseline_health"] == 0.7


@pytest.mark.asyncio
async def test_canary_deployment_stable_dry_run(mock_service):
    """Test canary deployment succeeds in dry-run mode with stable health."""
    # Mock planning to return a ready plan
    mock_plan = {
        "plan_id": "test_plan_123",
        "status": "ready",
        "actions": [{"action": "register_plugin", "target": {"file_id": "test_123"}}],
    }

    with (
        patch.object(mock_service, "_run_integration_planning", return_value=mock_plan),
        patch.object(mock_service, "_get_system_health_score", return_value=0.95),
    ):
        result = await mock_service.integrate_with_canary(
            dry_run=True,
            canary_duration=0,  # Skip health monitoring for speed
        )

        assert result["ok"] is True
        assert result["status"] == "canary_stable"
        assert result["deployment"] == "canary_promoted"
        assert result["baseline_health"] == 0.95
        assert result["rollback_reason"] is None


@pytest.mark.asyncio
async def test_canary_deployment_auto_rollback_on_health_drop(mock_service):
    """Test automatic rollback when health drops below threshold."""
    # Mock planning to return a ready plan
    mock_plan = {
        "plan_id": "test_plan_123",
        "status": "ready",
        "actions": [{"action": "register_plugin", "target": {"file_id": "test_123"}}],
    }

    # Mock execution result
    mock_exec_result = {
        "ok": True,
        "applied": 1,
        "skipped": 0,
        "errors": 0,
    }

    # Mock health score: baseline 0.95, then drops to 0.85 (below threshold)
    health_values = [0.95, 0.85]  # Baseline, then after integration
    health_call_count = [0]

    async def mock_get_health():
        """Mock health score that changes over time."""
        idx = health_call_count[0]
        health_call_count[0] += 1
        if idx < len(health_values):
            return health_values[idx]
        return health_values[-1]

    # Mock rollback
    mock_rollback = AsyncMock(return_value={"ok": True})

    with (
        patch.object(mock_service, "_run_integration_planning", return_value=mock_plan),
        patch.object(
            mock_service, "_get_system_health_score", side_effect=mock_get_health
        ),
        patch.object(
            mock_service.core_integrator, "execute_plan", return_value=mock_exec_result
        ),
        patch.object(mock_service, "trigger_rollback", new=mock_rollback),
    ):
        # Set metrics to provide rollback token
        mock_service.metrics["last_rollback_token"] = "rb_test_token_123"

        result = await mock_service.integrate_with_canary(
            canary_duration=10,  # 10 seconds
            health_check_interval=10,  # Check once
            rollback_threshold=0.9,
        )

        assert result["ok"] is False
        assert result["status"] == "auto_rollback"
        assert result["deployment"] == "canary_failed"
        assert result["baseline_health"] == 0.95
        assert result["min_health"] == 0.85
        assert "health_below_threshold" in result["rollback_reason"]

        # Verify rollback was triggered
        mock_rollback.assert_called_once_with("rb_test_token_123")


@pytest.mark.asyncio
async def test_canary_deployment_configurable_parameters(mock_service):
    """Test canary deployment with custom parameters."""
    # Mock planning to return a ready plan
    mock_plan = {
        "plan_id": "test_plan_custom",
        "status": "ready",
        "actions": [{"action": "register_plugin", "target": {"file_id": "test_456"}}],
    }

    with (
        patch.object(mock_service, "_run_integration_planning", return_value=mock_plan),
        patch.object(mock_service, "_get_system_health_score", return_value=0.98),
    ):
        result = await mock_service.integrate_with_canary(
            canary_percent=0.2,  # 20% canary
            canary_duration=0,  # Skip monitoring for speed
            health_check_interval=5,
            rollback_threshold=0.85,  # Lower threshold
            dry_run=True,
        )

        assert result["ok"] is True
        assert result["status"] == "canary_stable"
        assert result["baseline_health"] == 0.98
        assert result["avg_health"] == 0.98


@pytest.mark.asyncio
async def test_canary_metrics_tracking(mock_service):
    """Test that canary deployment tracks success/failure metrics."""
    # Mock planning to return a ready plan
    mock_plan = {"plan_id": "test_plan_metrics", "status": "ready", "actions": []}

    with (
        patch.object(mock_service, "_run_integration_planning", return_value=mock_plan),
        patch.object(mock_service, "_get_system_health_score", return_value=0.95),
    ):
        # Initial metrics
        initial_successful = mock_service.metrics.get(
            "canary_deployments_successful", 0
        )

        # Successful canary
        result = await mock_service.integrate_with_canary(
            dry_run=True,
            canary_duration=0,
        )

        assert result["ok"] is True
        # Metrics not incremented in dry-run
        assert (
            mock_service.metrics.get("canary_deployments_successful", 0)
            == initial_successful
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

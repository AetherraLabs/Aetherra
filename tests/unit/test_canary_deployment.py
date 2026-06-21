#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Unit tests for canary deployment functionality.

Tests the integrate_with_canary() method in Self-Incorporation service.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)


@pytest.fixture
def temp_config(monkeypatch, tmp_path):
    """Create a temporary configuration for testing."""
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
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
    mock_hmr_info.instance.rollback_token.return_value = {"ok": True}
    mock_hmr_info.instance.supports_rollback_action.return_value = True
    mock_registry.get_service_info.return_value = mock_hmr_info

    service.service_registry = mock_registry

    return service


def _audit_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@pytest.mark.asyncio
async def test_canary_deployment_hmr_disabled(mock_service):
    """Test canary deployment fails gracefully when HMR is disabled."""
    mock_service.config.hmr_enabled = False

    result = await mock_service.integrate_with_canary()

    assert result["ok"] is False
    assert result["status"] == "error"
    assert result["error"] == "hmr_disabled"


@pytest.mark.asyncio
async def test_canary_deployment_blocks_hmr_without_token_rollback_support(
    mock_service,
):
    """Non-dry-run canary requires HMR token rollback support."""
    mock_hmr_info = MagicMock()
    mock_hmr_info.instance = object()
    mock_service.service_registry.get_service_info.return_value = mock_hmr_info
    mock_plan = {
        "plan_id": "test_plan_rollback_unsupported",
        "status": "ready",
        "actions": [{"action": "register_plugin", "target": {"file_id": "test_123"}}],
    }

    with patch.object(
        mock_service, "_run_integration_planning", return_value=mock_plan
    ):
        result = await mock_service.integrate_with_canary(dry_run=False)

    assert result["ok"] is False
    assert result["status"] == "error"
    assert (
        result["error"]
        == "rollback_unavailable:register_plugin:hmr_token_rollback_unsupported"
    )


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
async def test_canary_deployment_writes_guardian_audit_without_raw_plan_ids(
    mock_service, tmp_path
):
    """Canary deployment must pass through Guardian without leaking plan IDs."""
    mock_plan = {
        "plan_id": "plan-do-not-audit-this-value",
        "status": "ready",
        "actions": [{"action": "register_plugin", "target": {"file_id": "test_456"}}],
    }

    with (
        patch.object(mock_service, "_run_integration_planning", return_value=mock_plan),
        patch.object(mock_service, "_get_system_health_score", return_value=0.98),
    ):
        result = await mock_service.integrate_with_canary(
            plan_id="tracking-do-not-audit-this-value",
            canary_duration=0,
            dry_run=True,
        )

    entries = _audit_entries(tmp_path)
    audit_json = json.dumps(entries[-1])

    assert result["ok"] is True
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.canary_deploy"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in audit_json


@pytest.mark.asyncio
async def test_canary_deployment_blocks_external_requester_without_capability(
    monkeypatch, mock_service, tmp_path
):
    """Strict capability mode must stop untrusted operators before execution."""
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    mock_plan = {
        "plan_id": "test_plan_denied",
        "status": "ready",
        "actions": [{"action": "register_plugin", "target": {"file_id": "test_456"}}],
    }

    with (
        patch.object(mock_service, "_run_integration_planning", return_value=mock_plan),
        patch.object(
            mock_service, "_get_system_health_score", new=AsyncMock()
        ) as health_score,
        patch.object(
            mock_service.core_integrator, "execute_plan", new=AsyncMock()
        ) as execute_plan,
    ):
        result = await mock_service.integrate_with_canary(
            canary_duration=0,
            dry_run=False,
            requester="untrusted_operator",
        )

    assert result["ok"] is False
    assert result["error"].startswith("guardian_denied:missing_capability")
    assert health_score.await_count == 0
    assert execute_plan.await_count == 0


@pytest.mark.asyncio
async def test_canary_rollback_writes_guardian_audit_without_raw_token(
    mock_service, tmp_path
):
    """Rollback must be Guardian-audited without storing the raw rollback token."""
    rollback_token = "rb_do-not-audit-this-value"
    mock_service._workflows = {
        "workflow-test": {
            "path": None,
            "file_id": "workflow-test",
            "rollback_token": rollback_token,
        }
    }
    mock_service.audit_ledger.append(
        plan_id="test-plan",
        action="register_workflow",
        status="applied",
        target={"plan_id": "test-plan"},
        result={"name": "workflow-test", "rollback_token": rollback_token},
    )

    result = await mock_service.trigger_rollback(rollback_token)
    entries = _audit_entries(tmp_path)
    audit_json = json.dumps(entries[-1])

    assert result["ok"] is True
    assert "workflow-test" not in mock_service._workflows
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.rollback"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert rollback_token not in audit_json
    assert "do-not-audit-this-value" not in audit_json


@pytest.mark.asyncio
async def test_canary_rollback_blocks_external_requester_before_audit_mutation(
    monkeypatch, mock_service, tmp_path
):
    """Denied rollback requests must not append self-incorporation rollback records."""
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    rollback_token = "rb_test_denied"
    mock_service.audit_ledger.append(
        plan_id="test-plan",
        action="integration_plan",
        status="applied",
        target={"plan_id": "test-plan"},
        result={"rollback_token": rollback_token},
    )
    before = len(mock_service.audit_ledger.recent(limit=100))

    result = await mock_service.trigger_rollback(
        rollback_token,
        requester="untrusted_operator",
    )
    after = len(mock_service.audit_ledger.recent(limit=100))

    assert result["ok"] is False
    assert result["error"].startswith("guardian_denied:missing_capability")
    assert after == before


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

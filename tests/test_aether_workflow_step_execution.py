#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Tests for workflow step execution, parameter validation, and context management."""

import pytest

import aetherra_script_service


class TestWorkflowStepExecution:
    """Test workflow step execution mechanics."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        return aetherra_script_service.AetherScriptService()

    def test_normalize_duration_milliseconds(self, service):
        """Test _normalize_duration with milliseconds."""
        result = service._normalize_duration("100ms")
        assert result == 0.1

    def test_normalize_duration_seconds(self, service):
        """Test _normalize_duration with seconds."""
        result = service._normalize_duration("5s")
        assert result == 5.0

    def test_normalize_duration_minutes(self, service):
        """Test _normalize_duration with minutes."""
        result = service._normalize_duration("2m")
        assert result == 120.0

    def test_normalize_duration_hours(self, service):
        """Test _normalize_duration with hours."""
        result = service._normalize_duration("1h")
        assert result == 3600.0

    def test_normalize_duration_plain_number(self, service):
        """Test _normalize_duration with plain number (seconds)."""
        result = service._normalize_duration("30")
        assert result == 30.0

    def test_normalize_duration_float(self, service):
        """Test _normalize_duration with float value."""
        result = service._normalize_duration("0.5s")
        assert result == 0.5

    def test_normalize_duration_invalid_format(self, service):
        """Test _normalize_duration with invalid format."""
        result = service._normalize_duration("invalid")
        assert result is None

    def test_normalize_duration_empty_string(self, service):
        """Test _normalize_duration with empty string."""
        result = service._normalize_duration("")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_workflow_step_success(self, service):
        """Test _execute_workflow_step successful execution."""
        step = {"name": "test_step"}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is True
        assert result["attempts"] == 1
        assert "result" in result
        assert "duration_ms" in result
        assert "start_time" in result
        assert "end_time" in result

    @pytest.mark.asyncio
    async def test_execute_workflow_step_with_retry_success(self, service):
        """Test _execute_workflow_step with retry count."""
        step = {"name": "test_step", "retry": 2}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is True
        assert result["attempts"] == 1  # Success on first try
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_workflow_step_failure(self, service):
        """Test _execute_workflow_step with simulated failure."""
        step = {"name": "fail_step"}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is False
        assert result["attempts"] == 1
        assert "error" in result
        assert "Simulated failure" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_workflow_step_timeout(self, service):
        """Test _execute_workflow_step with timeout enforcement."""
        step = {"name": "slow_step", "timeout_secs": 0.1}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is False
        assert "error" in result
        assert "Timeout" in result["error"] or "timeout" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_workflow_step_timeout_from_raw_string(self, service):
        """Test _execute_workflow_step with raw timeout string."""
        step = {"name": "slow_step", "timeout": "0.1s"}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_workflow_step_preserves_step_data(self, service):
        """Test that execution preserves original step data."""
        step = {
            "name": "test_step",
            "args": [1, 2, 3],
            "kwargs": {"key": "value"},
            "as": "result_alias",
        }
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["name"] == "test_step"
        assert result["args"] == [1, 2, 3]
        assert result["kwargs"] == {"key": "value"}
        assert result["as"] == "result_alias"

    @pytest.mark.asyncio
    async def test_execute_workflow_step_timing_metadata(self, service):
        """Test that execution includes accurate timing metadata."""
        step = {"name": "test_step"}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert "start_time" in result
        assert "end_time" in result
        assert "duration_ms" in result
        assert result["end_time"] >= result["start_time"]
        assert result["duration_ms"] >= 0

    @pytest.mark.asyncio
    async def test_execute_workflow_step_multiple_retries(self, service):
        """Test step execution with multiple retry attempts."""
        step = {"name": "fail_step", "retry": 3}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is False
        assert result["attempts"] == 4  # Initial attempt + 3 retries
        assert "error" in result

    def test_normalize_duration_with_whitespace(self, service):
        """Test _normalize_duration handles whitespace."""
        result = service._normalize_duration("  10s  ")
        assert result == 10.0

    def test_normalize_duration_fractional_milliseconds(self, service):
        """Test _normalize_duration with fractional milliseconds."""
        result = service._normalize_duration("500.5ms")
        assert result == 0.5005

    @pytest.mark.asyncio
    async def test_execute_workflow_step_no_timeout(self, service):
        """Test step execution without timeout constraint."""
        step = {"name": "test_step"}  # No timeout specified
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is True
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_workflow_step_zero_retry(self, service):
        """Test step execution with explicit zero retry."""
        step = {"name": "fail_step", "retry": 0}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is False
        assert result["attempts"] == 1  # No retries, just initial attempt

    @pytest.mark.asyncio
    async def test_execute_workflow_step_result_value(self, service):
        """Test that step execution returns expected result value."""
        step = {"name": "custom_step"}
        context = {}
        result = await service._execute_workflow_step(step, context)

        assert result["success"] is True
        assert result["result"] == "result_custom_step"

    @pytest.mark.asyncio
    async def test_execute_workflow_step_unknown_name(self, service):
        """Test step execution with unknown step name."""
        step = {"name": "unknown_step"}
        context = {}
        result = await service._execute_workflow_step(step, context)

        # Should still succeed with placeholder implementation
        assert result["success"] is True
        assert "result_unknown_step" in result.get("result", "")

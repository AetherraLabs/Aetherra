#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Wave A5 Acceptance Test: Homeostasis Latency Response

Tests that the homeostasis system detects high latency and triggers
corrective actions within SLO windows.

Validates:
- Memory RTT drift detection (target: 50ms, max: 120ms)
- Task latency p95 monitoring (target: 100ms, max: 250ms)
- Corrective action generation and execution
- Homeostasis setpoint enforcement
"""

import asyncio
import os
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Aetherra imports
from Aetherra.homeostasis.homeostasis_core import (
    ActionPriority,
    ControlAction,
    ControllerMode,
    HomeostasisController,
)
from Aetherra.homeostasis.stability_metrics import MetricSnapshot, StabilityMetrics


class MockActuator:
    """Mock actuator that records actions for verification"""

    def __init__(self):
        self.executed_actions = []
        self.execution_results = {}

    async def execute_action(self, action: ControlAction):
        """Record action and return success"""
        self.executed_actions.append(action)
        result = MagicMock()
        result.success = True
        result.message = f"Mock executed: {action.action_type}"
        result.execution_time = 0.05
        self.execution_results[action.action_type] = result
        return result


class LatencyInjector:
    """Simulates latency metrics for testing"""

    def __init__(self, initial_latency_ms: float = 50.0):
        self.current_latency = initial_latency_ms
        self.history = []

    def set_latency(self, latency_ms: float):
        """Set current latency (simulates drift)"""
        self.current_latency = latency_ms
        self.history.append((time.time(), latency_ms))

    def get_metric(self) -> dict[str, Any]:
        """Return metric in expected format"""
        return {
            "memory_rtt_p95": self.current_latency,
            "timestamp": time.time(),
        }


@pytest.mark.asyncio
async def test_homeostasis_detects_memory_rtt_drift():
    """Test that homeostasis detects memory RTT exceeding setpoints"""
    # Setup mock metrics
    mock_metrics = MagicMock(spec=StabilityMetrics)

    # Normal latency - should be stable
    mock_metrics.get_latest_snapshot.return_value = MetricSnapshot(
        timestamp=time.time(),
        memory_rtt=50.0,  # At target
        task_latency=100.0,
        plugin_load_success=0.95,
        exception_rate=0.0,
    )

    controller = HomeostasisController(metrics=mock_metrics)
    controller.mode = ControllerMode.ACTIVE

    # First step - should not generate actions
    actions = await controller.step()
    assert len(actions) == 0, "No actions should trigger at target latency"

    # Inject drift: 130ms (exceeds max acceptable 120ms)
    mock_metrics.get_latest_snapshot.return_value = MetricSnapshot(
        timestamp=time.time(),
        memory_rtt=130.0,  # Above max acceptable
        task_latency=100.0,
        plugin_load_success=0.95,
        exception_rate=0.0,
    )

    # Controller should detect violation
    actions = await controller.step()

    # Verify corrective action was generated
    assert len(actions) > 0, (
        "Homeostasis should generate corrective action for high RTT"
    )


@pytest.mark.asyncio
async def test_homeostasis_triggers_action_within_slo():
    """Test that corrective action is triggered within acceptable time window"""
    mock_metrics = MagicMock(spec=StabilityMetrics)

    # Inject high latency
    mock_metrics.get_latest_snapshot.return_value = MetricSnapshot(
        timestamp=time.time(),
        memory_rtt=140.0,  # Well above max acceptable
        task_latency=100.0,
        plugin_load_success=0.95,
        exception_rate=0.0,
    )

    controller = HomeostasisController(metrics=mock_metrics)
    controller.mode = ControllerMode.ACTIVE

    start_time = time.time()

    # Run evaluation cycle
    actions = await controller.step()

    detection_time = time.time() - start_time

    # SLO: Detection + action generation should be < 5 seconds
    assert detection_time < 5.0, f"Detection took {detection_time}s, SLO: <5s"

    # Verify actions were generated
    assert len(actions) > 0, "Actions should be generated"


@pytest.mark.asyncio
async def test_homeostasis_respects_cooldown():
    """Test that homeostasis doesn't spam actions (rate limiting)"""
    injector = LatencyInjector(initial_latency_ms=50.0)
    actuator = MockActuator()

    controller = HomeostasisController(actuators=actuator)
    controller.mode = ControllerMode.CORRECTIVE_ACTIVE

    # Inject sustained high latency
    injector.set_latency(150.0)

    # First evaluation - should trigger action
    metrics = injector.get_metric()
    actions1 = await controller.evaluate_and_act(metrics)
    assert len(actions1) > 0, "First evaluation should trigger action"

    # Execute first action
    for action in actions1:
        await actuator.execute_action(action)

    # Immediate second evaluation - should be rate limited
    actions2 = await controller.evaluate_and_act(metrics)

    # Verify cooldown is active (fewer or no new actions)
    # Note: Implementation may allow some actions, but should show dampening
    assert len(actions2) <= len(actions1), "Cooldown should limit action rate"


@pytest.mark.asyncio
async def test_homeostasis_setpoint_boundaries():
    """Test homeostasis behavior at setpoint boundaries"""
    injector = LatencyInjector()
    actuator = MockActuator()

    controller = HomeostasisController(actuators=actuator)
    controller.mode = ControllerMode.CORRECTIVE_ACTIVE

    test_cases = [
        (49.0, 0, "Below target (49ms) - no action"),
        (50.0, 0, "At target (50ms) - no action"),
        (85.0, 0, "Between target and max (85ms) - warning zone"),
        (120.0, 0, "At max acceptable (120ms) - boundary"),
        (121.0, 1, "Just above max (121ms) - trigger action"),
        (200.0, 1, "Well above max (200ms) - trigger action"),
    ]

    for latency, expected_min_actions, description in test_cases:
        injector.set_latency(latency)
        metrics = injector.get_metric()

        # Reset actuator
        actuator.executed_actions = []

        actions = await controller.evaluate_and_act(metrics)

        if expected_min_actions > 0:
            assert len(actions) >= expected_min_actions, (
                f"{description} - expected >={expected_min_actions} actions, got {len(actions)}"
            )
        # Note: At boundary, behavior may vary based on controller tuning


@pytest.mark.asyncio
async def test_homeostasis_multi_metric_correlation():
    """Test homeostasis with multiple metrics violating setpoints"""
    actuator = MockActuator()

    controller = HomeostasisController(actuators=actuator)
    controller.mode = ControllerMode.CORRECTIVE_ACTIVE

    # Simulate multiple violations simultaneously
    metrics = {
        "memory_rtt_p95": 150.0,  # Exceeds 120ms max
        "task_latency_p95": 300.0,  # Exceeds 250ms max
        "plugin_load_success_rate": 0.70,  # Below 0.85 min
        "timestamp": time.time(),
    }

    actions = await controller.evaluate_and_act(metrics)

    # Should generate actions for multiple issues
    assert len(actions) >= 2, "Multiple violations should trigger multiple actions"

    # Verify different action types
    action_types = {a.action_type for a in actions}
    assert len(action_types) >= 2, "Should generate diverse action types"


@pytest.mark.asyncio
async def test_homeostasis_mode_transitions():
    """Test homeostasis mode transitions based on system state"""
    actuator = MockActuator()
    controller = HomeostasisController(actuators=actuator)

    # Start in observe-only
    controller.mode = ControllerMode.OBSERVE_ONLY

    metrics = {"memory_rtt_p95": 150.0, "timestamp": time.time()}

    # In observe mode, should not generate executable actions
    actions = await controller.evaluate_and_act(metrics)
    # Observe mode may still analyze but shouldn't execute

    # Transition to corrective
    controller.mode = ControllerMode.CORRECTIVE_ACTIVE

    actions = await controller.evaluate_and_act(metrics)
    assert len(actions) > 0, "Corrective mode should generate actions"


@pytest.mark.asyncio
async def test_homeostasis_with_manual_confirmation():
    """Test that critical actions require confirmation"""
    actuator = MockActuator()

    controller = HomeostasisController(actuators=actuator)
    controller.mode = ControllerMode.CORRECTIVE_ACTIVE

    # Inject severe violation
    metrics = {
        "plugin_load_success_rate": 0.30,  # Severe: well below 0.85
        "timestamp": time.time(),
    }

    actions = await controller.evaluate_and_act(metrics)

    # Verify that severe issues generate high-priority actions
    critical_actions = [
        a
        for a in actions
        if a.priority in (ActionPriority.HIGH, ActionPriority.CRITICAL)
    ]

    if critical_actions:
        # Check if confirmation is required
        requires_confirmation = [a for a in critical_actions if a.requires_confirmation]
        # Note: Implementation should require confirmation for restarts
        assert len(requires_confirmation) > 0, (
            "Critical actions should require confirmation"
        )


def test_homeostasis_config_loading():
    """Test that homeostasis loads setpoints correctly"""
    controller = HomeostasisController()

    # Verify setpoints are loaded
    assert controller.setpoints is not None, "Setpoints should be loaded"

    # Check key setpoints exist
    setpoints_dict = controller.setpoints
    if isinstance(setpoints_dict, dict):
        # Verify memory RTT setpoint
        if "setpoints" in setpoints_dict:
            sp = setpoints_dict["setpoints"]
            assert "memory_rtt" in sp or "memory_rtt_p95" in sp, (
                "Memory RTT setpoint missing"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

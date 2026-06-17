#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Wave A5 Acceptance Test: Homeostasis System Validation

Minimal integration test verifying homeostasis system is operational
and configured correctly for production deployment.

Validates:
- Homeostasis controller initializes correctly
- Setpoints are loaded from configuration
- Control loops are created for key metrics
- Mode transitions work as expected
- System responds within SLO time windows
"""

import asyncio
import time
from pathlib import Path

import pytest

# Aetherra imports
from Aetherra.homeostasis.homeostasis_core import ControllerMode, HomeostasisController


@pytest.fixture(autouse=True)
def isolate_homeostasis_security_state(monkeypatch):
    """Keep controller behavior tests independent from persisted lockdown state."""
    monkeypatch.setenv(
        "AETHERRA_WORKSPACE_ROOT",
        str(Path.cwd() / ".pytest_homeostasis_wave_a5"),
    )
    monkeypatch.delenv("AETHERRA_SAFE_MODE", raising=False)
    monkeypatch.delenv("AETHERRA_HOMEOSTASIS_RESTRICTED", raising=False)


def test_homeostasis_initialization():
    """Test that homeostasis controller initializes with valid configuration"""
    controller = HomeostasisController()

    # Verify controller is initialized
    assert controller is not None, "Controller should initialize"
    assert controller.setpoints is not None, "Setpoints should be loaded"
    assert controller.control_loops is not None, "Control loops should be initialized"

    # Verify default mode
    assert controller.mode == ControllerMode.OBSERVE_ONLY, (
        "Should start in observe-only mode"
    )

    # Verify key control loops exist
    loop_names = list(controller.control_loops.keys())
    assert len(loop_names) > 0, "Should have control loops configured"

    # Check for expected control loops
    expected_loops = [
        "memory_rtt_control",
        "task_latency_control",
        "plugin_success_control",
    ]
    for loop_name in expected_loops:
        assert loop_name in loop_names, f"Missing expected control loop: {loop_name}"


def test_homeostasis_setpoints_loaded():
    """Test that setpoints are loaded correctly from configuration"""
    controller = HomeostasisController()

    setpoints = controller.setpoints

    # Verify core setpoints exist
    assert (
        "core_metrics" in setpoints
        or "cognitive_metrics" in setpoints
        or "setpoints" in setpoints
    ), "Setpoints should contain metric configurations"

    # Verify control parameters
    control_params = setpoints.get("control_parameters", {})
    assert control_params is not None, "Control parameters should be loaded"


def test_homeostasis_mode_transitions():
    """Test that controller mode transitions work correctly"""
    controller = HomeostasisController()

    # Start in observe-only
    assert controller.mode == ControllerMode.OBSERVE_ONLY

    # Transition to advisory
    controller.set_mode(ControllerMode.ADVISORY)
    assert controller.mode == ControllerMode.ADVISORY

    # Transition to active
    controller.set_mode(ControllerMode.ACTIVE)
    assert controller.mode == ControllerMode.ACTIVE

    # Emergency stop should force disabled
    controller.emergency_stop()
    assert controller._emergency_stop is True

    # Reset emergency stop
    controller.reset_emergency_stop()
    assert controller._emergency_stop is False


@pytest.mark.asyncio
async def test_homeostasis_step_execution_time():
    """Test that controller step executes within SLO time window"""
    controller = HomeostasisController()
    controller.mode = ControllerMode.ACTIVE

    start_time = time.time()

    # Execute a single control cycle
    actions = await controller.step()

    execution_time = time.time() - start_time

    # SLO: Step execution should complete in < 5 seconds
    assert execution_time < 5.0, f"Step execution took {execution_time}s, SLO: <5s"

    # Verify actions is a list (may be empty if no corrections needed)
    assert isinstance(actions, list), "Step should return list of actions"


@pytest.mark.asyncio
async def test_homeostasis_control_loop_state():
    """Test that control loops maintain proper state"""
    controller = HomeostasisController()
    controller.mode = ControllerMode.ACTIVE

    # Get initial state
    loop_status = controller.get_control_loop_status()
    # The method returns the loop dict directly, not wrapped
    assert isinstance(loop_status, dict), "Should return dict of control loops"
    assert len(loop_status) > 0, "Should have control loops"

    # Execute a step to update state
    await controller.step()

    # Verify state was updated
    updated_status = controller.get_control_loop_status()
    assert isinstance(updated_status, dict), "Status should still be a dict"
    assert len(updated_status) > 0, "Should still have control loops"


def test_homeostasis_policy_loading():
    """Test that policy constraints are loaded"""
    controller = HomeostasisController()

    policy = controller.policy
    assert policy is not None, "Policy should be loaded"

    # Verify policy has expected structure
    # (actual policy structure depends on config file)
    assert isinstance(policy, dict), "Policy should be a dictionary"


@pytest.mark.asyncio
async def test_homeostasis_emergency_stop_blocks_actions():
    """Test that emergency stop prevents action execution"""
    controller = HomeostasisController()
    controller.mode = ControllerMode.ACTIVE

    # Trigger emergency stop
    controller.emergency_stop()

    # Attempt to execute step
    actions = await controller.step()

    # Emergency stop should prevent actions
    assert len(actions) == 0, "Emergency stop should block all actions"


def test_homeostasis_status_reporting():
    """Test that controller provides comprehensive status"""
    controller = HomeostasisController()

    status = controller.get_controller_status()

    # Verify status includes key information
    assert "mode" in status, "Status should include mode"
    assert "running" in status, "Status should include running state"
    assert "emergency_stop" in status, "Status should include emergency stop state"

    # Verify mode is reported correctly
    assert status["mode"] == ControllerMode.OBSERVE_ONLY.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

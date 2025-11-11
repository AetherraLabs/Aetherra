#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧪 Homeostasis Test Infrastructure
==================================

Basic test structure and utilities for testing the Aetherra Homeostasis system.
Provides test fixtures, mocks, and utilities for unit and integration testing.

Author: Aetherra Labs
"""

# Standard library imports
import asyncio
import time
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock

# Test imports
import pytest

from Aetherra.homeostasis.homeostasis_actuators import (  # type: ignore
    ActuatorResult,
    HomeostasisActuators,
)
from Aetherra.homeostasis.homeostasis_core import (  # type: ignore
    ControllerMode,
    HomeostasisController,
)

# Aetherra imports
from Aetherra.homeostasis.stability_metrics import (  # type: ignore
    MetricSnapshot,
    StabilityMetrics,
)
from Aetherra.homeostasis.system_supervisor import (  # type: ignore
    SystemRunlevel,
    SystemSupervisor,
)


class MockServiceRegistry:
    """Mock service registry for testing."""

    def __init__(self):
        self.services = {}
        self.running = True

    def get_service_info(self, service_name: str):
        return self.services.get(service_name)

    async def broadcast_message(self, message_type: str, data: dict[str, Any]):
        pass


class MockMetricsSnapshot:
    """Mock metrics snapshot for testing."""

    def __init__(self, **kwargs):
        self.timestamp = kwargs.get("timestamp", time.time())
        self.task_throughput = kwargs.get("task_throughput", 10.0)
        self.task_latency = kwargs.get("task_latency", 100.0)
        self.queue_depth = kwargs.get("queue_depth", 5.0)
        self.memory_rtt = kwargs.get("memory_rtt", 50.0)
        self.memory_timeouts = kwargs.get("memory_timeouts", 0.0)
        self.exception_suppression = kwargs.get("exception_suppression", 0.0)
        self.plugin_load_success = kwargs.get("plugin_load_success", 95.0)
        self.plugin_timeout_rate = kwargs.get("plugin_timeout_rate", 1.0)
        self.hub_connection = kwargs.get("hub_connection", 1.0)
        self.hub_websocket_status = kwargs.get("hub_websocket_status", 1.0)
        self.gui_heartbeat = kwargs.get("gui_heartbeat", 1.0)
        self.gui_responsiveness = kwargs.get("gui_responsiveness", 100.0)
        self.learning_rate = kwargs.get("learning_rate", 0.01)
        self.learning_cycle_time = kwargs.get("learning_cycle_time", 300.0)
        self.confidence_level = kwargs.get("confidence_level", 0.8)
        self.uncertainty_level = kwargs.get("uncertainty_level", 0.1)
        self.model_fallback_rate = kwargs.get("model_fallback_rate", 0.0)
        self.reflection_stability = kwargs.get("reflection_stability", 0.9)
        self.registry_health = kwargs.get("registry_health", 1.0)
        self.service_count = kwargs.get("service_count", 8.0)
        self.kernel_loop_health = kwargs.get("kernel_loop_health", 1.0)
        self.os_runlevel = kwargs.get("os_runlevel", "ONLINE")
        self.raw_data = kwargs.get("raw_data", {})


@pytest.fixture
def mock_service_registry():
    """Provide a mock service registry for tests."""
    return MockServiceRegistry()


@pytest.fixture
def healthy_metrics_snapshot():
    """Provide a healthy metrics snapshot for tests."""
    return MockMetricsSnapshot()


@pytest.fixture
def degraded_metrics_snapshot():
    """Provide a degraded metrics snapshot for tests."""
    return MockMetricsSnapshot(
        plugin_load_success=75.0,  # Below target
        memory_rtt=150.0,  # Above target
        task_latency=250.0,  # Above target
        exception_suppression=10.0,  # Above target
    )


@pytest.fixture
def failed_metrics_snapshot():
    """Provide a failed metrics snapshot for tests."""
    return MockMetricsSnapshot(
        hub_connection=0.0,
        registry_health=0.0,
        plugin_load_success=30.0,
        memory_rtt=500.0,
        task_latency=1000.0,
        os_runlevel="FAILED",
    )


@pytest.fixture
def mock_stability_metrics():
    """Provide a mock stability metrics collector."""
    metrics = Mock(spec=StabilityMetrics)
    metrics.get_current_snapshot = Mock(return_value=MockMetricsSnapshot())
    metrics.collect_snapshot = AsyncMock(return_value=MockMetricsSnapshot())
    metrics.get_health_summary = Mock(
        return_value={
            "status": "healthy",
            "health_score": 95.0,
            "total_metrics": 10,
            "healthy_metrics": 9,
            "out_of_bounds_metrics": [],
        }
    )
    return metrics


@pytest.fixture
def mock_actuators():
    """Provide a mock actuators system."""
    actuators = Mock(spec=HomeostasisActuators)
    actuators.execute_action = AsyncMock(return_value=True)
    actuators.get_actuator_status = Mock(
        return_value={
            "actions_executed": 5,
            "rollback_actions_available": 3,
        }
    )
    actuators.get_action_history = Mock(return_value=[])
    return actuators


@pytest.fixture
def homeostasis_controller(mock_stability_metrics, mock_actuators):
    """Provide a homeostasis controller for tests."""
    controller = HomeostasisController(
        metrics=mock_stability_metrics, actuators=mock_actuators
    )
    # Don't start the actual control loop in tests
    controller.control_interval = 0.1  # Fast interval for tests
    return controller


@pytest.fixture
def system_supervisor():
    """Provide a system supervisor for tests."""
    supervisor = SystemSupervisor()
    supervisor.health_check_interval = 0.1  # Fast interval for tests
    return supervisor


class TestUtils:
    """Utilities for homeostasis testing."""

    @staticmethod
    def create_test_action(action_type: str = "test_action", success: bool = True):
        """Create a test control action."""
        from Aetherra.homeostasis.homeostasis_core import (  # type: ignore
            ActionPriority,
            ControlAction,
        )

        return ControlAction(
            action_type=action_type,
            target_service="test_service",
            parameters={"test": True},
            priority=ActionPriority.MEDIUM,
            timestamp=time.time(),
            controller_name="test_controller",
            reason="Test action",
        )

    @staticmethod
    def create_test_actuator_result(success: bool = True, message: str = "Test result"):
        """Create a test actuator result."""
        return ActuatorResult(
            success=success,
            message=message,
            rollback_data={"test": "data"} if success else None,
            execution_time=0.1,
        )

    @staticmethod
    async def wait_for_condition(
        condition_func, timeout: float = 5.0, interval: float = 0.1
    ):
        """Wait for a condition to become true."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            await asyncio.sleep(interval)
        return False


# Integration test helpers


async def setup_test_homeostasis_system():
    """Set up a complete homeostasis system for integration tests."""
    from Aetherra.homeostasis.homeostasis_integration import (
        HomeostasisOrchestrator,  # type: ignore
    )

    orchestrator = HomeostasisOrchestrator()

    # Use mock components for testing
    orchestrator.metrics = Mock(spec=StabilityMetrics)
    orchestrator.actuators = Mock(spec=HomeostasisActuators)
    orchestrator.controller = Mock(spec=HomeostasisController)
    orchestrator.supervisor = Mock(spec=SystemSupervisor)

    # Mock the async methods
    orchestrator.metrics.collect_snapshot = AsyncMock(
        return_value=MockMetricsSnapshot()
    )
    orchestrator.actuators.execute_action = AsyncMock(return_value=True)

    return orchestrator


def assert_metrics_within_bounds(snapshot: MetricSnapshot, bounds: dict[str, float]):
    """Assert that metrics are within specified bounds."""
    for metric_name, max_value in bounds.items():
        metric_value = getattr(snapshot, metric_name, None)
        if metric_value is not None:
            assert metric_value <= max_value, (
                f"{metric_name} ({metric_value}) exceeds bound ({max_value})"
            )


def assert_runlevel_transition(
    supervisor: SystemSupervisor, expected_level: SystemRunlevel
):
    """Assert that supervisor has transitioned to expected runlevel."""
    assert supervisor.get_runlevel() == expected_level


def assert_controller_mode(
    controller: HomeostasisController, expected_mode: ControllerMode
):
    """Assert that controller is in expected mode."""
    assert controller.mode == expected_mode

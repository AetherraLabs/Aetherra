#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧪 Multi-Node Homeostasis Coordination Tests
============================================

Comprehensive test suite for multi-node homeostasis coordination system.
Tests cluster discovery, distributed coordination, assistance protocols,
and integration with local homeostasis systems.

Author: Aetherra Labs
"""

import asyncio
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the modules we're testing
from Aetherra.homeostasis.multi_node_coordination import (
    ClusterDiscovery,
    ClusterNode,
    DistributedAction,
    DistributedHomeostasisCoordinator,
    DistributedStabilitySignal,
    NodeState,
    initialize_multi_node_coordination,
)
from Aetherra.homeostasis.multi_node_integration import (
    MultiNodeHomeostasisIntegration,
    get_multi_node_integration,
)


class TestClusterDiscovery:
    """Test cluster discovery functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.discovery = ClusterDiscovery(
            node_id="test_node_1",
            discovery_port=8766,  # Use different port for testing
            heartbeat_interval=1.0,  # Faster for testing
        )

    def teardown_method(self):
        """Clean up after tests."""
        if self.discovery.discovery_active:
            asyncio.run(self.discovery.stop_discovery())

    def test_cluster_discovery_initialization(self):
        """Test cluster discovery initialization."""
        assert self.discovery.node_id == "test_node_1"
        assert self.discovery.discovery_port == 8766
        assert self.discovery.heartbeat_interval == 1.0
        assert not self.discovery.discovery_active
        assert len(self.discovery.cluster_nodes) == 0
        assert self.discovery.local_node is None

    @pytest.mark.asyncio
    async def test_start_stop_discovery(self):
        """Test starting and stopping discovery."""
        # Start discovery
        await self.discovery.start_discovery(
            advertise_address="localhost", seed_nodes=[]
        )

        assert self.discovery.discovery_active
        assert self.discovery.local_node is not None
        assert self.discovery.local_node.node_id == "test_node_1"
        assert self.discovery.local_node.hostname == "localhost"
        assert self.discovery.local_node.node_state == NodeState.HEALTHY
        assert len(self.discovery.cluster_nodes) == 1  # Self

        # Stop discovery
        await self.discovery.stop_discovery()

        assert not self.discovery.discovery_active

    def test_get_cluster_status(self):
        """Test cluster status reporting."""
        # Add mock nodes
        self.discovery.cluster_nodes = {
            "node1": ClusterNode(
                node_id="node1",
                hostname="host1",
                port=8765,
                protocol="tcp",
                node_state=NodeState.HEALTHY,
                stability_score=0.8,
                load_level=0.3,
                resource_utilization={"cpu": 0.3},
                error_rate=0.01,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis"],
                available_for_assistance=True,
                cluster_role="worker",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            ),
            "node2": ClusterNode(
                node_id="node2",
                hostname="host2",
                port=8765,
                protocol="tcp",
                node_state=NodeState.DEGRADED,
                stability_score=0.5,
                load_level=0.7,
                resource_utilization={"cpu": 0.7},
                error_rate=0.05,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis"],
                available_for_assistance=False,
                cluster_role="worker",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            ),
        }

        status = self.discovery.get_cluster_status()

        assert status["cluster_size"] == 2
        assert status["healthy_nodes"] == 1
        assert status["average_stability"] == 0.65
        assert status["available_assistants"] == 1
        assert not status["discovery_active"]

    def test_get_assistance_candidates(self):
        """Test getting assistance candidates."""
        # Add mock nodes
        self.discovery.node_id = "self_node"
        self.discovery.cluster_nodes = {
            "self_node": ClusterNode(
                node_id="self_node",
                hostname="self",
                port=8765,
                protocol="tcp",
                node_state=NodeState.HEALTHY,
                stability_score=0.9,
                load_level=0.2,
                resource_utilization={"cpu": 0.2},
                error_rate=0.01,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis", "coordination"],
                available_for_assistance=True,
                cluster_role="coordinator",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            ),
            "helper1": ClusterNode(
                node_id="helper1",
                hostname="helper1",
                port=8765,
                protocol="tcp",
                node_state=NodeState.HEALTHY,
                stability_score=0.8,
                load_level=0.3,
                resource_utilization={"cpu": 0.3},
                error_rate=0.01,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis", "memory_management"],
                available_for_assistance=True,
                cluster_role="worker",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            ),
            "busy_node": ClusterNode(
                node_id="busy_node",
                hostname="busy",
                port=8765,
                protocol="tcp",
                node_state=NodeState.HEALTHY,
                stability_score=0.4,  # Below default threshold
                load_level=0.9,
                resource_utilization={"cpu": 0.9},
                error_rate=0.02,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis"],
                available_for_assistance=True,
                cluster_role="worker",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            ),
            "unavailable": ClusterNode(
                node_id="unavailable",
                hostname="unavailable",
                port=8765,
                protocol="tcp",
                node_state=NodeState.HEALTHY,
                stability_score=0.9,
                load_level=0.1,
                resource_utilization={"cpu": 0.1},
                error_rate=0.001,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis"],
                available_for_assistance=False,  # Not available
                cluster_role="observer",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            ),
        }

        # Test basic candidate selection
        candidates = self.discovery.get_assistance_candidates()
        assert len(candidates) == 1  # Only helper1 meets criteria
        assert candidates[0].node_id == "helper1"

        # Test with capability requirements
        candidates = self.discovery.get_assistance_candidates(
            required_capabilities=["memory_management"]
        )
        assert len(candidates) == 1
        assert candidates[0].node_id == "helper1"

        # Test with capability requirements that no one has
        candidates = self.discovery.get_assistance_candidates(
            required_capabilities=["non_existent_capability"]
        )
        assert len(candidates) == 0

        # Test with lower stability threshold
        candidates = self.discovery.get_assistance_candidates(min_stability=0.3)
        assert len(candidates) == 2  # helper1 and busy_node

        # Sort should put higher stability first
        assert candidates[0].stability_score >= candidates[1].stability_score


class TestDistributedHomeostasisCoordinator:
    """Test distributed homeostasis coordination."""

    def setup_method(self):
        """Set up test environment."""
        self.discovery = ClusterDiscovery(
            node_id="coordinator_test", discovery_port=8767
        )
        self.coordinator = DistributedHomeostasisCoordinator(self.discovery)

    def teardown_method(self):
        """Clean up after tests."""
        if self.coordinator.coordination_active:
            asyncio.run(self.coordinator.stop_coordination())
        if self.discovery.discovery_active:
            asyncio.run(self.discovery.stop_discovery())

    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        assert self.coordinator.cluster_discovery == self.discovery
        assert not self.coordinator.coordination_active
        assert len(self.coordinator.pending_signals) == 0
        assert len(self.coordinator.assistance_offers) == 0
        assert self.coordinator.signals_distributed == 0

    @pytest.mark.asyncio
    async def test_start_stop_coordination(self):
        """Test starting and stopping coordination."""
        await self.coordinator.start_coordination()
        assert self.coordinator.coordination_active

        await self.coordinator.stop_coordination()
        assert not self.coordinator.coordination_active

    @pytest.mark.asyncio
    async def test_request_cluster_assistance(self):
        """Test requesting cluster assistance."""
        # Set up mock cluster with candidates
        self.discovery.node_id = "requester"
        self.discovery.cluster_nodes = {
            "requester": ClusterNode(
                node_id="requester",
                hostname="requester",
                port=8765,
                protocol="tcp",
                node_state=NodeState.DEGRADED,
                stability_score=0.4,
                load_level=0.8,
                resource_utilization={"cpu": 0.8},
                error_rate=0.05,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis"],
                available_for_assistance=False,  # Can't help ourselves
                cluster_role="worker",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            ),
            "helper": ClusterNode(
                node_id="helper",
                hostname="helper",
                port=8765,
                protocol="tcp",
                node_state=NodeState.HEALTHY,
                stability_score=0.8,
                load_level=0.3,
                resource_utilization={"cpu": 0.3},
                error_rate=0.01,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis", "load_balancing"],
                available_for_assistance=True,
                cluster_role="worker",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            ),
        }

        # Request assistance
        signal_id = await self.coordinator.request_cluster_assistance(
            assistance_type=DistributedAction.LOAD_REDISTRIBUTION,
            severity=0.7,
            urgency="high",
            description="CPU overload requiring load redistribution",
            required_capabilities=["load_balancing"],
            context_data={"cpu_usage": 0.85, "memory_usage": 0.6},
        )

        assert signal_id is not None
        assert signal_id in self.coordinator.pending_signals

        signal = self.coordinator.pending_signals[signal_id]
        assert signal.source_node_id == "requester"
        assert signal.assistance_type == DistributedAction.LOAD_REDISTRIBUTION
        assert signal.severity == 0.7
        assert signal.urgency == "high"
        assert "load_balancing" in signal.required_capabilities
        assert signal.status == "pending"
        assert len(signal.target_nodes) == 1
        assert signal.target_nodes[0] == "helper"

        assert self.coordinator.signals_distributed == 1
        assert self.coordinator.assistance_requests_sent == 1

    @pytest.mark.asyncio
    async def test_request_assistance_no_candidates(self):
        """Test requesting assistance when no candidates available."""
        # Set up cluster with no available helpers
        self.discovery.node_id = "lonely_node"
        self.discovery.cluster_nodes = {
            "lonely_node": ClusterNode(
                node_id="lonely_node",
                hostname="lonely",
                port=8765,
                protocol="tcp",
                node_state=NodeState.CRITICAL,
                stability_score=0.2,
                load_level=0.95,
                resource_utilization={"cpu": 0.95},
                error_rate=0.1,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis"],
                available_for_assistance=False,
                cluster_role="worker",
                api_endpoints={},
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            )
        }

        signal_id = await self.coordinator.request_cluster_assistance(
            assistance_type=DistributedAction.EMERGENCY_ISOLATION,
            severity=0.9,
            urgency="critical",
            description="System failure requiring isolation",
        )

        assert signal_id is None  # No candidates available
        assert len(self.coordinator.pending_signals) == 0

    def test_get_coordination_status(self):
        """Test coordination status reporting."""
        # Add some mock data
        signal = DistributedStabilitySignal(
            signal_id="test_signal",
            source_node_id="source",
            target_nodes=["target1"],
            signal_type="assistance_request",
            severity=0.7,
            urgency="high",
            assistance_type=DistributedAction.PEER_ASSISTANCE,
            required_capabilities=[],
            estimated_duration=300.0,
            priority=70,
            description="Test signal",
            context_data={},
            timestamp=datetime.now().isoformat(),
            expires_at=datetime.now().isoformat(),
            responses={},
            assistance_provided=[],
            status="pending",
        )
        self.coordinator.pending_signals["test_signal"] = signal
        self.coordinator.signals_distributed = 5

        status = self.coordinator.get_coordination_status()

        assert not status["coordination_active"]
        assert status["pending_signals"] == 1
        assert status["active_signals"] == 1
        assert status["signals_distributed"] == 5


class TestMultiNodeHomeostasisIntegration:
    """Test multi-node homeostasis integration."""

    def setup_method(self):
        """Set up test environment."""
        self.integration = MultiNodeHomeostasisIntegration()

    def teardown_method(self):
        """Clean up after tests."""
        if self.integration.integration_active:
            asyncio.run(self.integration.stop_integration())

    def test_integration_initialization(self):
        """Test integration initialization."""
        assert not self.integration.integration_active
        assert self.integration.cluster_discovery is None
        assert self.integration.distributed_coordinator is None
        assert self.integration.cluster_stability_threshold == 0.6
        assert self.integration.assistance_request_cooldown == 300.0

    @pytest.mark.asyncio
    async def test_start_stop_integration(self):
        """Test starting and stopping integration."""
        # Mock the port to avoid conflicts
        with patch("socket.getfqdn", return_value="localhost"):
            await self.integration.start_integration(
                node_id="integration_test",
                discovery_port=8768,
                advertise_address="localhost",
            )

        assert self.integration.integration_active
        assert self.integration.cluster_discovery is not None
        assert self.integration.distributed_coordinator is not None

        await self.integration.stop_integration()
        assert not self.integration.integration_active

    @pytest.mark.asyncio
    async def test_handle_local_instability_no_assistance(self):
        """Test handling instability that doesn't require assistance."""
        # Low severity shouldn't request assistance
        result = await self.integration.handle_local_instability(
            severity=0.3,
            instability_type="minor_memory_pressure",
            context={"memory_usage": 0.45},
        )

        assert not result  # No assistance requested
        assert self.integration.cluster_assistance_requests == 0

    def test_get_cluster_stability_status_uninitialized(self):
        """Test getting status when not initialized."""
        status = self.integration.get_cluster_stability_status()
        assert "error" in status
        assert "not initialized" in status["error"]

    def test_instability_mapping(self):
        """Test mapping instability types to assistance actions."""
        # Test various instability mappings
        assert (
            self.integration._map_instability_to_assistance("memory_pressure")
            == DistributedAction.LOAD_REDISTRIBUTION
        )
        assert (
            self.integration._map_instability_to_assistance("cpu_overload")
            == DistributedAction.LOAD_REDISTRIBUTION
        )
        assert (
            self.integration._map_instability_to_assistance("service_failure")
            == DistributedAction.FAILOVER
        )
        assert (
            self.integration._map_instability_to_assistance("critical_error")
            == DistributedAction.EMERGENCY_ISOLATION
        )
        assert (
            self.integration._map_instability_to_assistance("unknown_type")
            == DistributedAction.PEER_ASSISTANCE
        )

    def test_required_capabilities_mapping(self):
        """Test mapping instability types to required capabilities."""
        capabilities = self.integration._get_required_capabilities("memory_pressure")
        assert "memory_management" in capabilities
        assert "load_balancing" in capabilities

        capabilities = self.integration._get_required_capabilities("disk_full")
        assert "storage_management" in capabilities
        assert "data_migration" in capabilities

        capabilities = self.integration._get_required_capabilities("unknown_type")
        assert capabilities == ["general_assistance"]

    def test_should_request_assistance_conditions(self):
        """Test conditions for requesting assistance."""
        # Low severity should not request assistance
        assert not asyncio.run(
            self.integration._should_request_assistance(0.3, "memory_pressure")
        )

        # High severity should request assistance
        assert asyncio.run(
            self.integration._should_request_assistance(0.8, "cpu_overload")
        )

        # Test cooldown behavior
        self.integration.last_assistance_request["memory_pressure"] = time.time()
        assert not asyncio.run(
            self.integration._should_request_assistance(0.7, "memory_pressure")
        )

        # Different instability type should not be affected by cooldown
        assert asyncio.run(
            self.integration._should_request_assistance(0.7, "cpu_overload")
        )

    def test_can_provide_assistance(self):
        """Test conditions for providing assistance."""
        # Add some stability history
        self.integration.local_stability_history = [
            {"timestamp": datetime.now().isoformat(), "stability": 0.8},
            {"timestamp": datetime.now().isoformat(), "stability": 0.7},
            {"timestamp": datetime.now().isoformat(), "stability": 0.75},
        ]

        # Should be able to assist with good stability
        assert asyncio.run(
            self.integration._can_provide_assistance(
                DistributedAction.PEER_ASSISTANCE, 0.6
            )
        )

        # Add unstable history
        self.integration.local_stability_history = [
            {"timestamp": datetime.now().isoformat(), "stability": 0.3},
            {"timestamp": datetime.now().isoformat(), "stability": 0.4},
            {"timestamp": datetime.now().isoformat(), "stability": 0.2},
        ]

        # Should not assist when unstable
        assert not asyncio.run(
            self.integration._can_provide_assistance(
                DistributedAction.PEER_ASSISTANCE, 0.6
            )
        )

    def test_assistance_capacity_calculation(self):
        """Test assistance capacity calculation."""
        # Add stable history
        self.integration.local_stability_history = [
            {"timestamp": datetime.now().isoformat(), "stability": 0.9}
        ]

        capacity = asyncio.run(
            self.integration._calculate_assistance_capacity(
                DistributedAction.PEER_ASSISTANCE
            )
        )

        assert 0.0 < capacity <= 0.8  # Should be positive and capped

        # Test with different assistance types
        failover_capacity = asyncio.run(
            self.integration._calculate_assistance_capacity(DistributedAction.FAILOVER)
        )

        # Failover should offer more capacity than peer assistance
        assert failover_capacity >= capacity

    def test_stability_trend_calculation(self):
        """Test stability trend calculation."""
        # Insufficient data
        assert self.integration._calculate_stability_trend() == "insufficient_data"

        # Improving trend
        self.integration.local_stability_history = [
            {"timestamp": datetime.now().isoformat(), "stability": 0.5},
            {"timestamp": datetime.now().isoformat(), "stability": 0.6},
            {"timestamp": datetime.now().isoformat(), "stability": 0.7},
            {"timestamp": datetime.now().isoformat(), "stability": 0.8},
            {"timestamp": datetime.now().isoformat(), "stability": 0.9},
        ]
        assert self.integration._calculate_stability_trend() == "improving"

        # Degrading trend
        self.integration.local_stability_history = [
            {"timestamp": datetime.now().isoformat(), "stability": 0.9},
            {"timestamp": datetime.now().isoformat(), "stability": 0.8},
            {"timestamp": datetime.now().isoformat(), "stability": 0.7},
            {"timestamp": datetime.now().isoformat(), "stability": 0.6},
            {"timestamp": datetime.now().isoformat(), "stability": 0.5},
        ]
        assert self.integration._calculate_stability_trend() == "degrading"

        # Stable trend
        self.integration.local_stability_history = [
            {"timestamp": datetime.now().isoformat(), "stability": 0.7},
            {"timestamp": datetime.now().isoformat(), "stability": 0.75},
            {"timestamp": datetime.now().isoformat(), "stability": 0.7},
            {"timestamp": datetime.now().isoformat(), "stability": 0.72},
            {"timestamp": datetime.now().isoformat(), "stability": 0.73},
        ]
        assert self.integration._calculate_stability_trend() == "stable"


class TestIntegrationFlow:
    """Test end-to-end integration scenarios."""

    @pytest.mark.asyncio
    async def test_cluster_assistance_flow(self):
        """Test complete cluster assistance flow."""
        # Create two nodes
        node1 = MultiNodeHomeostasisIntegration()
        node2 = MultiNodeHomeostasisIntegration()

        try:
            # Start both nodes
            with patch("socket.getfqdn", return_value="localhost"):
                await node1.start_integration(
                    node_id="node1", discovery_port=8769, advertise_address="localhost"
                )

                await node2.start_integration(
                    node_id="node2",
                    discovery_port=8770,
                    advertise_address="localhost",
                    seed_nodes=["localhost:8769"],
                )

            # Wait for discovery
            await asyncio.sleep(1.0)

            # Simulate instability on node1
            with patch.object(node1, "_should_request_assistance", return_value=True):
                with patch.object(
                    node1.distributed_coordinator, "_distribute_signal"
                ) as mock_distribute:
                    result = await node1.handle_local_instability(
                        severity=0.8,
                        instability_type="memory_pressure",
                        context={"memory_usage": 0.85},
                    )

                    assert result
                    assert node1.cluster_assistance_requests > 0
                    mock_distribute.assert_called_once()

        finally:
            # Clean up
            await node1.stop_integration()
            await node2.stop_integration()

    def test_global_instance_access(self):
        """Test global instance access."""
        integration1 = get_multi_node_integration()
        integration2 = get_multi_node_integration()

        # Should return the same instance
        assert integration1 is integration2

    @pytest.mark.asyncio
    async def test_initialization_function(self):
        """Test initialization function."""
        discovery, coordinator = initialize_multi_node_coordination(
            node_id="test_init", discovery_port=8771
        )

        assert discovery.node_id == "test_init"
        assert discovery.discovery_port == 8771
        assert coordinator.cluster_discovery == discovery

        # Clean up
        if discovery.discovery_active:
            await discovery.stop_discovery()
        if coordinator.coordination_active:
            await coordinator.stop_coordination()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

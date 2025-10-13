#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌐 Multi-Node Homeostasis Integration
====================================

Integration layer that connects the multi-node coordination framework with
the existing homeostasis system, enabling distributed stability management.

This module:
- Extends existing homeostasis actuators with cluster coordination
- Integrates distributed signals with local homeostasis decisions
- Provides cluster-aware stability monitoring
- Enables automatic peer assistance during instability
- Supports distributed load balancing and failover

Author: Aetherra Labs
"""

import asyncio
import contextlib
import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .multi_node_coordination import (
    ClusterDiscovery,
    DistributedAction,
    DistributedHomeostasisCoordinator,
    initialize_multi_node_coordination,
)

logger = logging.getLogger(__name__)


class MultiNodeHomeostasisIntegration:
    """
    Integration layer for multi-node homeostasis coordination.

    Connects local homeostasis systems with distributed cluster coordination,
    enabling peer assistance and distributed stability management.
    """

    def __init__(self):
        self.integration_active = False
        self.integration_task: Optional[asyncio.Task] = None

        # Coordination components
        self.cluster_discovery: Optional[ClusterDiscovery] = None
        self.distributed_coordinator: Optional[DistributedHomeostasisCoordinator] = None

        # Integration state
        self.cluster_stability_threshold = 0.6
        self.assistance_request_cooldown = 300.0  # 5 minutes
        self.last_assistance_request = {}  # action_type -> timestamp

        # Metrics
        self.cluster_assistance_requests = 0
        self.assistance_provided_count = 0
        self.distributed_actions_executed = 0
        self.peer_stability_improvements = 0

        # Local stability tracking
        self.local_stability_history = []
        self.stability_degradation_threshold = 0.3
        self.consecutive_degradation_limit = 3

        logger.info("🌐 Multi-node homeostasis integration initialized")

    async def start_integration(
        self,
        node_id: Optional[str] = None,
        discovery_port: int = 8765,
        advertise_address: Optional[str] = None,
        seed_nodes: Optional[List[str]] = None,
    ):
        """Start multi-node homeostasis integration."""
        if self.integration_active:
            logger.warning("Multi-node integration already active")
            return

        try:
            # Initialize coordination components
            self.cluster_discovery, self.distributed_coordinator = (
                initialize_multi_node_coordination(
                    node_id=node_id,
                    discovery_port=discovery_port,
                    advertise_address=advertise_address,
                    seed_nodes=seed_nodes,
                )
            )

            # Start cluster discovery
            await self.cluster_discovery.start_discovery(
                advertise_address=advertise_address, seed_nodes=seed_nodes
            )

            # Start distributed coordination
            await self.distributed_coordinator.start_coordination()

            # Start integration loop
            self.integration_active = True
            self.integration_task = asyncio.create_task(self._integration_loop())

            logger.info("🌐 Multi-node homeostasis integration started")

        except Exception as e:
            logger.error(f"❌ Failed to start multi-node integration: {e}")
            raise

    async def stop_integration(self):
        """Stop multi-node homeostasis integration."""
        if not self.integration_active:
            return

        self.integration_active = False

        # Stop integration loop
        if self.integration_task:
            self.integration_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.integration_task

        # Stop coordination components
        if self.distributed_coordinator:
            await self.distributed_coordinator.stop_coordination()

        if self.cluster_discovery:
            await self.cluster_discovery.stop_discovery()

        logger.info("🌐 Multi-node homeostasis integration stopped")

    async def handle_local_instability(
        self, severity: float, instability_type: str, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Handle local instability with potential cluster assistance.

        Args:
            severity: Instability severity (0.0 to 1.0)
            instability_type: Type of instability (e.g., "memory_pressure", "cpu_overload")
            context: Additional context data

        Returns:
            True if cluster assistance was requested, False otherwise
        """
        if not self.integration_active or not self.distributed_coordinator:
            return False

        try:
            # Check if we should request cluster assistance
            should_request = await self._should_request_assistance(severity, instability_type)

            if not should_request:
                logger.debug(
                    f"Local instability {instability_type} (severity: {severity:.2f}) - no cluster assistance needed"
                )
                return False

            # Determine assistance type
            assistance_type = self._map_instability_to_assistance(instability_type)

            # Determine urgency
            urgency = "critical" if severity > 0.8 else "high" if severity > 0.6 else "medium"

            # Request cluster assistance
            signal_id = await self.distributed_coordinator.request_cluster_assistance(
                assistance_type=assistance_type,
                severity=severity,
                urgency=urgency,
                description=f"Local {instability_type} requiring peer assistance",
                required_capabilities=self._get_required_capabilities(instability_type),
                context_data=context or {},
            )

            if signal_id:
                # Update cooldown tracking
                self.last_assistance_request[instability_type] = time.time()
                self.cluster_assistance_requests += 1

                logger.info(
                    f"🌐 Requested cluster assistance for {instability_type} (severity: {severity:.2f}, signal: {signal_id})"
                )
                return True
            else:
                logger.warning(f"Failed to request cluster assistance for {instability_type}")
                return False

        except Exception as e:
            logger.error(f"❌ Error handling local instability: {e}")
            return False

    async def evaluate_assistance_request(
        self,
        signal_id: str,
        requesting_node_id: str,
        assistance_type: DistributedAction,
        severity: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Evaluate whether to provide assistance to a requesting node.

        Args:
            signal_id: ID of the assistance signal
            requesting_node_id: Node requesting assistance
            assistance_type: Type of assistance requested
            severity: Severity of the requesting node's situation
            context: Additional context data

        Returns:
            True if assistance should be provided, False otherwise
        """
        if not self.integration_active or not self.distributed_coordinator:
            return False

        try:
            # Evaluate our capacity to provide assistance
            can_assist = await self._can_provide_assistance(assistance_type, severity)

            if not can_assist:
                logger.debug(
                    f"Cannot provide assistance for signal {signal_id} - insufficient capacity"
                )
                await self.distributed_coordinator.respond_to_assistance_request(
                    signal_id=signal_id, accept=False
                )
                return False

            # Calculate assistance capacity we can offer
            offered_capacity = await self._calculate_assistance_capacity(assistance_type)

            # Accept the assistance request
            success = await self.distributed_coordinator.respond_to_assistance_request(
                signal_id=signal_id,
                accept=True,
                offered_capacity=offered_capacity,
                conditions=self._get_assistance_conditions(assistance_type),
            )

            if success:
                self.assistance_provided_count += 1
                logger.info(
                    f"🌐 Accepted assistance request {signal_id} from {requesting_node_id} "
                    f"(type: {assistance_type}, capacity: {offered_capacity:.2f})"
                )

            return success

        except Exception as e:
            logger.error(f"❌ Error evaluating assistance request: {e}")
            return False

    def get_cluster_stability_status(self) -> Dict[str, Any]:
        """Get current cluster stability status."""
        if not self.cluster_discovery:
            return {"error": "Cluster discovery not initialized"}

        try:
            cluster_status = self.cluster_discovery.get_cluster_status()
            coordination_status = (
                self.distributed_coordinator.get_coordination_status()
                if self.distributed_coordinator
                else {}
            )

            # Calculate cluster stability metrics
            cluster_stability = cluster_status.get("average_stability", 0.0)
            stability_trend = self._calculate_stability_trend()

            return {
                "integration_active": self.integration_active,
                "cluster_info": cluster_status,
                "coordination_info": coordination_status,
                "stability_metrics": {
                    "cluster_stability": cluster_stability,
                    "stability_trend": stability_trend,
                    "local_stability_history": self.local_stability_history[
                        -10:
                    ],  # Last 10 samples
                    "cluster_threshold": self.cluster_stability_threshold,
                },
                "assistance_metrics": {
                    "requests_made": self.cluster_assistance_requests,
                    "assistance_provided": self.assistance_provided_count,
                    "distributed_actions": self.distributed_actions_executed,
                    "peer_improvements": self.peer_stability_improvements,
                },
                "cooldown_status": {
                    action_type: max(
                        0, self.assistance_request_cooldown - (time.time() - last_request)
                    )
                    for action_type, last_request in self.last_assistance_request.items()
                },
            }

        except Exception as e:
            logger.error(f"❌ Error getting cluster stability status: {e}")
            return {"error": str(e)}

    # Private methods

    async def _integration_loop(self):
        """Main integration loop for multi-node coordination."""
        try:
            while self.integration_active:
                # Monitor local stability and update cluster
                await self._monitor_local_stability()

                # Check for incoming assistance requests
                await self._process_incoming_assistance_requests()

                # Monitor cluster health and stability trends
                await self._monitor_cluster_health()

                # Execute any pending distributed actions
                await self._execute_distributed_actions()

                # Wait before next cycle
                await asyncio.sleep(15.0)  # Check every 15 seconds

        except asyncio.CancelledError:
            logger.info("Multi-node integration loop cancelled")
        except Exception as e:
            logger.error(f"❌ Integration loop error: {e}")

    async def _monitor_local_stability(self):
        """Monitor and report local stability to cluster."""
        try:
            # In practice, this would get real stability metrics
            # For now, we'll simulate stability tracking

            current_stability = 0.8 + 0.2 * (0.5 - (time.time() % 1))  # Simulated stability

            # Update local stability history
            self.local_stability_history.append(
                {"timestamp": datetime.now().isoformat(), "stability": current_stability}
            )

            # Keep history limited
            if len(self.local_stability_history) > 100:
                self.local_stability_history = self.local_stability_history[-50:]

            # Update cluster node info if available
            if self.cluster_discovery and self.cluster_discovery.local_node:
                self.cluster_discovery.local_node.stability_score = current_stability

        except Exception as e:
            logger.error(f"❌ Error monitoring local stability: {e}")

    async def _process_incoming_assistance_requests(self):
        """Process incoming assistance requests from cluster peers."""
        # This would process pending assistance requests
        # In the full implementation, this would check for new signals
        # and evaluate them for potential assistance
        pass

    async def _monitor_cluster_health(self):
        """Monitor overall cluster health and stability trends."""
        if not self.cluster_discovery:
            return

        try:
            cluster_status = self.cluster_discovery.get_cluster_status()

            # Check for cluster-wide stability issues
            avg_stability = cluster_status.get("average_stability", 1.0)

            if avg_stability < self.cluster_stability_threshold:
                logger.warning(f"🌐 Cluster stability below threshold: {avg_stability:.2f}")

                # Could trigger cluster-wide stabilization actions here
                await self._initiate_cluster_stabilization()

        except Exception as e:
            logger.error(f"❌ Error monitoring cluster health: {e}")

    async def _execute_distributed_actions(self):
        """Execute any pending distributed actions."""
        # This would handle execution of distributed actions
        # such as load redistribution, failover, etc.
        pass

    async def _should_request_assistance(self, severity: float, instability_type: str) -> bool:
        """Determine if cluster assistance should be requested."""
        # Check severity threshold
        if severity < 0.5:
            return False

        # Check cooldown
        last_request = self.last_assistance_request.get(instability_type, 0)
        if time.time() - last_request < self.assistance_request_cooldown:
            return False

        # Check if cluster has available assistants
        if self.cluster_discovery:
            candidates = self.cluster_discovery.get_assistance_candidates()
            if len(candidates) < 1:
                return False

        # Check for consecutive degradation
        recent_stability = self.local_stability_history[-self.consecutive_degradation_limit :]
        if len(recent_stability) >= self.consecutive_degradation_limit:
            consecutive_degraded = all(
                sample["stability"] < self.stability_degradation_threshold
                for sample in recent_stability
            )
            if consecutive_degraded:
                return True

        # High severity always requests assistance
        return severity > 0.7

    def _map_instability_to_assistance(self, instability_type: str) -> DistributedAction:
        """Map instability type to assistance action."""
        mapping = {
            "memory_pressure": DistributedAction.LOAD_REDISTRIBUTION,
            "cpu_overload": DistributedAction.LOAD_REDISTRIBUTION,
            "disk_full": DistributedAction.PEER_ASSISTANCE,
            "network_congestion": DistributedAction.PEER_ASSISTANCE,
            "service_failure": DistributedAction.FAILOVER,
            "resource_exhaustion": DistributedAction.CLUSTER_REBALANCE,
            "critical_error": DistributedAction.EMERGENCY_ISOLATION,
        }

        return mapping.get(instability_type, DistributedAction.PEER_ASSISTANCE)

    def _get_required_capabilities(self, instability_type: str) -> List[str]:
        """Get required capabilities for handling instability type."""
        capability_mapping = {
            "memory_pressure": ["memory_management", "load_balancing"],
            "cpu_overload": ["cpu_optimization", "load_balancing"],
            "disk_full": ["storage_management", "data_migration"],
            "network_congestion": ["network_optimization", "traffic_shaping"],
            "service_failure": ["service_management", "failover"],
            "resource_exhaustion": ["resource_management", "capacity_planning"],
            "critical_error": ["error_handling", "emergency_response"],
        }

        return capability_mapping.get(instability_type, ["general_assistance"])

    async def _can_provide_assistance(
        self, assistance_type: DistributedAction, severity: float
    ) -> bool:
        """Check if we can provide the requested assistance."""
        # Check our own stability
        if self.local_stability_history:
            recent_stability = self.local_stability_history[-3:]  # Last 3 samples
            avg_recent_stability = sum(s["stability"] for s in recent_stability) / len(
                recent_stability
            )

            # Don't assist if we're unstable ourselves
            if avg_recent_stability < self.cluster_stability_threshold:
                return False

        # Check available resources (simulated)
        # In practice, this would check actual resource availability

        resource_requirements = {
            DistributedAction.PEER_ASSISTANCE: 0.2,
            DistributedAction.LOAD_REDISTRIBUTION: 0.4,
            DistributedAction.FAILOVER: 0.6,
            DistributedAction.CLUSTER_REBALANCE: 0.3,
            DistributedAction.EMERGENCY_ISOLATION: 0.1,
        }

        required_capacity = resource_requirements.get(assistance_type, 0.3)

        # Simple capacity check (in practice, would check actual resources)
        available_capacity = 0.6  # Simulated available capacity

        return available_capacity >= required_capacity

    async def _calculate_assistance_capacity(self, assistance_type: DistributedAction) -> float:
        """Calculate how much assistance capacity we can offer."""
        base_capacity = {
            DistributedAction.PEER_ASSISTANCE: 0.3,
            DistributedAction.LOAD_REDISTRIBUTION: 0.5,
            DistributedAction.FAILOVER: 0.7,
            DistributedAction.CLUSTER_REBALANCE: 0.4,
            DistributedAction.EMERGENCY_ISOLATION: 0.2,
        }

        # Adjust based on our current stability
        capacity = base_capacity.get(assistance_type, 0.3)

        if self.local_stability_history:
            recent_stability = self.local_stability_history[-1]["stability"]
            capacity *= recent_stability  # Scale by our stability

        return min(capacity, 0.8)  # Cap at 80%

    def _get_assistance_conditions(self, assistance_type: DistributedAction) -> List[str]:
        """Get conditions for providing assistance."""
        conditions = ["maintain_local_stability", "time_limited_assistance"]

        if assistance_type in [DistributedAction.FAILOVER, DistributedAction.EMERGENCY_ISOLATION]:
            conditions.append("critical_situation_only")

        if assistance_type == DistributedAction.CLUSTER_REBALANCE:
            conditions.append("coordinated_cluster_action")

        return conditions

    def _calculate_stability_trend(self) -> str:
        """Calculate stability trend from recent history."""
        if len(self.local_stability_history) < 5:
            return "insufficient_data"

        recent_samples = self.local_stability_history[-5:]
        stabilities = [s["stability"] for s in recent_samples]

        # Simple trend calculation
        first_half = sum(stabilities[:2]) / 2
        second_half = sum(stabilities[-2:]) / 2

        if second_half > first_half + 0.1:
            return "improving"
        elif second_half < first_half - 0.1:
            return "degrading"
        else:
            return "stable"

    async def _initiate_cluster_stabilization(self):
        """Initiate cluster-wide stabilization actions."""
        logger.info("🌐 Initiating cluster stabilization actions")

        # This would implement cluster-wide stabilization logic
        # such as coordinated load balancing, resource redistribution, etc.

        # For now, we'll just log the action
        self.distributed_actions_executed += 1


# Global instance for easy access
_multi_node_integration_instance: Optional[MultiNodeHomeostasisIntegration] = None
_integration_lock = threading.Lock()


def get_multi_node_integration() -> MultiNodeHomeostasisIntegration:
    """Get the global multi-node integration instance."""
    global _multi_node_integration_instance

    if _multi_node_integration_instance is None:
        with _integration_lock:
            if _multi_node_integration_instance is None:
                _multi_node_integration_instance = MultiNodeHomeostasisIntegration()

    return _multi_node_integration_instance

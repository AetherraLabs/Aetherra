#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌐 Aetherra Multi-Node Homeostasis Coordination Framework
==========================================================

Strategic Enhancement #3: Distributed homeostasis system enabling cross-instance
Aetherra cluster coordination where peer nodes assist with rebalancing when one
node destabilizes.

This module:
- Extends watchdog signals to cross-instance communication
- Implements distributed homeostasis protocols
- Provides peer-to-peer stability assistance
- Enables cluster-wide stability monitoring
- Supports autonomous load redistribution and failover

Author: Aetherra Labs
"""

import asyncio
import json
import logging
import socket
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class NodeState(Enum):
    """States for cluster nodes."""

    UNKNOWN = "unknown"
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    FAILED = "failed"
    OFFLINE = "offline"


class DistributedAction(Enum):
    """Types of distributed homeostasis actions."""

    PEER_ASSISTANCE = "peer_assistance"
    LOAD_REDISTRIBUTION = "load_redistribution"
    FAILOVER = "failover"
    CLUSTER_REBALANCE = "cluster_rebalance"
    STABILITY_SYNC = "stability_sync"
    EMERGENCY_ISOLATION = "emergency_isolation"


@dataclass
class ClusterNode:
    """Cluster node information."""

    node_id: str
    hostname: str
    port: int
    protocol: str  # "http", "https", "ws", "wss"
    node_state: NodeState

    # Stability metrics
    stability_score: float
    load_level: float
    resource_utilization: Dict[str, float]
    error_rate: float

    # Cluster coordination
    last_heartbeat: str
    capabilities: List[str]
    available_for_assistance: bool
    cluster_role: str  # "coordinator", "worker", "observer"

    # Network information
    api_endpoints: Dict[str, str]
    discovery_timestamp: str
    trust_level: float  # 0.0 to 1.0


@dataclass
class DistributedStabilitySignal:
    """Distributed stability signal for cluster coordination."""

    signal_id: str
    source_node_id: str
    target_nodes: List[str]  # "all", specific node_ids, or ["coordinator"]

    signal_type: str
    severity: float
    urgency: str

    # Request details
    assistance_type: DistributedAction
    required_capabilities: List[str]
    estimated_duration: float
    priority: int

    # Context and data
    description: str
    context_data: Dict[str, Any]
    timestamp: str
    expires_at: str

    # Response tracking
    responses: Dict[str, Dict[str, Any]]
    assistance_provided: List[str]
    status: str  # "pending", "in_progress", "completed", "failed", "expired"


@dataclass
class AssistanceOffer:
    """Assistance offer from a peer node."""

    offer_id: str
    offering_node_id: str
    target_signal_id: str

    # Capabilities
    offered_assistance: DistributedAction
    available_resources: Dict[str, float]
    estimated_capacity: float

    # Terms
    offer_expires_at: str
    conditions: List[str]
    confidence: float

    # Status
    offer_status: str  # "pending", "accepted", "declined", "expired"
    response_data: Dict[str, Any]


class ClusterDiscovery:
    """
    Service discovery and node registry for distributed homeostasis.

    Handles automatic discovery of cluster nodes, heartbeat monitoring,
    and maintains the cluster topology for coordination.
    """

    def __init__(
        self, node_id: Optional[str] = None, discovery_port: int = 8765, heartbeat_interval: float = 30.0
    ):
        self.node_id = node_id or f"aetherra_node_{uuid.uuid4().hex[:8]}"
        self.discovery_port = discovery_port
        self.heartbeat_interval = heartbeat_interval

        # Cluster state
        self.cluster_nodes: Dict[str, ClusterNode] = {}
        self.local_node: Optional[ClusterNode] = None
        self.cluster_coordinator: Optional[str] = None

        # Discovery state
        self.discovery_active = False
        self.discovery_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None

        # Network state
        self.discovery_server: Optional[asyncio.Server] = None
        self.known_discovery_addresses: Set[str] = set()

        # Statistics
        self.nodes_discovered = 0
        self.heartbeats_sent = 0
        self.heartbeats_received = 0

        logger.info(f"🌐 Cluster discovery initialized for node {self.node_id}")

    async def start_discovery(
        self, advertise_address: Optional[str] = None, seed_nodes: Optional[List[str]] = None
    ):
        """Start cluster discovery process."""
        if self.discovery_active:
            logger.warning("Cluster discovery already active")
            return

        try:
            # Create local node entry
            hostname = advertise_address or socket.getfqdn()
            self.local_node = ClusterNode(
                node_id=self.node_id,
                hostname=hostname,
                port=self.discovery_port,
                protocol="tcp",
                node_state=NodeState.STARTING,
                stability_score=0.8,
                load_level=0.2,
                resource_utilization={"cpu": 0.3, "memory": 0.4, "disk": 0.1},
                error_rate=0.01,
                last_heartbeat=datetime.now().isoformat(),
                capabilities=["homeostasis", "coordination", "assistance"],
                available_for_assistance=True,
                cluster_role="worker",
                api_endpoints={
                    "homeostasis": f"http://{hostname}:8080/homeostasis",
                    "assistance": f"http://{hostname}:8080/assistance",
                },
                discovery_timestamp=datetime.now().isoformat(),
                trust_level=1.0,
            )

            # Start discovery server
            self.discovery_server = await asyncio.start_server(
                self._handle_discovery_connection, "0.0.0.0", self.discovery_port
            )

            # Add seed nodes to known addresses
            if seed_nodes:
                self.known_discovery_addresses.update(seed_nodes)

            # Start background tasks
            self.discovery_active = True
            self.discovery_task = asyncio.create_task(self._discovery_loop())
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            # Update local node state
            self.local_node.node_state = NodeState.HEALTHY
            self.cluster_nodes[self.node_id] = self.local_node

            logger.info(f"🌐 Cluster discovery started on {hostname}:{self.discovery_port}")

        except Exception as e:
            logger.error(f"❌ Failed to start cluster discovery: {e}")
            raise

    async def stop_discovery(self):
        """Stop cluster discovery process."""
        if not self.discovery_active:
            return

        self.discovery_active = False

        # Stop background tasks
        if self.discovery_task:
            self.discovery_task.cancel()
            import contextlib
            with contextlib.suppress(asyncio.CancelledError):
                await self.discovery_task

        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            import contextlib
            with contextlib.suppress(asyncio.CancelledError):
                await self.heartbeat_task

        # Stop discovery server
        if self.discovery_server:
            self.discovery_server.close()
            await self.discovery_server.wait_closed()

        logger.info("🌐 Cluster discovery stopped")

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get current cluster status."""
        healthy_nodes = sum(
            1 for node in self.cluster_nodes.values() if node.node_state == NodeState.HEALTHY
        )

        total_stability = sum(node.stability_score for node in self.cluster_nodes.values())
        avg_stability = total_stability / len(self.cluster_nodes) if self.cluster_nodes else 0.0

        available_assistants = sum(
            1
            for node in self.cluster_nodes.values()
            if node.available_for_assistance
            and node.node_state in [NodeState.HEALTHY, NodeState.DEGRADED]
        )

        return {
            "cluster_size": len(self.cluster_nodes),
            "healthy_nodes": healthy_nodes,
            "coordinator": self.cluster_coordinator,
            "average_stability": avg_stability,
            "available_assistants": available_assistants,
            "local_node_id": self.node_id,
            "discovery_active": self.discovery_active,
            "nodes_discovered": self.nodes_discovered,
            "heartbeats_exchanged": self.heartbeats_sent + self.heartbeats_received,
        }

    def get_assistance_candidates(
        self, required_capabilities: Optional[List[str]] = None, min_stability: float = 0.6
    ) -> List[ClusterNode]:
        """Get nodes available for assistance."""
        candidates = []

        for node in self.cluster_nodes.values():
            # Skip self
            if node.node_id == self.node_id:
                continue

            # Check availability and state
            if (
                node.available_for_assistance
                and node.node_state in [NodeState.HEALTHY, NodeState.DEGRADED]
                and node.stability_score >= min_stability
            ):
                # Check capabilities if specified
                if required_capabilities and not all(cap in node.capabilities for cap in required_capabilities):
                    continue

                candidates.append(node)

        # Sort by stability score (higher is better)
        candidates.sort(key=lambda n: n.stability_score, reverse=True)

        return candidates

    # Private methods

    async def _discovery_loop(self):
        """Main discovery loop."""
        try:
            while self.discovery_active:
                # Attempt to discover new nodes
                await self._discover_peers()

                # Clean up stale nodes
                await self._cleanup_stale_nodes()

                # Update cluster coordinator if needed
                await self._update_cluster_coordinator()

                # Wait before next discovery cycle
                await asyncio.sleep(30.0)  # Discovery every 30 seconds

        except asyncio.CancelledError:
            logger.info("Discovery loop cancelled")
        except Exception as e:
            logger.error(f"❌ Discovery loop error: {e}")

    async def _heartbeat_loop(self):
        """Heartbeat loop for cluster maintenance."""
        try:
            while self.discovery_active:
                # Send heartbeats to known nodes
                await self._send_heartbeats()

                # Update local node metrics
                await self._update_local_metrics()

                # Wait for next heartbeat
                await asyncio.sleep(self.heartbeat_interval)

        except asyncio.CancelledError:
            logger.info("Heartbeat loop cancelled")
        except Exception as e:
            logger.error(f"❌ Heartbeat loop error: {e}")

    async def _handle_discovery_connection(self, reader, writer):
        """Handle incoming discovery connections."""
        try:
            # Read discovery message
            data = await reader.read(4096)
            if not data:
                return

            message = json.loads(data.decode())

            if message.get("type") == "discovery":
                # Process node discovery
                node_info = message.get("node_info")
                if node_info:
                    await self._process_discovered_node(node_info)

                # Send our node info back
                response = {
                    "type": "discovery_response",
                    "node_info": asdict(self.local_node) if self.local_node else {},
                }

                writer.write(json.dumps(response).encode())
                await writer.drain()

            elif message.get("type") == "heartbeat":
                # Process heartbeat
                node_id = message.get("node_id")
                if node_id in self.cluster_nodes:
                    self.cluster_nodes[node_id].last_heartbeat = datetime.now().isoformat()
                    self.heartbeats_received += 1

                # Send heartbeat response
                response = {
                    "type": "heartbeat_response",
                    "node_id": self.node_id,
                    "timestamp": datetime.now().isoformat(),
                }

                writer.write(json.dumps(response).encode())
                await writer.drain()

        except Exception as e:
            logger.error(f"❌ Discovery connection error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _discover_peers(self):
        """Attempt to discover peer nodes."""
        discovery_addresses = list(self.known_discovery_addresses)

        # Try common local discovery addresses
        discovery_addresses.extend(
            [
                "localhost:8765",
                "127.0.0.1:8765",
                # Could add broadcast discovery here
            ]
        )

        for address in discovery_addresses:
            try:
                await self._contact_discovery_peer(address)
            except Exception as e:
                logger.debug(f"Discovery contact failed for {address}: {e}")

    async def _contact_discovery_peer(self, address: str):
        """Contact a specific peer for discovery."""
        try:
            host, port = address.split(":")
            port_num = int(port)

            # Skip self
            if host in ["localhost", "127.0.0.1"] and port_num == self.discovery_port:
                return

            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port_num), timeout=5.0
            )

            # Send discovery message
            discovery_msg = {
                "type": "discovery",
                "node_info": asdict(self.local_node) if self.local_node else {},
            }

            writer.write(json.dumps(discovery_msg).encode())
            await writer.drain()

            # Read response
            data = await asyncio.wait_for(reader.read(4096), timeout=5.0)
            response = json.loads(data.decode())

            if response.get("type") == "discovery_response":
                node_info = response.get("node_info")
                if node_info:
                    await self._process_discovered_node(node_info)

            writer.close()
            await writer.wait_closed()

        except Exception as e:
            logger.debug(f"Discovery contact failed for {address}: {e}")

    async def _process_discovered_node(self, node_data: Dict[str, Any]):
        """Process a discovered node."""
        try:
            node_id = node_data.get("node_id")
            if not node_id or node_id == self.node_id:
                return  # Skip self

            # Create or update node
            if node_id not in self.cluster_nodes:
                # Convert dict to ClusterNode
                node = ClusterNode(**node_data)
                self.cluster_nodes[node_id] = node
                self.nodes_discovered += 1
                logger.info(f"🌐 Discovered new cluster node: {node_id}")
            else:
                # Update existing node
                existing_node = self.cluster_nodes[node_id]
                for key, value in node_data.items():
                    if hasattr(existing_node, key):
                        setattr(existing_node, key, value)

        except Exception as e:
            logger.error(f"❌ Failed to process discovered node: {e}")

    async def _send_heartbeats(self):
        """Send heartbeats to cluster nodes."""
        for node in self.cluster_nodes.values():
            if node.node_id == self.node_id:
                continue  # Skip self

            try:
                await self._send_heartbeat_to_node(node)
            except Exception as e:
                logger.debug(f"Heartbeat failed to {node.node_id}: {e}")

    async def _send_heartbeat_to_node(self, node: ClusterNode):
        """Send heartbeat to a specific node."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(node.hostname, node.port), timeout=3.0
            )

            heartbeat_msg = {
                "type": "heartbeat",
                "node_id": self.node_id,
                "timestamp": datetime.now().isoformat(),
            }

            writer.write(json.dumps(heartbeat_msg).encode())
            await writer.drain()

            # Read response
            data = await asyncio.wait_for(reader.read(1024), timeout=3.0)
            response = json.loads(data.decode())

            if response.get("type") == "heartbeat_response":
                self.heartbeats_sent += 1

            writer.close()
            await writer.wait_closed()

        except Exception:
            # Mark node as potentially failed
            if node.node_state == NodeState.HEALTHY:
                node.node_state = NodeState.DEGRADED
            elif node.node_state == NodeState.DEGRADED:
                node.node_state = NodeState.FAILED

    async def _cleanup_stale_nodes(self):
        """Remove stale nodes from cluster."""
        cutoff_time = datetime.now() - timedelta(minutes=5)
        stale_nodes = []

        for node_id, node in self.cluster_nodes.items():
            if node_id == self.node_id:
                continue  # Skip self

            try:
                last_heartbeat = datetime.fromisoformat(node.last_heartbeat)
                if last_heartbeat < cutoff_time:
                    stale_nodes.append(node_id)
            except Exception:
                stale_nodes.append(node_id)

        for node_id in stale_nodes:
            del self.cluster_nodes[node_id]
            logger.warning(f"🌐 Removed stale cluster node: {node_id}")

    async def _update_cluster_coordinator(self):
        """Update cluster coordinator selection."""
        # Simple coordinator selection: node with highest stability and longest uptime
        # In practice, this could use more sophisticated leader election

        candidates = [
            node
            for node in self.cluster_nodes.values()
            if node.node_state == NodeState.HEALTHY and "coordination" in node.capabilities
        ]

        if candidates:
            # Sort by stability score and discovery time
            candidates.sort(key=lambda n: (n.stability_score, n.discovery_timestamp), reverse=True)
            new_coordinator = candidates[0].node_id

            if new_coordinator != self.cluster_coordinator:
                self.cluster_coordinator = new_coordinator
                logger.info(f"🌐 Cluster coordinator updated: {new_coordinator}")

    async def _update_local_metrics(self):
        """Update local node metrics."""
        if self.local_node:
            # Update metrics - in practice, these would come from actual monitoring
            self.local_node.last_heartbeat = datetime.now().isoformat()
            self.local_node.stability_score = max(
                0.1, self.local_node.stability_score + (0.05 * (2 * (time.time() % 1) - 1))
            )  # Simulated variation

            # Update in cluster registry
            self.cluster_nodes[self.node_id] = self.local_node


class DistributedHomeostasisCoordinator:
    """
    Coordinates distributed homeostasis actions across cluster nodes.

    Handles stability signal distribution, assistance coordination,
    and cluster-wide rebalancing operations.
    """

    def __init__(self, cluster_discovery: ClusterDiscovery):
        self.cluster_discovery = cluster_discovery

        # Coordination state
        self.coordination_active = False
        self.coordination_task: Optional[asyncio.Task] = None

        # Distributed signals
        self.pending_signals: Dict[str, DistributedStabilitySignal] = {}
        self.assistance_offers: Dict[str, AssistanceOffer] = {}
        self.active_assistance: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.signals_distributed = 0
        self.assistance_requests_sent = 0
        self.assistance_requests_received = 0
        self.successful_coordinations = 0

        logger.info("🌐 Distributed homeostasis coordinator initialized")

    async def start_coordination(self):
        """Start distributed coordination."""
        if self.coordination_active:
            logger.warning("Distributed coordination already active")
            return

        self.coordination_active = True
        self.coordination_task = asyncio.create_task(self._coordination_loop())

        logger.info("🌐 Distributed homeostasis coordination started")

    async def stop_coordination(self):
        """Stop distributed coordination."""
        if not self.coordination_active:
            return

        self.coordination_active = False

        if self.coordination_task:
            self.coordination_task.cancel()
            import contextlib
            with contextlib.suppress(asyncio.CancelledError):
                await self.coordination_task

        logger.info("🌐 Distributed homeostasis coordination stopped")

    async def request_cluster_assistance(
        self,
        assistance_type: DistributedAction,
        severity: float,
        urgency: str,
        description: str,
        required_capabilities: Optional[List[str]] = None,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Request assistance from cluster peers."""
        try:
            # Get available assistance candidates
            candidates = self.cluster_discovery.get_assistance_candidates(
                required_capabilities=required_capabilities or []
            )

            if not candidates:
                logger.warning("No assistance candidates available in cluster")
                return None

            # Create distributed stability signal
            signal_id = f"dist_sig_{uuid.uuid4().hex[:8]}"

            signal = DistributedStabilitySignal(
                signal_id=signal_id,
                source_node_id=self.cluster_discovery.node_id,
                target_nodes=[node.node_id for node in candidates[:3]],  # Limit to top 3
                signal_type="assistance_request",
                severity=severity,
                urgency=urgency,
                assistance_type=assistance_type,
                required_capabilities=required_capabilities or [],
                estimated_duration=max(60.0, 300.0 * severity),
                priority=self._calculate_priority(severity, urgency),
                description=description,
                context_data=context_data or {},
                timestamp=datetime.now().isoformat(),
                expires_at=(datetime.now() + timedelta(minutes=10)).isoformat(),
                responses={},
                assistance_provided=[],
                status="pending",
            )

            # Store signal
            self.pending_signals[signal_id] = signal

            # Distribute signal to target nodes
            await self._distribute_signal(signal)

            self.signals_distributed += 1
            self.assistance_requests_sent += 1

            logger.info(f"🌐 Distributed assistance request {signal_id} to {len(candidates)} nodes")

            return signal_id

        except Exception as e:
            logger.error(f"❌ Failed to request cluster assistance: {e}")
            return None

    async def respond_to_assistance_request(
        self,
        signal_id: str,
        accept: bool,
        offered_capacity: float = 0.5,
        conditions: Optional[List[str]] = None,
    ) -> bool:
        """Respond to an assistance request from another node."""
        try:
            if signal_id not in self.pending_signals:
                logger.warning(f"Unknown assistance signal: {signal_id}")
                return False

            signal = self.pending_signals[signal_id]

            if accept:
                # Create assistance offer
                offer_id = f"offer_{uuid.uuid4().hex[:8]}"

                offer = AssistanceOffer(
                    offer_id=offer_id,
                    offering_node_id=self.cluster_discovery.node_id,
                    target_signal_id=signal_id,
                    offered_assistance=signal.assistance_type,
                    available_resources={"cpu": 0.3, "memory": 0.4, "network": 0.5},
                    estimated_capacity=offered_capacity,
                    offer_expires_at=(datetime.now() + timedelta(minutes=5)).isoformat(),
                    conditions=conditions or [],
                    confidence=0.8,
                    offer_status="pending",
                    response_data={},
                )

                self.assistance_offers[offer_id] = offer

                # Send offer to requesting node
                await self._send_assistance_offer(signal.source_node_id, offer)

                logger.info(f"🌐 Sent assistance offer {offer_id} for signal {signal_id}")
            else:
                # Send decline response
                await self._send_assistance_decline(signal.source_node_id, signal_id)

                logger.info(f"🌐 Declined assistance request {signal_id}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to respond to assistance request: {e}")
            return False

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status."""
        active_signals = sum(
            1
            for signal in self.pending_signals.values()
            if signal.status in ["pending", "in_progress"]
        )

        pending_offers = sum(
            1 for offer in self.assistance_offers.values() if offer.offer_status == "pending"
        )

        return {
            "coordination_active": self.coordination_active,
            "pending_signals": len(self.pending_signals),
            "active_signals": active_signals,
            "assistance_offers": len(self.assistance_offers),
            "pending_offers": pending_offers,
            "active_assistance": len(self.active_assistance),
            "signals_distributed": self.signals_distributed,
            "assistance_requests_sent": self.assistance_requests_sent,
            "assistance_requests_received": self.assistance_requests_received,
            "successful_coordinations": self.successful_coordinations,
        }

    # Private methods

    async def _coordination_loop(self):
        """Main coordination loop."""
        try:
            while self.coordination_active:
                # Process pending signals
                await self._process_pending_signals()

                # Process assistance offers
                await self._process_assistance_offers()

                # Cleanup expired items
                await self._cleanup_expired_items()

                # Wait before next cycle
                await asyncio.sleep(10.0)

        except asyncio.CancelledError:
            logger.info("Coordination loop cancelled")
        except Exception as e:
            logger.error(f"❌ Coordination loop error: {e}")

    async def _distribute_signal(self, signal: DistributedStabilitySignal):
        """Distribute signal to target nodes."""
        for target_node_id in signal.target_nodes:
            try:
                await self._send_signal_to_node(target_node_id, signal)
            except Exception as e:
                logger.error(f"Failed to send signal to {target_node_id}: {e}")

    async def _send_signal_to_node(self, node_id: str, signal: DistributedStabilitySignal):
        """Send signal to a specific node."""
        # In practice, this would use the node's API endpoint
        # For now, we'll simulate the communication

        node = self.cluster_discovery.cluster_nodes.get(node_id)
        if not node:
            logger.warning(f"Target node {node_id} not found in cluster")
            return

        # Simulate network communication
        logger.debug(f"🌐 Sending signal {signal.signal_id} to node {node_id}")

        # In a real implementation, this would be an HTTP/WebSocket call
        # await self._make_api_call(node.api_endpoints["assistance"], signal_data)

    async def _send_assistance_offer(self, target_node_id: str, offer: AssistanceOffer):
        """Send assistance offer to requesting node."""
        # Simulate sending offer
        logger.debug(f"🌐 Sending assistance offer {offer.offer_id} to {target_node_id}")

    async def _send_assistance_decline(self, target_node_id: str, signal_id: str):
        """Send assistance decline to requesting node."""
        logger.debug(f"🌐 Sending assistance decline for {signal_id} to {target_node_id}")

    async def _process_pending_signals(self):
        """Process pending signals for timeouts and status updates."""
        current_time = datetime.now()

        for signal_id, signal in list(self.pending_signals.items()):
            try:
                expires_at = datetime.fromisoformat(signal.expires_at)

                if current_time > expires_at:
                    signal.status = "expired"
                    logger.info(f"🌐 Signal {signal_id} expired")

            except Exception as e:
                logger.error(f"Error processing signal {signal_id}: {e}")

    async def _process_assistance_offers(self):
        """Process assistance offers for acceptance/decline."""
        # This would handle the logic for accepting offers and coordinating assistance
        pass

    async def _cleanup_expired_items(self):
        """Clean up expired signals and offers."""
        current_time = datetime.now()

        # Clean up expired signals
        expired_signals = []
        for signal_id, signal in self.pending_signals.items():
            try:
                expires_at = datetime.fromisoformat(signal.expires_at)
                if current_time > expires_at and signal.status in [
                    "expired",
                    "completed",
                    "failed",
                ]:
                    expired_signals.append(signal_id)
            except Exception:
                expired_signals.append(signal_id)

        for signal_id in expired_signals:
            del self.pending_signals[signal_id]

        # Clean up expired offers
        expired_offers = []
        for offer_id, offer in self.assistance_offers.items():
            try:
                expires_at = datetime.fromisoformat(offer.offer_expires_at)
                if current_time > expires_at:
                    expired_offers.append(offer_id)
            except Exception:
                expired_offers.append(offer_id)

        for offer_id in expired_offers:
            del self.assistance_offers[offer_id]

    def _calculate_priority(self, severity: float, urgency: str) -> int:
        """Calculate priority for assistance request."""
        base_priority = int(severity * 100)

        urgency_bonus = {"low": 0, "medium": 25, "high": 50, "critical": 100}.get(urgency, 0)

        return base_priority + urgency_bonus


# Global instances for easy access
_cluster_discovery_instance: Optional[ClusterDiscovery] = None
_distributed_coordinator_instance: Optional[DistributedHomeostasisCoordinator] = None
_multi_node_lock = threading.Lock()


def get_cluster_discovery() -> ClusterDiscovery:
    """Get the global cluster discovery instance."""
    global _cluster_discovery_instance

    if _cluster_discovery_instance is None:
        with _multi_node_lock:
            if _cluster_discovery_instance is None:
                _cluster_discovery_instance = ClusterDiscovery()

    return _cluster_discovery_instance


def get_distributed_coordinator() -> DistributedHomeostasisCoordinator:
    """Get the global distributed coordinator instance."""
    global _distributed_coordinator_instance

    if _distributed_coordinator_instance is None:
        with _multi_node_lock:
            if _distributed_coordinator_instance is None:
                discovery = get_cluster_discovery()
                _distributed_coordinator_instance = DistributedHomeostasisCoordinator(discovery)

    return _distributed_coordinator_instance


def initialize_multi_node_coordination(
    node_id: Optional[str] = None,
    discovery_port: int = 8765,
    advertise_address: Optional[str] = None,
    seed_nodes: Optional[List[str]] = None,
) -> Tuple[ClusterDiscovery, DistributedHomeostasisCoordinator]:
    """Initialize multi-node coordination system."""
    global _cluster_discovery_instance, _distributed_coordinator_instance

    with _multi_node_lock:
        # Initialize discovery
        _cluster_discovery_instance = ClusterDiscovery(
            node_id=node_id, discovery_port=discovery_port
        )

        # Initialize coordinator
        _distributed_coordinator_instance = DistributedHomeostasisCoordinator(
            _cluster_discovery_instance
        )

    return _cluster_discovery_instance, _distributed_coordinator_instance

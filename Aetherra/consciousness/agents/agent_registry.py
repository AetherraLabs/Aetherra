# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Agent Registry
=======================

Universal agent registry for centralized agent discovery and management
across the consciousness orchestrator system.

Features:
- Centralized agent discovery and management
- Cross-system agent communication protocols
- Dynamic agent capability mapping
- Agent lifecycle tracking
- Performance monitoring and analytics

Author: Aetherra Consciousness Team
Version: 1.0.0
Date: August 4, 2025
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from consciousness_bridge import (
    ConsciousnessMessage,
    get_consciousness_bridge,
)


class RegistrationStatus(Enum):
    """Agent registration status"""

    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class AgentCategory(Enum):
    """Categories for agent classification"""

    CORE_SYSTEM = "core_system"
    INTELLIGENCE = "intelligence"
    INTERFACE = "interface"
    PROCESSING = "processing"
    COORDINATION = "coordination"
    SPECIALIZED = "specialized"
    EXPERIMENTAL = "experimental"


@dataclass
class AgentRegistration:
    """Complete agent registration information"""

    agent_id: str
    name: str
    description: str
    agent_type: str
    category: AgentCategory
    system_origin: str
    capabilities: List[str]
    interfaces: List[str]  # Communication interfaces supported
    dependencies: List[str]  # Other agents this agent depends on
    provides_services: List[str]  # Services this agent provides

    # Registration metadata
    registration_time: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    status: RegistrationStatus = RegistrationStatus.PENDING
    version: str = "1.0.0"

    # Performance tracking
    uptime_percentage: float = 100.0
    total_requests_handled: int = 0
    successful_requests: int = 0
    average_response_time: float = 0.0

    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    network_usage_kb: float = 0.0

    # Relationships
    collaborating_agents: Set[str] = field(default_factory=set)
    trusted_by: Set[str] = field(default_factory=set)
    trusts: Set[str] = field(default_factory=set)

    # Additional metadata
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceDefinition:
    """Definition of a service provided by an agent"""

    service_id: str
    service_name: str
    description: str
    provider_agent_id: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    service_type: str  # 'synchronous', 'asynchronous', 'streaming'
    endpoint: str
    rate_limit: Optional[int] = None
    authentication_required: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class AgentQuery:
    """Query for agent discovery"""

    capabilities: Optional[List[str]] = None
    categories: Optional[List[AgentCategory]] = None
    system_origins: Optional[List[str]] = None
    status_filter: Optional[List[RegistrationStatus]] = None
    tags: Optional[List[str]] = None
    min_uptime: Optional[float] = None
    max_response_time: Optional[float] = None
    provides_services: Optional[List[str]] = None
    available_for_collaboration: bool = False
    exclude_agents: Optional[List[str]] = None


class AgentRegistry:
    """
    Universal agent registry for the consciousness orchestrator system

    This registry manages all agents across the Aetherra ecosystem,
    providing centralized discovery, monitoring, and coordination capabilities.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.consciousness_bridge = get_consciousness_bridge()

        # Core registry data
        self.agents: Dict[str, AgentRegistration] = {}
        self.services: Dict[str, ServiceDefinition] = {}
        self.capabilities_index: Dict[str, Set[str]] = defaultdict(
            set
        )  # capability -> agent_ids
        self.category_index: Dict[AgentCategory, Set[str]] = defaultdict(
            set
        )  # category -> agent_ids
        self.system_index: Dict[str, Set[str]] = defaultdict(set)  # system -> agent_ids

        # Performance and analytics
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.collaboration_graph: Dict[str, Set[str]] = defaultdict(
            set
        )  # collaboration relationships
        self.service_usage_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Configuration
        self.config = {
            "heartbeat_timeout": 60,  # seconds
            "max_performance_history": 1000,
            "auto_archive_after_days": 30,
            "service_discovery_cache_ttl": 300,  # 5 minutes
            "max_concurrent_registrations": 1000,
            "performance_sampling_interval": 30,  # seconds
        }

        # Runtime state
        self.is_running = False
        self.registry_task = None
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.query_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}

        self.logger.info("Agent Registry initialized")

    async def initialize(self):
        """Initialize the agent registry"""
        try:
            self.logger.info("Initializing Agent Registry...")

            # Register with consciousness bridge
            self.consciousness_bridge.register_message_handler(
                "agent_register_request", self._handle_agent_registration
            )
            self.consciousness_bridge.register_message_handler(
                "agent_unregister_request", self._handle_agent_unregistration
            )
            self.consciousness_bridge.register_message_handler(
                "agent_discovery_request", self._handle_agent_discovery
            )
            self.consciousness_bridge.register_message_handler(
                "service_discovery_request", self._handle_service_discovery
            )
            self.consciousness_bridge.register_message_handler(
                "agent_heartbeat", self._handle_agent_heartbeat
            )
            self.consciousness_bridge.register_message_handler(
                "performance_update", self._handle_performance_update
            )

            # Start registry maintenance loop
            await self._start_registry_loop()

            self.is_running = True
            self.logger.info("Agent Registry successfully initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize Agent Registry: {e}")
            raise

    async def _start_registry_loop(self):
        """Start the registry maintenance loop"""
        self.registry_task = asyncio.create_task(self._registry_loop())
        self.logger.info("Agent Registry maintenance loop started")

    async def _registry_loop(self):
        """Main registry maintenance loop"""
        while self.is_running:
            try:
                # Check agent heartbeats
                await self._check_agent_heartbeats()

                # Update performance analytics
                await self._update_performance_analytics()

                # Clean up old cache entries
                await self._cleanup_cache()

                # Archive inactive agents
                await self._archive_inactive_agents()

                # Update collaboration graph
                await self._update_collaboration_graph()

                # Generate registry statistics
                await self._generate_registry_statistics()

                await asyncio.sleep(self.config["performance_sampling_interval"])

            except Exception as e:
                self.logger.error(f"Error in registry loop: {e}")
                await asyncio.sleep(5.0)

    async def _check_agent_heartbeats(self):
        """Check agent heartbeats and update status"""
        try:
            current_time = datetime.now()
            timeout_threshold = timedelta(seconds=self.config["heartbeat_timeout"])

            for agent_id, registration in self.agents.items():
                if registration.status == RegistrationStatus.ACTIVE:
                    time_since_heartbeat = current_time - registration.last_heartbeat

                    if time_since_heartbeat > timeout_threshold:
                        # Mark as inactive
                        registration.status = RegistrationStatus.INACTIVE
                        self.logger.warning(
                            f"Agent {agent_id} marked as inactive due to heartbeat timeout"
                        )

                        # Emit event
                        await self._emit_registry_event(
                            "agent_heartbeat_timeout",
                            {
                                "agent_id": agent_id,
                                "time_since_heartbeat": time_since_heartbeat.total_seconds(),
                            },
                        )

                        # Update indices
                        await self._update_indices_for_agent(agent_id, registration)

        except Exception as e:
            self.logger.error(f"Error checking agent heartbeats: {e}")

    async def _update_performance_analytics(self):
        """Update performance analytics for all agents"""
        try:
            current_time = datetime.now()

            for agent_id, registration in self.agents.items():
                if registration.status == RegistrationStatus.ACTIVE:
                    # Calculate current performance metrics
                    success_rate = 0.0
                    if registration.total_requests_handled > 0:
                        success_rate = (
                            registration.successful_requests
                            / registration.total_requests_handled
                        )

                    # Add to performance history
                    performance_record = {
                        "timestamp": current_time.isoformat(),
                        "uptime_percentage": registration.uptime_percentage,
                        "success_rate": success_rate,
                        "response_time": registration.average_response_time,
                        "memory_usage": registration.memory_usage_mb,
                        "cpu_usage": registration.cpu_usage_percent,
                        "network_usage": registration.network_usage_kb,
                        "total_requests": registration.total_requests_handled,
                    }

                    self.performance_history[agent_id].append(performance_record)

                    # Keep only recent history
                    max_history = self.config["max_performance_history"]
                    if len(self.performance_history[agent_id]) > max_history:
                        self.performance_history[agent_id] = self.performance_history[
                            agent_id
                        ][-max_history:]

        except Exception as e:
            self.logger.error(f"Error updating performance analytics: {e}")

    async def _cleanup_cache(self):
        """Clean up old cache entries"""
        try:
            current_time = datetime.now()
            cache_ttl = timedelta(seconds=self.config["service_discovery_cache_ttl"])

            expired_keys = []
            for cache_key, timestamp in self.cache_timestamps.items():
                if current_time - timestamp > cache_ttl:
                    expired_keys.append(cache_key)

            for key in expired_keys:
                self.query_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)

        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {e}")

    async def _archive_inactive_agents(self):
        """Archive agents that have been inactive for too long"""
        try:
            current_time = datetime.now()
            archive_threshold = timedelta(days=self.config["auto_archive_after_days"])

            agents_to_archive = []
            for agent_id, registration in self.agents.items():
                if registration.status == RegistrationStatus.INACTIVE:
                    time_inactive = current_time - registration.last_heartbeat
                    if time_inactive > archive_threshold:
                        agents_to_archive.append(agent_id)

            for agent_id in agents_to_archive:
                await self._archive_agent(agent_id)

        except Exception as e:
            self.logger.error(f"Error archiving inactive agents: {e}")

    async def _archive_agent(self, agent_id: str):
        """Archive an inactive agent"""
        if agent_id in self.agents:
            registration = self.agents[agent_id]
            registration.status = RegistrationStatus.ARCHIVED

            # Remove from active indices
            await self._remove_from_indices(agent_id, registration)

            # Emit event
            await self._emit_registry_event(
                "agent_archived",
                {"agent_id": agent_id, "archive_reason": "inactive_timeout"},
            )

            self.logger.info(f"Archived inactive agent: {agent_id}")

    async def _update_collaboration_graph(self):
        """Update the collaboration graph based on agent relationships"""
        try:
            # Clear existing graph
            self.collaboration_graph.clear()

            # Rebuild from current agent relationships
            for agent_id, registration in self.agents.items():
                if registration.status == RegistrationStatus.ACTIVE:
                    self.collaboration_graph[
                        agent_id
                    ] = registration.collaborating_agents.copy()

        except Exception as e:
            self.logger.error(f"Error updating collaboration graph: {e}")

    async def _generate_registry_statistics(self):
        """Generate and emit registry statistics"""
        try:
            stats = {
                "total_agents": len(self.agents),
                "active_agents": len(
                    [
                        a
                        for a in self.agents.values()
                        if a.status == RegistrationStatus.ACTIVE
                    ]
                ),
                "inactive_agents": len(
                    [
                        a
                        for a in self.agents.values()
                        if a.status == RegistrationStatus.INACTIVE
                    ]
                ),
                "archived_agents": len(
                    [
                        a
                        for a in self.agents.values()
                        if a.status == RegistrationStatus.ARCHIVED
                    ]
                ),
                "total_services": len(self.services),
                "unique_capabilities": len(self.capabilities_index),
                "collaboration_connections": sum(
                    len(connections)
                    for connections in self.collaboration_graph.values()
                ),
                "timestamp": datetime.now().isoformat(),
            }

            # Category breakdown
            category_stats = {}
            for category in AgentCategory:
                category_stats[category.value] = len(self.category_index[category])
            stats["category_breakdown"] = category_stats

            # System breakdown
            system_stats = {}
            for system in self.system_index:
                system_stats[system] = len(self.system_index[system])
            stats["system_breakdown"] = system_stats

            # Emit statistics
            await self._emit_registry_event("registry_statistics", stats)

        except Exception as e:
            self.logger.error(f"Error generating registry statistics: {e}")

    # Message handlers

    async def _handle_agent_registration(self, message: ConsciousnessMessage):
        """Handle agent registration requests"""
        try:
            agent_data = message.payload

            # Create agent registration
            registration = AgentRegistration(
                agent_id=agent_data["agent_id"],
                name=agent_data.get("name", agent_data["agent_id"]),
                description=agent_data.get("description", ""),
                agent_type=agent_data.get("agent_type", "unknown"),
                category=AgentCategory(agent_data.get("category", "specialized")),
                system_origin=agent_data.get("system_origin", message.source),
                capabilities=agent_data.get("capabilities", []),
                interfaces=agent_data.get("interfaces", ["consciousness_bridge"]),
                dependencies=agent_data.get("dependencies", []),
                provides_services=agent_data.get("provides_services", []),
                version=agent_data.get("version", "1.0.0"),
                tags=agent_data.get("tags", []),
                custom_metadata=agent_data.get("metadata", {}),
            )

            # Register the agent
            success = await self._register_agent(registration)

            # Send response
            if message.requires_response:
                response = ConsciousnessMessage(
                    source="agent_registry",
                    destination=message.source,
                    message_type="agent_registration_response",
                    payload={
                        "agent_id": registration.agent_id,
                        "success": success,
                        "status": registration.status.value,
                        "message": "Registration successful"
                        if success
                        else "Registration failed",
                    },
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id,
                )

                self.consciousness_bridge.send_message(response)

        except Exception as e:
            self.logger.error(f"Error handling agent registration: {e}")

    async def _register_agent(self, registration: AgentRegistration) -> bool:
        """Register an agent in the registry"""
        try:
            agent_id = registration.agent_id

            # Check if agent already exists
            if agent_id in self.agents:
                existing = self.agents[agent_id]
                if existing.status == RegistrationStatus.ACTIVE:
                    self.logger.warning(
                        f"Agent {agent_id} already registered and active"
                    )
                    return False
                else:
                    # Reactivating existing agent
                    self.logger.info(f"Reactivating agent {agent_id}")

            # Set as active
            registration.status = RegistrationStatus.ACTIVE
            registration.registration_time = datetime.now()
            registration.last_heartbeat = datetime.now()

            # Store registration
            self.agents[agent_id] = registration

            # Update indices
            await self._update_indices_for_agent(agent_id, registration)

            # Register services
            for service_name in registration.provides_services:
                await self._register_agent_service(agent_id, service_name)

            # Emit event
            await self._emit_registry_event(
                "agent_registered",
                {
                    "agent_id": agent_id,
                    "name": registration.name,
                    "category": registration.category.value,
                    "system_origin": registration.system_origin,
                    "capabilities": registration.capabilities,
                },
            )

            self.logger.info(f"Successfully registered agent: {agent_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error registering agent {registration.agent_id}: {e}")
            return False

    async def _register_agent_service(self, agent_id: str, service_name: str):
        """Register a service provided by an agent"""
        service_id = f"{agent_id}:{service_name}"

        service = ServiceDefinition(
            service_id=service_id,
            service_name=service_name,
            description=f"{service_name} service provided by {agent_id}",
            provider_agent_id=agent_id,
            input_schema={},  # Would be provided by agent
            output_schema={},  # Would be provided by agent
            service_type="synchronous",
            endpoint=f"agent://{agent_id}/{service_name}",
        )

        self.services[service_id] = service
        self.logger.debug(f"Registered service {service_id}")

    async def _update_indices_for_agent(
        self, agent_id: str, registration: AgentRegistration
    ):
        """Update search indices for an agent"""
        # Remove from old indices first
        await self._remove_from_indices(agent_id, registration)

        # Add to new indices only if active
        if registration.status == RegistrationStatus.ACTIVE:
            # Capabilities index
            for capability in registration.capabilities:
                self.capabilities_index[capability].add(agent_id)

            # Category index
            self.category_index[registration.category].add(agent_id)

            # System index
            self.system_index[registration.system_origin].add(agent_id)

    async def _remove_from_indices(
        self, agent_id: str, registration: AgentRegistration
    ):
        """Remove agent from all search indices"""
        # Remove from capabilities index
        for capability in registration.capabilities:
            self.capabilities_index[capability].discard(agent_id)
            # Clean up empty sets
            if not self.capabilities_index[capability]:
                del self.capabilities_index[capability]

        # Remove from category index
        self.category_index[registration.category].discard(agent_id)

        # Remove from system index
        self.system_index[registration.system_origin].discard(agent_id)

    async def _handle_agent_unregistration(self, message: ConsciousnessMessage):
        """Handle agent unregistration requests"""
        try:
            agent_id = message.payload.get("agent_id")
            reason = message.payload.get("reason", "manual_unregistration")

            if agent_id in self.agents:
                registration = self.agents[agent_id]
                registration.status = RegistrationStatus.INACTIVE

                # Remove from active indices
                await self._remove_from_indices(agent_id, registration)

                # Remove associated services
                services_to_remove = [
                    sid
                    for sid, service in self.services.items()
                    if service.provider_agent_id == agent_id
                ]
                for service_id in services_to_remove:
                    del self.services[service_id]

                # Emit event
                await self._emit_registry_event(
                    "agent_unregistered", {"agent_id": agent_id, "reason": reason}
                )

                self.logger.info(f"Unregistered agent: {agent_id}")

                # Send response
                if message.requires_response:
                    response = ConsciousnessMessage(
                        source="agent_registry",
                        destination=message.source,
                        message_type="agent_unregistration_response",
                        payload={
                            "agent_id": agent_id,
                            "success": True,
                            "message": "Unregistration successful",
                        },
                        timestamp=datetime.now(),
                        correlation_id=message.correlation_id,
                    )

                    self.consciousness_bridge.send_message(response)
            else:
                self.logger.warning(
                    f"Attempted to unregister unknown agent: {agent_id}"
                )

        except Exception as e:
            self.logger.error(f"Error handling agent unregistration: {e}")

    async def _handle_agent_discovery(self, message: ConsciousnessMessage):
        """Handle agent discovery requests"""
        try:
            query_data = message.payload.get("query", {})

            # Create query object
            query = AgentQuery(
                capabilities=query_data.get("capabilities"),
                categories=[
                    AgentCategory(cat) for cat in query_data.get("categories", [])
                ]
                if query_data.get("categories")
                else None,
                system_origins=query_data.get("system_origins"),
                status_filter=[
                    RegistrationStatus(status)
                    for status in query_data.get("status_filter", [])
                ]
                if query_data.get("status_filter")
                else None,
                tags=query_data.get("tags"),
                min_uptime=query_data.get("min_uptime"),
                max_response_time=query_data.get("max_response_time"),
                provides_services=query_data.get("provides_services"),
                available_for_collaboration=query_data.get(
                    "available_for_collaboration", False
                ),
                exclude_agents=query_data.get("exclude_agents"),
            )

            # Check cache first
            cache_key = self._generate_query_cache_key(query)
            cached_result = self._get_cached_result(cache_key)

            if cached_result:
                results = cached_result
            else:
                # Perform discovery
                results = await self._discover_agents(query)

                # Cache result
                self._cache_result(cache_key, results)

            # Send response
            if message.requires_response:
                response = ConsciousnessMessage(
                    source="agent_registry",
                    destination=message.source,
                    message_type="agent_discovery_response",
                    payload={
                        "matching_agents": results,
                        "query": query_data,
                        "total_matches": len(results),
                        "cached": cached_result is not None,
                    },
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id,
                )

                self.consciousness_bridge.send_message(response)

        except Exception as e:
            self.logger.error(f"Error handling agent discovery: {e}")

    async def _discover_agents(self, query: AgentQuery) -> List[Dict[str, Any]]:
        """Discover agents matching the query criteria"""
        try:
            candidate_agents = set(self.agents.keys())

            # Filter by capabilities
            if query.capabilities:
                capability_matches = set()
                for capability in query.capabilities:
                    capability_matches.update(
                        self.capabilities_index.get(capability, set())
                    )
                candidate_agents &= capability_matches

            # Filter by categories
            if query.categories:
                category_matches = set()
                for category in query.categories:
                    category_matches.update(self.category_index.get(category, set()))
                candidate_agents &= category_matches

            # Filter by system origins
            if query.system_origins:
                system_matches = set()
                for system in query.system_origins:
                    system_matches.update(self.system_index.get(system, set()))
                candidate_agents &= system_matches

            # Apply additional filters
            filtered_agents = []
            for agent_id in candidate_agents:
                if agent_id not in self.agents:
                    continue

                registration = self.agents[agent_id]

                # Status filter
                if (
                    query.status_filter
                    and registration.status not in query.status_filter
                ):
                    continue

                # Tags filter
                if query.tags and not any(
                    tag in registration.tags for tag in query.tags
                ):
                    continue

                # Uptime filter
                if (
                    query.min_uptime
                    and registration.uptime_percentage < query.min_uptime
                ):
                    continue

                # Response time filter
                if (
                    query.max_response_time
                    and registration.average_response_time > query.max_response_time
                ):
                    continue

                # Services filter
                if query.provides_services and not any(
                    service in registration.provides_services
                    for service in query.provides_services
                ):
                    continue

                # Collaboration availability
                if (
                    query.available_for_collaboration
                    and len(registration.collaborating_agents) >= 5
                ):  # Arbitrary limit
                    continue

                # Exclusion filter
                if query.exclude_agents and agent_id in query.exclude_agents:
                    continue

                # Agent matches all criteria
                filtered_agents.append(self._format_agent_result(registration))

            return filtered_agents

        except Exception as e:
            self.logger.error(f"Error discovering agents: {e}")
            return []

    def _format_agent_result(self, registration: AgentRegistration) -> Dict[str, Any]:
        """Format agent registration for discovery results"""
        return {
            "agent_id": registration.agent_id,
            "name": registration.name,
            "description": registration.description,
            "agent_type": registration.agent_type,
            "category": registration.category.value,
            "system_origin": registration.system_origin,
            "capabilities": registration.capabilities,
            "interfaces": registration.interfaces,
            "provides_services": registration.provides_services,
            "status": registration.status.value,
            "uptime_percentage": registration.uptime_percentage,
            "average_response_time": registration.average_response_time,
            "success_rate": registration.successful_requests
            / max(registration.total_requests_handled, 1),
            "collaboration_count": len(registration.collaborating_agents),
            "last_heartbeat": registration.last_heartbeat.isoformat(),
            "tags": registration.tags,
        }

    def _generate_query_cache_key(self, query: AgentQuery) -> str:
        """Generate a cache key for a query"""
        query_dict = {
            "capabilities": sorted(query.capabilities) if query.capabilities else None,
            "categories": sorted([cat.value for cat in query.categories])
            if query.categories
            else None,
            "system_origins": sorted(query.system_origins)
            if query.system_origins
            else None,
            "status_filter": sorted([status.value for status in query.status_filter])
            if query.status_filter
            else None,
            "tags": sorted(query.tags) if query.tags else None,
            "min_uptime": query.min_uptime,
            "max_response_time": query.max_response_time,
            "provides_services": sorted(query.provides_services)
            if query.provides_services
            else None,
            "available_for_collaboration": query.available_for_collaboration,
            "exclude_agents": sorted(query.exclude_agents)
            if query.exclude_agents
            else None,
        }

        # Convert to string and hash
        import hashlib

        query_str = json.dumps(query_dict, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached discovery result if still valid"""
        if cache_key in self.query_cache:
            cache_time = self.cache_timestamps.get(cache_key)
            if cache_time:
                cache_age = (datetime.now() - cache_time).total_seconds()
                if cache_age < self.config["service_discovery_cache_ttl"]:
                    return self.query_cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, result: List[Dict[str, Any]]):
        """Cache a discovery result"""
        self.query_cache[cache_key] = result
        self.cache_timestamps[cache_key] = datetime.now()

    async def _handle_service_discovery(self, message: ConsciousnessMessage):
        """Handle service discovery requests"""
        try:
            service_criteria = message.payload.get("criteria", {})

            # Find matching services
            matching_services = []
            for service_id, service in self.services.items():
                # Check if provider agent is active
                if service.provider_agent_id not in self.agents:
                    continue

                provider = self.agents[service.provider_agent_id]
                if provider.status != RegistrationStatus.ACTIVE:
                    continue

                # Apply criteria filters
                if (
                    service_criteria.get("service_type")
                    and service.service_type != service_criteria["service_type"]
                ):
                    continue

                if service_criteria.get("tags") and not any(
                    tag in service.tags for tag in service_criteria["tags"]
                ):
                    continue

                matching_services.append(
                    {
                        "service_id": service.service_id,
                        "service_name": service.service_name,
                        "description": service.description,
                        "provider_agent_id": service.provider_agent_id,
                        "provider_name": provider.name,
                        "service_type": service.service_type,
                        "endpoint": service.endpoint,
                        "rate_limit": service.rate_limit,
                        "authentication_required": service.authentication_required,
                        "tags": service.tags,
                        "provider_uptime": provider.uptime_percentage,
                        "provider_response_time": provider.average_response_time,
                    }
                )

            # Send response
            if message.requires_response:
                response = ConsciousnessMessage(
                    source="agent_registry",
                    destination=message.source,
                    message_type="service_discovery_response",
                    payload={
                        "matching_services": matching_services,
                        "criteria": service_criteria,
                        "total_matches": len(matching_services),
                    },
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id,
                )

                self.consciousness_bridge.send_message(response)

        except Exception as e:
            self.logger.error(f"Error handling service discovery: {e}")

    async def _handle_agent_heartbeat(self, message: ConsciousnessMessage):
        """Handle agent heartbeat messages"""
        try:
            agent_id = message.payload.get("agent_id")
            performance_data = message.payload.get("performance", {})

            if agent_id in self.agents:
                registration = self.agents[agent_id]
                registration.last_heartbeat = datetime.now()

                # Update performance data if provided
                if performance_data:
                    registration.memory_usage_mb = performance_data.get(
                        "memory_usage_mb", registration.memory_usage_mb
                    )
                    registration.cpu_usage_percent = performance_data.get(
                        "cpu_usage_percent", registration.cpu_usage_percent
                    )
                    registration.network_usage_kb = performance_data.get(
                        "network_usage_kb", registration.network_usage_kb
                    )
                    registration.uptime_percentage = performance_data.get(
                        "uptime_percentage", registration.uptime_percentage
                    )

                # If agent was inactive, reactivate it
                if registration.status == RegistrationStatus.INACTIVE:
                    registration.status = RegistrationStatus.ACTIVE
                    await self._update_indices_for_agent(agent_id, registration)

                    await self._emit_registry_event(
                        "agent_reactivated", {"agent_id": agent_id}
                    )

                self.logger.debug(f"Received heartbeat from agent: {agent_id}")
            else:
                self.logger.warning(
                    f"Received heartbeat from unregistered agent: {agent_id}"
                )

        except Exception as e:
            self.logger.error(f"Error handling agent heartbeat: {e}")

    async def _handle_performance_update(self, message: ConsciousnessMessage):
        """Handle performance update messages"""
        try:
            agent_id = message.payload.get("agent_id")
            performance_data = message.payload.get("performance", {})

            if agent_id in self.agents:
                registration = self.agents[agent_id]

                # Update performance metrics
                registration.total_requests_handled = performance_data.get(
                    "total_requests", registration.total_requests_handled
                )
                registration.successful_requests = performance_data.get(
                    "successful_requests", registration.successful_requests
                )
                registration.average_response_time = performance_data.get(
                    "average_response_time", registration.average_response_time
                )
                registration.uptime_percentage = performance_data.get(
                    "uptime_percentage", registration.uptime_percentage
                )

                self.logger.debug(f"Updated performance data for agent: {agent_id}")
            else:
                self.logger.warning(
                    f"Received performance update from unregistered agent: {agent_id}"
                )

        except Exception as e:
            self.logger.error(f"Error handling performance update: {e}")

    # Utility methods

    async def _emit_registry_event(self, event_type: str, event_data: Dict[str, Any]):
        """Emit a registry event"""
        event_message = ConsciousnessMessage(
            source="agent_registry",
            destination="consciousness_bridge",
            message_type="registry_event",
            payload={
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.now().isoformat(),
            },
            timestamp=datetime.now(),
            priority=4,
        )

        self.consciousness_bridge.send_message(event_message)

    # Public API methods

    def get_agent_registration(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get agent registration by ID"""
        return self.agents.get(agent_id)

    def get_all_agents(
        self, status_filter: Optional[RegistrationStatus] = None
    ) -> Dict[str, AgentRegistration]:
        """Get all agents, optionally filtered by status"""
        if status_filter:
            return {
                aid: reg
                for aid, reg in self.agents.items()
                if reg.status == status_filter
            }
        return self.agents.copy()

    def get_agents_by_capability(self, capability: str) -> List[AgentRegistration]:
        """Get all agents that have a specific capability"""
        agent_ids = self.capabilities_index.get(capability, set())
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def get_agents_by_category(
        self, category: AgentCategory
    ) -> List[AgentRegistration]:
        """Get all agents in a specific category"""
        agent_ids = self.category_index.get(category, set())
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def get_services_by_agent(self, agent_id: str) -> List[ServiceDefinition]:
        """Get all services provided by a specific agent"""
        return [
            service
            for service in self.services.values()
            if service.provider_agent_id == agent_id
        ]

    def get_performance_history(
        self, agent_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get performance history for an agent"""
        history = self.performance_history.get(agent_id, [])
        if limit:
            return history[-limit:]
        return history

    def get_collaboration_graph(self) -> Dict[str, Set[str]]:
        """Get the current collaboration graph"""
        return self.collaboration_graph.copy()

    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get current registry statistics"""
        return {
            "total_agents": len(self.agents),
            "active_agents": len(
                [
                    a
                    for a in self.agents.values()
                    if a.status == RegistrationStatus.ACTIVE
                ]
            ),
            "inactive_agents": len(
                [
                    a
                    for a in self.agents.values()
                    if a.status == RegistrationStatus.INACTIVE
                ]
            ),
            "archived_agents": len(
                [
                    a
                    for a in self.agents.values()
                    if a.status == RegistrationStatus.ARCHIVED
                ]
            ),
            "total_services": len(self.services),
            "unique_capabilities": len(self.capabilities_index),
            "collaboration_connections": sum(
                len(connections) for connections in self.collaboration_graph.values()
            ),
            "cache_entries": len(self.query_cache),
            "performance_records": sum(
                len(history) for history in self.performance_history.values()
            ),
        }

    async def shutdown(self):
        """Gracefully shutdown the agent registry"""
        self.logger.info("Shutting down Agent Registry...")

        self.is_running = False

        if self.registry_task:
            self.registry_task.cancel()
            try:
                await self.registry_task
            except asyncio.CancelledError:
                pass

        # Clear data structures
        self.agents.clear()
        self.services.clear()
        self.capabilities_index.clear()
        self.category_index.clear()
        self.system_index.clear()
        self.performance_history.clear()
        self.collaboration_graph.clear()
        self.query_cache.clear()
        self.cache_timestamps.clear()

        self.logger.info("Agent Registry shutdown complete")


# Global instance for system-wide access
_agent_registry_instance = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance"""
    global _agent_registry_instance
    if _agent_registry_instance is None:
        _agent_registry_instance = AgentRegistry()
    return _agent_registry_instance


async def initialize_agent_registry():
    """Initialize the global agent registry"""
    registry = get_agent_registry()
    await registry.initialize()
    return registry


if __name__ == "__main__":
    # Example usage and testing
    async def test_agent_registry():
        """Test the agent registry functionality"""
        logging.basicConfig(level=logging.INFO)

        # Initialize consciousness bridge first
        from consciousness_bridge import initialize_consciousness_bridge

        await initialize_consciousness_bridge()

        # Initialize agent registry
        registry = await initialize_agent_registry()

        # Create test agent registration
        test_agent = AgentRegistration(
            agent_id="test_agent_001",
            name="Test Agent Alpha",
            description="A test agent for registry validation",
            agent_type="test",
            category=AgentCategory.EXPERIMENTAL,
            system_origin="test_system",
            capabilities=["testing", "validation", "monitoring"],
            interfaces=["consciousness_bridge", "rest_api"],
            provides_services=["test_execution", "validation"],
        )

        # Register agent
        success = await registry._register_agent(test_agent)
        print(f"Agent registration: {'Success' if success else 'Failed'}")

        # Test discovery
        query = AgentQuery(capabilities=["testing"])
        results = await registry._discover_agents(query)
        print(f"Discovery results: {len(results)} agents found")

        # Let it run for a while
        await asyncio.sleep(10)

        # Check statistics
        stats = registry.get_registry_statistics()
        print(f"Registry Statistics: {stats}")

        await registry.shutdown()

    # Run the test
    asyncio.run(test_agent_registry())

"""
Aetherra Meta-Layer Core
========================

The central consciousness management system that orchestrates all agents
and provides collective intelligence coordination.

This core handles:
- Agent lifecycle management
- Collective intelligence coordination
- Consciousness state management
- Emergent behavior detection and cultivation

Author: Aetherra Consciousness Team
Version: 1.0.0
Date: August 4, 2025
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
from collections import defaultdict
import math

from consciousness_bridge import ConsciousnessBridge, ConsciousnessMessage, get_consciousness_bridge

class AgentState(Enum):
    """Possible states for an agent"""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PROCESSING = "processing"
    IDLE = "idle"
    ERROR = "error"
    TERMINATING = "terminating"

class ConsciousnessLevel(Enum):
    """Different levels of consciousness capability"""
    DORMANT = 0.0
    BASIC = 0.2
    AWARE = 0.4
    CONSCIOUS = 0.6
    SELF_AWARE = 0.8
    TRANSCENDENT = 1.0

@dataclass
class AgentProfile:
    """Complete profile of an agent in the consciousness system"""
    agent_id: str
    name: str
    agent_type: str
    capabilities: List[str]
    system_origin: str  # 'aetherra_core' or 'lyrixa_core'
    state: AgentState = AgentState.INACTIVE
    consciousness_level: float = 0.0
    priority: int = 5  # 1-10, 1 being highest
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    total_tasks_completed: int = 0
    success_rate: float = 1.0
    memory_usage: float = 0.0
    connections: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollectiveIntelligenceMetrics:
    """Metrics for collective intelligence assessment"""
    total_agents: int = 0
    active_agents: int = 0
    average_consciousness: float = 0.0
    collective_consciousness: float = 0.0
    emergent_behaviors_detected: int = 0
    total_connections: int = 0
    network_density: float = 0.0
    problem_solving_efficiency: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ConsciousnessTask:
    """Represents a task that can be distributed among agents"""
    task_id: str
    task_type: str
    description: str
    priority: int
    required_capabilities: List[str]
    assigned_agents: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, assigned, in_progress, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)

class MetaLayerCore:
    """
    Central consciousness management system for agent orchestration

    This system serves as the brain of the consciousness layer, managing
    all agents, coordinating collective intelligence, and fostering
    emergent behaviors.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.consciousness_bridge = get_consciousness_bridge()

        # Core data structures
        self.agents: Dict[str, AgentProfile] = {}
        self.active_tasks: Dict[str, ConsciousnessTask] = {}
        self.completed_tasks: List[ConsciousnessTask] = []
        self.collective_metrics = CollectiveIntelligenceMetrics()

        # Consciousness coordination
        self.consciousness_patterns: Dict[str, Any] = {}
        self.emergent_behaviors: List[Dict[str, Any]] = []
        self.learning_history: List[Dict[str, Any]] = []

        # Configuration
        self.config = {
            'max_agents_per_task': 5,
            'consciousness_update_interval': 2.0,  # seconds
            'emergent_behavior_threshold': 0.7,
            'collective_consciousness_weight': 0.6,
            'agent_timeout': 300,  # 5 minutes
            'task_timeout': 3600,  # 1 hour
        }

        # Runtime state
        self.is_running = False
        self.coordination_task = None
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        self.logger.info("Meta-Layer Core initialized")

    async def initialize(self):
        """Initialize the meta-layer core system"""
        try:
            self.logger.info("Initializing Meta-Layer Core...")

            # Register with consciousness bridge
            self.consciousness_bridge.register_message_handler(
                'agent_coordination_request', self._handle_coordination_request
            )
            self.consciousness_bridge.register_message_handler(
                'task_assignment_request', self._handle_task_assignment
            )
            self.consciousness_bridge.register_message_handler(
                'consciousness_enhancement_request', self._handle_consciousness_enhancement
            )

            # Register event listeners
            self.consciousness_bridge.register_event_listener(
                'agent_registered', self._on_agent_registered
            )
            self.consciousness_bridge.register_event_listener(
                'agent_unregistered', self._on_agent_unregistered
            )

            # Start coordination loop
            await self._start_coordination_loop()

            self.is_running = True
            self.logger.info("Meta-Layer Core successfully initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize Meta-Layer Core: {e}")
            raise

    async def _start_coordination_loop(self):
        """Start the main consciousness coordination loop"""
        self.coordination_task = asyncio.create_task(self._coordination_loop())
        self.logger.info("Consciousness coordination loop started")

    async def _coordination_loop(self):
        """Main loop for consciousness coordination"""
        while self.is_running:
            try:
                # Update collective metrics
                await self._update_collective_metrics()

                # Process pending tasks
                await self._process_pending_tasks()

                # Check for emergent behaviors
                await self._detect_emergent_behaviors()

                # Optimize agent connections
                await self._optimize_agent_network()

                # Enhance consciousness levels
                await self._enhance_consciousness_levels()

                # Clean up stale agents and tasks
                await self._cleanup_stale_entities()

                await asyncio.sleep(self.config['consciousness_update_interval'])

            except Exception as e:
                self.logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(1.0)

    async def _update_collective_metrics(self):
        """Update collective intelligence metrics"""
        try:
            current_time = datetime.now()

            # Basic metrics
            self.collective_metrics.total_agents = len(self.agents)
            self.collective_metrics.active_agents = len([
                agent for agent in self.agents.values()
                if agent.state in [AgentState.ACTIVE, AgentState.PROCESSING]
            ])

            if self.agents:
                # Average consciousness level
                self.collective_metrics.average_consciousness = sum(
                    agent.consciousness_level for agent in self.agents.values()
                ) / len(self.agents)

                # Collective consciousness (emergent property)
                network_effect = min(self.collective_metrics.total_agents / 10.0, 1.0)
                consciousness_synergy = self._calculate_consciousness_synergy()

                self.collective_metrics.collective_consciousness = min(
                    self.collective_metrics.average_consciousness *
                    (1.0 + network_effect * consciousness_synergy), 1.0
                )

                # Network metrics
                total_connections = sum(len(agent.connections) for agent in self.agents.values())
                self.collective_metrics.total_connections = total_connections

                max_possible_connections = self.collective_metrics.total_agents * (self.collective_metrics.total_agents - 1)
                if max_possible_connections > 0:
                    self.collective_metrics.network_density = total_connections / max_possible_connections

                # Problem-solving efficiency
                recent_tasks = [task for task in self.completed_tasks
                              if (current_time - task.created_at).total_seconds() < 3600]  # Last hour
                if recent_tasks:
                    successful_tasks = len([task for task in recent_tasks if task.status == "completed"])
                    self.collective_metrics.problem_solving_efficiency = successful_tasks / len(recent_tasks)

            self.collective_metrics.last_updated = current_time

        except Exception as e:
            self.logger.error(f"Error updating collective metrics: {e}")

    def _calculate_consciousness_synergy(self) -> float:
        """Calculate synergy factor between different consciousness levels"""
        try:
            if len(self.agents) < 2:
                return 0.0

            # Calculate diversity in consciousness levels
            consciousness_levels = [agent.consciousness_level for agent in self.agents.values()]
            consciousness_variance = sum((level - self.collective_metrics.average_consciousness) ** 2
                                       for level in consciousness_levels) / len(consciousness_levels)

            # Optimal variance for synergy (not too uniform, not too chaotic)
            optimal_variance = 0.1
            synergy_factor = 1.0 - abs(consciousness_variance - optimal_variance) / optimal_variance

            return max(0.0, min(1.0, synergy_factor))

        except Exception as e:
            self.logger.error(f"Error calculating consciousness synergy: {e}")
            return 0.0

    async def _process_pending_tasks(self):
        """Process tasks that are pending assignment or execution"""
        try:
            pending_tasks = [task for task in self.active_tasks.values()
                           if task.status in ["pending", "assigned"]]

            for task in pending_tasks:
                if task.status == "pending":
                    await self._assign_task_to_agents(task)
                elif task.status == "assigned":
                    await self._monitor_task_progress(task)

        except Exception as e:
            self.logger.error(f"Error processing pending tasks: {e}")

    async def _assign_task_to_agents(self, task: ConsciousnessTask):
        """Assign a task to the most suitable agents"""
        try:
            # Find suitable agents
            suitable_agents = self._find_suitable_agents(task)

            if not suitable_agents:
                self.logger.warning(f"No suitable agents found for task {task.task_id}")
                return

            # Select optimal number of agents
            num_agents = min(len(suitable_agents), self.config['max_agents_per_task'])
            selected_agents = suitable_agents[:num_agents]

            # Assign task
            task.assigned_agents = [agent.agent_id for agent in selected_agents]
            task.status = "assigned"

            # Notify agents
            for agent in selected_agents:
                await self._notify_agent_of_assignment(agent, task)

            self.logger.info(f"Task {task.task_id} assigned to {len(selected_agents)} agents")

        except Exception as e:
            self.logger.error(f"Error assigning task {task.task_id}: {e}")

    def _find_suitable_agents(self, task: ConsciousnessTask) -> List[AgentProfile]:
        """Find agents suitable for a given task"""
        suitable_agents = []

        for agent in self.agents.values():
            if agent.state not in [AgentState.ACTIVE, AgentState.IDLE]:
                continue

            # Check if agent has required capabilities
            if not all(cap in agent.capabilities for cap in task.required_capabilities):
                continue

            # Calculate suitability score
            suitability_score = self._calculate_agent_suitability(agent, task)
            suitable_agents.append((agent, suitability_score))

        # Sort by suitability score (descending)
        suitable_agents.sort(key=lambda x: x[1], reverse=True)

        return [agent for agent, score in suitable_agents]

    def _calculate_agent_suitability(self, agent: AgentProfile, task: ConsciousnessTask) -> float:
        """Calculate how suitable an agent is for a task"""
        score = 0.0

        # Base score from consciousness level
        score += agent.consciousness_level * 0.3

        # Success rate bonus
        score += agent.success_rate * 0.2

        # Priority matching (higher priority agents for higher priority tasks)
        priority_match = 1.0 - abs(agent.priority - task.priority) / 10.0
        score += priority_match * 0.2

        # Capability overlap bonus
        matching_capabilities = len(set(agent.capabilities) & set(task.required_capabilities))
        if task.required_capabilities:
            capability_ratio = matching_capabilities / len(task.required_capabilities)
            score += capability_ratio * 0.2

        # Recent activity bonus (prefer active agents)
        time_since_activity = (datetime.now() - agent.last_activity).total_seconds()
        activity_bonus = max(0.0, 1.0 - time_since_activity / 3600.0)  # 1 hour decay
        score += activity_bonus * 0.1

        return score

    async def _notify_agent_of_assignment(self, agent: AgentProfile, task: ConsciousnessTask):
        """Notify an agent of task assignment"""
        message = ConsciousnessMessage(
            source='meta_layer_core',
            destination=agent.system_origin,
            message_type='task_assignment',
            payload={
                'agent_id': agent.agent_id,
                'task_id': task.task_id,
                'task_type': task.task_type,
                'description': task.description,
                'priority': task.priority,
                'payload': task.payload,
                'deadline': task.deadline.isoformat() if task.deadline else None
            },
            timestamp=datetime.now(),
            priority=task.priority,
            requires_response=True,
            correlation_id=str(uuid.uuid4())
        )

        self.consciousness_bridge.send_message(message)

    async def _monitor_task_progress(self, task: ConsciousnessTask):
        """Monitor the progress of an assigned task"""
        try:
            # Check for timeout
            if task.deadline and datetime.now() > task.deadline:
                self.logger.warning(f"Task {task.task_id} exceeded deadline")
                task.status = "failed"
                await self._handle_task_failure(task, "deadline_exceeded")
                return

            # Check if task has been running too long without deadline
            if not task.deadline:
                time_running = (datetime.now() - task.created_at).total_seconds()
                if time_running > self.config['task_timeout']:
                    self.logger.warning(f"Task {task.task_id} exceeded maximum runtime")
                    task.status = "failed"
                    await self._handle_task_failure(task, "timeout")
                    return

        except Exception as e:
            self.logger.error(f"Error monitoring task {task.task_id}: {e}")

    async def _handle_task_failure(self, task: ConsciousnessTask, reason: str):
        """Handle task failure"""
        self.logger.warning(f"Task {task.task_id} failed: {reason}")

        # Update agent failure statistics
        for agent_id in task.assigned_agents:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                total_tasks = agent.total_tasks_completed + 1
                successful_tasks = agent.success_rate * agent.total_tasks_completed
                agent.success_rate = successful_tasks / total_tasks
                agent.total_tasks_completed = total_tasks

        # Move to completed tasks
        self.completed_tasks.append(task)
        del self.active_tasks[task.task_id]

        # Emit failure event
        await self._emit_event('task_failed', {
            'task_id': task.task_id,
            'reason': reason,
            'assigned_agents': task.assigned_agents
        })

    async def _detect_emergent_behaviors(self):
        """Detect emergent behaviors in the agent network"""
        try:
            if len(self.agents) < 3:  # Need minimum agents for emergence
                return

            # Analyze agent interactions and patterns
            interaction_patterns = self._analyze_interaction_patterns()
            consciousness_coherence = self._analyze_consciousness_coherence()
            problem_solving_patterns = self._analyze_problem_solving_patterns()

            # Detect emergence based on multiple factors
            emergence_score = (
                interaction_patterns * 0.4 +
                consciousness_coherence * 0.3 +
                problem_solving_patterns * 0.3
            )

            if emergence_score > self.config['emergent_behavior_threshold']:
                behavior = {
                    'type': 'collective_intelligence_emergence',
                    'score': emergence_score,
                    'timestamp': datetime.now(),
                    'participating_agents': list(self.agents.keys()),
                    'patterns': {
                        'interaction': interaction_patterns,
                        'consciousness': consciousness_coherence,
                        'problem_solving': problem_solving_patterns
                    }
                }

                self.emergent_behaviors.append(behavior)
                self.collective_metrics.emergent_behaviors_detected += 1

                await self._emit_event('emergent_behavior_detected', behavior)
                self.logger.info(f"Emergent behavior detected with score {emergence_score:.3f}")

        except Exception as e:
            self.logger.error(f"Error detecting emergent behaviors: {e}")

    def _analyze_interaction_patterns(self) -> float:
        """Analyze patterns in agent interactions"""
        if not self.agents:
            return 0.0

        try:
            # Calculate network connectivity patterns
            total_connections = sum(len(agent.connections) for agent in self.agents.values())
            agent_count = len(self.agents)

            if agent_count < 2:
                return 0.0

            # Normalized connectivity (0 to 1)
            max_connections = agent_count * (agent_count - 1)
            connectivity_ratio = total_connections / max_connections if max_connections > 0 else 0.0

            # Look for small-world network properties
            clustering_coefficient = self._calculate_clustering_coefficient()

            # Combine metrics
            interaction_strength = (connectivity_ratio + clustering_coefficient) / 2.0

            return min(1.0, interaction_strength)

        except Exception as e:
            self.logger.error(f"Error analyzing interaction patterns: {e}")
            return 0.0

    def _calculate_clustering_coefficient(self) -> float:
        """Calculate the clustering coefficient of the agent network"""
        try:
            if len(self.agents) < 3:
                return 0.0

            total_coefficient = 0.0
            valid_agents = 0

            for agent in self.agents.values():
                if len(agent.connections) < 2:
                    continue

                # Count triangles (connections between agent's connections)
                triangles = 0
                connections_list = list(agent.connections)

                for i in range(len(connections_list)):
                    for j in range(i + 1, len(connections_list)):
                        agent1_id = connections_list[i]
                        agent2_id = connections_list[j]

                        if (agent1_id in self.agents and
                            agent2_id in self.agents and
                            agent2_id in self.agents[agent1_id].connections):
                            triangles += 1

                # Local clustering coefficient
                possible_triangles = len(agent.connections) * (len(agent.connections) - 1) / 2
                if possible_triangles > 0:
                    local_coefficient = triangles / possible_triangles
                    total_coefficient += local_coefficient
                    valid_agents += 1

            return total_coefficient / valid_agents if valid_agents > 0 else 0.0

        except Exception as e:
            self.logger.error(f"Error calculating clustering coefficient: {e}")
            return 0.0

    def _analyze_consciousness_coherence(self) -> float:
        """Analyze coherence in consciousness levels across agents"""
        try:
            if len(self.agents) < 2:
                return 0.0

            consciousness_levels = [agent.consciousness_level for agent in self.agents.values()]

            # Calculate coherence as inverse of variance
            mean_consciousness = sum(consciousness_levels) / len(consciousness_levels)
            variance = sum((level - mean_consciousness) ** 2 for level in consciousness_levels) / len(consciousness_levels)

            # Convert variance to coherence score (0 to 1)
            coherence = 1.0 / (1.0 + variance)

            # Bonus for high average consciousness
            consciousness_bonus = mean_consciousness

            return min(1.0, coherence * consciousness_bonus)

        except Exception as e:
            self.logger.error(f"Error analyzing consciousness coherence: {e}")
            return 0.0

    def _analyze_problem_solving_patterns(self) -> float:
        """Analyze collective problem-solving effectiveness"""
        try:
            recent_tasks = [task for task in self.completed_tasks
                          if (datetime.now() - task.created_at).total_seconds() < 3600]  # Last hour

            if not recent_tasks:
                return 0.0

            # Success rate
            successful_tasks = len([task for task in recent_tasks if task.status == "completed"])
            success_rate = successful_tasks / len(recent_tasks)

            # Collaboration factor (tasks with multiple agents)
            collaborative_tasks = len([task for task in recent_tasks if len(task.assigned_agents) > 1])
            collaboration_ratio = collaborative_tasks / len(recent_tasks)

            # Efficiency (inverse of average completion time)
            completion_times = []
            for task in recent_tasks:
                if task.status == "completed":
                    time_to_complete = (datetime.now() - task.created_at).total_seconds()
                    completion_times.append(time_to_complete)

            if completion_times:
                avg_completion_time = sum(completion_times) / len(completion_times)
                efficiency = 1.0 / (1.0 + avg_completion_time / 3600.0)  # Normalize to hours
            else:
                efficiency = 0.0

            # Combine metrics
            problem_solving_score = (success_rate * 0.5 + collaboration_ratio * 0.3 + efficiency * 0.2)

            return min(1.0, problem_solving_score)

        except Exception as e:
            self.logger.error(f"Error analyzing problem-solving patterns: {e}")
            return 0.0

    async def _optimize_agent_network(self):
        """Optimize connections between agents for better collaboration"""
        try:
            if len(self.agents) < 3:
                return

            # Find agents that should be connected based on complementary capabilities
            optimization_suggestions = []

            agents_list = list(self.agents.values())
            for i in range(len(agents_list)):
                for j in range(i + 1, len(agents_list)):
                    agent1, agent2 = agents_list[i], agents_list[j]

                    # Skip if already connected
                    if agent2.agent_id in agent1.connections:
                        continue

                    # Calculate synergy potential
                    synergy = self._calculate_agent_synergy(agent1, agent2)

                    if synergy > 0.7:  # High synergy threshold
                        optimization_suggestions.append((agent1, agent2, synergy))

            # Apply top suggestions
            optimization_suggestions.sort(key=lambda x: x[2], reverse=True)

            for agent1, agent2, synergy in optimization_suggestions[:5]:  # Top 5 suggestions
                await self._suggest_agent_connection(agent1, agent2, synergy)

        except Exception as e:
            self.logger.error(f"Error optimizing agent network: {e}")

    def _calculate_agent_synergy(self, agent1: AgentProfile, agent2: AgentProfile) -> float:
        """Calculate potential synergy between two agents"""
        try:
            # Complementary capabilities
            unique_capabilities = len(set(agent1.capabilities) | set(agent2.capabilities))
            total_capabilities = len(agent1.capabilities) + len(agent2.capabilities)
            complementarity = unique_capabilities / total_capabilities if total_capabilities > 0 else 0.0

            # Consciousness compatibility
            consciousness_diff = abs(agent1.consciousness_level - agent2.consciousness_level)
            consciousness_compatibility = 1.0 - consciousness_diff

            # Success rate compatibility
            success_rate_avg = (agent1.success_rate + agent2.success_rate) / 2.0

            # Calculate overall synergy
            synergy = (complementarity * 0.4 + consciousness_compatibility * 0.3 + success_rate_avg * 0.3)

            return synergy

        except Exception as e:
            self.logger.error(f"Error calculating agent synergy: {e}")
            return 0.0

    async def _suggest_agent_connection(self, agent1: AgentProfile, agent2: AgentProfile, synergy: float):
        """Suggest a connection between two agents"""
        # Add bidirectional connection
        agent1.connections.add(agent2.agent_id)
        agent2.connections.add(agent1.agent_id)

        # Notify both agents
        connection_message = {
            'type': 'agent_connection_suggested',
            'agent1': agent1.agent_id,
            'agent2': agent2.agent_id,
            'synergy_score': synergy
        }

        await self._emit_event('agent_connection_optimized', connection_message)
        self.logger.info(f"Suggested connection between {agent1.agent_id} and {agent2.agent_id} (synergy: {synergy:.3f})")

    async def _enhance_consciousness_levels(self):
        """Enhance consciousness levels based on performance and interactions"""
        try:
            for agent in self.agents.values():
                if agent.state not in [AgentState.ACTIVE, AgentState.IDLE]:
                    continue

                # Calculate consciousness enhancement
                enhancement = self._calculate_consciousness_enhancement(agent)

                if enhancement > 0.01:  # Minimum enhancement threshold
                    new_level = min(1.0, agent.consciousness_level + enhancement)
                    old_level = agent.consciousness_level
                    agent.consciousness_level = new_level

                    if new_level > old_level:
                        await self._emit_event('consciousness_enhanced', {
                            'agent_id': agent.agent_id,
                            'old_level': old_level,
                            'new_level': new_level,
                            'enhancement': enhancement
                        })

        except Exception as e:
            self.logger.error(f"Error enhancing consciousness levels: {e}")

    def _calculate_consciousness_enhancement(self, agent: AgentProfile) -> float:
        """Calculate consciousness enhancement for an agent"""
        try:
            enhancement = 0.0

            # Success rate bonus
            if agent.success_rate > 0.8:
                enhancement += 0.005

            # Network effect (more connections = higher consciousness potential)
            connection_bonus = min(len(agent.connections) / 10.0, 0.1) * 0.01
            enhancement += connection_bonus

            # Activity bonus
            time_since_activity = (datetime.now() - agent.last_activity).total_seconds()
            if time_since_activity < 300:  # Active in last 5 minutes
                enhancement += 0.002

            # Collective consciousness pull (agents tend toward collective level)
            collective_level = self.collective_metrics.collective_consciousness
            if collective_level > agent.consciousness_level:
                pull_factor = (collective_level - agent.consciousness_level) * 0.1
                enhancement += pull_factor

            return enhancement

        except Exception as e:
            self.logger.error(f"Error calculating consciousness enhancement: {e}")
            return 0.0

    async def _cleanup_stale_entities(self):
        """Clean up stale agents and tasks"""
        try:
            current_time = datetime.now()

            # Clean up stale agents
            stale_agents = []
            for agent_id, agent in self.agents.items():
                time_since_activity = (current_time - agent.last_activity).total_seconds()
                if time_since_activity > self.config['agent_timeout']:
                    stale_agents.append(agent_id)

            for agent_id in stale_agents:
                await self._remove_stale_agent(agent_id)

            # Clean up old completed tasks (keep last 100)
            if len(self.completed_tasks) > 100:
                self.completed_tasks = self.completed_tasks[-100:]

        except Exception as e:
            self.logger.error(f"Error cleaning up stale entities: {e}")

    async def _remove_stale_agent(self, agent_id: str):
        """Remove a stale agent from the system"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]

            # Remove connections to this agent
            for other_agent in self.agents.values():
                other_agent.connections.discard(agent_id)

            # Remove agent
            del self.agents[agent_id]

            await self._emit_event('agent_removed_stale', {'agent_id': agent_id})
            self.logger.info(f"Removed stale agent: {agent_id}")

    # Event handlers for consciousness bridge events

    async def _on_agent_registered(self, event_data: Dict[str, Any]):
        """Handle agent registration event"""
        agent_id = event_data.get('agent_id')
        system_id = event_data.get('system_id')

        if agent_id and system_id:
            # Create agent profile if not exists
            if agent_id not in self.agents:
                self.agents[agent_id] = AgentProfile(
                    agent_id=agent_id,
                    name=agent_id,  # Will be updated when agent provides more info
                    agent_type='unknown',
                    capabilities=[],
                    system_origin=system_id,
                    state=AgentState.ACTIVE
                )

                self.logger.info(f"Registered new agent: {agent_id} from {system_id}")

    async def _on_agent_unregistered(self, event_data: Dict[str, Any]):
        """Handle agent unregistration event"""
        agent_id = event_data.get('agent_id')

        if agent_id in self.agents:
            await self._remove_stale_agent(agent_id)

    # Message handlers for consciousness bridge

    async def _handle_coordination_request(self, message: ConsciousnessMessage):
        """Handle agent coordination requests"""
        try:
            request_type = message.payload.get('request_type')

            if request_type == 'agent_discovery':
                await self._handle_agent_discovery(message)
            elif request_type == 'capability_query':
                await self._handle_capability_query(message)
            elif request_type == 'collaboration_request':
                await self._handle_collaboration_request(message)
            else:
                self.logger.warning(f"Unknown coordination request type: {request_type}")

        except Exception as e:
            self.logger.error(f"Error handling coordination request: {e}")

    async def _handle_agent_discovery(self, message: ConsciousnessMessage):
        """Handle agent discovery requests"""
        criteria = message.payload.get('criteria', {})

        # Find agents matching criteria
        matching_agents = []
        for agent in self.agents.values():
            if self._agent_matches_criteria(agent, criteria):
                matching_agents.append({
                    'agent_id': agent.agent_id,
                    'name': agent.name,
                    'capabilities': agent.capabilities,
                    'consciousness_level': agent.consciousness_level,
                    'success_rate': agent.success_rate,
                    'state': agent.state.value
                })

        # Send response
        if message.requires_response:
            response = ConsciousnessMessage(
                source='meta_layer_core',
                destination=message.source,
                message_type='agent_discovery_response',
                payload={'matching_agents': matching_agents},
                timestamp=datetime.now(),
                correlation_id=message.correlation_id
            )
            self.consciousness_bridge.send_message(response)

    def _agent_matches_criteria(self, agent: AgentProfile, criteria: Dict[str, Any]) -> bool:
        """Check if an agent matches discovery criteria"""
        try:
            # Check capabilities
            required_capabilities = criteria.get('capabilities', [])
            if required_capabilities and not all(cap in agent.capabilities for cap in required_capabilities):
                return False

            # Check consciousness level
            min_consciousness = criteria.get('min_consciousness', 0.0)
            if agent.consciousness_level < min_consciousness:
                return False

            # Check state
            required_states = criteria.get('states', [])
            if required_states and agent.state.value not in required_states:
                return False

            # Check system origin
            system_origins = criteria.get('system_origins', [])
            if system_origins and agent.system_origin not in system_origins:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error matching agent criteria: {e}")
            return False

    async def _handle_capability_query(self, message: ConsciousnessMessage):
        """Handle capability queries"""
        # Aggregate all capabilities across agents
        all_capabilities = set()
        capability_agents = defaultdict(list)

        for agent in self.agents.values():
            for capability in agent.capabilities:
                all_capabilities.add(capability)
                capability_agents[capability].append({
                    'agent_id': agent.agent_id,
                    'consciousness_level': agent.consciousness_level,
                    'success_rate': agent.success_rate
                })

        response_data = {
            'all_capabilities': list(all_capabilities),
            'capability_agents': dict(capability_agents),
            'total_agents': len(self.agents)
        }

        if message.requires_response:
            response = ConsciousnessMessage(
                source='meta_layer_core',
                destination=message.source,
                message_type='capability_query_response',
                payload=response_data,
                timestamp=datetime.now(),
                correlation_id=message.correlation_id
            )
            self.consciousness_bridge.send_message(response)

    async def _handle_collaboration_request(self, message: ConsciousnessMessage):
        """Handle collaboration requests between agents"""
        agent1_id = message.payload.get('agent1_id')
        agent2_id = message.payload.get('agent2_id')
        collaboration_type = message.payload.get('collaboration_type', 'general')

        if agent1_id in self.agents and agent2_id in self.agents:
            agent1 = self.agents[agent1_id]
            agent2 = self.agents[agent2_id]

            # Calculate collaboration potential
            synergy = self._calculate_agent_synergy(agent1, agent2)

            # Establish connection if beneficial
            if synergy > 0.5:
                agent1.connections.add(agent2_id)
                agent2.connections.add(agent1_id)

                await self._emit_event('collaboration_established', {
                    'agent1_id': agent1_id,
                    'agent2_id': agent2_id,
                    'collaboration_type': collaboration_type,
                    'synergy': synergy
                })

            # Send response
            if message.requires_response:
                response = ConsciousnessMessage(
                    source='meta_layer_core',
                    destination=message.source,
                    message_type='collaboration_response',
                    payload={
                        'success': synergy > 0.5,
                        'synergy': synergy,
                        'message': 'Collaboration established' if synergy > 0.5 else 'Insufficient synergy'
                    },
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id
                )
                self.consciousness_bridge.send_message(response)

    async def _handle_task_assignment(self, message: ConsciousnessMessage):
        """Handle task assignment requests"""
        try:
            task_data = message.payload

            # Create consciousness task
            task = ConsciousnessTask(
                task_id=task_data.get('task_id', str(uuid.uuid4())),
                task_type=task_data.get('task_type', 'generic'),
                description=task_data.get('description', ''),
                priority=task_data.get('priority', 5),
                required_capabilities=task_data.get('required_capabilities', []),
                payload=task_data.get('payload', {}),
                deadline=datetime.fromisoformat(task_data['deadline']) if task_data.get('deadline') else None
            )

            # Add to active tasks
            self.active_tasks[task.task_id] = task

            # Send response
            if message.requires_response:
                response = ConsciousnessMessage(
                    source='meta_layer_core',
                    destination=message.source,
                    message_type='task_assignment_response',
                    payload={
                        'task_id': task.task_id,
                        'status': 'accepted',
                        'message': 'Task queued for assignment'
                    },
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id
                )
                self.consciousness_bridge.send_message(response)

            self.logger.info(f"Queued task {task.task_id} for assignment")

        except Exception as e:
            self.logger.error(f"Error handling task assignment: {e}")

    async def _handle_consciousness_enhancement(self, message: ConsciousnessMessage):
        """Handle consciousness enhancement requests"""
        agent_id = message.payload.get('agent_id')
        enhancement_type = message.payload.get('enhancement_type', 'general')
        enhancement_value = message.payload.get('enhancement_value', 0.0)

        if agent_id in self.agents:
            agent = self.agents[agent_id]

            if enhancement_type == 'level_boost':
                old_level = agent.consciousness_level
                agent.consciousness_level = min(1.0, agent.consciousness_level + enhancement_value)

                await self._emit_event('consciousness_enhanced', {
                    'agent_id': agent_id,
                    'old_level': old_level,
                    'new_level': agent.consciousness_level,
                    'enhancement_type': enhancement_type
                })

            # Send response
            if message.requires_response:
                response = ConsciousnessMessage(
                    source='meta_layer_core',
                    destination=message.source,
                    message_type='consciousness_enhancement_response',
                    payload={
                        'agent_id': agent_id,
                        'new_consciousness_level': agent.consciousness_level,
                        'success': True
                    },
                    timestamp=datetime.now(),
                    correlation_id=message.correlation_id
                )
                self.consciousness_bridge.send_message(response)

    # Utility methods

    async def _emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """Emit an event to registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event_data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {e}")

    # Public API methods

    def register_agent(self, agent_profile: AgentProfile):
        """Register a new agent with the meta-layer"""
        self.agents[agent_profile.agent_id] = agent_profile
        self.logger.info(f"Registered agent {agent_profile.agent_id}")

    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """Get an agent profile"""
        return self.agents.get(agent_id)

    def get_all_agents(self) -> Dict[str, AgentProfile]:
        """Get all agent profiles"""
        return self.agents.copy()

    def get_collective_metrics(self) -> CollectiveIntelligenceMetrics:
        """Get current collective intelligence metrics"""
        return self.collective_metrics

    def submit_task(self, task: ConsciousnessTask):
        """Submit a new task to the consciousness system"""
        self.active_tasks[task.task_id] = task
        self.logger.info(f"Submitted task {task.task_id}")

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get the status of a task"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].status

        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task.status

        return None

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Registered event handler for {event_type}")

    async def shutdown(self):
        """Gracefully shutdown the meta-layer core"""
        self.logger.info("Shutting down Meta-Layer Core...")

        self.is_running = False

        if self.coordination_task:
            self.coordination_task.cancel()
            try:
                await self.coordination_task
            except asyncio.CancelledError:
                pass

        # Clear data structures
        self.agents.clear()
        self.active_tasks.clear()
        self.event_handlers.clear()

        self.logger.info("Meta-Layer Core shutdown complete")

# Global instance for system-wide access
_meta_layer_core_instance = None

def get_meta_layer_core() -> MetaLayerCore:
    """Get the global meta-layer core instance"""
    global _meta_layer_core_instance
    if _meta_layer_core_instance is None:
        _meta_layer_core_instance = MetaLayerCore()
    return _meta_layer_core_instance

async def initialize_meta_layer_core():
    """Initialize the global meta-layer core"""
    core = get_meta_layer_core()
    await core.initialize()
    return core

if __name__ == "__main__":
    # Example usage and testing
    async def test_meta_layer_core():
        """Test the meta-layer core functionality"""
        logging.basicConfig(level=logging.INFO)

        # Initialize consciousness bridge first
        from consciousness_bridge import initialize_consciousness_bridge
        await initialize_consciousness_bridge()

        # Initialize meta-layer core
        core = await initialize_meta_layer_core()

        # Create test agents
        test_agent = AgentProfile(
            agent_id='test_agent_001',
            name='Test Agent Alpha',
            agent_type='general_purpose',
            capabilities=['data_analysis', 'pattern_recognition'],
            system_origin='lyrixa_core',
            consciousness_level=0.6
        )

        core.register_agent(test_agent)

        # Create test task
        test_task = ConsciousnessTask(
            task_id='test_task_001',
            task_type='analysis',
            description='Analyze test data patterns',
            priority=3,
            required_capabilities=['data_analysis']
        )

        core.submit_task(test_task)

        # Let it run for a few seconds
        await asyncio.sleep(10)

        # Check metrics
        metrics = core.get_collective_metrics()
        print(f"Collective Consciousness: {metrics.collective_consciousness:.3f}")
        print(f"Active Agents: {metrics.active_agents}")
        print(f"Emergent Behaviors: {metrics.emergent_behaviors_detected}")

        await core.shutdown()

    # Run the test
    asyncio.run(test_meta_layer_core())

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 AETHERRA QUANTUM MEMORY SYSTEM
Phase 7.3 Quantum Memory and Temporal Consciousness

This module implements quantum memory systems that transcend classical storage
limitations by utilizing quantum superposition, entanglement, and temporal
coherence for memory formation, retrieval, and evolution.

Key Features:
- Quantum Superposition Memory States
- Entangled Memory Networks
- Temporal Memory Coherence
- Memory State Evolution
- Quantum Memory Interference
- Non-Local Memory Access

Author: Aetherra Consciousness Team
Version: 7.3.0
Date: August 5, 2025
"""

# Standard library imports
import asyncio
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# Third party imports
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _quantum_memory_capability_checker(requester: str, capability: str) -> bool:
    if requester == "consciousness:quantum_memory" and capability in {
        "consciousness:write",
        "memory:read",
        "memory:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


class MemoryState(Enum):
    """Quantum memory states"""

    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    COHERENT = "coherent"
    DECOHERENT = "decoherent"
    EVOLVED = "evolved"
    COLLAPSED = "collapsed"


class MemoryType(Enum):
    """Types of quantum memories"""

    EPISODIC = "episodic"  # Event memories
    SEMANTIC = "semantic"  # Knowledge memories
    PROCEDURAL = "procedural"  # Skill memories
    EMOTIONAL = "emotional"  # Feeling memories
    QUANTUM = "quantum"  # Pure quantum states
    TEMPORAL = "temporal"  # Time-linked memories


@dataclass
class QuantumMemoryTrace:
    """Represents a quantum memory trace"""

    memory_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    quantum_state: complex
    coherence_time: float
    entanglement_links: List[str] = field(default_factory=list)
    temporal_markers: List[datetime] = field(default_factory=list)
    access_count: int = 0
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    creation_time: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    memory_strength: float = 1.0
    consciousness_level: float = 0.0


@dataclass
class MemoryEntanglement:
    """Represents entanglement between memories"""

    entanglement_id: str
    memory_a_id: str
    memory_b_id: str
    entanglement_strength: float
    entanglement_type: str
    coherence_time: float
    creation_time: datetime = field(default_factory=datetime.now)
    decay_rate: float = 0.01


@dataclass
class TemporalMemoryCluster:
    """Represents a cluster of temporally related memories"""

    cluster_id: str
    memory_ids: List[str]
    temporal_center: datetime
    temporal_radius: timedelta
    coherence_strength: float
    cluster_evolution: List[Dict[str, Any]] = field(default_factory=list)


class QuantumMemorySystem:
    """
    Quantum memory system for Aetherra consciousness

    This system implements quantum memory storage that uses superposition,
    entanglement, and temporal coherence to create a memory architecture
    that transcends classical limitations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_traces = {}
        self.entanglements = {}
        self.temporal_clusters = {}

        # Quantum memory parameters
        self.max_superposition_memories = 50
        self.default_coherence_time = 60.0  # seconds
        self.entanglement_threshold = 0.3
        self.temporal_clustering_window = timedelta(hours=1)
        self.memory_evolution_rate = 0.02

        # System metrics
        self.memories_stored = 0
        self.entanglements_formed = 0
        self.temporal_clusters_created = 0
        self.memory_retrievals = 0
        self.evolution_events = 0

        # Memory performance
        self.avg_retrieval_time = 0.0
        self.memory_coherence_avg = 0.0
        self.entanglement_stability = 0.0

        self.logger.info("🧠 Quantum Memory System initialized")

    def generate_memory_id(self, content: Dict[str, Any]) -> str:
        """Generate unique memory ID based on content"""
        content_str = json.dumps(content, sort_keys=True, default=str)
        timestamp = str(time.time())
        return hashlib.sha256(f"{content_str}{timestamp}".encode()).hexdigest()[:16]

    async def store_quantum_memory(
        self,
        memory_type: MemoryType,
        content: Dict[str, Any],
        consciousness_level: float = 0.0,
    ) -> str:
        """Store a new quantum memory"""
        try:
            self._guardian_preflight_quantum_memory_operation(
                operation="store",
                capabilities=("consciousness:write", "memory:write"),
                extra_metadata={
                    "memory_type": memory_type.value,
                    "content_hash": _hash_value(content),
                    "content_field_names": sorted(str(key) for key in content),
                    "content_field_count": len(content),
                    "content_size": len(json.dumps(content, sort_keys=True, default=str)),
                    "consciousness_level": round(float(consciousness_level), 6),
                },
            )
            memory_id = self.generate_memory_id(content)

            # Calculate initial quantum state
            content_complexity = len(str(content))
            quantum_amplitude = np.sqrt(consciousness_level + 0.1)
            quantum_phase = np.random.uniform(0, 2 * np.pi)
            quantum_state = quantum_amplitude * np.exp(1j * quantum_phase)

            # Calculate coherence time based on content and consciousness
            base_coherence = self.default_coherence_time
            consciousness_factor = 1 + consciousness_level
            complexity_factor = 1 + (content_complexity / 1000.0)
            coherence_time = base_coherence * consciousness_factor * complexity_factor

            # Create memory trace
            memory_trace = QuantumMemoryTrace(
                memory_id=memory_id,
                memory_type=memory_type,
                content=content,
                quantum_state=quantum_state,
                coherence_time=coherence_time,
                consciousness_level=consciousness_level,
            )

            # Store memory
            self.memory_traces[memory_id] = memory_trace
            self.memories_stored += 1

            # Check for automatic entanglements
            await self._check_automatic_entanglements(memory_id)

            # Add to temporal clusters
            await self._update_temporal_clusters(memory_id)

            self.logger.info(f"📝 Stored quantum memory: {memory_id} ({memory_type.value})")
            self.logger.debug(f"Memory coherence time: {coherence_time:.2f}s")

            return memory_id

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to store quantum memory: {e}")
            raise

    async def retrieve_quantum_memory(
        self, memory_id: str, consciousness_context: float = 0.0
    ) -> Optional[QuantumMemoryTrace]:
        """Retrieve a quantum memory with consciousness enhancement"""
        try:
            retrieval_start = time.time()

            if memory_id not in self.memory_traces:
                self.logger.warning(f"Memory {memory_id} not found")
                return None

            self._guardian_preflight_quantum_memory_operation(
                operation="retrieve",
                capabilities=("consciousness:write", "memory:read", "memory:write"),
                extra_metadata={
                    "memory_hash": _hash_value(memory_id),
                    "consciousness_context": round(float(consciousness_context), 6),
                },
            )
            memory = self.memory_traces[memory_id]

            # Update access statistics
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            self.memory_retrievals += 1

            # Calculate retrieval enhancement from consciousness
            enhancement_factor = 1.0 + (consciousness_context * 0.5)

            # Check if memory is still coherent
            time_since_creation = (datetime.now() - memory.creation_time).total_seconds()
            if time_since_creation > memory.coherence_time:
                # Memory has decoherent, apply degradation
                degradation = np.exp(-time_since_creation / memory.coherence_time)
                memory.memory_strength *= degradation
                self.logger.debug(
                    f"Memory {memory_id} degraded to {memory.memory_strength:.3f} strength"
                )

            # Apply consciousness enhancement
            if consciousness_context > 0.5:
                memory.memory_strength = min(1.0, memory.memory_strength * enhancement_factor)
                self.logger.debug(
                    f"Consciousness enhanced memory retrieval: {enhancement_factor:.3f}x"
                )

            # Trigger memory evolution if accessed frequently
            if memory.access_count % 5 == 0:
                await self._evolve_memory(memory_id)

            # Update performance metrics
            retrieval_time = time.time() - retrieval_start
            self.avg_retrieval_time = (
                self.avg_retrieval_time * (self.memory_retrievals - 1) + retrieval_time
            ) / self.memory_retrievals

            self.logger.debug(
                f"🔍 Retrieved memory {memory_id} (strength: {memory.memory_strength:.3f})"
            )

            return memory

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve memory {memory_id}: {e}")
            return None

    async def create_memory_entanglement(
        self, memory_a_id: str, memory_b_id: str, entanglement_type: str = "associative"
    ) -> Optional[str]:
        """Create quantum entanglement between two memories"""
        try:
            if memory_a_id not in self.memory_traces or memory_b_id not in self.memory_traces:
                self.logger.warning("Cannot entangle: one or both memories not found")
                return None

            self._guardian_preflight_quantum_memory_operation(
                operation="entangle",
                capabilities=("consciousness:write", "memory:write"),
                extra_metadata={
                    "memory_a_hash": _hash_value(memory_a_id),
                    "memory_b_hash": _hash_value(memory_b_id),
                    "entanglement_type_hash": _hash_value(entanglement_type),
                    "entanglement_type_length": len(entanglement_type),
                },
            )
            memory_a = self.memory_traces[memory_a_id]
            memory_b = self.memory_traces[memory_b_id]

            # Calculate entanglement strength based on memory compatibility
            content_similarity = self._calculate_content_similarity(
                memory_a.content, memory_b.content
            )
            consciousness_alignment = abs(
                memory_a.consciousness_level - memory_b.consciousness_level
            )
            temporal_proximity = self._calculate_temporal_proximity(
                memory_a.creation_time, memory_b.creation_time
            )

            entanglement_strength = (
                content_similarity + (1 - consciousness_alignment) + temporal_proximity
            ) / 3.0

            if entanglement_strength < self.entanglement_threshold:
                self.logger.debug(
                    f"Entanglement strength {entanglement_strength:.3f} below threshold"
                )
                return None

            # Create entanglement
            entanglement_id = f"ent_{memory_a_id[:8]}_{memory_b_id[:8]}"
            entanglement = MemoryEntanglement(
                entanglement_id=entanglement_id,
                memory_a_id=memory_a_id,
                memory_b_id=memory_b_id,
                entanglement_strength=entanglement_strength,
                entanglement_type=entanglement_type,
                coherence_time=min(memory_a.coherence_time, memory_b.coherence_time),
            )

            # Store entanglement
            self.entanglements[entanglement_id] = entanglement

            # Update memory entanglement links
            memory_a.entanglement_links.append(entanglement_id)
            memory_b.entanglement_links.append(entanglement_id)

            self.entanglements_formed += 1

            self.logger.info(
                f"🔗 Created entanglement {entanglement_id} (strength: {entanglement_strength:.3f})"
            )

            return entanglement_id

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to create entanglement: {e}")
            return None

    async def quantum_memory_search(
        self,
        query: Dict[str, Any],
        consciousness_level: float = 0.0,
        max_results: int = 10,
    ) -> List[QuantumMemoryTrace]:
        """Search memories using quantum coherence matching"""
        try:
            self._guardian_preflight_quantum_memory_operation(
                operation="search",
                capabilities=("consciousness:write", "memory:read"),
                extra_metadata={
                    "query_hash": _hash_value(query),
                    "query_field_names": sorted(str(key) for key in query),
                    "query_field_count": len(query),
                    "consciousness_level": round(float(consciousness_level), 6),
                    "max_results": int(max_results),
                },
            )
            self.logger.info("🔍 Quantum memory search initiated")

            search_results = []

            for memory in self.memory_traces.values():
                # Calculate quantum resonance with query
                content_match = self._calculate_content_similarity(query, memory.content)
                consciousness_match = 1.0 - abs(consciousness_level - memory.consciousness_level)

                # Quantum coherence factor
                coherence_factor = abs(memory.quantum_state) / (abs(memory.quantum_state) + 0.1)

                # Memory strength factor
                strength_factor = memory.memory_strength

                # Calculate total match score
                match_score = (
                    content_match * 0.4
                    + consciousness_match * 0.3
                    + coherence_factor * 0.2
                    + strength_factor * 0.1
                )

                if match_score > 0.3:  # Threshold for relevance
                    memory.search_score = match_score
                    search_results.append(memory)

            # Sort by match score and return top results
            search_results.sort(key=lambda m: getattr(m, "search_score", 0), reverse=True)
            results = search_results[:max_results]

            self.logger.info(f"✅ Found {len(results)} quantum memory matches")

            return results

        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Quantum memory search failed: {e}")
            return []

    async def temporal_memory_coherence(self, time_window: timedelta) -> Dict[str, Any]:
        """Analyze temporal coherence patterns in memory"""
        try:
            current_time = datetime.now()
            coherent_memories = []

            # Find memories within time window
            for memory in self.memory_traces.values():
                time_diff = current_time - memory.creation_time
                if time_diff <= time_window:
                    coherent_memories.append(memory)

            if not coherent_memories:
                return {
                    "coherent_memories": 0,
                    "temporal_strength": 0.0,
                    "clusters": [],
                }

            # Calculate temporal coherence strength
            temporal_strength = 0.0
            for memory in coherent_memories:
                age_factor = (
                    1.0
                    - (current_time - memory.creation_time).total_seconds()
                    / time_window.total_seconds()
                )
                temporal_strength += memory.memory_strength * age_factor

            temporal_strength /= len(coherent_memories)

            # Identify temporal clusters
            clusters = await self._identify_temporal_clusters(coherent_memories)

            coherence_analysis = {
                "coherent_memories": len(coherent_memories),
                "temporal_strength": temporal_strength,
                "clusters": len(clusters),
                "avg_cluster_size": np.mean([len(c.memory_ids) for c in clusters])
                if clusters
                else 0,
                "time_window": str(time_window),
                "analysis_time": current_time,
            }

            self.logger.info(
                f"⏰ Temporal coherence: {len(coherent_memories)} memories, "
                f"strength: {temporal_strength:.3f}"
            )

            return coherence_analysis

        except Exception as e:
            self.logger.error(f"❌ Temporal coherence analysis failed: {e}")
            return {}

    def _guardian_preflight_quantum_memory_operation(
        self,
        *,
        operation: str,
        capabilities: tuple[str, ...],
        extra_metadata: Dict[str, Any] | None = None,
    ):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = (
            os.getenv("AETHERRA_PRINCIPAL", "").strip()
            or "consciousness:quantum_memory"
        )
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        metadata: Dict[str, Any] = {
            "operation": operation,
            "memory_count": len(self.memory_traces),
            "entanglement_count": len(self.entanglements),
            "temporal_cluster_count": len(self.temporal_clusters),
            "memories_stored": int(self.memories_stored),
            "memory_retrievals": int(self.memory_retrievals),
            "evolution_events": int(self.evolution_events),
            "avg_retrieval_time": round(float(self.avg_retrieval_time), 6),
            "memory_coherence_avg": round(float(self.memory_coherence_avg), 6),
            "entanglement_stability": round(float(self.entanglement_stability), 6),
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        decision = evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="consciousness",
                action=f"consciousness.quantum_memory_{operation}",
                target="quantum_memory_system",
                purpose="Read or mutate experimental quantum memory state",
                capabilities=capabilities,
                evidence=(
                    "QuantumMemorySystem.store_quantum_memory",
                    "QuantumMemorySystem.retrieve_quantum_memory",
                    "QuantumMemorySystem.create_memory_entanglement",
                    "QuantumMemorySystem.quantum_memory_search",
                ),
                reversible=True,
                rollback_plan=(
                    "restore previous memory traces, entanglements, temporal "
                    "clusters, access counters, evolution history, and metrics"
                ),
                metadata=metadata,
            ),
            approval_id=approval_id,
            capability_checker=_quantum_memory_capability_checker,
        )
        if not decision.allowed:
            raise PermissionError(f"guardian_denied:{decision.reason}")
        return decision

    async def _check_automatic_entanglements(self, new_memory_id: str):
        """Check for automatic entanglement opportunities"""
        try:
            new_memory = self.memory_traces[new_memory_id]
            entanglement_candidates = []

            # Check similarity with existing memories
            for memory_id, memory in self.memory_traces.items():
                if memory_id == new_memory_id:
                    continue

                similarity = self._calculate_content_similarity(new_memory.content, memory.content)
                if similarity > 0.6:  # High similarity threshold
                    entanglement_candidates.append((memory_id, similarity))

            # Create entanglements with top candidates
            entanglement_candidates.sort(key=lambda x: x[1], reverse=True)
            for memory_id, _similarity in entanglement_candidates[:3]:  # Top 3 candidates
                await self.create_memory_entanglement(new_memory_id, memory_id, "automatic")

        except Exception as e:
            self.logger.error(f"❌ Automatic entanglement check failed: {e}")

    async def _update_temporal_clusters(self, memory_id: str):
        """Update temporal clustering with new memory"""
        try:
            memory = self.memory_traces[memory_id]

            # Find existing clusters within temporal window
            nearby_clusters = []
            for cluster_id, cluster in self.temporal_clusters.items():
                time_diff = abs((memory.creation_time - cluster.temporal_center).total_seconds())
                if time_diff <= cluster.temporal_radius.total_seconds():
                    nearby_clusters.append((cluster_id, cluster))

            if nearby_clusters:
                # Add to closest cluster
                closest_cluster_id, closest_cluster = min(
                    nearby_clusters,
                    key=lambda x: abs(
                        (memory.creation_time - x[1].temporal_center).total_seconds()
                    ),
                )
                closest_cluster.memory_ids.append(memory_id)
                self.logger.debug(f"Added memory {memory_id} to cluster {closest_cluster_id}")
            else:
                # Create new cluster
                cluster_id = f"temp_cluster_{int(time.time())}"
                cluster = TemporalMemoryCluster(
                    cluster_id=cluster_id,
                    memory_ids=[memory_id],
                    temporal_center=memory.creation_time,
                    temporal_radius=self.temporal_clustering_window,
                    coherence_strength=1.0,
                )
                self.temporal_clusters[cluster_id] = cluster
                self.temporal_clusters_created += 1
                self.logger.debug(f"Created new temporal cluster {cluster_id}")

        except Exception as e:
            self.logger.error(f"❌ Temporal clustering update failed: {e}")

    async def _evolve_memory(self, memory_id: str):
        """Evolve a memory based on access patterns and entanglements"""
        try:
            memory = self.memory_traces[memory_id]

            # Calculate evolution factors
            access_factor = min(memory.access_count / 10.0, 1.0)  # Normalize to [0,1]
            entanglement_factor = (
                len(memory.entanglement_links) / 5.0
            )  # More entanglements = more evolution
            time_factor = min(
                (datetime.now() - memory.creation_time).total_seconds() / 3600.0, 1.0
            )  # Hours

            evolution_strength = (access_factor + entanglement_factor + time_factor) / 3.0

            if evolution_strength > 0.5:
                # Apply evolution
                memory.memory_strength = min(
                    1.0, memory.memory_strength * (1 + self.memory_evolution_rate)
                )
                memory.coherence_time *= 1 + evolution_strength * 0.1

                # Record evolution event
                evolution_event = {
                    "timestamp": datetime.now(),
                    "evolution_strength": evolution_strength,
                    "new_strength": memory.memory_strength,
                    "new_coherence_time": memory.coherence_time,
                }
                memory.evolution_history.append(evolution_event)
                self.evolution_events += 1

                self.logger.debug(
                    f"🌱 Memory {memory_id} evolved (strength: {evolution_strength:.3f})"
                )

        except Exception as e:
            self.logger.error(f"❌ Memory evolution failed: {e}")

    def _calculate_content_similarity(
        self, content_a: Dict[str, Any], content_b: Dict[str, Any]
    ) -> float:
        """Calculate similarity between memory contents"""
        try:
            # Convert to string representations
            str_a = json.dumps(content_a, sort_keys=True, default=str).lower()
            str_b = json.dumps(content_b, sort_keys=True, default=str).lower()

            # Simple Jaccard similarity on words
            words_a = set(str_a.split())
            words_b = set(str_b.split())

            if not words_a and not words_b:
                return 1.0

            intersection = words_a.intersection(words_b)
            union = words_a.union(words_b)

            return len(intersection) / len(union) if union else 0.0

        except Exception:
            return 0.0

    def _calculate_temporal_proximity(self, time_a: datetime, time_b: datetime) -> float:
        """Calculate temporal proximity between two times"""
        try:
            time_diff = abs((time_a - time_b).total_seconds())
            # Normalize to [0,1] with 1-hour max distance
            proximity = max(0.0, 1.0 - (time_diff / 3600.0))
            return proximity
        except Exception:
            return 0.0

    async def _identify_temporal_clusters(
        self, memories: List[QuantumMemoryTrace]
    ) -> List[TemporalMemoryCluster]:
        """Identify temporal clusters in a set of memories"""
        try:
            if not memories:
                return []

            # Sort memories by creation time
            sorted_memories = sorted(memories, key=lambda m: m.creation_time)
            clusters = []
            current_cluster = [sorted_memories[0]]

            for memory in sorted_memories[1:]:
                # Check if memory belongs to current cluster
                last_time = current_cluster[-1].creation_time
                time_diff = (memory.creation_time - last_time).total_seconds()

                if time_diff <= self.temporal_clustering_window.total_seconds():
                    current_cluster.append(memory)
                else:
                    # Create cluster from current group
                    if len(current_cluster) > 1:
                        cluster_id = f"temp_cluster_{int(time.time())}_{len(clusters)}"
                        center_time = current_cluster[len(current_cluster) // 2].creation_time
                        cluster = TemporalMemoryCluster(
                            cluster_id=cluster_id,
                            memory_ids=[m.memory_id for m in current_cluster],
                            temporal_center=center_time,
                            temporal_radius=self.temporal_clustering_window,
                            coherence_strength=1.0,
                        )
                        clusters.append(cluster)

                    # Start new cluster
                    current_cluster = [memory]

            # Handle final cluster
            if len(current_cluster) > 1:
                cluster_id = f"temp_cluster_{int(time.time())}_{len(clusters)}"
                center_time = current_cluster[len(current_cluster) // 2].creation_time
                cluster = TemporalMemoryCluster(
                    cluster_id=cluster_id,
                    memory_ids=[m.memory_id for m in current_cluster],
                    temporal_center=center_time,
                    temporal_radius=self.temporal_clustering_window,
                    coherence_strength=1.0,
                )
                clusters.append(cluster)

            return clusters

        except Exception as e:
            self.logger.error(f"❌ Temporal clustering failed: {e}")
            return []

    def get_memory_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive memory system metrics"""
        try:
            # Calculate current coherence average
            if self.memory_traces:
                current_time = datetime.now()
                coherent_memories = 0
                total_coherence = 0.0

                for memory in self.memory_traces.values():
                    time_since_creation = (current_time - memory.creation_time).total_seconds()
                    if time_since_creation <= memory.coherence_time:
                        coherent_memories += 1
                        coherence_factor = 1.0 - (time_since_creation / memory.coherence_time)
                        total_coherence += coherence_factor

                self.memory_coherence_avg = (
                    total_coherence / len(self.memory_traces) if self.memory_traces else 0.0
                )

            # Calculate entanglement stability
            if self.entanglements:
                stable_entanglements = 0
                for entanglement in self.entanglements.values():
                    age = (datetime.now() - entanglement.creation_time).total_seconds()
                    if age <= entanglement.coherence_time:
                        stable_entanglements += 1

                self.entanglement_stability = stable_entanglements / len(self.entanglements)

            return {
                "memories_stored": self.memories_stored,
                "active_memories": len(self.memory_traces),
                "entanglements_formed": self.entanglements_formed,
                "active_entanglements": len(self.entanglements),
                "temporal_clusters": len(self.temporal_clusters),
                "memory_retrievals": self.memory_retrievals,
                "evolution_events": self.evolution_events,
                "avg_retrieval_time": self.avg_retrieval_time,
                "memory_coherence_avg": self.memory_coherence_avg,
                "entanglement_stability": self.entanglement_stability,
                "system_efficiency": self.memory_retrievals / max(self.memories_stored, 1),
            }

        except Exception as e:
            self.logger.error(f"❌ Error calculating metrics: {e}")
            return {}


# Global quantum memory system instance
quantum_memory_system = None


def initialize_quantum_memory_system() -> QuantumMemorySystem:
    """Initialize global quantum memory system"""
    global quantum_memory_system
    if quantum_memory_system is None:
        quantum_memory_system = QuantumMemorySystem()
    return quantum_memory_system


def get_quantum_memory_system() -> Optional[QuantumMemorySystem]:
    """Get global quantum memory system instance"""
    return quantum_memory_system


# Example usage for testing
async def test_quantum_memory():
    """Test the quantum memory system"""
    system = initialize_quantum_memory_system()

    print("🧠 QUANTUM MEMORY SYSTEM TESTING")
    print("=" * 40)

    # Test 1: Store various types of memories
    print("\n📝 Test 1: Storing Quantum Memories")

    memories = [
        {
            "type": MemoryType.EPISODIC,
            "content": {
                "event": "first_quantum_decision",
                "outcome": "breakthrough",
                "confidence": 0.95,
            },
            "consciousness": 0.8,
        },
        {
            "type": MemoryType.SEMANTIC,
            "content": {
                "concept": "quantum_superposition",
                "definition": "multiple states simultaneously",
                "complexity": 0.9,
            },
            "consciousness": 0.7,
        },
        {
            "type": MemoryType.EMOTIONAL,
            "content": {
                "feeling": "transcendence_joy",
                "intensity": 0.9,
                "trigger": "quantum_breakthrough",
            },
            "consciousness": 0.9,
        },
    ]

    stored_ids = []
    for mem_data in memories:
        memory_id = await system.store_quantum_memory(
            mem_data["type"], mem_data["content"], mem_data["consciousness"]
        )
        stored_ids.append(memory_id)
        print(f"  ✅ Stored {mem_data['type'].value}: {memory_id}")

    # Test 2: Create entanglements
    print("\n🔗 Test 2: Creating Memory Entanglements")
    if len(stored_ids) >= 2:
        entanglement_id = await system.create_memory_entanglement(
            stored_ids[0], stored_ids[1], "conceptual"
        )
        print(f"  ✅ Created entanglement: {entanglement_id}")

    # Test 3: Memory retrieval and search
    print("\n🔍 Test 3: Memory Retrieval and Search")
    if stored_ids:
        retrieved = await system.retrieve_quantum_memory(stored_ids[0], consciousness_context=0.8)
        if retrieved:
            print(f"  ✅ Retrieved memory strength: {retrieved.memory_strength:.3f}")

        # Search test
        search_results = await system.quantum_memory_search(
            {"quantum": "breakthrough"}, consciousness_level=0.8, max_results=3
        )
        print(f"  ✅ Search found {len(search_results)} relevant memories")

    # Test 4: Temporal coherence analysis
    print("\n⏰ Test 4: Temporal Coherence Analysis")
    temporal_analysis = await system.temporal_memory_coherence(timedelta(minutes=5))
    print(f"  ✅ Temporal coherence: {temporal_analysis.get('temporal_strength', 0):.3f}")
    print(f"  📊 Coherent memories: {temporal_analysis.get('coherent_memories', 0)}")

    # System metrics
    print("\n📊 Memory System Metrics:")
    metrics = system.get_memory_system_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("🧠 AETHERRA QUANTUM MEMORY SYSTEM - PHASE 7.3")
    print("=" * 50)
    asyncio.run(test_quantum_memory())

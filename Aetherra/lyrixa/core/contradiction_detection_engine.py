#!/usr/bin/env python3
"""
⚖️ Contradiction Detection Engine - Memory Consistency Analyzer

This engine detects contradictions and inconsistencies in memory using
FractalMesh links and confidence spread analysis. It identifies conflicting
beliefs, inconsistent patterns, and logical contradictions.

Features:
- Semantic contradiction detection using vector similarity
- Confidence-based conflict analysis
- Temporal consistency checking
- Logical inconsistency identification
- Resolution strategy generation
"""

import asyncio
import json
import logging
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Try to import memory components with fallbacks
try:
    from ..memory.fractal_mesh.base import FractalMesh
    from ..memory.fractal_mesh.concepts.concept_clusters import ConceptClusterManager
    from ..memory.vector import VectorMemory
except ImportError:
    print("⚠️ Memory components not available, using mock implementations")
    FractalMesh = None
    ConceptClusterManager = None
    VectorMemory = None


@dataclass
class MemoryContradiction:
    """Represents a detected contradiction between memory fragments"""

    contradiction_id: str
    contradiction_type: str  # "semantic", "temporal", "logical", "confidence", "value"
    severity: str  # "critical", "major", "minor", "potential"
    memory_a_id: str
    memory_b_id: str
    memory_a_content: str
    memory_b_content: str
    confidence_a: float
    confidence_b: float
    conflict_score: float  # 0.0 to 1.0, higher = more contradictory
    evidence_strength: float  # How strong the evidence is for contradiction
    context_similarity: float  # How similar the contexts are
    temporal_distance: float  # Hours between memories
    related_memories: List[str]
    resolution_strategies: List[str]
    timestamp: str
    status: str = "detected"  # "detected", "analyzing", "resolved", "dismissed"


@dataclass
class ConsistencyPattern:
    """Represents a pattern of consistency or inconsistency"""

    pattern_id: str
    pattern_type: str  # "consistent", "inconsistent", "evolving", "context_dependent"
    topic: str
    memory_ids: List[str]
    consistency_score: float  # -1.0 to 1.0, negative = inconsistent
    confidence_trend: List[float]  # Confidence over time
    temporal_span: float  # Hours covered by pattern
    context_factors: List[str]
    insights: List[str]
    timestamp: str


class ContradictionDetectionEngine:
    """
    Detects and analyzes contradictions in memory system
    """

    def __init__(self, memory_engine=None, data_dir="contradiction_data"):
        self.memory_engine = memory_engine
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize components
        self.fractal_mesh = None
        self.concept_clusters = None
        self.vector_memory = None

        if memory_engine:
            self._initialize_memory_components()

        # Storage
        self.detected_contradictions: Dict[str, MemoryContradiction] = {}
        self.consistency_patterns: Dict[str, ConsistencyPattern] = {}

        # Configuration
        self.contradiction_threshold = 0.7  # Minimum score to flag as contradiction
        self.confidence_difference_threshold = 0.3  # Significant confidence gaps
        self.temporal_relevance_hours = 168  # 1 week
        self.semantic_similarity_threshold = 0.8  # For related content detection

        # Contradiction detection rules
        self.contradiction_rules = self._initialize_contradiction_rules()

        # Load existing data
        self._load_persistence_data()

        logging.info("⚖️ Contradiction Detection Engine initialized")

    def _initialize_memory_components(self):
        """Initialize memory system components"""
        try:
            if FractalMesh:
                self.fractal_mesh = FractalMesh()
            if ConceptClusterManager:
                self.concept_clusters = ConceptClusterManager()
            if VectorMemory:
                self.vector_memory = VectorMemory()

            logging.info("✅ Contradiction detection components initialized")
        except Exception as e:
            logging.warning(f"⚠️ Could not initialize components: {e}")

    def _initialize_contradiction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rules for detecting different types of contradictions"""
        return {
            "semantic_contradiction": {
                "description": "Memories with opposite meanings in similar contexts",
                "indicators": ["not", "never", "always", "opposite", "contrary"],
                "weight": 1.0,
                "min_similarity": 0.7,
            },
            "confidence_conflict": {
                "description": "High-confidence memories that contradict each other",
                "indicators": [],
                "weight": 0.8,
                "min_confidence_sum": 1.4,
            },
            "temporal_inconsistency": {
                "description": "Memories that contradict based on temporal ordering",
                "indicators": ["before", "after", "then", "now", "previously"],
                "weight": 0.9,
                "max_temporal_gap": 24,  # hours
            },
            "logical_contradiction": {
                "description": "Memories that violate logical consistency",
                "indicators": ["if", "then", "because", "therefore", "implies"],
                "weight": 1.0,
                "min_logic_score": 0.6,
            },
            "value_conflict": {
                "description": "Memories that represent conflicting values or preferences",
                "indicators": ["prefer", "like", "dislike", "value", "important"],
                "weight": 0.7,
                "min_value_score": 0.5,
            },
        }

    async def detect_contradictions(
        self, timeframe_hours: int = 168
    ) -> List[MemoryContradiction]:
        """
        Detect contradictions in memory system

        Args:
            timeframe_hours: How far back to analyze

        Returns:
            List of detected contradictions
        """
        contradictions = []

        try:
            # Get relevant memories
            memories = await self._get_recent_memories(timeframe_hours)

            if len(memories) < 2:
                logging.info("⚖️ Not enough memories for contradiction detection")
                return contradictions

            # Detect different types of contradictions
            semantic_contradictions = await self._detect_semantic_contradictions(
                memories
            )
            contradictions.extend(semantic_contradictions)

            confidence_conflicts = await self._detect_confidence_conflicts(memories)
            contradictions.extend(confidence_conflicts)

            temporal_inconsistencies = await self._detect_temporal_inconsistencies(
                memories
            )
            contradictions.extend(temporal_inconsistencies)

            logical_contradictions = await self._detect_logical_contradictions(memories)
            contradictions.extend(logical_contradictions)

            value_conflicts = await self._detect_value_conflicts(memories)
            contradictions.extend(value_conflicts)

            # Filter and prioritize contradictions
            filtered_contradictions = self._filter_contradictions(contradictions)
            prioritized_contradictions = self._prioritize_contradictions(
                filtered_contradictions
            )

            # Store detected contradictions
            for contradiction in prioritized_contradictions:
                self.detected_contradictions[contradiction.contradiction_id] = (
                    contradiction
                )

            # Save to persistence
            self._save_persistence_data()

            logging.info(f"⚖️ Detected {len(prioritized_contradictions)} contradictions")
            return prioritized_contradictions

        except Exception as e:
            logging.error(f"❌ Error detecting contradictions: {e}")
            return []

    async def _get_recent_memories(self, timeframe_hours: int) -> List[Dict[str, Any]]:
        """Get recent memories for analysis"""
        # Mock implementation - in production, this would query the memory engine
        memories = [
            {
                "id": "mem_1",
                "content": "Async programming always improves performance",
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
                "topic": "performance",
                "context": "programming",
            },
            {
                "id": "mem_2",
                "content": "Async programming sometimes hurts performance due to overhead",
                "confidence": 0.7,
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "topic": "performance",
                "context": "programming",
            },
            {
                "id": "mem_3",
                "content": "I prefer using synchronous code for simple tasks",
                "confidence": 0.9,
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "topic": "preferences",
                "context": "programming",
            },
            {
                "id": "mem_4",
                "content": "Memory optimization is critical for performance",
                "confidence": 0.95,
                "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                "topic": "performance",
                "context": "memory_systems",
            },
            {
                "id": "mem_5",
                "content": "Memory optimization is not important for small applications",
                "confidence": 0.6,
                "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                "topic": "performance",
                "context": "small_applications",
            },
        ]

        return memories

    async def _detect_semantic_contradictions(
        self, memories: List[Dict[str, Any]]
    ) -> List[MemoryContradiction]:
        """Detect semantic contradictions between memories"""
        contradictions = []

        try:
            for i, memory_a in enumerate(memories):
                for memory_b in memories[i + 1 :]:
                    # Check if memories are about similar topics
                    if memory_a.get("topic") != memory_b.get("topic"):
                        continue

                    # Calculate semantic similarity
                    similarity = self._calculate_semantic_similarity(
                        memory_a["content"], memory_b["content"]
                    )

                    if similarity < self.semantic_similarity_threshold:
                        continue

                    # Check for contradiction indicators
                    conflict_score = self._calculate_semantic_conflict_score(
                        memory_a["content"], memory_b["content"]
                    )

                    if conflict_score >= self.contradiction_threshold:
                        contradiction = await self._create_contradiction(
                            "semantic", memory_a, memory_b, conflict_score
                        )
                        contradictions.append(contradiction)

            logging.info(f"⚖️ Found {len(contradictions)} semantic contradictions")

        except Exception as e:
            logging.error(f"❌ Error detecting semantic contradictions: {e}")

        return contradictions

    async def _detect_confidence_conflicts(
        self, memories: List[Dict[str, Any]]
    ) -> List[MemoryContradiction]:
        """Detect conflicts between high-confidence memories"""
        contradictions = []

        try:
            # Group memories by topic
            topic_groups = defaultdict(list)
            for memory in memories:
                topic_groups[memory.get("topic", "unknown")].append(memory)

            for topic, topic_memories in topic_groups.items():
                if len(topic_memories) < 2:
                    continue

                # Find high-confidence memories that might conflict
                high_conf_memories = [
                    m for m in topic_memories if m.get("confidence", 0) > 0.7
                ]

                for i, memory_a in enumerate(high_conf_memories):
                    for memory_b in high_conf_memories[i + 1 :]:
                        # Check confidence criteria
                        conf_sum = memory_a["confidence"] + memory_b["confidence"]
                        conf_diff = abs(memory_a["confidence"] - memory_b["confidence"])

                        if (
                            conf_sum
                            < self.contradiction_rules["confidence_conflict"][
                                "min_confidence_sum"
                            ]
                        ):
                            continue

                        # Calculate conflict based on content and confidence
                        content_conflict = self._calculate_semantic_conflict_score(
                            memory_a["content"], memory_b["content"]
                        )

                        # Weight by confidence levels
                        conflict_score = content_conflict * (conf_sum / 2.0)

                        if conflict_score >= self.contradiction_threshold:
                            contradiction = await self._create_contradiction(
                                "confidence", memory_a, memory_b, conflict_score
                            )
                            contradictions.append(contradiction)

            logging.info(f"⚖️ Found {len(contradictions)} confidence conflicts")

        except Exception as e:
            logging.error(f"❌ Error detecting confidence conflicts: {e}")

        return contradictions

    async def _detect_temporal_inconsistencies(
        self, memories: List[Dict[str, Any]]
    ) -> List[MemoryContradiction]:
        """Detect temporal inconsistencies in memory sequence"""
        contradictions = []

        try:
            # Sort memories by timestamp
            sorted_memories = sorted(
                memories, key=lambda m: datetime.fromisoformat(m["timestamp"])
            )

            for i, memory_a in enumerate(sorted_memories):
                for memory_b in sorted_memories[i + 1 :]:
                    # Calculate temporal distance
                    time_a = datetime.fromisoformat(memory_a["timestamp"])
                    time_b = datetime.fromisoformat(memory_b["timestamp"])
                    temporal_distance = (
                        time_b - time_a
                    ).total_seconds() / 3600  # hours

                    # Check if within relevant timeframe
                    max_gap = self.contradiction_rules["temporal_inconsistency"][
                        "max_temporal_gap"
                    ]
                    if temporal_distance > max_gap:
                        continue

                    # Check for temporal contradiction indicators
                    conflict_score = self._calculate_temporal_conflict_score(
                        memory_a, memory_b, temporal_distance
                    )

                    if conflict_score >= self.contradiction_threshold:
                        contradiction = await self._create_contradiction(
                            "temporal", memory_a, memory_b, conflict_score
                        )
                        contradictions.append(contradiction)

            logging.info(f"⚖️ Found {len(contradictions)} temporal inconsistencies")

        except Exception as e:
            logging.error(f"❌ Error detecting temporal inconsistencies: {e}")

        return contradictions

    async def _detect_logical_contradictions(
        self, memories: List[Dict[str, Any]]
    ) -> List[MemoryContradiction]:
        """Detect logical contradictions between memories"""
        contradictions = []

        try:
            # Look for logical statements
            logical_memories = [
                m
                for m in memories
                if any(
                    indicator in m["content"].lower()
                    for indicator in self.contradiction_rules["logical_contradiction"][
                        "indicators"
                    ]
                )
            ]

            for i, memory_a in enumerate(logical_memories):
                for memory_b in logical_memories[i + 1 :]:
                    # Check if memories are logically related
                    logic_score = self._calculate_logical_relationship_score(
                        memory_a["content"], memory_b["content"]
                    )

                    if (
                        logic_score
                        < self.contradiction_rules["logical_contradiction"][
                            "min_logic_score"
                        ]
                    ):
                        continue

                    # Check for logical contradiction
                    conflict_score = self._calculate_logical_conflict_score(
                        memory_a["content"], memory_b["content"]
                    )

                    if conflict_score >= self.contradiction_threshold:
                        contradiction = await self._create_contradiction(
                            "logical", memory_a, memory_b, conflict_score
                        )
                        contradictions.append(contradiction)

            logging.info(f"⚖️ Found {len(contradictions)} logical contradictions")

        except Exception as e:
            logging.error(f"❌ Error detecting logical contradictions: {e}")

        return contradictions

    async def _detect_value_conflicts(
        self, memories: List[Dict[str, Any]]
    ) -> List[MemoryContradiction]:
        """Detect conflicts in values and preferences"""
        contradictions = []

        try:
            # Look for value-related statements
            value_memories = [
                m
                for m in memories
                if any(
                    indicator in m["content"].lower()
                    for indicator in self.contradiction_rules["value_conflict"][
                        "indicators"
                    ]
                )
            ]

            for i, memory_a in enumerate(value_memories):
                for memory_b in value_memories[i + 1 :]:
                    # Check for value conflict
                    conflict_score = self._calculate_value_conflict_score(
                        memory_a["content"], memory_b["content"]
                    )

                    if conflict_score >= self.contradiction_threshold:
                        contradiction = await self._create_contradiction(
                            "value", memory_a, memory_b, conflict_score
                        )
                        contradictions.append(contradiction)

            logging.info(f"⚖️ Found {len(contradictions)} value conflicts")

        except Exception as e:
            logging.error(f"❌ Error detecting value conflicts: {e}")

        return contradictions

    def _calculate_semantic_similarity(self, content_a: str, content_b: str) -> float:
        """Calculate semantic similarity between two content strings"""
        # Simple word overlap similarity (in production, use embeddings)
        words_a = set(content_a.lower().split())
        words_b = set(content_b.lower().split())

        intersection = words_a & words_b
        union = words_a | words_b

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _calculate_semantic_conflict_score(
        self, content_a: str, content_b: str
    ) -> float:
        """Calculate how much two content strings contradict each other"""
        content_a_lower = content_a.lower()
        content_b_lower = content_b.lower()

        # Look for direct contradictions
        contradiction_pairs = [
            ("always", "never"),
            ("yes", "no"),
            ("true", "false"),
            ("good", "bad"),
            ("fast", "slow"),
            ("improves", "hurts"),
            ("increases", "decreases"),
            ("critical", "not important"),
            ("prefer", "dislike"),
        ]

        conflict_score = 0.0
        total_pairs = len(contradiction_pairs)

        for pos_word, neg_word in contradiction_pairs:
            if (pos_word in content_a_lower and neg_word in content_b_lower) or (
                neg_word in content_a_lower and pos_word in content_b_lower
            ):
                conflict_score += 1.0

        # Normalize by number of pairs checked
        if total_pairs > 0:
            conflict_score /= total_pairs

        # Boost score if both contents have high similarity but opposing words
        similarity = self._calculate_semantic_similarity(content_a, content_b)
        if similarity > 0.5:
            conflict_score *= 1.0 + similarity

        return min(conflict_score, 1.0)

    def _calculate_temporal_conflict_score(
        self,
        memory_a: Dict[str, Any],
        memory_b: Dict[str, Any],
        temporal_distance: float,
    ) -> float:
        """Calculate temporal conflict score"""
        # Check for temporal contradictions
        content_a = memory_a["content"].lower()
        content_b = memory_b["content"].lower()

        temporal_indicators = [
            ("before", "after"),
            ("first", "last"),
            ("early", "late"),
            ("previous", "next"),
            ("old", "new"),
        ]

        conflict_score = 0.0

        for early_word, late_word in temporal_indicators:
            if (early_word in content_a and late_word in content_b) or (
                late_word in content_a and early_word in content_b
            ):
                # Check if temporal order makes sense
                time_a = datetime.fromisoformat(memory_a["timestamp"])
                time_b = datetime.fromisoformat(memory_b["timestamp"])

                # If memory A is earlier but claims to be "after" something in memory B
                if time_a < time_b and late_word in content_a:
                    conflict_score += 0.5
                elif time_a > time_b and early_word in content_a:
                    conflict_score += 0.5

        # Weight by temporal proximity (closer in time = more suspicious)
        max_gap = self.contradiction_rules["temporal_inconsistency"]["max_temporal_gap"]
        proximity_weight = 1.0 - (temporal_distance / max_gap)

        return conflict_score * proximity_weight

    def _calculate_logical_relationship_score(
        self, content_a: str, content_b: str
    ) -> float:
        """Calculate how logically related two statements are"""
        content_a_lower = content_a.lower()
        content_b_lower = content_b.lower()

        logical_connectors = [
            "if",
            "then",
            "because",
            "therefore",
            "implies",
            "leads to",
            "causes",
        ]

        # Check if either statement contains logical connectors
        has_logic_a = any(
            connector in content_a_lower for connector in logical_connectors
        )
        has_logic_b = any(
            connector in content_b_lower for connector in logical_connectors
        )

        if not (has_logic_a or has_logic_b):
            return 0.0

        # Check for shared concepts
        shared_concepts = self._calculate_semantic_similarity(content_a, content_b)

        return shared_concepts

    def _calculate_logical_conflict_score(
        self, content_a: str, content_b: str
    ) -> float:
        """Calculate logical conflict between statements"""
        # Simple logical conflict detection
        content_a_lower = content_a.lower()
        content_b_lower = content_b.lower()

        # Look for if-then relationships that contradict
        conflict_score = 0.0

        # If A implies X and B implies not-X
        if "if" in content_a_lower and "if" in content_b_lower:
            # Extract what comes after "then" or similar
            conflict_score = self._calculate_semantic_conflict_score(
                content_a, content_b
            )

        return conflict_score

    def _calculate_value_conflict_score(self, content_a: str, content_b: str) -> float:
        """Calculate value conflict between statements"""
        content_a_lower = content_a.lower()
        content_b_lower = content_b.lower()

        # Look for preference conflicts
        value_conflicts = [
            ("prefer", "dislike"),
            ("like", "hate"),
            ("important", "unimportant"),
            ("valuable", "worthless"),
            ("good", "bad"),
            ("useful", "useless"),
        ]

        conflict_score = 0.0

        for pos_value, neg_value in value_conflicts:
            if (pos_value in content_a_lower and neg_value in content_b_lower) or (
                neg_value in content_a_lower and pos_value in content_b_lower
            ):
                # Check if talking about the same thing
                similarity = self._calculate_semantic_similarity(content_a, content_b)
                if similarity > 0.3:
                    conflict_score += similarity

        return min(conflict_score, 1.0)

    async def _create_contradiction(
        self,
        contradiction_type: str,
        memory_a: Dict[str, Any],
        memory_b: Dict[str, Any],
        conflict_score: float,
    ) -> MemoryContradiction:
        """Create a contradiction object"""
        # Calculate additional metrics
        time_a = datetime.fromisoformat(memory_a["timestamp"])
        time_b = datetime.fromisoformat(memory_b["timestamp"])
        temporal_distance = abs((time_b - time_a).total_seconds() / 3600)

        context_similarity = (
            0.8 if memory_a.get("context") == memory_b.get("context") else 0.3
        )

        # Determine severity
        severity = (
            "critical"
            if conflict_score > 0.9
            else "major"
            if conflict_score > 0.7
            else "minor"
            if conflict_score > 0.5
            else "potential"
        )

        # Generate resolution strategies
        resolution_strategies = self._generate_resolution_strategies(
            contradiction_type, memory_a, memory_b, conflict_score
        )

        contradiction = MemoryContradiction(
            contradiction_id=f"{contradiction_type}_{memory_a['id']}_{memory_b['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            contradiction_type=contradiction_type,
            severity=severity,
            memory_a_id=memory_a["id"],
            memory_b_id=memory_b["id"],
            memory_a_content=memory_a["content"],
            memory_b_content=memory_b["content"],
            confidence_a=memory_a.get("confidence", 0.0),
            confidence_b=memory_b.get("confidence", 0.0),
            conflict_score=conflict_score,
            evidence_strength=self._calculate_evidence_strength(memory_a, memory_b),
            context_similarity=context_similarity,
            temporal_distance=temporal_distance,
            related_memories=await self._find_related_memories(memory_a, memory_b),
            resolution_strategies=resolution_strategies,
            timestamp=datetime.now().isoformat(),
        )

        return contradiction

    def _calculate_evidence_strength(
        self, memory_a: Dict[str, Any], memory_b: Dict[str, Any]
    ) -> float:
        """Calculate strength of evidence for contradiction"""
        # Combine confidence levels and other factors
        conf_strength = (
            memory_a.get("confidence", 0) + memory_b.get("confidence", 0)
        ) / 2

        # Factor in recency (more recent = stronger evidence)
        time_a = datetime.fromisoformat(memory_a["timestamp"])
        time_b = datetime.fromisoformat(memory_b["timestamp"])
        avg_age_hours = (
            (
                (datetime.now() - time_a).total_seconds()
                + (datetime.now() - time_b).total_seconds()
            )
            / 2
            / 3600
        )

        recency_factor = max(0.1, 1.0 - (avg_age_hours / (7 * 24)))  # Decay over a week

        return conf_strength * recency_factor

    async def _find_related_memories(
        self, memory_a: Dict[str, Any], memory_b: Dict[str, Any]
    ) -> List[str]:
        """Find memories related to the contradiction"""
        # Mock implementation - in production, use vector similarity search
        return []

    def _generate_resolution_strategies(
        self,
        contradiction_type: str,
        memory_a: Dict[str, Any],
        memory_b: Dict[str, Any],
        conflict_score: float,
    ) -> List[str]:
        """Generate strategies for resolving the contradiction"""
        strategies = []

        base_strategies = [
            "Gather additional evidence to determine which memory is more accurate",
            "Examine the contexts in which each memory was formed",
            "Look for conditional factors that might explain the difference",
            "Consider temporal changes that might explain the evolution",
        ]

        if contradiction_type == "semantic":
            strategies.extend(
                [
                    "Clarify the precise meaning of key terms in each memory",
                    "Look for unstated assumptions that might resolve the conflict",
                    "Consider whether both statements could be true in different contexts",
                ]
            )
        elif contradiction_type == "confidence":
            strategies.extend(
                [
                    "Re-evaluate the confidence levels based on available evidence",
                    "Identify the source of confidence for each memory",
                    "Look for additional data points to break the tie",
                ]
            )
        elif contradiction_type == "temporal":
            strategies.extend(
                [
                    "Verify the temporal sequence of events",
                    "Check for memory errors in timestamp or sequence",
                    "Look for intermediate events that might explain the progression",
                ]
            )
        elif contradiction_type == "logical":
            strategies.extend(
                [
                    "Examine the logical structure of each statement",
                    "Look for hidden premises that might resolve the contradiction",
                    "Consider whether the logical rules being applied are appropriate",
                ]
            )
        elif contradiction_type == "value":
            strategies.extend(
                [
                    "Explore whether values have changed over time",
                    "Consider context-dependent value preferences",
                    "Look for higher-level values that might reconcile the conflict",
                ]
            )

        # Add conflict-specific strategies based on severity
        if conflict_score > 0.8:
            strategies.append(
                "This is a high-confidence contradiction that requires immediate attention"
            )

        return strategies[:5]  # Limit to top 5 strategies

    def _filter_contradictions(
        self, contradictions: List[MemoryContradiction]
    ) -> List[MemoryContradiction]:
        """Filter out weak or false positive contradictions"""
        filtered = []

        for contradiction in contradictions:
            # Filter by conflict score
            if contradiction.conflict_score < self.contradiction_threshold:
                continue

            # Filter by evidence strength
            if contradiction.evidence_strength < 0.3:
                continue

            # Filter duplicates (same memory pair)
            is_duplicate = False
            for existing in filtered:
                if (
                    existing.memory_a_id == contradiction.memory_a_id
                    and existing.memory_b_id == contradiction.memory_b_id
                ) or (
                    existing.memory_a_id == contradiction.memory_b_id
                    and existing.memory_b_id == contradiction.memory_a_id
                ):
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(contradiction)

        return filtered

    def _prioritize_contradictions(
        self, contradictions: List[MemoryContradiction]
    ) -> List[MemoryContradiction]:
        """Prioritize contradictions by importance and urgency"""

        def priority_score(contradiction: MemoryContradiction) -> float:
            severity_weights = {
                "critical": 1.0,
                "major": 0.8,
                "minor": 0.6,
                "potential": 0.4,
            }

            base_score = (
                contradiction.conflict_score
                * contradiction.evidence_strength
                * severity_weights.get(contradiction.severity, 0.5)
            )

            # Boost for high-confidence memories
            confidence_boost = (
                (contradiction.confidence_a + contradiction.confidence_b) / 2 * 0.2
            )

            # Boost for recent contradictions
            recency_boost = (
                max(0, 1.0 - (contradiction.temporal_distance / (24 * 7))) * 0.1
            )

            return base_score + confidence_boost + recency_boost

        return sorted(contradictions, key=priority_score, reverse=True)

    async def analyze_consistency_patterns(
        self, timeframe_hours: int = 168
    ) -> List[ConsistencyPattern]:
        """Analyze patterns of consistency and inconsistency"""
        patterns = []

        try:
            # Get memories and group by topic
            memories = await self._get_recent_memories(timeframe_hours)
            topic_groups = defaultdict(list)

            for memory in memories:
                topic_groups[memory.get("topic", "unknown")].append(memory)

            # Analyze each topic group
            for topic, topic_memories in topic_groups.items():
                if len(topic_memories) < 2:
                    continue

                pattern = await self._analyze_topic_consistency(topic, topic_memories)
                if pattern:
                    patterns.append(pattern)
                    self.consistency_patterns[pattern.pattern_id] = pattern

            # Save to persistence
            self._save_persistence_data()

            logging.info(f"⚖️ Analyzed {len(patterns)} consistency patterns")

        except Exception as e:
            logging.error(f"❌ Error analyzing consistency patterns: {e}")

        return patterns

    async def _analyze_topic_consistency(
        self, topic: str, memories: List[Dict[str, Any]]
    ) -> Optional[ConsistencyPattern]:
        """Analyze consistency within a topic"""
        try:
            # Sort by timestamp
            sorted_memories = sorted(
                memories, key=lambda m: datetime.fromisoformat(m["timestamp"])
            )

            # Calculate pairwise consistency scores
            consistency_scores = []
            for i, memory_a in enumerate(sorted_memories):
                for memory_b in sorted_memories[i + 1 :]:
                    conflict_score = self._calculate_semantic_conflict_score(
                        memory_a["content"], memory_b["content"]
                    )
                    consistency_score = 1.0 - conflict_score
                    consistency_scores.append(consistency_score)

            if not consistency_scores:
                return None

            # Calculate overall consistency
            avg_consistency = sum(consistency_scores) / len(consistency_scores)

            # Determine pattern type
            if avg_consistency > 0.7:
                pattern_type = "consistent"
            elif avg_consistency < 0.3:
                pattern_type = "inconsistent"
            elif len(set(m.get("context") for m in memories)) > 1:
                pattern_type = "context_dependent"
            else:
                pattern_type = "evolving"

            # Extract insights
            insights = self._extract_consistency_insights(
                pattern_type, memories, avg_consistency
            )

            # Calculate temporal span
            first_time = datetime.fromisoformat(sorted_memories[0]["timestamp"])
            last_time = datetime.fromisoformat(sorted_memories[-1]["timestamp"])
            temporal_span = (last_time - first_time).total_seconds() / 3600

            pattern = ConsistencyPattern(
                pattern_id=f"consistency_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                pattern_type=pattern_type,
                topic=topic,
                memory_ids=[m["id"] for m in memories],
                consistency_score=avg_consistency,
                confidence_trend=[m.get("confidence", 0) for m in sorted_memories],
                temporal_span=temporal_span,
                context_factors=list(
                    set(m.get("context", "unknown") for m in memories)
                ),
                insights=insights,
                timestamp=datetime.now().isoformat(),
            )

            return pattern

        except Exception as e:
            logging.error(f"❌ Error analyzing topic consistency: {e}")
            return None

    def _extract_consistency_insights(
        self,
        pattern_type: str,
        memories: List[Dict[str, Any]],
        consistency_score: float,
    ) -> List[str]:
        """Extract insights from consistency analysis"""
        insights = []

        if pattern_type == "consistent":
            insights.append(
                f"High consistency (score: {consistency_score:.2f}) indicates stable understanding"
            )
            if all(m.get("confidence", 0) > 0.8 for m in memories):
                insights.append(
                    "High confidence across all memories supports reliability"
                )

        elif pattern_type == "inconsistent":
            insights.append(
                f"Low consistency (score: {consistency_score:.2f}) suggests contradictory beliefs"
            )
            insights.append("This topic may require resolution or clarification")

            # Check if inconsistency correlates with confidence
            confidences = [m.get("confidence", 0) for m in memories]
            if max(confidences) - min(confidences) > 0.4:
                insights.append(
                    "Confidence varies significantly - some memories may be unreliable"
                )

        elif pattern_type == "context_dependent":
            contexts = set(m.get("context") for m in memories)
            insights.append(f"Consistency varies by context: {', '.join(contexts)}")
            insights.append(
                "Understanding may be context-dependent rather than contradictory"
            )

        elif pattern_type == "evolving":
            insights.append("Understanding appears to be evolving over time")

            # Check if confidence is increasing over time
            confidences = [m.get("confidence", 0) for m in memories]
            if len(confidences) > 1:
                if confidences[-1] > confidences[0]:
                    insights.append("Confidence is increasing - learning in progress")
                else:
                    insights.append("Confidence is decreasing - may need review")

        return insights

    def get_contradiction_summary(self) -> Dict[str, Any]:
        """Get summary of contradiction detection results"""
        total_contradictions = len(self.detected_contradictions)

        # Count by type
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)

        for contradiction in self.detected_contradictions.values():
            type_counts[contradiction.contradiction_type] += 1
            severity_counts[contradiction.severity] += 1

        # Calculate average scores
        if total_contradictions > 0:
            avg_conflict_score = (
                sum(c.conflict_score for c in self.detected_contradictions.values())
                / total_contradictions
            )
            avg_evidence_strength = (
                sum(c.evidence_strength for c in self.detected_contradictions.values())
                / total_contradictions
            )
        else:
            avg_conflict_score = 0.0
            avg_evidence_strength = 0.0

        # Get recent contradictions
        recent_contradictions = sorted(
            self.detected_contradictions.values(),
            key=lambda c: c.timestamp,
            reverse=True,
        )[:3]

        return {
            "timestamp": datetime.now().isoformat(),
            "total_contradictions": total_contradictions,
            "total_patterns": len(self.consistency_patterns),
            "type_breakdown": dict(type_counts),
            "severity_breakdown": dict(severity_counts),
            "average_conflict_score": avg_conflict_score,
            "average_evidence_strength": avg_evidence_strength,
            "recent_contradictions": [
                {
                    "type": c.contradiction_type,
                    "severity": c.severity,
                    "conflict_score": c.conflict_score,
                    "summary": f"{c.memory_a_content[:50]}... vs {c.memory_b_content[:50]}...",
                }
                for c in recent_contradictions
            ],
        }

    def _load_persistence_data(self):
        """Load persistent data from files"""
        try:
            # Load contradictions
            contradictions_file = self.data_dir / "contradictions.json"
            if contradictions_file.exists():
                with open(contradictions_file, "r") as f:
                    contradictions_data = json.load(f)
                    self.detected_contradictions = {
                        c_id: MemoryContradiction(**c_data)
                        for c_id, c_data in contradictions_data.items()
                    }

            # Load consistency patterns
            patterns_file = self.data_dir / "consistency_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, "r") as f:
                    patterns_data = json.load(f)
                    self.consistency_patterns = {
                        p_id: ConsistencyPattern(**p_data)
                        for p_id, p_data in patterns_data.items()
                    }

            logging.info(
                f"📂 Loaded {len(self.detected_contradictions)} contradictions and {len(self.consistency_patterns)} patterns"
            )

        except Exception as e:
            logging.warning(f"⚠️ Could not load persistence data: {e}")

    def _save_persistence_data(self):
        """Save persistent data to files"""
        try:
            # Save contradictions
            contradictions_file = self.data_dir / "contradictions.json"
            with open(contradictions_file, "w") as f:
                contradictions_data = {
                    c_id: asdict(contradiction)
                    for c_id, contradiction in self.detected_contradictions.items()
                }
                json.dump(contradictions_data, f, indent=2)

            # Save consistency patterns
            patterns_file = self.data_dir / "consistency_patterns.json"
            with open(patterns_file, "w") as f:
                patterns_data = {
                    p_id: asdict(pattern)
                    for p_id, pattern in self.consistency_patterns.items()
                }
                json.dump(patterns_data, f, indent=2)

            logging.info("💾 Saved contradiction detection data to persistence")

        except Exception as e:
            logging.error(f"❌ Could not save persistence data: {e}")


# Convenience functions for integration
async def detect_memory_contradictions(
    memory_engine=None, timeframe_hours: int = 168
) -> List[MemoryContradiction]:
    """Convenience function to detect contradictions"""
    engine = ContradictionDetectionEngine(memory_engine)
    return await engine.detect_contradictions(timeframe_hours)


async def analyze_memory_consistency(
    memory_engine=None, timeframe_hours: int = 168
) -> List[ConsistencyPattern]:
    """Convenience function to analyze consistency patterns"""
    engine = ContradictionDetectionEngine(memory_engine)
    return await engine.analyze_consistency_patterns(timeframe_hours)


if __name__ == "__main__":

    async def demo():
        """Demo the Contradiction Detection Engine"""
        print("⚖️ Contradiction Detection Engine Demo")
        print("=" * 50)

        # Initialize engine
        engine = ContradictionDetectionEngine()

        # Detect contradictions
        print("\n🔍 Detecting contradictions...")
        contradictions = await engine.detect_contradictions(timeframe_hours=168)

        print(f"\n📊 Contradiction Detection Results:")
        print(f"   Total contradictions found: {len(contradictions)}")

        for i, contradiction in enumerate(contradictions[:3], 1):
            print(
                f"\n   {i}. [{contradiction.contradiction_type}] {contradiction.severity.upper()}"
            )
            print(f"      Conflict Score: {contradiction.conflict_score:.2f}")
            print(f"      Memory A: {contradiction.memory_a_content[:60]}...")
            print(f"      Memory B: {contradiction.memory_b_content[:60]}...")
            print(f"      Evidence Strength: {contradiction.evidence_strength:.2f}")
            print(
                f"      Top Resolution Strategy: {contradiction.resolution_strategies[0] if contradiction.resolution_strategies else 'None'}"
            )

        # Analyze consistency patterns
        print(f"\n🔍 Analyzing consistency patterns...")
        patterns = await engine.analyze_consistency_patterns(timeframe_hours=168)

        print(f"\n📈 Consistency Analysis Results:")
        print(f"   Total patterns analyzed: {len(patterns)}")

        for i, pattern in enumerate(patterns[:3], 1):
            print(f"\n   {i}. [{pattern.pattern_type}] {pattern.topic}")
            print(f"      Consistency Score: {pattern.consistency_score:.2f}")
            print(f"      Temporal Span: {pattern.temporal_span:.1f} hours")
            print(
                f"      Key Insight: {pattern.insights[0] if pattern.insights else 'None'}"
            )

        # Show summary
        summary = engine.get_contradiction_summary()
        print(f"\n📊 Detection Summary:")
        print(f"   Total contradictions: {summary['total_contradictions']}")
        print(f"   Average conflict score: {summary['average_conflict_score']:.2f}")
        print(f"   Types detected: {list(summary['type_breakdown'].keys())}")
        print(f"   Severity distribution: {summary['severity_breakdown']}")

        print("\n🎉 Demo completed!")

    # Run demo
    asyncio.run(demo())

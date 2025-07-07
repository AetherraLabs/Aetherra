"""
Aetherra Emotional Memory System
Revolutionary AI memory that learns from emotional patterns and user satisfaction.
"""

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class EmotionalValence(Enum):
    """Emotional impact classification"""

    HIGHLY_POSITIVE = 1.0
    POSITIVE = 0.5
    NEUTRAL = 0.0
    NEGATIVE = -0.5
    HIGHLY_NEGATIVE = -1.0


class MemoryType(Enum):
    """Types of emotional memories"""

    SUCCESS_PATTERN = "success_pattern"
    ERROR_PATTERN = "error_pattern"
    BREAKTHROUGH = "breakthrough"
    FRUSTRATION = "frustration"
    SATISFACTION = "satisfaction"
    LEARNING_MOMENT = "learning_moment"
    COLLABORATION = "collaboration"


@dataclass
class EmotionalMemory:
    """A single emotional memory with context and impact"""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    memory_type: MemoryType = MemoryType.COLLABORATION
    valence: EmotionalValence = EmotionalValence.NEUTRAL

    # Context information
    context: str = ""  # What was happening
    user_action: str = ""  # What the user did
    ai_response: str = ""  # How AI responded
    outcome: str = ""  # What happened as a result

    # Emotional markers
    user_satisfaction: float = 0.5  # 0.0 to 1.0
    confidence_level: float = 0.5  # How confident the AI was
    emotional_intensity: float = 0.5  # How strong the emotion was

    # Learning metadata
    patterns_identified: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result["memory_type"] = self.memory_type.value
        result["valence"] = self.valence.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmotionalMemory":
        """Create from dictionary"""
        data["memory_type"] = MemoryType(data["memory_type"])
        data["valence"] = EmotionalValence(data["valence"])
        return cls(**data)


class EmotionalMemorySystem:
    """Advanced AI memory system that learns from emotional patterns"""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.memories: List[EmotionalMemory] = []
        self.emotional_patterns: Dict[str, Any] = {}
        self.load_memories()

    def record_interaction(
        self,
        context: str,
        user_action: str,
        ai_response: str,
        outcome: str,
        user_satisfaction: float = 0.5,
        confidence_level: float = 0.5,
        tags: List[str] | None = None,
    ) -> EmotionalMemory:
        """Record a new emotional memory from an interaction"""

        # Analyze emotional valence
        valence = self._analyze_valence(user_satisfaction, outcome)
        memory_type = self._classify_memory_type(context, outcome, user_satisfaction)
        emotional_intensity = abs(user_satisfaction - 0.5) * 2  # 0.0 to 1.0

        # Create memory
        memory = EmotionalMemory(
            memory_type=memory_type,
            valence=valence,
            context=context,
            user_action=user_action,
            ai_response=ai_response,
            outcome=outcome,
            user_satisfaction=user_satisfaction,
            confidence_level=confidence_level,
            emotional_intensity=emotional_intensity,
            tags=tags or [],
        )

        # Identify patterns
        memory.patterns_identified = self._identify_patterns(memory)

        # Link to related memories
        memory.related_memories = self._find_related_memories(memory)

        # Store and analyze
        self.memories.append(memory)
        self._update_emotional_patterns(memory)
        self.save_memories()

        return memory

    def get_emotional_guidance(self, current_context: str) -> Dict[str, Any]:
        """Get emotional guidance based on past experiences"""
        relevant_memories = self._find_relevant_memories(current_context)

        if not relevant_memories:
            return {
                "confidence": 0.0,
                "guidance": "No relevant emotional memories found",
            }

        # Analyze emotional patterns
        positive_patterns = [m for m in relevant_memories if m.valence.value > 0]
        negative_patterns = [m for m in relevant_memories if m.valence.value < 0]

        guidance = {
            "confidence": min(
                len(relevant_memories) / 5.0, 1.0
            ),  # Max confidence at 5+ memories
            "emotional_context": self._analyze_emotional_context(relevant_memories),
            "recommended_approach": self._recommend_approach(
                positive_patterns, negative_patterns
            ),
            "potential_pitfalls": self._identify_pitfalls(negative_patterns),
            "encouragement_level": self._calculate_encouragement_level(
                relevant_memories
            ),
            "memory_count": len(relevant_memories),
        }

        return guidance

    def learn_from_satisfaction(self, memory_id: str, actual_satisfaction: float):
        """Update learning based on actual user satisfaction"""
        for memory in self.memories:
            if memory.id == memory_id:
                # Calculate learning delta
                prediction_error = abs(memory.user_satisfaction - actual_satisfaction)

                # Update emotional patterns based on accuracy
                self._adjust_patterns_from_feedback(
                    memory, prediction_error, actual_satisfaction
                )

                # Update the memory
                memory.user_satisfaction = actual_satisfaction
                memory.tags.append(f"satisfaction_updated_{time.time():.0f}")

                self.save_memories()
                break

    def get_emotional_trends(self) -> Dict[str, Any]:
        """Analyze emotional trends over time"""
        if not self.memories:
            return {"status": "no_data"}

        recent_memories = self.memories[-50:]  # Last 50 interactions

        trends = {
            "overall_satisfaction": sum(m.user_satisfaction for m in recent_memories)
            / len(recent_memories),
            "emotional_trajectory": self._calculate_emotional_trajectory(
                recent_memories
            ),
            "most_satisfying_patterns": self._find_most_satisfying_patterns(),
            "areas_for_improvement": self._identify_improvement_areas(),
            "learning_velocity": self._calculate_learning_velocity(),
            "emotional_stability": self._calculate_emotional_stability(recent_memories),
        }

        return trends

    def _analyze_valence(self, satisfaction: float, outcome: str) -> EmotionalValence:
        """Analyze the emotional valence of an interaction"""
        # Success indicators
        success_keywords = ["success", "works", "perfect", "excellent", "breakthrough"]
        error_keywords = ["error", "failed", "problem", "stuck", "frustrated"]

        outcome_lower = outcome.lower()

        if satisfaction >= 0.8 or any(
            keyword in outcome_lower for keyword in success_keywords
        ):
            return EmotionalValence.HIGHLY_POSITIVE
        elif satisfaction >= 0.6:
            return EmotionalValence.POSITIVE
        elif satisfaction <= 0.2 or any(
            keyword in outcome_lower for keyword in error_keywords
        ):
            return EmotionalValence.HIGHLY_NEGATIVE
        elif satisfaction <= 0.4:
            return EmotionalValence.NEGATIVE
        else:
            return EmotionalValence.NEUTRAL

    def _classify_memory_type(
        self, context: str, outcome: str, satisfaction: float
    ) -> MemoryType:
        """Classify the type of memory based on context"""
        context_lower = context.lower()
        outcome_lower = outcome.lower()

        if "debug" in context_lower and satisfaction > 0.7:
            return MemoryType.SUCCESS_PATTERN
        elif "error" in outcome_lower or satisfaction < 0.3:
            return MemoryType.ERROR_PATTERN
        elif "breakthrough" in outcome_lower or satisfaction > 0.9:
            return MemoryType.BREAKTHROUGH
        elif "frustrated" in outcome_lower or satisfaction < 0.2:
            return MemoryType.FRUSTRATION
        elif satisfaction > 0.7:
            return MemoryType.SATISFACTION
        elif "learn" in context_lower:
            return MemoryType.LEARNING_MOMENT
        else:
            return MemoryType.COLLABORATION

    def _identify_patterns(self, memory: EmotionalMemory) -> List[str]:
        """Identify patterns in the current memory"""
        patterns = []

        # Context patterns
        if "debug" in memory.context.lower():
            patterns.append("debugging_context")
        if "create" in memory.context.lower():
            patterns.append("creative_context")
        if "learn" in memory.context.lower():
            patterns.append("learning_context")

        # Outcome patterns
        if memory.valence.value > 0.5:
            patterns.append("positive_outcome")
        elif memory.valence.value < -0.5:
            patterns.append("negative_outcome")

        # Interaction patterns
        if memory.confidence_level > 0.8:
            patterns.append("high_confidence")
        elif memory.confidence_level < 0.3:
            patterns.append("low_confidence")

        return patterns

    def _find_related_memories(self, memory: EmotionalMemory) -> List[str]:
        """Find memories related to the current one"""
        related = []

        for existing_memory in self.memories[-20:]:  # Check last 20 memories
            if existing_memory.id == memory.id:
                continue

            # Check for similar context
            if any(
                pattern in existing_memory.patterns_identified
                for pattern in memory.patterns_identified
            ):
                related.append(existing_memory.id)

            # Check for similar tags
            if any(tag in existing_memory.tags for tag in memory.tags):
                related.append(existing_memory.id)

        return list(set(related))  # Remove duplicates

    def _find_relevant_memories(self, context: str) -> List[EmotionalMemory]:
        """Find memories relevant to the current context"""
        context_lower = context.lower()
        relevant = []

        for memory in self.memories:
            relevance_score = 0

            # Direct context match
            if context_lower in memory.context.lower():
                relevance_score += 3

            # Pattern match
            for pattern in memory.patterns_identified:
                if pattern.replace("_", " ") in context_lower:
                    relevance_score += 2

            # Tag match
            for tag in memory.tags:
                if tag in context_lower:
                    relevance_score += 1

            if relevance_score > 0:
                relevant.append(memory)

        # Sort by relevance (recent memories get slight boost)
        relevant.sort(key=lambda m: m.timestamp, reverse=True)
        return relevant[:10]  # Return top 10

    def _update_emotional_patterns(self, memory: EmotionalMemory):
        """Update global emotional patterns based on new memory"""
        for pattern in memory.patterns_identified:
            if pattern not in self.emotional_patterns:
                self.emotional_patterns[pattern] = {
                    "count": 0,
                    "average_satisfaction": 0.5,
                    "average_confidence": 0.5,
                    "success_rate": 0.5,
                }

            # Update pattern statistics
            pattern_data = self.emotional_patterns[pattern]
            pattern_data["count"] += 1

            # Running average
            weight = 1.0 / pattern_data["count"]
            pattern_data["average_satisfaction"] = (1 - weight) * pattern_data[
                "average_satisfaction"
            ] + weight * memory.user_satisfaction
            pattern_data["average_confidence"] = (1 - weight) * pattern_data[
                "average_confidence"
            ] + weight * memory.confidence_level

            # Success rate (satisfaction > 0.6)
            success = 1.0 if memory.user_satisfaction > 0.6 else 0.0
            pattern_data["success_rate"] = (1 - weight) * pattern_data[
                "success_rate"
            ] + weight * success

    def _analyze_emotional_context(self, memories: List[EmotionalMemory]) -> str:
        """Analyze the emotional context of relevant memories"""
        if not memories:
            return "neutral"

        avg_satisfaction = sum(m.user_satisfaction for m in memories) / len(memories)
        avg_intensity = sum(m.emotional_intensity for m in memories) / len(memories)

        if avg_satisfaction > 0.7 and avg_intensity > 0.6:
            return "highly_positive"
        elif avg_satisfaction > 0.6:
            return "positive"
        elif avg_satisfaction < 0.3 and avg_intensity > 0.6:
            return "highly_negative"
        elif avg_satisfaction < 0.4:
            return "negative"
        else:
            return "neutral"

    def _recommend_approach(
        self,
        positive_patterns: List[EmotionalMemory],
        negative_patterns: List[EmotionalMemory],
    ) -> str:
        """Recommend an approach based on emotional patterns"""
        if not positive_patterns and not negative_patterns:
            return "Standard approach - no strong emotional patterns found"

        if len(positive_patterns) > len(negative_patterns) * 2:
            return "Confident approach - strong positive pattern history"
        elif len(negative_patterns) > len(positive_patterns) * 2:
            return "Cautious approach - previous challenges identified"
        else:
            return "Balanced approach - mixed emotional history"

    def _identify_pitfalls(self, negative_patterns: List[EmotionalMemory]) -> List[str]:
        """Identify potential pitfalls based on negative patterns"""
        pitfalls = []

        for memory in negative_patterns:
            if "error" in memory.outcome.lower():
                pitfalls.append(f"Error pattern: {memory.context}")
            if memory.confidence_level < 0.3:
                pitfalls.append(f"Low confidence scenario: {memory.context}")

        return list(set(pitfalls))[:3]  # Top 3 unique pitfalls

    def _calculate_encouragement_level(self, memories: List[EmotionalMemory]) -> str:
        """Calculate appropriate level of encouragement"""
        if not memories:
            return "moderate"

        recent_struggles = sum(1 for m in memories[-5:] if m.user_satisfaction < 0.4)
        recent_successes = sum(1 for m in memories[-5:] if m.user_satisfaction > 0.7)

        if recent_struggles > recent_successes + 1:
            return "high"  # User needs encouragement
        elif recent_successes > recent_struggles + 1:
            return "moderate"  # User is doing well
        else:
            return "balanced"  # Mixed recent experience

    def _calculate_emotional_trajectory(self, memories: List[EmotionalMemory]) -> str:
        """Calculate the emotional trajectory over recent interactions"""
        if len(memories) < 3:
            return "insufficient_data"

        # Compare first third to last third
        first_third = memories[: len(memories) // 3]
        last_third = memories[-len(memories) // 3 :]

        first_avg = sum(m.user_satisfaction for m in first_third) / len(first_third)
        last_avg = sum(m.user_satisfaction for m in last_third) / len(last_third)

        diff = last_avg - first_avg

        if diff > 0.2:
            return "improving"
        elif diff < -0.2:
            return "declining"
        else:
            return "stable"

    def _find_most_satisfying_patterns(self) -> List[str]:
        """Find the most satisfying interaction patterns"""
        pattern_satisfaction = {}

        for pattern, data in self.emotional_patterns.items():
            if data["count"] >= 3:  # Only consider patterns with enough data
                pattern_satisfaction[pattern] = data["average_satisfaction"]

        # Sort by satisfaction
        sorted_patterns = sorted(
            pattern_satisfaction.items(), key=lambda x: x[1], reverse=True
        )

        return [pattern for pattern, satisfaction in sorted_patterns[:5]]

    def _identify_improvement_areas(self) -> List[str]:
        """Identify areas that need improvement"""
        improvement_areas = []

        for pattern, data in self.emotional_patterns.items():
            if data["count"] >= 3 and data["average_satisfaction"] < 0.4:
                improvement_areas.append(pattern)

        return improvement_areas[:3]  # Top 3 areas

    def _calculate_learning_velocity(self) -> float:
        """Calculate how quickly the AI is learning and improving"""
        if len(self.memories) < 10:
            return 0.0

        # Compare satisfaction trends over time windows
        old_window = self.memories[: len(self.memories) // 2]
        new_window = self.memories[len(self.memories) // 2 :]

        old_avg = sum(m.user_satisfaction for m in old_window) / len(old_window)
        new_avg = sum(m.user_satisfaction for m in new_window) / len(new_window)

        return max(0.0, min(1.0, (new_avg - old_avg + 1.0) / 2.0))

    def _calculate_emotional_stability(self, memories: List[EmotionalMemory]) -> float:
        """Calculate emotional stability (consistency of satisfaction)"""
        if len(memories) < 3:
            return 0.5

        satisfactions = [m.user_satisfaction for m in memories]
        avg_satisfaction = sum(satisfactions) / len(satisfactions)

        # Calculate variance
        variance = sum((s - avg_satisfaction) ** 2 for s in satisfactions) / len(
            satisfactions
        )

        # Convert to stability score (lower variance = higher stability)
        stability = max(0.0, min(1.0, 1.0 - variance))

        return stability

    def _adjust_patterns_from_feedback(
        self,
        memory: EmotionalMemory,
        prediction_error: float,
        actual_satisfaction: float,
    ):
        """Adjust pattern weights based on prediction accuracy"""

        for pattern in memory.patterns_identified:
            if pattern in self.emotional_patterns:
                pattern_data = self.emotional_patterns[pattern]

                # If prediction was accurate, reinforce the pattern
                if prediction_error < 0.2:
                    pattern_data["confidence_boost"] = (
                        pattern_data.get("confidence_boost", 1.0) + 0.1
                    )
                else:
                    # If prediction was poor, reduce confidence
                    pattern_data["confidence_boost"] = max(
                        0.5, pattern_data.get("confidence_boost", 1.0) - 0.1
                    )

    def save_memories(self):
        """Save emotional memories to disk"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "memories": [memory.to_dict() for memory in self.memories],
            "patterns": self.emotional_patterns,
            "last_updated": time.time(),
        }

        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_memories(self):
        """Load emotional memories from disk"""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, encoding="utf-8") as f:
                data = json.load(f)

            self.memories = [
                EmotionalMemory.from_dict(memory_data)
                for memory_data in data.get("memories", [])
            ]
            self.emotional_patterns = data.get("patterns", {})

        except Exception as e:
            print(f"Warning: Could not load emotional memories: {e}")
            self.memories = []
            self.emotional_patterns = {}


def get_emotional_memory_system(installation_path: Path) -> EmotionalMemorySystem:
    """Get the global emotional memory system instance"""
    memory_path = installation_path / "emotional_memory.json"
    return EmotionalMemorySystem(memory_path)

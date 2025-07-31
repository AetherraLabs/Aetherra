"""
Memory-Based Style Learning - Phase 2 Implementation
====================================================

This module extends Lyrixa's memory system to learn and remember successful
interaction patterns, communication styles, and user preferences. It creates
a feedback loop for continuous improvement based on past experiences.

Features:
- Successful interaction pattern storage
- Style preference learning
- User-specific adaptation memories
- Context-aware style selection
- Performance-based memory weighting
"""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

# Import Phase 1 and Phase 2 components
from .emotion_detector import detect_user_emotion


class MemoryBasedStyleLearning:
    """
    System for learning and remembering successful communication patterns
    """

    def __init__(self, memory_system=None):
        self.memory_system = memory_system

        # Style memory storage
        self.successful_patterns = defaultdict(list)
        self.user_preferences = defaultdict(dict)
        self.context_style_mappings = defaultdict(lambda: defaultdict(float))
        self.style_effectiveness_scores = defaultdict(list)

        # Learning parameters
        self.success_threshold = 0.7  # Minimum score to consider "successful"
        self.pattern_confidence_threshold = 0.6
        self.memory_decay_rate = 0.02  # How fast old memories fade
        self.learning_rate = 0.1

        # Memory categories
        self.memory_categories = {
            "successful_style": "Communication styles that worked well",
            "user_preference": "Learned user-specific preferences",
            "context_adaptation": "Context-specific adaptations",
            "effective_responses": "High-scoring response patterns",
            "failed_patterns": "Patterns that didn't work well",
        }

        # Pattern tracking
        self.interaction_history = []
        self.learned_patterns = {
            "greeting_styles": {},
            "explanation_styles": {},
            "question_styles": {},
            "emotional_responses": {},
            "technical_discussions": {},
            "casual_conversations": {},
        }

    async def learn_from_interaction(
        self,
        user_input: str,
        lyrixa_response: str,
        effectiveness_score: float,
        style_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Learn from a single interaction and update style memories

        Args:
            user_input: What the user said
            lyrixa_response: Lyrixa's response
            effectiveness_score: How effective the response was (0.0-1.0)
            style_data: Style analysis data from other systems
            context: Additional context about the interaction
            user_id: Identifier for the user (if available)

        Returns:
            Learning results and updates made
        """
        if context is None:
            context = {}

        learning_result = {
            "patterns_learned": 0,
            "preferences_updated": 0,
            "memories_stored": 0,
            "adaptations_identified": 0,
        }

        # Classify interaction type
        interaction_type = self._classify_interaction_type(
            user_input, lyrixa_response, context
        )

        # Extract style patterns
        style_patterns = self._extract_style_patterns(lyrixa_response, style_data)

        # Learn from successful interactions
        if effectiveness_score >= self.success_threshold:
            await self._learn_successful_pattern(
                interaction_type, style_patterns, effectiveness_score, context
            )
            learning_result["patterns_learned"] += 1

            # Store as successful pattern memory
            if self.memory_system:
                await self._store_successful_pattern_memory(
                    user_input,
                    lyrixa_response,
                    effectiveness_score,
                    style_patterns,
                    context,
                )
                learning_result["memories_stored"] += 1

        # Learn user preferences (if user ID available)
        if user_id:
            preference_updates = await self._learn_user_preferences(
                user_id, style_patterns, effectiveness_score, context
            )
            learning_result["preferences_updated"] = len(preference_updates)

        # Update context-style mappings
        context_features = self._extract_context_features(user_input, context)
        await self._update_context_style_mappings(
            context_features, style_patterns, effectiveness_score
        )

        # Learn from failures
        if effectiveness_score < 0.5:
            await self._learn_from_failure(
                interaction_type, style_patterns, effectiveness_score, context
            )

        # Store interaction in history
        interaction_record = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "lyrixa_response": lyrixa_response,
            "effectiveness_score": effectiveness_score,
            "style_data": style_data,
            "style_patterns": style_patterns,
            "interaction_type": interaction_type,
            "context": context,
            "user_id": user_id,
        }

        self.interaction_history.append(interaction_record)

        # Keep only recent history
        if len(self.interaction_history) > 500:
            self.interaction_history = self.interaction_history[-250:]

        # Identify new adaptations
        new_adaptations = await self._identify_adaptation_opportunities(
            interaction_record
        )
        learning_result["adaptations_identified"] = len(new_adaptations)

        return learning_result

    def _classify_interaction_type(
        self, user_input: str, response: str, context: Dict[str, Any]
    ) -> str:
        """Classify the type of interaction for learning purposes"""

        user_lower = user_input.lower()

        # Greeting detection
        if any(
            word in user_lower
            for word in ["hello", "hi", "hey", "good morning", "good afternoon"]
        ):
            return "greeting"

        # Question detection
        if "?" in user_input:
            if any(
                word in user_lower for word in ["how", "what", "why", "when", "where"]
            ):
                return "question"
            else:
                return "clarification"

        # Help request detection
        if any(
            word in user_lower
            for word in ["help", "assist", "support", "guide", "teach"]
        ):
            return "help_request"

        # Technical discussion detection
        if any(
            word in user_lower
            for word in ["code", "function", "class", "algorithm", "programming"]
        ):
            return "technical_discussion"

        # Emotional expression detection
        user_emotion = detect_user_emotion(user_input)
        if user_emotion["primary_emotion"] != "neutral":
            return "emotional_expression"

        # Problem solving detection
        if any(
            word in user_lower for word in ["problem", "issue", "error", "bug", "fix"]
        ):
            return "problem_solving"

        # Casual conversation
        if any(
            word in user_lower
            for word in ["think", "feel", "opinion", "like", "prefer"]
        ):
            return "casual_conversation"

        return "general_interaction"

    def _extract_style_patterns(
        self, response: str, style_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract key style patterns from the response and analysis data"""

        patterns = {
            "length": len(response.split()),
            "question_count": response.count("?"),
            "exclamation_count": response.count("!"),
            "personal_pronouns": self._count_personal_pronouns(response),
            "technical_terms": self._count_technical_terms(response),
            "emotional_words": self._count_emotional_words(response),
            "sentence_structure": self._analyze_sentence_structure(response),
        }

        # Add style analysis data if available
        if style_data:
            if "styles_detected" in style_data:
                patterns["dominant_style"] = style_data.get("dominant_style", "neutral")
                patterns["style_scores"] = style_data.get("styles_detected", {})

            if "trait_expressions" in style_data:
                patterns["trait_expressions"] = style_data["trait_expressions"]

        return patterns

    def _count_personal_pronouns(self, text: str) -> int:
        """Count personal pronouns in text"""
        pronouns = [
            "i",
            "me",
            "my",
            "myself",
            "we",
            "us",
            "our",
            "you",
            "your",
            "yourself",
        ]
        words = text.lower().split()
        return sum(1 for word in words if word in pronouns)

    def _count_technical_terms(self, text: str) -> int:
        """Count technical terms in text"""
        tech_terms = [
            "function",
            "class",
            "method",
            "variable",
            "algorithm",
            "data",
            "code",
            "programming",
            "development",
            "software",
            "system",
            "database",
            "api",
            "framework",
            "library",
            "interface",
        ]
        words = text.lower().split()
        return sum(1 for word in words if word in tech_terms)

    def _count_emotional_words(self, text: str) -> int:
        """Count emotional words in text"""
        emotional_words = [
            "feel",
            "emotion",
            "happy",
            "sad",
            "excited",
            "frustrated",
            "amazing",
            "wonderful",
            "terrible",
            "fantastic",
            "love",
            "hate",
            "care",
            "worry",
            "hope",
            "fear",
            "joy",
            "anger",
        ]
        words = text.lower().split()
        return sum(1 for word in words if word in emotional_words)

    def _analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
        """Analyze sentence structure patterns"""
        sentences = text.split(".")

        return {
            "sentence_count": len([s for s in sentences if s.strip()]),
            "average_sentence_length": sum(
                len(s.split()) for s in sentences if s.strip()
            )
            / max(len(sentences), 1),
            "has_compound_sentences": any("," in s for s in sentences),
            "has_questions": any("?" in s for s in sentences),
            "starts_with_acknowledgment": text.lower()
            .strip()
            .startswith(("i", "that", "yes", "of course")),
        }

    def _extract_context_features(
        self, user_input: str, context: Dict[str, Any]
    ) -> List[str]:
        """Extract key features from the interaction context"""

        features = []

        # User emotion as context
        user_emotion = detect_user_emotion(user_input)
        features.append(f"emotion_{user_emotion['primary_emotion']}")

        # Time-based context
        hour = datetime.now().hour
        if 6 <= hour < 12:
            features.append("time_morning")
        elif 12 <= hour < 18:
            features.append("time_afternoon")
        elif 18 <= hour < 22:
            features.append("time_evening")
        else:
            features.append("time_night")

        # Context from provided data
        if context:
            # Conversation history length
            if "conversation_length" in context:
                length = context["conversation_length"]
                if length <= 3:
                    features.append("conversation_start")
                elif length <= 10:
                    features.append("conversation_mid")
                else:
                    features.append("conversation_long")

            # Topic context
            if "topic" in context:
                features.append(f"topic_{context['topic']}")

            # User mood if specified
            if "user_mood" in context:
                features.append(f"mood_{context['user_mood']}")

        # Input characteristics
        if len(user_input.split()) > 20:
            features.append("input_long")
        elif len(user_input.split()) < 5:
            features.append("input_short")
        else:
            features.append("input_medium")

        return features

    async def _learn_successful_pattern(
        self,
        interaction_type: str,
        style_patterns: Dict[str, Any],
        effectiveness_score: float,
        context: Dict[str, Any],
    ) -> None:
        """Learn from a successful interaction pattern"""

        # Store in successful patterns
        pattern_data = {
            "style_patterns": style_patterns,
            "effectiveness_score": effectiveness_score,
            "timestamp": datetime.now().isoformat(),
            "context": context,
        }

        self.successful_patterns[interaction_type].append(pattern_data)

        # Keep only recent successful patterns
        if len(self.successful_patterns[interaction_type]) > 50:
            self.successful_patterns[interaction_type] = self.successful_patterns[
                interaction_type
            ][-25:]

        # Update learned patterns for this interaction type
        if interaction_type in self.learned_patterns:
            await self._update_learned_patterns(
                interaction_type, style_patterns, effectiveness_score
            )

    async def _update_learned_patterns(
        self,
        interaction_type: str,
        style_patterns: Dict[str, Any],
        effectiveness_score: float,
    ) -> None:
        """Update learned patterns with new successful data"""

        if interaction_type not in self.learned_patterns:
            self.learned_patterns[interaction_type] = {}

        # Update patterns with weighted average
        weight = effectiveness_score  # Use effectiveness as weight

        for pattern_key, pattern_value in style_patterns.items():
            if isinstance(pattern_value, (int, float)):
                current_value = self.learned_patterns[interaction_type].get(
                    pattern_key, pattern_value
                )

                # Weighted average update
                new_value = (current_value * (1 - self.learning_rate)) + (
                    pattern_value * self.learning_rate * weight
                )
                self.learned_patterns[interaction_type][pattern_key] = new_value

            elif isinstance(pattern_value, dict):
                if pattern_key not in self.learned_patterns[interaction_type]:
                    self.learned_patterns[interaction_type][pattern_key] = {}

                for sub_key, sub_value in pattern_value.items():
                    if isinstance(sub_value, (int, float)):
                        current_sub_value = self.learned_patterns[interaction_type][
                            pattern_key
                        ].get(sub_key, sub_value)
                        new_sub_value = (
                            current_sub_value * (1 - self.learning_rate)
                        ) + (sub_value * self.learning_rate * weight)
                        self.learned_patterns[interaction_type][pattern_key][
                            sub_key
                        ] = new_sub_value

    async def _learn_user_preferences(
        self,
        user_id: str,
        style_patterns: Dict[str, Any],
        effectiveness_score: float,
        context: Dict[str, Any],
    ) -> List[str]:
        """Learn user-specific preferences"""

        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "preferred_styles": defaultdict(float),
                "preferred_patterns": defaultdict(float),
                "interaction_count": 0,
                "average_effectiveness": 0.0,
                "last_updated": datetime.now().isoformat(),
            }

        user_prefs = self.user_preferences[user_id]
        updates = []

        # Update interaction count and average effectiveness
        user_prefs["interaction_count"] += 1
        count = user_prefs["interaction_count"]
        current_avg = user_prefs["average_effectiveness"]
        user_prefs["average_effectiveness"] = (
            (current_avg * (count - 1)) + effectiveness_score
        ) / count

        # Update preferred styles if effective
        if effectiveness_score >= self.success_threshold:
            if "dominant_style" in style_patterns:
                style = style_patterns["dominant_style"]
                user_prefs["preferred_styles"][style] += (
                    effectiveness_score * self.learning_rate
                )
                updates.append(f"Updated preference for {style} style")

            # Update preferred patterns
            for pattern_key, pattern_value in style_patterns.items():
                if isinstance(pattern_value, (int, float)) and pattern_value > 0:
                    user_prefs["preferred_patterns"][pattern_key] += (
                        effectiveness_score * self.learning_rate
                    )
                    updates.append(f"Updated preference for {pattern_key} pattern")

        user_prefs["last_updated"] = datetime.now().isoformat()

        return updates

    async def _update_context_style_mappings(
        self,
        context_features: List[str],
        style_patterns: Dict[str, Any],
        effectiveness_score: float,
    ) -> None:
        """Update mappings between context and effective styles"""

        if effectiveness_score >= self.success_threshold:
            dominant_style = style_patterns.get("dominant_style", "neutral")

            for feature in context_features:
                current_score = self.context_style_mappings[feature][dominant_style]
                # Exponential moving average update
                self.context_style_mappings[feature][dominant_style] = (
                    current_score * (1 - self.learning_rate)
                    + effectiveness_score * self.learning_rate
                )

    async def _learn_from_failure(
        self,
        interaction_type: str,
        style_patterns: Dict[str, Any],
        effectiveness_score: float,
        context: Dict[str, Any],
    ) -> None:
        """Learn what to avoid from failed interactions"""

        # Store failed pattern for analysis
        failure_data = {
            "style_patterns": style_patterns,
            "effectiveness_score": effectiveness_score,
            "timestamp": datetime.now().isoformat(),
            "context": context,
        }

        # Store in memory system as learning experience
        if self.memory_system:
            try:
                await self.memory_system.store_memory(
                    content=f"Ineffective {interaction_type} pattern: score {effectiveness_score:.2f}",
                    memory_type="failed_pattern",
                    tags=["learning", "failure", "improvement"],
                    confidence=0.7,
                    context={"failure_analysis": failure_data},
                )
            except Exception as e:
                print(f"⚠️ Failed to store failure pattern: {e}")

    async def _store_successful_pattern_memory(
        self,
        user_input: str,
        response: str,
        effectiveness_score: float,
        style_patterns: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        """Store successful pattern in memory system"""

        if self.memory_system:
            try:
                await self.memory_system.store_memory(
                    content=f"Successful response pattern: {effectiveness_score:.2f} effectiveness",
                    memory_type="successful_style",
                    tags=["learning", "success", "style", "pattern"],
                    confidence=effectiveness_score,
                    context={
                        "user_input": user_input[:200],  # Truncate for storage
                        "response_preview": response[:200],
                        "style_patterns": style_patterns,
                        "context": context,
                    },
                )
            except Exception as e:
                print(f"⚠️ Failed to store successful pattern: {e}")

    async def _identify_adaptation_opportunities(
        self, interaction_record: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify opportunities for style adaptation based on patterns"""

        opportunities = []

        # Check if we have enough data for this interaction type
        interaction_type = interaction_record["interaction_type"]
        if interaction_type in self.successful_patterns:
            successful_count = len(self.successful_patterns[interaction_type])

            if successful_count >= 3:  # Enough data to identify patterns
                # Analyze what made successful interactions work
                successful_patterns = self.successful_patterns[interaction_type]
                avg_effectiveness = (
                    sum(p["effectiveness_score"] for p in successful_patterns)
                    / successful_count
                )

                current_effectiveness = interaction_record["effectiveness_score"]

                if current_effectiveness < avg_effectiveness - 0.1:
                    # Current interaction underperformed - identify adaptation
                    opportunities.append(
                        {
                            "type": "style_adaptation",
                            "interaction_type": interaction_type,
                            "current_effectiveness": current_effectiveness,
                            "target_effectiveness": avg_effectiveness,
                            "recommendation": f"Adapt {interaction_type} style based on successful patterns",
                        }
                    )

        return opportunities

    async def recommend_style_for_context(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Recommend communication style based on learned patterns"""

        if context is None:
            context = {}

        # Extract context features
        context_features = self._extract_context_features(user_input, context)

        # Classify interaction type for this input
        interaction_type = self._classify_interaction_type(user_input, "", context)

        recommendations = {
            "recommended_style": "neutral",
            "confidence": 0.5,
            "style_adjustments": {},
            "pattern_recommendations": {},
            "reasoning": [],
        }

        # Check learned patterns for this interaction type
        if interaction_type in self.learned_patterns:
            learned = self.learned_patterns[interaction_type]

            if "dominant_style" in learned:
                recommendations["recommended_style"] = learned["dominant_style"]
                recommendations["confidence"] += 0.2
                recommendations["reasoning"].append(
                    f"Learned style for {interaction_type}"
                )

            # Extract pattern recommendations
            for pattern_key, pattern_value in learned.items():
                if isinstance(pattern_value, (int, float)):
                    recommendations["pattern_recommendations"][pattern_key] = (
                        pattern_value
                    )

        # Check context-based style mappings
        context_style_scores = defaultdict(float)
        for feature in context_features:
            if feature in self.context_style_mappings:
                for style, score in self.context_style_mappings[feature].items():
                    context_style_scores[style] += score

        if context_style_scores:
            best_context_style = max(context_style_scores.items(), key=lambda x: x[1])
            if best_context_style[1] > 0.3:
                recommendations["recommended_style"] = best_context_style[0]
                recommendations["confidence"] += 0.15
                recommendations["reasoning"].append(
                    f"Context suggests {best_context_style[0]} style"
                )

        # Check user preferences
        if user_id and user_id in self.user_preferences:
            user_prefs = self.user_preferences[user_id]

            if user_prefs["preferred_styles"]:
                preferred_style = max(
                    user_prefs["preferred_styles"].items(), key=lambda x: x[1]
                )
                if preferred_style[1] > 0.3:
                    recommendations["recommended_style"] = preferred_style[0]
                    recommendations["confidence"] += 0.25
                    recommendations["reasoning"].append(
                        f"User prefers {preferred_style[0]} style"
                    )

            # Add pattern preferences
            for pattern, score in user_prefs["preferred_patterns"].items():
                if score > 0.3:
                    recommendations["style_adjustments"][pattern] = score

        # Normalize confidence
        recommendations["confidence"] = min(1.0, recommendations["confidence"])

        return recommendations

    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about what has been learned"""

        insights = {
            "total_patterns_learned": sum(
                len(patterns) for patterns in self.successful_patterns.values()
            ),
            "interaction_types_covered": list(self.learned_patterns.keys()),
            "users_with_preferences": len(self.user_preferences),
            "context_mappings": len(self.context_style_mappings),
            "most_successful_patterns": {},
            "learning_trends": {},
            "recommendations": [],
        }

        # Find most successful patterns
        for interaction_type, patterns in self.successful_patterns.items():
            if patterns:
                avg_score = sum(p["effectiveness_score"] for p in patterns) / len(
                    patterns
                )
                insights["most_successful_patterns"][interaction_type] = {
                    "count": len(patterns),
                    "average_effectiveness": avg_score,
                    "best_score": max(p["effectiveness_score"] for p in patterns),
                }

        # Analyze learning trends
        if self.interaction_history:
            recent_interactions = self.interaction_history[-20:]
            older_interactions = (
                self.interaction_history[-40:-20]
                if len(self.interaction_history) >= 40
                else []
            )

            if recent_interactions:
                recent_avg = sum(
                    i["effectiveness_score"] for i in recent_interactions
                ) / len(recent_interactions)
                insights["learning_trends"]["recent_average_effectiveness"] = recent_avg

                if older_interactions:
                    older_avg = sum(
                        i["effectiveness_score"] for i in older_interactions
                    ) / len(older_interactions)
                    trend = recent_avg - older_avg
                    insights["learning_trends"]["effectiveness_trend"] = (
                        "improving"
                        if trend > 0.05
                        else "declining"
                        if trend < -0.05
                        else "stable"
                    )
                    insights["learning_trends"]["trend_magnitude"] = abs(trend)

        # Generate recommendations
        if insights["total_patterns_learned"] < 10:
            insights["recommendations"].append(
                "Need more interaction data to improve learning"
            )

        if len(insights["interaction_types_covered"]) < 5:
            insights["recommendations"].append(
                "Expand interaction type coverage for better adaptation"
            )

        return insights

    def get_learning_status(self) -> Dict[str, Any]:
        """Get current status of the learning system"""

        return {
            "system_status": "active",
            "total_interactions_processed": len(self.interaction_history),
            "successful_patterns_stored": sum(
                len(patterns) for patterns in self.successful_patterns.values()
            ),
            "learned_interaction_types": list(self.learned_patterns.keys()),
            "users_tracked": len(self.user_preferences),
            "context_features_mapped": len(self.context_style_mappings),
            "memory_decay_rate": self.memory_decay_rate,
            "learning_rate": self.learning_rate,
            "last_learning_update": self.interaction_history[-1]["timestamp"]
            if self.interaction_history
            else None,
        }


# Global memory learning system instance
memory_style_learning = MemoryBasedStyleLearning()


async def learn_from_response_effectiveness(
    user_input: str,
    lyrixa_response: str,
    effectiveness_score: float,
    style_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function for learning from response effectiveness

    Args:
        user_input: User's input
        lyrixa_response: Lyrixa's response
        effectiveness_score: How effective the response was
        style_data: Style analysis data
        context: Additional context
        user_id: User identifier

    Returns:
        Learning results
    """
    return await memory_style_learning.learn_from_interaction(
        user_input, lyrixa_response, effectiveness_score, style_data, context, user_id
    )


async def get_style_recommendation(
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Get style recommendation for a given input and context"""
    return await memory_style_learning.recommend_style_for_context(
        user_input, context, user_id
    )


def get_learning_system_status() -> Dict[str, Any]:
    """Get current status of the learning system"""
    return memory_style_learning.get_learning_status()

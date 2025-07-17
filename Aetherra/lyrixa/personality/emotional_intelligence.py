"""
Emotional Intelligence Enhancement - Phase 3.2 Implementation
============================================================

This module implements advanced emotional intelligence capabilities that go beyond
basic emotion detection to provide deep emotional modeling, empathetic response
generation, and emotional memory integration.

Features:
- Advanced emotion detection with subtle cue recognition
- Complex emotional state modeling and tracking
- Empathetic response generation system
- Emotional memory and pattern recognition
- Mood tracking and long-term adaptation
- Emotional contagion and appropriate mirroring
"""

import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .emotion_detector import EmotionDetector, detect_user_emotion


class EmotionalState:
    """Represents a complex emotional state with multiple dimensions"""

    def __init__(
        self,
        primary_emotion: str,
        intensity: float,
        valence: float,  # Positive/negative scale (-1 to 1)
        arousal: float,  # Energy/activation level (0 to 1)
        dominance: float,  # Control/power feeling (0 to 1)
        confidence: float = 0.8,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.primary_emotion = primary_emotion
        self.intensity = max(0.0, min(1.0, intensity))
        self.valence = max(-1.0, min(1.0, valence))
        self.arousal = max(0.0, min(1.0, arousal))
        self.dominance = max(0.0, min(1.0, dominance))
        self.confidence = max(0.0, min(1.0, confidence))
        self.context = context or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage and transmission"""
        return {
            "primary_emotion": self.primary_emotion,
            "intensity": self.intensity,
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "confidence": self.confidence,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }

    def emotional_distance(self, other: "EmotionalState") -> float:
        """Calculate emotional distance between two states"""
        if not isinstance(other, EmotionalState):
            return 1.0

        # Weighted distance calculation
        intensity_diff = abs(self.intensity - other.intensity)
        valence_diff = abs(self.valence - other.valence)
        arousal_diff = abs(self.arousal - other.arousal)
        dominance_diff = abs(self.dominance - other.dominance)

        # Weight factors for different dimensions
        weights = {"intensity": 0.3, "valence": 0.4, "arousal": 0.2, "dominance": 0.1}

        distance = (
            weights["intensity"] * intensity_diff
            + weights["valence"] * valence_diff
            + weights["arousal"] * arousal_diff
            + weights["dominance"] * dominance_diff
        )

        return distance


class EmotionalMemory:
    """Manages emotional memory and pattern recognition"""

    def __init__(self, max_memory_size: int = 500):
        self.emotional_history: List[EmotionalState] = []
        self.max_memory_size = max_memory_size
        self.pattern_cache: Dict[str, Any] = {}
        self.last_analysis = None

    def add_emotional_state(self, state: EmotionalState):
        """Add new emotional state to memory"""
        self.emotional_history.append(state)

        # Trim memory if too large
        if len(self.emotional_history) > self.max_memory_size:
            self.emotional_history = self.emotional_history[-self.max_memory_size :]

        # Invalidate pattern cache when new data is added
        self.pattern_cache.clear()

    def get_recent_emotional_trend(
        self, time_window_minutes: int = 30
    ) -> Dict[str, Any]:
        """Analyze recent emotional trends"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_states = [
            state for state in self.emotional_history if state.timestamp >= cutoff_time
        ]

        if not recent_states:
            return {"trend": "neutral", "stability": "unknown", "states_count": 0}

        # Calculate trends
        valences = [state.valence for state in recent_states]
        intensities = [state.intensity for state in recent_states]

        avg_valence = statistics.mean(valences)
        avg_intensity = statistics.mean(intensities)
        valence_stability = (
            1.0 - statistics.stdev(valences) if len(valences) > 1 else 1.0
        )

        # Determine trend direction
        if len(recent_states) >= 3:
            recent_valence_trend = valences[-1] - valences[0]
            trend = (
                "improving"
                if recent_valence_trend > 0.1
                else "declining"
                if recent_valence_trend < -0.1
                else "stable"
            )
        else:
            trend = "stable"

        return {
            "trend": trend,
            "avg_valence": avg_valence,
            "avg_intensity": avg_intensity,
            "stability": "high"
            if valence_stability > 0.8
            else "medium"
            if valence_stability > 0.5
            else "low",
            "states_count": len(recent_states),
            "dominant_emotions": self._get_dominant_emotions(recent_states),
        }

    def _get_dominant_emotions(self, states: List[EmotionalState]) -> List[str]:
        """Get most frequent emotions in the given states"""
        emotion_counts = {}
        for state in states:
            emotion_counts[state.primary_emotion] = (
                emotion_counts.get(state.primary_emotion, 0) + 1
            )

        # Sort by frequency and return top 3
        sorted_emotions = sorted(
            emotion_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [emotion for emotion, _ in sorted_emotions[:3]]

    def detect_emotional_patterns(self) -> Dict[str, Any]:
        """Detect patterns in emotional history"""
        if not self.emotional_history:
            return {"patterns": [], "insights": []}

        patterns = []
        insights = []

        # Pattern 1: Recurring emotional cycles
        if len(self.emotional_history) >= 10:
            cycles = self._detect_emotional_cycles()
            if cycles:
                patterns.append({"type": "emotional_cycles", "data": cycles})
                insights.append("Detected recurring emotional patterns")

        # Pattern 2: Emotional triggers
        triggers = self._detect_emotional_triggers()
        if triggers:
            patterns.append({"type": "emotional_triggers", "data": triggers})
            insights.append("Identified specific emotional triggers")

        # Pattern 3: Recovery patterns
        recovery = self._analyze_emotional_recovery()
        if recovery:
            patterns.append({"type": "recovery_patterns", "data": recovery})
            insights.append("Learned emotional recovery patterns")

        return {"patterns": patterns, "insights": insights}

    def _detect_emotional_cycles(self) -> List[Dict[str, Any]]:
        """Detect recurring emotional cycles"""
        # Simplified cycle detection - could be enhanced with more sophisticated algorithms
        cycles = []

        if len(self.emotional_history) >= 20:
            # Look for patterns in valence changes
            valences = [state.valence for state in self.emotional_history[-20:]]

            # Simple pattern: consistent low-high-low patterns
            for i in range(len(valences) - 6):
                window = valences[i : i + 6]
                if self._is_cycle_pattern(window):
                    cycles.append(
                        {
                            "pattern": "low_high_low",
                            "strength": 0.7,
                            "frequency": "recent",
                        }
                    )
                    break

        return cycles

    def _is_cycle_pattern(self, values: List[float]) -> bool:
        """Check if values show a low-high-low pattern"""
        if len(values) < 3:
            return False

        # Simple pattern recognition
        low_threshold = -0.3
        high_threshold = 0.3

        pattern_found = (
            values[0] < low_threshold
            and any(v > high_threshold for v in values[1:3])
            and values[-1] < low_threshold
        )

        return pattern_found

    def _detect_emotional_triggers(self) -> List[Dict[str, Any]]:
        """Detect emotional triggers from context"""
        triggers = []

        # Group states by context keywords
        context_emotions = {}
        for state in self.emotional_history[-50:]:  # Last 50 states
            if state.context:
                for key, value in state.context.items():
                    if isinstance(value, str) and len(value) > 0:
                        context_key = f"{key}:{value.lower()}"
                        if context_key not in context_emotions:
                            context_emotions[context_key] = []
                        context_emotions[context_key].append(state.valence)

        # Find contexts that consistently produce negative emotions
        for context, valences in context_emotions.items():
            if len(valences) >= 3:
                avg_valence = statistics.mean(valences)
                if avg_valence < -0.3:
                    triggers.append(
                        {
                            "context": context,
                            "avg_impact": avg_valence,
                            "frequency": len(valences),
                            "trigger_type": "negative",
                        }
                    )

        return triggers[:5]  # Top 5 triggers

    def _analyze_emotional_recovery(self) -> Dict[str, Any]:
        """Analyze how quickly user recovers from negative emotions"""
        recovery_times = []

        for i in range(len(self.emotional_history) - 5):
            state = self.emotional_history[i]

            # Look for negative emotional states
            if state.valence < -0.3:
                # Find when valence returns to neutral/positive
                for j in range(i + 1, min(i + 10, len(self.emotional_history))):
                    later_state = self.emotional_history[j]
                    if later_state.valence > 0.1:
                        time_diff = later_state.timestamp - state.timestamp
                        recovery_times.append(time_diff.total_seconds() / 60)  # Minutes
                        break

        if recovery_times:
            avg_recovery = statistics.mean(recovery_times)
            return {
                "avg_recovery_minutes": avg_recovery,
                "recovery_count": len(recovery_times),
                "resilience_score": max(
                    0, 1.0 - (avg_recovery / 60)
                ),  # Faster recovery = higher resilience
            }

        return {}


class EmpatheticResponseGenerator:
    """Generates emotionally appropriate and empathetic responses"""

    def __init__(self):
        self.empathy_strategies = {
            "validation": [
                "I can understand how {emotion} that must feel.",
                "It sounds like you're experiencing {emotion}, and that's completely valid.",
                "I can see why that would make you feel {emotion}.",
            ],
            "support": [
                "I'm here to help you through this {emotion} feeling.",
                "You don't have to handle this {emotion} situation alone.",
                "Let's work together to address what's making you feel {emotion}.",
            ],
            "encouragement": [
                "Even though you're feeling {emotion}, I believe in your ability to handle this.",
                "This {emotion} feeling is temporary, and we can work through it together.",
                "You've overcome challenges before, and you can get through this {emotion} period too.",
            ],
            "curiosity": [
                "I'm curious to learn more about what's got you feeling {emotion}.",
                "Would you like to explore what's behind this {emotion} feeling?",
                "I'm interested in understanding your {emotion} experience better.",
            ],
        }

        self.emotional_responses = {
            "frustration": {
                "acknowledgment": "That sounds really frustrating.",
                "empathy": "I can imagine how annoying that must be.",
                "support": "Let's see if we can find a way to make this easier.",
            },
            "excitement": {
                "acknowledgment": "Your excitement is wonderful to see!",
                "empathy": "I can feel your enthusiasm through your message!",
                "support": "I'm excited to help you with this!",
            },
            "sadness": {
                "acknowledgment": "I'm sorry you're going through a difficult time.",
                "empathy": "That sounds really hard to deal with.",
                "support": "I'm here to listen and help however I can.",
            },
            "confusion": {
                "acknowledgment": "I can see this is confusing for you.",
                "empathy": "It's totally normal to feel confused about this.",
                "support": "Let me help clarify things step by step.",
            },
            "anger": {
                "acknowledgment": "I can sense your frustration and anger.",
                "empathy": "It's understandable to feel angry about this situation.",
                "support": "Let's work together to address what's causing this anger.",
            },
        }

    def generate_empathetic_response(
        self,
        user_emotional_state: EmotionalState,
        base_response: str,
        strategy: str = "auto",
    ) -> Dict[str, Any]:
        """Generate an empathetic enhancement to a base response"""

        if strategy == "auto":
            strategy = self._select_empathy_strategy(user_emotional_state)

        empathetic_elements = self._create_empathetic_elements(
            user_emotional_state, strategy
        )
        enhanced_response = self._integrate_empathy_with_response(
            base_response, empathetic_elements
        )

        return {
            "enhanced_response": enhanced_response,
            "empathy_strategy": strategy,
            "emotional_elements": empathetic_elements,
            "empathy_score": self._calculate_empathy_score(
                enhanced_response, user_emotional_state
            ),
        }

    def _select_empathy_strategy(self, emotional_state: EmotionalState) -> str:
        """Select appropriate empathy strategy based on emotional state"""

        # Strategy selection based on emotion and intensity
        if emotional_state.primary_emotion in ["sadness", "grief", "disappointment"]:
            return "validation" if emotional_state.intensity > 0.7 else "support"
        elif emotional_state.primary_emotion in ["anger", "frustration", "annoyance"]:
            return "validation" if emotional_state.intensity > 0.6 else "curiosity"
        elif emotional_state.primary_emotion in ["excitement", "joy", "happiness"]:
            return "encouragement"
        elif emotional_state.primary_emotion in ["confusion", "uncertainty"]:
            return "support"
        elif emotional_state.primary_emotion in ["anxiety", "worry", "fear"]:
            return "validation" if emotional_state.intensity > 0.5 else "support"
        else:
            return "curiosity"

    def _create_empathetic_elements(
        self, emotional_state: EmotionalState, strategy: str
    ) -> Dict[str, str]:
        """Create empathetic elements for the response"""

        emotion = emotional_state.primary_emotion
        intensity = emotional_state.intensity

        elements = {}

        # Get strategy-specific responses
        if strategy in self.empathy_strategies:
            strategy_responses = self.empathy_strategies[strategy]
            elements["strategy_phrase"] = strategy_responses[0].format(emotion=emotion)

        # Get emotion-specific responses
        if emotion in self.emotional_responses:
            emotion_responses = self.emotional_responses[emotion]
            elements.update(emotion_responses)

        # Intensity modifiers
        if intensity > 0.8:
            elements["intensity_modifier"] = "really"
        elif intensity > 0.6:
            elements["intensity_modifier"] = "quite"
        else:
            elements["intensity_modifier"] = "somewhat"

        return elements

    def _integrate_empathy_with_response(
        self, base_response: str, empathetic_elements: Dict[str, str]
    ) -> str:
        """Integrate empathetic elements with base response"""

        # Start with acknowledgment if available
        empathetic_parts = []

        if "acknowledgment" in empathetic_elements:
            empathetic_parts.append(empathetic_elements["acknowledgment"])
        elif "strategy_phrase" in empathetic_elements:
            empathetic_parts.append(empathetic_elements["strategy_phrase"])

        # Add the base response
        empathetic_parts.append(base_response)

        # Add support element if available
        if "support" in empathetic_elements:
            empathetic_parts.append(empathetic_elements["support"])

        return " ".join(empathetic_parts)

    def _calculate_empathy_score(
        self, response: str, emotional_state: EmotionalState
    ) -> float:
        """Calculate empathy score for the response"""

        empathy_indicators = [
            "understand",
            "feel",
            "sounds like",
            "can see",
            "imagine",
            "I'm here",
            "together",
            "help",
            "support",
            "sorry",
            "validate",
            "normal",
            "okay",
        ]

        response_lower = response.lower()
        empathy_count = sum(
            1 for indicator in empathy_indicators if indicator in response_lower
        )

        # Base score from empathy indicators
        base_score = min(0.8, empathy_count * 0.2)

        # Bonus for emotional context awareness
        if emotional_state.primary_emotion.lower() in response_lower:
            base_score += 0.2

        return min(1.0, base_score)


class MoodTracker:
    """Tracks long-term mood patterns and provides adaptation recommendations"""

    def __init__(self):
        self.mood_history: List[Dict[str, Any]] = []
        self.mood_categories = {
            "very_negative": (-1.0, -0.6),
            "negative": (-0.6, -0.2),
            "neutral": (-0.2, 0.2),
            "positive": (0.2, 0.6),
            "very_positive": (0.6, 1.0),
        }

    def update_mood(
        self, emotional_state: EmotionalState, session_context: Optional[Dict] = None
    ):
        """Update mood tracking with new emotional state"""

        mood_entry = {
            "timestamp": emotional_state.timestamp.isoformat(),
            "valence": emotional_state.valence,
            "arousal": emotional_state.arousal,
            "dominance": emotional_state.dominance,
            "primary_emotion": emotional_state.primary_emotion,
            "intensity": emotional_state.intensity,
            "mood_category": self._categorize_mood(emotional_state.valence),
            "session_context": session_context or {},
        }

        self.mood_history.append(mood_entry)

        # Keep only last 1000 entries
        if len(self.mood_history) > 1000:
            self.mood_history = self.mood_history[-1000:]

    def _categorize_mood(self, valence: float) -> str:
        """Categorize mood based on valence"""
        for category, (min_val, max_val) in self.mood_categories.items():
            if min_val <= valence < max_val:
                return category
        return "neutral"

    def get_mood_insights(self, time_window_days: int = 7) -> Dict[str, Any]:
        """Get mood insights for specified time window"""

        cutoff_time = datetime.now() - timedelta(days=time_window_days)
        recent_moods = [
            mood
            for mood in self.mood_history
            if datetime.fromisoformat(mood["timestamp"]) >= cutoff_time
        ]

        if not recent_moods:
            return {"status": "insufficient_data", "recommendations": []}

        # Calculate mood statistics
        valences = [mood["valence"] for mood in recent_moods]
        avg_valence = statistics.mean(valences)
        mood_volatility = statistics.stdev(valences) if len(valences) > 1 else 0

        # Mood distribution
        mood_distribution = {}
        for mood in recent_moods:
            category = mood["mood_category"]
            mood_distribution[category] = mood_distribution.get(category, 0) + 1

        # Generate insights and recommendations
        insights = self._generate_mood_insights(
            avg_valence, mood_volatility, mood_distribution
        )
        recommendations = self._generate_mood_recommendations(insights)

        return {
            "status": "analysis_complete",
            "avg_valence": avg_valence,
            "mood_volatility": mood_volatility,
            "mood_distribution": mood_distribution,
            "insights": insights,
            "recommendations": recommendations,
            "data_points": len(recent_moods),
        }

    def _generate_mood_insights(
        self, avg_valence: float, volatility: float, distribution: Dict[str, int]
    ) -> List[str]:
        """Generate insights from mood data"""

        insights = []

        # Valence insights
        if avg_valence > 0.3:
            insights.append("Overall mood has been quite positive recently")
        elif avg_valence < -0.3:
            insights.append("Mood has been more challenging lately")
        else:
            insights.append("Mood has been relatively balanced")

        # Volatility insights
        if volatility > 0.5:
            insights.append("Emotions have been quite variable")
        elif volatility < 0.2:
            insights.append("Emotional state has been relatively stable")

        # Distribution insights
        total_moods = sum(distribution.values())
        if total_moods > 0:
            positive_ratio = (
                distribution.get("positive", 0) + distribution.get("very_positive", 0)
            ) / total_moods
            if positive_ratio > 0.6:
                insights.append("Predominantly positive emotional experiences")
            elif positive_ratio < 0.3:
                insights.append("More negative emotions than positive recently")

        return insights

    def _generate_mood_recommendations(self, insights: List[str]) -> List[str]:
        """Generate recommendations based on mood insights"""

        recommendations = []

        for insight in insights:
            if "challenging" in insight or "negative" in insight:
                recommendations.extend(
                    [
                        "Consider breaking complex tasks into smaller steps",
                        "Take more frequent breaks during difficult conversations",
                        "Focus on acknowledging small wins and progress",
                    ]
                )
            elif "variable" in insight:
                recommendations.extend(
                    [
                        "Provide consistent, calming responses",
                        "Offer more emotional validation",
                        "Check in more frequently about emotional state",
                    ]
                )
            elif "positive" in insight:
                recommendations.extend(
                    [
                        "Capitalize on positive momentum",
                        "Engage with more creative and exploratory tasks",
                        "Encourage taking on new challenges",
                    ]
                )

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        return unique_recommendations[:5]  # Top 5 recommendations


class AdvancedEmotionalIntelligence:
    """Main coordinator for advanced emotional intelligence capabilities"""

    def __init__(self):
        self.emotion_detector = EmotionDetector()
        self.emotional_memory = EmotionalMemory()
        self.empathetic_responder = EmpatheticResponseGenerator()
        self.mood_tracker = MoodTracker()

        # Performance tracking
        self.performance_metrics = {
            "emotion_detections": 0,
            "empathetic_responses_generated": 0,
            "avg_empathy_score": 0.0,
            "mood_updates": 0,
            "processing_times": [],
        }

    async def process_emotional_interaction(
        self,
        user_input: str,
        base_response: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a complete emotional interaction"""

        start_time = datetime.now()

        try:
            # Step 1: Advanced emotion detection
            print("🧠 Analyzing emotional context...")
            user_emotion_data = detect_user_emotion(user_input)

            # Create detailed emotional state
            primary_emotion = user_emotion_data["primary_emotion"]

            # Calculate intensity from emotion scores
            emotion_scores = user_emotion_data.get("emotion_scores", {})
            max_score = max(emotion_scores.values()) if emotion_scores else 1.0
            intensity = min(1.0, max_score / 3.0)  # Normalize to 0-1 range

            # Calculate confidence based on data availability
            confidence = 0.8 if emotion_scores else 0.5

            emotional_state = EmotionalState(
                primary_emotion=primary_emotion,
                intensity=intensity,
                valence=self._calculate_valence(primary_emotion),
                arousal=intensity,  # Use intensity as arousal proxy
                dominance=self._calculate_dominance(primary_emotion),
                confidence=confidence,
                context=context,
            )

            # Step 2: Update emotional memory
            self.emotional_memory.add_emotional_state(emotional_state)

            # Step 3: Get emotional trends and patterns
            emotional_trend = self.emotional_memory.get_recent_emotional_trend()
            emotional_patterns = self.emotional_memory.detect_emotional_patterns()

            # Step 4: Update mood tracking
            self.mood_tracker.update_mood(emotional_state, context)
            mood_insights = self.mood_tracker.get_mood_insights()

            # Step 5: Generate empathetic response
            empathetic_result = self.empathetic_responder.generate_empathetic_response(
                emotional_state, base_response
            )

            # Step 6: Calculate performance metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_performance_metrics(
                empathetic_result["empathy_score"], processing_time
            )

            print(
                f"💫 Emotional intelligence processing complete: {processing_time:.1f}ms"
            )

            return {
                "enhanced_response": empathetic_result["enhanced_response"],
                "emotional_analysis": {
                    "user_emotional_state": emotional_state.to_dict(),
                    "emotional_trend": emotional_trend,
                    "emotional_patterns": emotional_patterns,
                    "mood_insights": mood_insights,
                },
                "empathy_metrics": {
                    "strategy_used": empathetic_result["empathy_strategy"],
                    "empathy_score": empathetic_result["empathy_score"],
                    "emotional_elements": empathetic_result["emotional_elements"],
                },
                "processing_time_ms": processing_time,
                "status": "success",
            }

        except Exception as e:
            print(f"⚠️ Emotional intelligence processing error: {e}")

            # Fallback: Basic empathetic enhancement
            simple_enhancement = self._create_simple_empathetic_response(
                user_input, base_response
            )

            return {
                "enhanced_response": simple_enhancement,
                "emotional_analysis": {"status": "fallback_mode"},
                "empathy_metrics": {"empathy_score": 0.5, "strategy_used": "fallback"},
                "processing_time_ms": (datetime.now() - start_time).total_seconds()
                * 1000,
                "status": "fallback",
                "error": str(e),
            }

    def _calculate_valence(self, emotion: str) -> float:
        """Calculate emotional valence (positive/negative) for emotion"""
        positive_emotions = {
            "joy": 0.8,
            "happiness": 0.7,
            "excitement": 0.8,
            "satisfaction": 0.6,
            "gratitude": 0.7,
            "relief": 0.5,
            "pride": 0.6,
            "curiosity": 0.3,
        }

        negative_emotions = {
            "sadness": -0.7,
            "anger": -0.6,
            "frustration": -0.5,
            "anxiety": -0.4,
            "fear": -0.6,
            "disappointment": -0.5,
            "confusion": -0.2,
            "boredom": -0.3,
        }

        return positive_emotions.get(emotion, negative_emotions.get(emotion, 0.0))

    def _calculate_dominance(self, emotion: str) -> float:
        """Calculate emotional dominance (feeling of control) for emotion"""
        high_dominance = {
            "anger": 0.8,
            "pride": 0.9,
            "excitement": 0.7,
            "satisfaction": 0.8,
            "confidence": 0.9,
            "determination": 0.8,
        }

        low_dominance = {
            "sadness": 0.2,
            "anxiety": 0.1,
            "fear": 0.1,
            "confusion": 0.3,
            "disappointment": 0.2,
            "grief": 0.1,
        }

        return high_dominance.get(emotion, low_dominance.get(emotion, 0.5))

    def _create_simple_empathetic_response(
        self, user_input: str, base_response: str
    ) -> str:
        """Create a simple empathetic response for fallback"""

        # Basic emotion keywords
        if any(
            word in user_input.lower()
            for word in ["frustrated", "annoying", "difficult"]
        ):
            return f"I understand this can be frustrating. {base_response}"
        elif any(
            word in user_input.lower() for word in ["excited", "great", "awesome"]
        ):
            return f"That's wonderful! {base_response}"
        elif any(
            word in user_input.lower()
            for word in ["confused", "unclear", "don't understand"]
        ):
            return f"I can see this is confusing. {base_response}"
        else:
            return f"I'm here to help. {base_response}"

    def _update_performance_metrics(self, empathy_score: float, processing_time: float):
        """Update performance tracking metrics"""

        self.performance_metrics["emotion_detections"] += 1
        self.performance_metrics["empathetic_responses_generated"] += 1

        # Update average empathy score
        current_avg = self.performance_metrics["avg_empathy_score"]
        total_responses = self.performance_metrics["empathetic_responses_generated"]
        new_avg = (
            (current_avg * (total_responses - 1)) + empathy_score
        ) / total_responses
        self.performance_metrics["avg_empathy_score"] = new_avg

        # Track processing times (keep last 100)
        self.performance_metrics["processing_times"].append(processing_time)
        if len(self.performance_metrics["processing_times"]) > 100:
            self.performance_metrics["processing_times"] = self.performance_metrics[
                "processing_times"
            ][-100:]

        self.performance_metrics["mood_updates"] += 1

    def get_emotional_intelligence_status(self) -> Dict[str, Any]:
        """Get status and performance metrics for emotional intelligence system"""

        processing_times = self.performance_metrics["processing_times"]

        return {
            "system_status": "operational",
            "components": {
                "emotion_detector": "active",
                "emotional_memory": "active",
                "empathetic_responder": "active",
                "mood_tracker": "active",
            },
            "performance_metrics": {
                "total_interactions": self.performance_metrics["emotion_detections"],
                "empathetic_responses": self.performance_metrics[
                    "empathetic_responses_generated"
                ],
                "avg_empathy_score": round(
                    self.performance_metrics["avg_empathy_score"], 3
                ),
                "avg_processing_time_ms": round(statistics.mean(processing_times), 1)
                if processing_times
                else 0,
                "mood_updates": self.performance_metrics["mood_updates"],
            },
            "memory_status": {
                "emotional_states_stored": len(self.emotional_memory.emotional_history),
                "mood_entries": len(self.mood_tracker.mood_history),
                "patterns_detected": len(
                    self.emotional_memory.detect_emotional_patterns()["patterns"]
                ),
            },
            "capabilities": [
                "Advanced emotion detection with subtle cue recognition",
                "Complex emotional state modeling and tracking",
                "Empathetic response generation system",
                "Emotional memory and pattern recognition",
                "Mood tracking and long-term adaptation",
                "Emotional contagion and appropriate mirroring",
            ],
        }


# Global emotional intelligence system instance
advanced_emotional_intelligence = AdvancedEmotionalIntelligence()


# Convenience functions for integration
async def enhance_response_with_emotional_intelligence(
    user_input: str,
    base_response: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Main function to enhance responses with emotional intelligence"""
    return await advanced_emotional_intelligence.process_emotional_interaction(
        user_input, base_response, context, user_id
    )


def get_emotional_intelligence_status() -> Dict[str, Any]:
    """Get emotional intelligence system status"""
    return advanced_emotional_intelligence.get_emotional_intelligence_status()


def get_emotional_memory_insights() -> Dict[str, Any]:
    """Get insights from emotional memory"""
    return advanced_emotional_intelligence.emotional_memory.detect_emotional_patterns()


def get_mood_analysis(days: int = 7) -> Dict[str, Any]:
    """Get mood analysis for specified time period"""
    return advanced_emotional_intelligence.mood_tracker.get_mood_insights(days)

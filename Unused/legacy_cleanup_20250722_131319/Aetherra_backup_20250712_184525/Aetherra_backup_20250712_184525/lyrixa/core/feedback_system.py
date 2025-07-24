#!/usr/bin/env python3
"""
🔄📈 LYRIXA FEEDBACK + SELF-IMPROVEMENT SYSTEM
==============================================

Advanced feedback collection and self-improvement system that enables Lyrixa to:
- Collect user feedback on suggestions, responses, and interactions
- Store judgments and refine personality and suggestion engine
- Automatically tune interruptiveness, language style, and behavior
- Learn from user preferences and adapt over time
- Provide continuous improvement through machine learning

This system leverages GUI intelligence, anticipation, and memory systems.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np

from ..core.conversation import PersonalityProcessor, PersonaMode
from ..core.enhanced_memory import LyrixaEnhancedMemorySystem
from ..core.memory import LyrixaMemorySystem


class FeedbackType(Enum):
    """Types of feedback that can be collected"""

    SUGGESTION_RATING = "suggestion_rating"
    RESPONSE_QUALITY = "response_quality"
    PERSONALITY_PREFERENCE = "personality_preference"
    INTERACTION_STYLE = "interaction_style"
    PROACTIVENESS = "proactiveness"
    LANGUAGE_STYLE = "language_style"
    TIMING = "timing"
    RELEVANCE = "relevance"
    HELPFULNESS = "helpfulness"


class FeedbackRating(Enum):
    """Standard feedback ratings"""

    EXCELLENT = 5
    GOOD = 4
    NEUTRAL = 3
    POOR = 2
    TERRIBLE = 1


class ImprovementArea(Enum):
    """Areas for improvement"""

    SUGGESTION_QUALITY = "suggestion_quality"
    RESPONSE_TONE = "response_tone"
    INTERACTION_TIMING = "interaction_timing"
    LANGUAGE_COMPLEXITY = "language_complexity"
    PROACTIVENESS_LEVEL = "proactiveness_level"
    PERSONALITY_FIT = "personality_fit"
    TECHNICAL_ACCURACY = "technical_accuracy"
    CONTEXT_AWARENESS = "context_awareness"


@dataclass
class FeedbackEntry:
    """Individual feedback entry"""

    feedback_id: str
    timestamp: datetime
    feedback_type: FeedbackType
    rating: Union[FeedbackRating, float, int]
    context: Dict[str, Any]
    user_comment: Optional[str]
    interaction_id: Optional[str]
    suggestion_id: Optional[str]
    response_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImprovementAction:
    """Action taken based on feedback"""

    action_id: str
    timestamp: datetime
    improvement_area: ImprovementArea
    action_type: str
    parameters_changed: Dict[str, Any]
    expected_outcome: str
    confidence: float


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""

    suggestion_acceptance_rate: float
    response_satisfaction: float
    personality_fit_score: float
    interaction_quality: float
    improvement_velocity: float
    user_engagement: float
    total_feedback_count: int
    last_updated: datetime


class LyrixaFeedbackSystem:
    """
    🔄📈 Lyrixa Feedback and Self-Improvement System

    Collects user feedback and automatically improves Lyrixa's:
    - Suggestion quality and relevance
    - Personality and interaction style
    - Response timing and proactiveness
    - Language complexity and tone
    - Technical accuracy and context awareness
    """

    def __init__(
        self,
        memory_system: Union[LyrixaMemorySystem, LyrixaEnhancedMemorySystem],
        personality_processor: PersonalityProcessor,
        suggestion_generator: Optional[Any] = None,
        proactive_assistant: Optional[Any] = None,
    ):
        self.memory = memory_system
        self.personality_processor = personality_processor
        self.suggestion_generator = suggestion_generator
        self.proactive_assistant = proactive_assistant

        # Feedback storage
        self.feedback_entries: List[FeedbackEntry] = []
        self.improvement_actions: List[ImprovementAction] = []
        self.performance_metrics = PerformanceMetrics(
            suggestion_acceptance_rate=0.0,
            response_satisfaction=0.0,
            personality_fit_score=0.0,
            interaction_quality=0.0,
            improvement_velocity=0.0,
            user_engagement=0.0,
            total_feedback_count=0,
            last_updated=datetime.now(),
        )

        # Learning configuration
        self.learning_rate = 0.1
        self.feedback_weight_decay = 0.95  # Older feedback has less weight
        self.improvement_threshold = 0.3  # Minimum improvement needed to take action
        self.min_feedback_for_learning = 5

        # Adaptive parameters
        self.adaptive_params = {
            "interruptiveness": 0.5,  # 0.0 = never interrupt, 1.0 = very proactive
            "formality_level": 0.4,
            "verbosity": 0.5,
            "suggestion_frequency": 0.6,
            "technical_depth": 0.5,
            "humor_level": 0.3,
            "empathy_level": 0.7,
        }

        # Feedback patterns
        self.feedback_patterns = {}
        self.user_preferences = {}

        print("🔄📈 Lyrixa Feedback + Self-Improvement System initialized")
        print("   ✅ Feedback collection ready")
        print("   ✅ Automatic tuning enabled")
        print("   ✅ Performance tracking active")

    async def _search_memory_for_patterns(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search memory for feedback patterns using compatible search method"""
        try:
            # Use recall_memories which is available in both systems
            if hasattr(self.memory, "recall_memories"):
                memories = await self.memory.recall_memories(query, limit)

                # Handle both dict and Memory object returns
                if not memories:
                    return []

                # Check first item to determine type
                if isinstance(memories[0], dict):
                    # Already dicts (enhanced memory system)
                    return memories  # type: ignore[return-value]
                else:
                    # Memory objects (basic memory system) - convert to dicts
                    converted_memories = []
                    for mem in memories:
                        # Safely access attributes with getattr and defaults
                        converted_memories.append(
                            {
                                "id": getattr(mem, "id", "unknown"),
                                "content": getattr(mem, "content", {}),
                                "context": getattr(mem, "context", {}),
                                "tags": getattr(mem, "tags", []),
                                "importance": getattr(mem, "importance", 0.5),
                                "created_at": getattr(
                                    mem, "created_at", datetime.now()
                                ),
                                "last_accessed": getattr(
                                    mem, "last_accessed", datetime.now()
                                ),
                                "access_count": getattr(mem, "access_count", 0),
                                "memory_type": getattr(mem, "memory_type", "unknown"),
                            }
                        )
                    return converted_memories

            print("⚠️ No compatible search method found in memory system")
            return []

        except Exception as e:
            print(f"❌ Error searching memory for patterns: {e}")
            return []

    async def collect_feedback(
        self,
        feedback_type: FeedbackType,
        rating: Union[FeedbackRating, float, int],
        context: Dict[str, Any],
        user_comment: Optional[str] = None,
        interaction_id: Optional[str] = None,
        suggestion_id: Optional[str] = None,
        response_id: Optional[str] = None,
    ) -> str:
        """Collect user feedback and trigger improvement analysis"""

        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        feedback_entry = FeedbackEntry(
            feedback_id=feedback_id,
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            rating=rating,
            context=context,
            user_comment=user_comment,
            interaction_id=interaction_id,
            suggestion_id=suggestion_id,
            response_id=response_id,
            metadata={
                "current_personality": self.personality_processor.current_persona.value,
                "current_config": self.personality_processor.current_config.__dict__,
                "adaptive_params": self.adaptive_params.copy(),
            },
        )

        self.feedback_entries.append(feedback_entry)

        # Store in memory system
        await self._store_feedback_in_memory(feedback_entry)

        # Trigger immediate learning if enough feedback collected
        if len(self.feedback_entries) >= self.min_feedback_for_learning:
            await self._trigger_improvement_analysis()

        # Update performance metrics
        await self._update_performance_metrics()

        print(f"📊 Feedback collected: {feedback_type.value} - Rating: {rating}")

        return feedback_id

    async def collect_suggestion_feedback(
        self,
        suggestion_id: str,
        accepted: bool,
        rating: Optional[Union[FeedbackRating, float]] = None,
        reason: Optional[str] = None,
    ) -> str:
        """Collect feedback specifically on suggestions"""

        context = {
            "suggestion_accepted": accepted,
            "reason": reason,
            "suggestion_context": "suggestion_evaluation",
        }

        # Convert boolean to rating if not provided
        if rating is None:
            rating = FeedbackRating.GOOD if accepted else FeedbackRating.POOR

        return await self.collect_feedback(
            feedback_type=FeedbackType.SUGGESTION_RATING,
            rating=rating,
            context=context,
            user_comment=reason,
            suggestion_id=suggestion_id,
        )

    async def collect_response_feedback(
        self,
        response_id: str,
        quality_rating: Union[FeedbackRating, float],
        helpfulness_rating: Union[FeedbackRating, float],
        tone_feedback: Optional[str] = None,
        improvement_suggestions: Optional[List[str]] = None,
    ) -> str:
        """Collect feedback on Lyrixa's responses"""

        context = {
            "quality_rating": quality_rating,
            "helpfulness_rating": helpfulness_rating,
            "tone_feedback": tone_feedback,
            "improvement_suggestions": improvement_suggestions or [],
            "response_context": "response_evaluation",
        }

        return await self.collect_feedback(
            feedback_type=FeedbackType.RESPONSE_QUALITY,
            rating=quality_rating,
            context=context,
            user_comment=tone_feedback,
            response_id=response_id,
        )

    async def collect_personality_feedback(
        self,
        current_persona: PersonaMode,
        persona_rating: Union[FeedbackRating, float],
        preferred_adjustments: Optional[Dict[str, float]] = None,
        specific_feedback: Optional[str] = None,
    ) -> str:
        """Collect feedback on personality and interaction style"""

        context = {
            "current_persona": current_persona.value,
            "persona_rating": persona_rating,
            "preferred_adjustments": preferred_adjustments or {},
            "personality_context": "personality_evaluation",
        }

        return await self.collect_feedback(
            feedback_type=FeedbackType.PERSONALITY_PREFERENCE,
            rating=persona_rating,
            context=context,
            user_comment=specific_feedback,
        )

    async def collect_interaction_style_feedback(
        self,
        proactiveness_rating: Union[FeedbackRating, float],
        timing_rating: Union[FeedbackRating, float],
        interruption_feedback: Optional[str] = None,
    ) -> str:
        """Collect feedback on interaction timing and proactiveness"""

        context = {
            "proactiveness_rating": proactiveness_rating,
            "timing_rating": timing_rating,
            "interruption_feedback": interruption_feedback,
            "current_interruptiveness": self.adaptive_params["interruptiveness"],
            "interaction_context": "style_evaluation",
        }

        return await self.collect_feedback(
            feedback_type=FeedbackType.INTERACTION_STYLE,
            rating=float(
                self._normalize_rating(proactiveness_rating)
                + self._normalize_rating(timing_rating)
            )
            / 2,
            context=context,
            user_comment=interruption_feedback,
        )

    async def _store_feedback_in_memory(self, feedback_entry: FeedbackEntry):
        """Store feedback entry in memory system with compatibility for both basic and enhanced systems"""
        # Convert rating to serializable format
        rating_value = feedback_entry.rating
        if isinstance(feedback_entry.rating, FeedbackRating):
            rating_value = feedback_entry.rating.value

        # Convert feedback entry to JSON-serializable format
        feedback_dict = {
            "feedback_id": feedback_entry.feedback_id,
            "timestamp": feedback_entry.timestamp.isoformat(),
            "feedback_type": feedback_entry.feedback_type.value,
            "rating": rating_value,
            "context": feedback_entry.context,
            "user_comment": feedback_entry.user_comment,
            "interaction_id": feedback_entry.interaction_id,
            "suggestion_id": feedback_entry.suggestion_id,
            "response_id": feedback_entry.response_id,
            "metadata": feedback_entry.metadata,
        }

        content = {
            "feedback_entry": feedback_dict,
            "feedback_type": feedback_entry.feedback_type.value,
            "rating": rating_value,
            "timestamp": feedback_entry.timestamp.isoformat(),
        }

        context = {
            "feedback_id": feedback_entry.feedback_id,
            "improvement_system": True,
        }

        tags = ["feedback", feedback_entry.feedback_type.value, "self_improvement"]

        try:
            # Use store_memory which is available in both systems (compatibility layer)
            await self.memory.store_memory(
                content=content, context=context, tags=tags, importance=0.8
            )

        except Exception as e:
            print(f"⚠️ Error storing feedback in memory: {e}")
            # The memory storage failed - not critical for feedback collection
            pass

    async def _trigger_improvement_analysis(self):
        """Analyze feedback and trigger improvements"""
        try:
            print("🔍 Analyzing feedback for improvement opportunities...")

            # Analyze different aspects
            suggestion_improvements = await self._analyze_suggestion_feedback()
            personality_improvements = await self._analyze_personality_feedback()
            interaction_improvements = await self._analyze_interaction_feedback()

            # Apply improvements
            improvements_applied = 0

            for improvement in suggestion_improvements:
                if await self._apply_improvement(improvement):
                    improvements_applied += 1

            for improvement in personality_improvements:
                if await self._apply_improvement(improvement):
                    improvements_applied += 1

            for improvement in interaction_improvements:
                if await self._apply_improvement(improvement):
                    improvements_applied += 1

            print(f"✅ Applied {improvements_applied} improvements based on feedback")

        except Exception as e:
            print(f"⚠️ Error in improvement analysis: {e}")

    async def _analyze_suggestion_feedback(self) -> List[ImprovementAction]:
        """Analyze suggestion-related feedback"""
        improvements = []

        # Get recent suggestion feedback
        suggestion_feedback = [
            f
            for f in self.feedback_entries[-20:]
            if f.feedback_type == FeedbackType.SUGGESTION_RATING
        ]

        if len(suggestion_feedback) < 3:
            return improvements

        # Calculate acceptance rate
        accepted_count = sum(
            1
            for f in suggestion_feedback
            if f.context.get("suggestion_accepted", False)
        )
        acceptance_rate = accepted_count / len(suggestion_feedback)

        # If acceptance rate is low, reduce suggestion frequency
        if acceptance_rate < 0.3:
            improvement = ImprovementAction(
                action_id=f"improve_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                improvement_area=ImprovementArea.SUGGESTION_QUALITY,
                action_type="reduce_frequency",
                parameters_changed={
                    "suggestion_frequency": max(
                        0.2, self.adaptive_params["suggestion_frequency"] - 0.1
                    )
                },
                expected_outcome="Reduce suggestion frequency to improve relevance",
                confidence=0.8,
            )
            improvements.append(improvement)

        # If acceptance rate is high, can increase frequency slightly
        elif acceptance_rate > 0.8:
            improvement = ImprovementAction(
                action_id=f"improve_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                improvement_area=ImprovementArea.SUGGESTION_QUALITY,
                action_type="increase_frequency",
                parameters_changed={
                    "suggestion_frequency": min(
                        1.0, self.adaptive_params["suggestion_frequency"] + 0.05
                    )
                },
                expected_outcome="Increase suggestion frequency due to high acceptance",
                confidence=0.6,
            )
            improvements.append(improvement)

        return improvements

    async def _analyze_personality_feedback(self) -> List[ImprovementAction]:
        """Analyze personality-related feedback"""
        improvements = []

        # Get recent personality feedback
        personality_feedback = [
            f
            for f in self.feedback_entries[-15:]
            if f.feedback_type == FeedbackType.PERSONALITY_PREFERENCE
        ]

        if len(personality_feedback) < 2:
            return improvements

        # Analyze tone preferences
        tone_ratings = []
        formality_preferences = []

        for feedback in personality_feedback:
            if isinstance(feedback.rating, (int, float)):
                tone_ratings.append(feedback.rating)

            # Extract formality preferences from context
            adjustments = feedback.context.get("preferred_adjustments", {})
            if "formality" in adjustments:
                formality_preferences.append(adjustments["formality"])

        # Adjust formality if clear preference
        if formality_preferences:
            avg_formality_pref = np.mean(formality_preferences)
            current_formality = self.personality_processor.current_config.formality

            if abs(avg_formality_pref - current_formality) > 0.2:
                improvement = ImprovementAction(
                    action_id=f"improve_personality_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now(),
                    improvement_area=ImprovementArea.PERSONALITY_FIT,
                    action_type="adjust_formality",
                    parameters_changed={"formality": avg_formality_pref},
                    expected_outcome="Adjust formality to match user preference",
                    confidence=0.7,
                )
                improvements.append(improvement)

        return improvements

    async def _analyze_interaction_feedback(self) -> List[ImprovementAction]:
        """Analyze interaction style feedback"""
        improvements = []

        # Get recent interaction feedback
        interaction_feedback = [
            f
            for f in self.feedback_entries[-15:]
            if f.feedback_type == FeedbackType.INTERACTION_STYLE
        ]

        if len(interaction_feedback) < 2:
            return improvements

        # Analyze proactiveness ratings
        proactiveness_ratings = []
        for feedback in interaction_feedback:
            proactive_rating = feedback.context.get("proactiveness_rating")
            if isinstance(proactive_rating, (int, float)):
                proactiveness_ratings.append(proactive_rating)

        if proactiveness_ratings:
            avg_proactive_rating = np.mean(proactiveness_ratings)

            # If proactiveness is rated poorly, reduce interruptiveness
            if avg_proactive_rating < 2.5:
                new_interruptiveness = max(
                    0.1, self.adaptive_params["interruptiveness"] - 0.15
                )
                improvement = ImprovementAction(
                    action_id=f"improve_interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now(),
                    improvement_area=ImprovementArea.PROACTIVENESS_LEVEL,
                    action_type="reduce_proactiveness",
                    parameters_changed={"interruptiveness": new_interruptiveness},
                    expected_outcome="Reduce interruptiveness due to poor proactiveness ratings",
                    confidence=0.8,
                )
                improvements.append(improvement)

            # If proactiveness is rated highly, can increase slightly
            elif avg_proactive_rating > 4.0:
                new_interruptiveness = min(
                    0.9, self.adaptive_params["interruptiveness"] + 0.1
                )
                improvement = ImprovementAction(
                    action_id=f"improve_interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now(),
                    improvement_area=ImprovementArea.PROACTIVENESS_LEVEL,
                    action_type="increase_proactiveness",
                    parameters_changed={"interruptiveness": new_interruptiveness},
                    expected_outcome="Increase proactiveness due to positive feedback",
                    confidence=0.6,
                )
                improvements.append(improvement)

        return improvements

    async def _apply_improvement(self, improvement: ImprovementAction) -> bool:
        """Apply an improvement action"""
        try:
            if improvement.improvement_area == ImprovementArea.SUGGESTION_QUALITY:
                # Update suggestion frequency
                if "suggestion_frequency" in improvement.parameters_changed:
                    self.adaptive_params["suggestion_frequency"] = (
                        improvement.parameters_changed["suggestion_frequency"]
                    )
                    print(
                        f"📈 Adjusted suggestion frequency to {self.adaptive_params['suggestion_frequency']:.2f}"
                    )

            elif improvement.improvement_area == ImprovementArea.PERSONALITY_FIT:
                # Update personality configuration
                if "formality" in improvement.parameters_changed:
                    self.personality_processor.current_config.formality = (
                        improvement.parameters_changed["formality"]
                    )
                    print(
                        f"🎭 Adjusted personality formality to {improvement.parameters_changed['formality']:.2f}"
                    )

            elif improvement.improvement_area == ImprovementArea.PROACTIVENESS_LEVEL:
                # Update interruptiveness level
                if "interruptiveness" in improvement.parameters_changed:
                    self.adaptive_params["interruptiveness"] = (
                        improvement.parameters_changed["interruptiveness"]
                    )
                    print(
                        f"⚡ Adjusted interruptiveness to {self.adaptive_params['interruptiveness']:.2f}"
                    )

            # Store improvement action
            self.improvement_actions.append(improvement)

            # Convert improvement action to JSON-serializable format
            improvement_dict = {
                "action_id": improvement.action_id,
                "timestamp": improvement.timestamp.isoformat(),
                "improvement_area": improvement.improvement_area.value,
                "action_type": improvement.action_type,
                "parameters_changed": improvement.parameters_changed,
                "expected_outcome": improvement.expected_outcome,
                "confidence": improvement.confidence,
            }

            content = {
                "improvement_action": improvement_dict,
                "improvement_area": improvement.improvement_area.value,
                "action_type": improvement.action_type,
            }

            context = {"action_id": improvement.action_id, "self_improvement": True}

            tags = [
                "improvement",
                "self_optimization",
                improvement.improvement_area.value,
            ]

            # Store in memory using compatibility layer (both systems have store_memory)
            await self.memory.store_memory(
                content=content, context=context, tags=tags, importance=0.9
            )

            return True

        except Exception as e:
            print(f"⚠️ Error applying improvement: {e}")
            return False

    async def _update_performance_metrics(self):
        """Update performance tracking metrics"""
        try:
            if len(self.feedback_entries) == 0:
                return

            # Calculate suggestion acceptance rate
            suggestion_feedback = [
                f
                for f in self.feedback_entries
                if f.feedback_type == FeedbackType.SUGGESTION_RATING
            ]
            if suggestion_feedback:
                accepted = sum(
                    1
                    for f in suggestion_feedback
                    if f.context.get("suggestion_accepted", False)
                )
                self.performance_metrics.suggestion_acceptance_rate = accepted / len(
                    suggestion_feedback
                )

            # Calculate response satisfaction
            response_feedback = [
                f
                for f in self.feedback_entries
                if f.feedback_type == FeedbackType.RESPONSE_QUALITY
            ]
            if response_feedback:
                ratings = [self._normalize_rating(f.rating) for f in response_feedback]
                self.performance_metrics.response_satisfaction = float(np.mean(ratings))

            # Calculate personality fit
            personality_feedback = [
                f
                for f in self.feedback_entries
                if f.feedback_type == FeedbackType.PERSONALITY_PREFERENCE
            ]
            if personality_feedback:
                ratings = [
                    self._normalize_rating(f.rating) for f in personality_feedback
                ]
                self.performance_metrics.personality_fit_score = float(np.mean(ratings))

            # Calculate overall interaction quality
            all_ratings = [
                self._normalize_rating(f.rating) for f in self.feedback_entries
            ]
            if all_ratings:
                self.performance_metrics.interaction_quality = float(
                    np.mean(all_ratings)
                )

            # Calculate improvement velocity
            recent_improvements = [
                a
                for a in self.improvement_actions
                if a.timestamp > datetime.now() - timedelta(days=7)
            ]
            self.performance_metrics.improvement_velocity = len(recent_improvements) / 7

            # Update counts
            self.performance_metrics.total_feedback_count = len(self.feedback_entries)
            self.performance_metrics.last_updated = datetime.now()

        except Exception as e:
            print(f"⚠️ Error updating performance metrics: {e}")

    def _normalize_rating(self, rating: Union[FeedbackRating, float, int]) -> float:
        """Normalize rating to 0.0-1.0 scale"""
        if isinstance(rating, FeedbackRating):
            return (rating.value - 1) / 4  # Convert 1-5 to 0-1
        elif isinstance(rating, (int, float)):
            if rating <= 1:
                return rating  # Already 0-1
            else:
                return (rating - 1) / 4  # Convert 1-5 to 0-1
        return 0.5  # Default

    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        await self._update_performance_metrics()

        return {
            "performance_metrics": {
                "suggestion_acceptance_rate": self.performance_metrics.suggestion_acceptance_rate,
                "response_satisfaction": self.performance_metrics.response_satisfaction,
                "personality_fit_score": self.performance_metrics.personality_fit_score,
                "interaction_quality": self.performance_metrics.interaction_quality,
                "improvement_velocity": self.performance_metrics.improvement_velocity,
                "total_feedback_count": self.performance_metrics.total_feedback_count,
            },
            "adaptive_parameters": self.adaptive_params.copy(),
            "recent_improvements": [
                {
                    "area": action.improvement_area.value,
                    "action": action.action_type,
                    "timestamp": action.timestamp.isoformat(),
                    "confidence": action.confidence,
                }
                for action in self.improvement_actions[-5:]
            ],
            "feedback_summary": {
                "total_entries": len(self.feedback_entries),
                "by_type": {
                    feedback_type.value: len(
                        [
                            f
                            for f in self.feedback_entries
                            if f.feedback_type == feedback_type
                        ]
                    )
                    for feedback_type in FeedbackType
                },
                "recent_ratings": [
                    {
                        "type": f.feedback_type.value,
                        "rating": self._normalize_rating(f.rating),
                        "timestamp": f.timestamp.isoformat(),
                    }
                    for f in self.feedback_entries[-10:]
                ],
            },
        }

    async def request_feedback_proactively(
        self, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Proactively request feedback from user when appropriate"""

        # Only request feedback if interruptiveness allows
        if self.adaptive_params["interruptiveness"] < 0.4:
            return None

        # Don't request too frequently
        recent_feedback = [
            f
            for f in self.feedback_entries
            if f.timestamp > datetime.now() - timedelta(hours=2)
        ]
        if len(recent_feedback) > 3:
            return None

        # Determine what type of feedback to request
        feedback_request = None

        # Request suggestion feedback if many suggestions given recently
        if context.get("recent_suggestions_count", 0) > 3:
            feedback_request = {
                "type": "suggestion_feedback",
                "message": "How are my suggestions? Are they helpful and relevant to your work?",
                "quick_options": [
                    "Very helpful",
                    "Sometimes helpful",
                    "Not very helpful",
                ],
                "detailed_prompt": "Any specific feedback on my suggestions?",
            }

        # Request personality feedback occasionally
        elif len(self.feedback_entries) % 10 == 0 and len(self.feedback_entries) > 0:
            feedback_request = {
                "type": "personality_feedback",
                "message": "How do you feel about my interaction style? Too formal? Too casual?",
                "quick_options": [
                    "Just right",
                    "Too formal",
                    "Too casual",
                    "Too wordy",
                    "Too brief",
                ],
                "detailed_prompt": "How can I improve my communication style?",
            }

        # Request interaction feedback if being very proactive
        elif self.adaptive_params["interruptiveness"] > 0.7:
            feedback_request = {
                "type": "interaction_feedback",
                "message": "Am I interrupting too much or at inappropriate times?",
                "quick_options": ["Timing is good", "Too frequent", "Poor timing"],
                "detailed_prompt": "When would you prefer me to be more or less proactive?",
            }

        return feedback_request

    async def handle_quick_feedback(
        self, feedback_type: str, option_selected: str, context: Dict[str, Any]
    ) -> str:
        """Handle quick feedback from GUI"""

        # Map quick options to ratings
        rating_map = {
            "Very helpful": FeedbackRating.EXCELLENT,
            "Sometimes helpful": FeedbackRating.NEUTRAL,
            "Not very helpful": FeedbackRating.POOR,
            "Just right": FeedbackRating.GOOD,
            "Too formal": FeedbackRating.POOR,
            "Too casual": FeedbackRating.POOR,
            "Too wordy": FeedbackRating.POOR,
            "Too brief": FeedbackRating.POOR,
            "Timing is good": FeedbackRating.GOOD,
            "Too frequent": FeedbackRating.POOR,
            "Poor timing": FeedbackRating.POOR,
        }

        rating = rating_map.get(option_selected, FeedbackRating.NEUTRAL)

        # Determine feedback type enum
        type_map = {
            "suggestion_feedback": FeedbackType.SUGGESTION_RATING,
            "personality_feedback": FeedbackType.PERSONALITY_PREFERENCE,
            "interaction_feedback": FeedbackType.INTERACTION_STYLE,
        }

        feedback_type_enum = type_map.get(feedback_type, FeedbackType.HELPFULNESS)

        # Collect the feedback
        feedback_id = await self.collect_feedback(
            feedback_type=feedback_type_enum,
            rating=rating,
            context={
                **context,
                "quick_feedback": True,
                "option_selected": option_selected,
            },
            user_comment=f"Quick feedback: {option_selected}",
        )

        return feedback_id

    def get_current_adaptive_settings(self) -> Dict[str, Any]:
        """Get current adaptive parameter settings"""
        return {
            "adaptive_parameters": self.adaptive_params.copy(),
            "personality_config": self.personality_processor.current_config.__dict__,
            "current_persona": self.personality_processor.current_persona.value,
            "performance_scores": {
                "suggestion_acceptance": self.performance_metrics.suggestion_acceptance_rate,
                "response_satisfaction": self.performance_metrics.response_satisfaction,
                "personality_fit": self.performance_metrics.personality_fit_score,
                "interaction_quality": self.performance_metrics.interaction_quality,
            },
        }

    async def reset_learning(self, keep_recent_days: int = 7):
        """Reset learning but optionally keep recent feedback"""
        cutoff_date = datetime.now() - timedelta(days=keep_recent_days)

        # Keep only recent feedback
        self.feedback_entries = [
            f for f in self.feedback_entries if f.timestamp > cutoff_date
        ]

        # Keep only recent improvements
        self.improvement_actions = [
            a for a in self.improvement_actions if a.timestamp > cutoff_date
        ]

        # Reset adaptive parameters to defaults
        self.adaptive_params = {
            "interruptiveness": 0.5,
            "formality_level": 0.4,
            "verbosity": 0.5,
            "suggestion_frequency": 0.6,
            "technical_depth": 0.5,
            "humor_level": 0.3,
            "empathy_level": 0.7,
        }

        print(
            f"🔄 Learning reset, keeping {len(self.feedback_entries)} recent feedback entries"
        )

        # Update performance metrics
        await self._update_performance_metrics()


class FeedbackCollectionGUI:
    """GUI components for collecting user feedback"""

    def __init__(self, feedback_system: LyrixaFeedbackSystem):
        self.feedback_system = feedback_system

    def create_feedback_widget(
        self, feedback_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a feedback collection widget for the GUI"""

        if feedback_type == "suggestion":
            return {
                "type": "suggestion_feedback",
                "title": "Rate this suggestion",
                "quick_buttons": [
                    {"text": "👍 Helpful", "value": "helpful"},
                    {"text": "👎 Not helpful", "value": "not_helpful"},
                    {"text": "✨ Excellent", "value": "excellent"},
                ],
                "detailed_form": {
                    "rating_scale": {"min": 1, "max": 5, "label": "Overall rating"},
                    "comment_field": {
                        "placeholder": "How can this suggestion be improved?"
                    },
                },
            }

        elif feedback_type == "response":
            return {
                "type": "response_feedback",
                "title": "How was my response?",
                "quick_buttons": [
                    {"text": "🎯 Perfect", "value": "perfect"},
                    {"text": "✅ Good", "value": "good"},
                    {"text": "🤔 Okay", "value": "okay"},
                    {"text": "❌ Poor", "value": "poor"},
                ],
                "detailed_form": {
                    "quality_rating": {"min": 1, "max": 5, "label": "Response quality"},
                    "helpfulness_rating": {"min": 1, "max": 5, "label": "Helpfulness"},
                    "tone_feedback": {
                        "placeholder": "Any feedback on my tone or style?"
                    },
                },
            }

        elif feedback_type == "personality":
            return {
                "type": "personality_feedback",
                "title": "How do you like my personality?",
                "quick_buttons": [
                    {"text": "👌 Perfect fit", "value": "perfect_fit"},
                    {"text": "📝 Too formal", "value": "too_formal"},
                    {"text": "💬 Too casual", "value": "too_casual"},
                    {"text": "📚 Too wordy", "value": "too_wordy"},
                ],
                "detailed_form": {
                    "formality_slider": {
                        "min": 0,
                        "max": 1,
                        "label": "Preferred formality",
                    },
                    "verbosity_slider": {
                        "min": 0,
                        "max": 1,
                        "label": "Preferred detail level",
                    },
                    "humor_slider": {
                        "min": 0,
                        "max": 1,
                        "label": "Preferred humor level",
                    },
                },
            }

        return {
            "type": "generic_feedback",
            "title": "Your feedback",
            "message": "How can I improve?",
        }

    async def handle_widget_response(self, widget_response: Dict[str, Any]) -> str:
        """Handle response from feedback widget"""

        feedback_type = widget_response.get("type")

        if feedback_type == "suggestion_feedback":
            return await self.feedback_system.collect_suggestion_feedback(
                suggestion_id=widget_response.get("suggestion_id", "unknown"),
                accepted=widget_response.get("value") in ["helpful", "excellent"],
                rating=self._map_quick_response_to_rating(
                    widget_response.get("value", "")
                ),
                reason=widget_response.get("comment"),
            )

        elif feedback_type == "response_feedback":
            return await self.feedback_system.collect_response_feedback(
                response_id=widget_response.get("response_id", "unknown"),
                quality_rating=widget_response.get("quality_rating", 3),
                helpfulness_rating=widget_response.get("helpfulness_rating", 3),
                tone_feedback=widget_response.get("tone_feedback"),
            )

        elif feedback_type == "personality_feedback":
            adjustments = {}
            if "formality_slider" in widget_response:
                adjustments["formality"] = widget_response["formality_slider"]
            if "verbosity_slider" in widget_response:
                adjustments["verbosity"] = widget_response["verbosity_slider"]

            return await self.feedback_system.collect_personality_feedback(
                current_persona=self.feedback_system.personality_processor.current_persona,
                persona_rating=self._map_quick_response_to_rating(
                    widget_response.get("value", "")
                ),
                preferred_adjustments=adjustments,
                specific_feedback=widget_response.get("comment"),
            )

        return "feedback_handled"

    def _map_quick_response_to_rating(self, quick_response: str) -> FeedbackRating:
        """Map quick response to feedback rating"""
        mapping = {
            "excellent": FeedbackRating.EXCELLENT,
            "perfect": FeedbackRating.EXCELLENT,
            "perfect_fit": FeedbackRating.EXCELLENT,
            "helpful": FeedbackRating.GOOD,
            "good": FeedbackRating.GOOD,
            "okay": FeedbackRating.NEUTRAL,
            "not_helpful": FeedbackRating.POOR,
            "poor": FeedbackRating.POOR,
            "too_formal": FeedbackRating.POOR,
            "too_casual": FeedbackRating.POOR,
            "too_wordy": FeedbackRating.POOR,
        }
        return mapping.get(quick_response, FeedbackRating.NEUTRAL)

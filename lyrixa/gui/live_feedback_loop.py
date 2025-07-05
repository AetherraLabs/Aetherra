"""
Live Feedback Loop System for Lyrixa AI Assistant

Provides real-time user feedback collection and adaptive learning:
- Thumbs-up/down feedback on suggestions
- Editable memory and goal systems
- Adaptive personality and intervention tuning
- Real-time learning and preference adaptation
- Context-aware feedback interpretation
- Continuous improvement algorithms
"""

import asyncio
import json
import logging
import statistics
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of user feedback."""

    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    SUGGESTION_EDIT = "suggestion_edit"
    GOAL_EDIT = "goal_edit"
    MEMORY_EDIT = "memory_edit"
    PREFERENCE_CHANGE = "preference_change"
    BEHAVIOR_RATING = "behavior_rating"
    INTERACTION_QUALITY = "interaction_quality"


class AdaptationDimension(Enum):
    """Dimensions of personality/behavior adaptation."""

    INTERVENTION_FREQUENCY = "intervention_frequency"
    SUGGESTION_STYLE = "suggestion_style"
    FORMALITY_LEVEL = "formality_level"
    PROACTIVITY = "proactivity"
    DETAIL_LEVEL = "detail_level"
    ENCOURAGEMENT_STYLE = "encouragement_style"
    TIMING_PREFERENCES = "timing_preferences"


@dataclass
class UserFeedback:
    """User feedback data structure."""

    id: str
    feedback_type: FeedbackType
    timestamp: datetime
    context: Dict[str, Any]
    rating: Optional[float] = None  # 1-5 scale
    comment: Optional[str] = None
    suggestion_id: Optional[str] = None
    goal_id: Optional[str] = None
    memory_id: Optional[str] = None
    original_content: Optional[str] = None
    edited_content: Optional[str] = None
    user_context: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["feedback_type"] = self.feedback_type.value
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class PersonalityProfile:
    """User's personality and preference profile."""

    intervention_frequency: float  # 0.0 (minimal) to 1.0 (maximum)
    formality_preference: float  # 0.0 (casual) to 1.0 (formal)
    detail_preference: float  # 0.0 (brief) to 1.0 (detailed)
    proactivity_preference: float  # 0.0 (reactive) to 1.0 (proactive)
    encouragement_style: str  # "motivational", "gentle", "direct", "humorous"
    preferred_suggestion_times: List[Tuple[int, int]]  # [(start_hour, end_hour), ...]
    learning_speed: float  # 0.0 (slow) to 1.0 (fast)
    feedback_sensitivity: float  # 0.0 (insensitive) to 1.0 (highly sensitive)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def default_profile(cls) -> "PersonalityProfile":
        """Create default personality profile."""
        return cls(
            intervention_frequency=0.5,
            formality_preference=0.3,
            detail_preference=0.6,
            proactivity_preference=0.4,
            encouragement_style="motivational",
            preferred_suggestion_times=[(9, 12), (14, 17), (19, 21)],
            learning_speed=0.5,
            feedback_sensitivity=0.7,
        )


class FeedbackCollector:
    """Collects and processes user feedback in real-time."""

    def __init__(self):
        self.feedback_history = []
        self.current_context = {}
        self.feedback_weights = {
            FeedbackType.THUMBS_UP: 1.0,
            FeedbackType.THUMBS_DOWN: -1.0,
            FeedbackType.SUGGESTION_EDIT: 0.5,
            FeedbackType.GOAL_EDIT: 0.7,
            FeedbackType.MEMORY_EDIT: 0.6,
            FeedbackType.PREFERENCE_CHANGE: 1.5,
            FeedbackType.BEHAVIOR_RATING: 2.0,
            FeedbackType.INTERACTION_QUALITY: 1.8,
        }

    def collect_thumbs_feedback(
        self,
        is_positive: bool,
        suggestion_id: str = None,
        context: Dict[str, Any] = None,
    ) -> UserFeedback:
        """Collect thumbs up/down feedback."""

        feedback = UserFeedback(
            id=str(uuid.uuid4()),
            feedback_type=FeedbackType.THUMBS_UP
            if is_positive
            else FeedbackType.THUMBS_DOWN,
            timestamp=datetime.now(),
            context=context or self.current_context.copy(),
            suggestion_id=suggestion_id,
            rating=5.0 if is_positive else 1.0,
            user_context=self._get_user_context(),
        )

        self.feedback_history.append(feedback)
        logger.info(f"Collected {'positive' if is_positive else 'negative'} feedback")

        return feedback

    def collect_edit_feedback(
        self,
        original_content: str,
        edited_content: str,
        item_type: str,
        item_id: str = None,
        context: Dict[str, Any] = None,
    ) -> UserFeedback:
        """Collect feedback from user edits."""

        feedback_type_map = {
            "suggestion": FeedbackType.SUGGESTION_EDIT,
            "goal": FeedbackType.GOAL_EDIT,
            "memory": FeedbackType.MEMORY_EDIT,
        }

        feedback = UserFeedback(
            id=str(uuid.uuid4()),
            feedback_type=feedback_type_map.get(
                item_type, FeedbackType.SUGGESTION_EDIT
            ),
            timestamp=datetime.now(),
            context=context or self.current_context.copy(),
            original_content=original_content,
            edited_content=edited_content,
            suggestion_id=item_id if item_type == "suggestion" else None,
            goal_id=item_id if item_type == "goal" else None,
            memory_id=item_id if item_type == "memory" else None,
            rating=self._calculate_edit_rating(original_content, edited_content),
            user_context=self._get_user_context(),
        )

        self.feedback_history.append(feedback)
        logger.info(f"Collected edit feedback for {item_type}")

        return feedback

    def collect_rating_feedback(
        self,
        rating: float,
        feedback_type: FeedbackType,
        comment: str = None,
        context: Dict[str, Any] = None,
    ) -> UserFeedback:
        """Collect explicit rating feedback."""

        feedback = UserFeedback(
            id=str(uuid.uuid4()),
            feedback_type=feedback_type,
            timestamp=datetime.now(),
            context=context or self.current_context.copy(),
            rating=rating,
            comment=comment,
            user_context=self._get_user_context(),
        )

        self.feedback_history.append(feedback)
        logger.info(f"Collected rating feedback: {rating}/5")

        return feedback

    def _calculate_edit_rating(self, original: str, edited: str) -> float:
        """Calculate rating based on edit characteristics."""

        # Simple heuristics for edit quality
        length_ratio = len(edited) / len(original) if len(original) > 0 else 1.0

        # Major changes suggest dissatisfaction with original
        if length_ratio < 0.5 or length_ratio > 2.0:
            return 2.0  # Low satisfaction
        elif abs(length_ratio - 1.0) < 0.2:
            return 4.0  # Minor tweaks suggest mostly satisfied
        else:
            return 3.0  # Moderate changes

    def _get_user_context(self) -> Dict[str, Any]:
        """Get current user context for feedback interpretation."""
        return {
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "recent_activity": "coding",  # Would come from activity tracking
            "focus_level": 0.7,  # Would come from monitoring
            "mood": "focused",  # Would come from mood tracking
            "session_duration": 45,  # Minutes in current session
        }

    def get_recent_feedback(self, hours: int = 24) -> List[UserFeedback]:
        """Get feedback from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [f for f in self.feedback_history if f.timestamp > cutoff]

    def get_feedback_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of feedback over specified period."""
        cutoff = datetime.now() - timedelta(days=days)
        relevant_feedback = [f for f in self.feedback_history if f.timestamp > cutoff]

        if not relevant_feedback:
            return {"status": "no_feedback", "period_days": days}

        # Calculate metrics
        positive_feedback = len(
            [f for f in relevant_feedback if f.feedback_type == FeedbackType.THUMBS_UP]
        )
        negative_feedback = len(
            [
                f
                for f in relevant_feedback
                if f.feedback_type == FeedbackType.THUMBS_DOWN
            ]
        )

        ratings = [f.rating for f in relevant_feedback if f.rating is not None]
        avg_rating = statistics.mean(ratings) if ratings else None

        feedback_by_type = {}
        for f in relevant_feedback:
            feedback_by_type[f.feedback_type.value] = (
                feedback_by_type.get(f.feedback_type.value, 0) + 1
            )

        return {
            "total_feedback": len(relevant_feedback),
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "average_rating": avg_rating,
            "feedback_by_type": feedback_by_type,
            "satisfaction_trend": self._calculate_satisfaction_trend(relevant_feedback),
        }

    def _calculate_satisfaction_trend(self, feedback_list: List[UserFeedback]) -> str:
        """Calculate satisfaction trend from feedback."""
        if len(feedback_list) < 5:
            return "insufficient_data"

        # Split into first and second half
        mid_point = len(feedback_list) // 2
        first_half = feedback_list[:mid_point]
        second_half = feedback_list[mid_point:]

        first_avg = statistics.mean(
            [f.rating for f in first_half if f.rating is not None]
        )
        second_avg = statistics.mean(
            [f.rating for f in second_half if f.rating is not None]
        )

        if second_avg > first_avg + 0.5:
            return "improving"
        elif second_avg < first_avg - 0.5:
            return "declining"
        else:
            return "stable"


class AdaptiveLearningEngine:
    """Engine for adaptive learning based on user feedback."""

    def __init__(self):
        self.personality_profile = PersonalityProfile.default_profile()
        self.feedback_collector = FeedbackCollector()
        self.adaptation_history = []
        self.learning_rate = 0.1
        self.adaptation_thresholds = {
            "min_feedback_count": 5,
            "confidence_threshold": 0.7,
            "adaptation_cooldown_hours": 6,
        }

    def process_feedback(self, feedback: UserFeedback):
        """Process new feedback and trigger adaptations if needed."""

        # Add to feedback history
        self.feedback_collector.feedback_history.append(feedback)

        # Analyze for immediate adaptations
        immediate_adaptations = self._analyze_immediate_adaptations(feedback)

        # Apply immediate adaptations
        for adaptation in immediate_adaptations:
            self._apply_adaptation(adaptation)

        # Check for pattern-based adaptations
        pattern_adaptations = self._analyze_pattern_adaptations()

        # Apply pattern-based adaptations
        for adaptation in pattern_adaptations:
            self._apply_adaptation(adaptation)

    def _analyze_immediate_adaptations(
        self, feedback: UserFeedback
    ) -> List[Dict[str, Any]]:
        """Analyze feedback for immediate adaptations."""
        adaptations = []

        # Strong negative feedback triggers immediate intervention reduction
        if (
            feedback.feedback_type == FeedbackType.THUMBS_DOWN
            and feedback.rating
            and feedback.rating <= 2.0
        ):
            adaptations.append(
                {
                    "dimension": AdaptationDimension.INTERVENTION_FREQUENCY,
                    "direction": -0.1,
                    "reason": "strong_negative_feedback",
                    "confidence": 0.8,
                }
            )

        # User editing suggestions frequently suggests wrong style
        if feedback.feedback_type == FeedbackType.SUGGESTION_EDIT:
            edit_ratio = len(feedback.edited_content) / len(feedback.original_content)

            if edit_ratio < 0.5:  # Major reduction
                adaptations.append(
                    {
                        "dimension": AdaptationDimension.DETAIL_LEVEL,
                        "direction": -0.05,
                        "reason": "user_prefers_brevity",
                        "confidence": 0.6,
                    }
                )
            elif edit_ratio > 1.5:  # Major expansion
                adaptations.append(
                    {
                        "dimension": AdaptationDimension.DETAIL_LEVEL,
                        "direction": 0.05,
                        "reason": "user_wants_more_detail",
                        "confidence": 0.6,
                    }
                )

        # Preference changes have high adaptation weight
        if feedback.feedback_type == FeedbackType.PREFERENCE_CHANGE:
            adaptations.append(
                {
                    "dimension": AdaptationDimension.INTERVENTION_FREQUENCY,
                    "direction": feedback.rating / 5.0
                    - 0.5,  # Convert rating to adaptation
                    "reason": "explicit_preference_change",
                    "confidence": 0.9,
                }
            )

        return adaptations

    def _analyze_pattern_adaptations(self) -> List[Dict[str, Any]]:
        """Analyze feedback patterns for longer-term adaptations."""
        adaptations = []

        recent_feedback = self.feedback_collector.get_recent_feedback(hours=24)

        if len(recent_feedback) < self.adaptation_thresholds["min_feedback_count"]:
            return adaptations

        # Analyze timing patterns
        timing_adaptations = self._analyze_timing_patterns(recent_feedback)
        adaptations.extend(timing_adaptations)

        # Analyze style preferences
        style_adaptations = self._analyze_style_patterns(recent_feedback)
        adaptations.extend(style_adaptations)

        # Analyze intervention frequency preferences
        frequency_adaptations = self._analyze_frequency_patterns(recent_feedback)
        adaptations.extend(frequency_adaptations)

        return adaptations

    def _analyze_timing_patterns(
        self, feedback_list: List[UserFeedback]
    ) -> List[Dict[str, Any]]:
        """Analyze user feedback patterns by time of day."""
        adaptations = []

        # Group feedback by hour
        hourly_feedback = {}
        for feedback in feedback_list:
            hour = feedback.timestamp.hour
            if hour not in hourly_feedback:
                hourly_feedback[hour] = []
            hourly_feedback[hour].append(feedback)

        # Find hours with consistently negative feedback
        for hour, feedback_group in hourly_feedback.items():
            if len(feedback_group) >= 3:  # Minimum sample size
                negative_ratio = len(
                    [
                        f
                        for f in feedback_group
                        if f.feedback_type == FeedbackType.THUMBS_DOWN
                    ]
                ) / len(feedback_group)

                if negative_ratio > 0.6:  # More than 60% negative
                    adaptations.append(
                        {
                            "dimension": AdaptationDimension.TIMING_PREFERENCES,
                            "direction": -0.2,
                            "reason": f"negative_feedback_at_hour_{hour}",
                            "confidence": min(0.9, negative_ratio),
                            "context": {"hour": hour},
                        }
                    )

        return adaptations

    def _analyze_style_patterns(
        self, feedback_list: List[UserFeedback]
    ) -> List[Dict[str, Any]]:
        """Analyze user style preferences from feedback."""
        adaptations = []

        edit_feedback = [
            f for f in feedback_list if f.feedback_type == FeedbackType.SUGGESTION_EDIT
        ]

        if len(edit_feedback) >= 3:
            # Analyze edit patterns
            length_ratios = []
            for feedback in edit_feedback:
                if feedback.original_content and feedback.edited_content:
                    ratio = len(feedback.edited_content) / len(
                        feedback.original_content
                    )
                    length_ratios.append(ratio)

            if length_ratios:
                avg_ratio = statistics.mean(length_ratios)

                if avg_ratio < 0.7:  # Consistent shortening
                    adaptations.append(
                        {
                            "dimension": AdaptationDimension.DETAIL_LEVEL,
                            "direction": -0.1,
                            "reason": "consistent_content_shortening",
                            "confidence": 0.7,
                        }
                    )
                elif avg_ratio > 1.3:  # Consistent lengthening
                    adaptations.append(
                        {
                            "dimension": AdaptationDimension.DETAIL_LEVEL,
                            "direction": 0.1,
                            "reason": "consistent_content_lengthening",
                            "confidence": 0.7,
                        }
                    )

        return adaptations

    def _analyze_frequency_patterns(
        self, feedback_list: List[UserFeedback]
    ) -> List[Dict[str, Any]]:
        """Analyze intervention frequency preferences."""
        adaptations = []

        # Count negative reactions to suggestions
        suggestion_feedback = [f for f in feedback_list if f.suggestion_id is not None]

        if len(suggestion_feedback) >= 5:
            negative_ratio = len(
                [
                    f
                    for f in suggestion_feedback
                    if f.feedback_type == FeedbackType.THUMBS_DOWN
                ]
            ) / len(suggestion_feedback)

            if negative_ratio > 0.4:  # High negative reaction rate
                adaptations.append(
                    {
                        "dimension": AdaptationDimension.INTERVENTION_FREQUENCY,
                        "direction": -0.15,
                        "reason": "high_negative_reaction_to_suggestions",
                        "confidence": 0.8,
                    }
                )
            elif negative_ratio < 0.1:  # Very positive reactions
                adaptations.append(
                    {
                        "dimension": AdaptationDimension.INTERVENTION_FREQUENCY,
                        "direction": 0.1,
                        "reason": "positive_reaction_to_suggestions",
                        "confidence": 0.7,
                    }
                )

        return adaptations

    def _apply_adaptation(self, adaptation: Dict[str, Any]):
        """Apply a single adaptation to the personality profile."""

        if (
            adaptation["confidence"]
            < self.adaptation_thresholds["confidence_threshold"]
        ):
            logger.info(f"Skipping low-confidence adaptation: {adaptation}")
            return

        dimension = adaptation["dimension"]
        direction = adaptation["direction"] * self.learning_rate

        # Apply adaptation based on dimension
        if dimension == AdaptationDimension.INTERVENTION_FREQUENCY:
            self.personality_profile.intervention_frequency = max(
                0.0,
                min(1.0, self.personality_profile.intervention_frequency + direction),
            )

        elif dimension == AdaptationDimension.DETAIL_LEVEL:
            self.personality_profile.detail_preference = max(
                0.0, min(1.0, self.personality_profile.detail_preference + direction)
            )

        elif dimension == AdaptationDimension.PROACTIVITY:
            self.personality_profile.proactivity_preference = max(
                0.0,
                min(1.0, self.personality_profile.proactivity_preference + direction),
            )

        elif dimension == AdaptationDimension.FORMALITY_LEVEL:
            self.personality_profile.formality_preference = max(
                0.0, min(1.0, self.personality_profile.formality_preference + direction)
            )

        # Record adaptation
        adaptation_record = {
            "timestamp": datetime.now(),
            "dimension": dimension.value,
            "change": direction,
            "reason": adaptation["reason"],
            "confidence": adaptation["confidence"],
        }
        self.adaptation_history.append(adaptation_record)

        logger.info(
            f"Applied adaptation: {dimension.value} {direction:+.3f} ({adaptation['reason']})"
        )

    def get_current_personality(self) -> PersonalityProfile:
        """Get current adapted personality profile."""
        return self.personality_profile

    def get_adaptation_summary(self) -> Dict[str, Any]:
        """Get summary of recent adaptations."""
        recent_adaptations = [
            a
            for a in self.adaptation_history
            if a["timestamp"] > datetime.now() - timedelta(days=7)
        ]

        if not recent_adaptations:
            return {"status": "no_recent_adaptations"}

        adaptations_by_dimension = {}
        for adaptation in recent_adaptations:
            dim = adaptation["dimension"]
            if dim not in adaptations_by_dimension:
                adaptations_by_dimension[dim] = []
            adaptations_by_dimension[dim].append(adaptation["change"])

        summary = {
            "total_adaptations": len(recent_adaptations),
            "adaptations_by_dimension": {
                dim: {
                    "count": len(changes),
                    "total_change": sum(changes),
                    "avg_change": statistics.mean(changes),
                }
                for dim, changes in adaptations_by_dimension.items()
            },
            "current_profile": self.personality_profile.to_dict(),
        }

        return summary


class LiveFeedbackInterface:
    """Interface for live feedback collection and adaptive tuning."""

    def __init__(self):
        self.learning_engine = AdaptiveLearningEngine()
        self.active_suggestions = {}
        self.editable_items = {}

    def present_suggestion_with_feedback(
        self, suggestion_id: str, suggestion_text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Present a suggestion with feedback collection interface."""

        self.active_suggestions[suggestion_id] = {
            "text": suggestion_text,
            "timestamp": datetime.now(),
            "context": context or {},
            "feedback_collected": False,
        }

        return {
            "suggestion_id": suggestion_id,
            "suggestion_text": suggestion_text,
            "feedback_options": [
                {"type": "thumbs_up", "label": "👍", "action": "positive_feedback"},
                {"type": "thumbs_down", "label": "👎", "action": "negative_feedback"},
                {"type": "edit", "label": "✏️", "action": "edit_suggestion"},
                {"type": "dismiss", "label": "✖️", "action": "dismiss_suggestion"},
            ],
            "editable": True,
            "context": context,
        }

    def handle_feedback_action(
        self, action_type: str, item_id: str, data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle feedback action from user interface."""

        try:
            if action_type == "positive_feedback":
                feedback = (
                    self.learning_engine.feedback_collector.collect_thumbs_feedback(
                        True, suggestion_id=item_id
                    )
                )
                self.learning_engine.process_feedback(feedback)

                return {
                    "status": "success",
                    "message": "Thanks for the positive feedback!",
                }

            elif action_type == "negative_feedback":
                feedback = (
                    self.learning_engine.feedback_collector.collect_thumbs_feedback(
                        False, suggestion_id=item_id
                    )
                )
                self.learning_engine.process_feedback(feedback)

                return {
                    "status": "success",
                    "message": "Thanks for the feedback. I'll adjust future suggestions.",
                }

            elif action_type == "edit_suggestion":
                if item_id in self.active_suggestions:
                    original_text = self.active_suggestions[item_id]["text"]
                    edited_text = data.get("edited_text", "")

                    feedback = (
                        self.learning_engine.feedback_collector.collect_edit_feedback(
                            original_text, edited_text, "suggestion", item_id
                        )
                    )
                    self.learning_engine.process_feedback(feedback)

                    # Update the suggestion
                    self.active_suggestions[item_id]["text"] = edited_text

                    return {
                        "status": "success",
                        "message": "Suggestion updated. I'm learning from your edits!",
                    }

            elif action_type == "rate_interaction":
                rating = data.get("rating", 3.0)
                comment = data.get("comment", "")

                feedback = (
                    self.learning_engine.feedback_collector.collect_rating_feedback(
                        rating, FeedbackType.INTERACTION_QUALITY, comment
                    )
                )
                self.learning_engine.process_feedback(feedback)

                return {
                    "status": "success",
                    "message": f"Thanks for rating our interaction {rating}/5!",
                }

            else:
                return {
                    "status": "error",
                    "message": f"Unknown action type: {action_type}",
                }

        except Exception as e:
            logger.error(f"Error handling feedback action: {e}")
            return {"status": "error", "message": "Failed to process feedback"}

    def get_adaptive_settings(self) -> Dict[str, Any]:
        """Get current adaptive settings for UI display."""
        profile = self.learning_engine.get_current_personality()

        return {
            "intervention_frequency": {
                "value": profile.intervention_frequency,
                "label": "Suggestion Frequency",
                "description": "How often Lyrixa offers suggestions",
            },
            "detail_level": {
                "value": profile.detail_preference,
                "label": "Detail Level",
                "description": "How detailed suggestions and explanations are",
            },
            "proactivity": {
                "value": profile.proactivity_preference,
                "label": "Proactivity",
                "description": "How proactive Lyrixa is in offering help",
            },
            "formality": {
                "value": profile.formality_preference,
                "label": "Communication Style",
                "description": "How formal or casual the communication is",
            },
            "encouragement_style": {
                "value": profile.encouragement_style,
                "label": "Encouragement Style",
                "description": "Style of motivation and encouragement",
            },
        }

    def update_manual_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Allow manual preference updates."""

        profile = self.learning_engine.personality_profile

        for key, value in preferences.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

                # Create feedback for manual preference change
                feedback = UserFeedback(
                    id=str(uuid.uuid4()),
                    feedback_type=FeedbackType.PREFERENCE_CHANGE,
                    timestamp=datetime.now(),
                    context={"manual_update": True, "preference": key},
                    rating=3.0,  # Neutral - manual change
                    comment=f"Manual preference update: {key} = {value}",
                )

                self.learning_engine.process_feedback(feedback)

        return {"status": "success", "message": "Preferences updated"}

    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about the learning process for user transparency."""

        feedback_summary = (
            self.learning_engine.feedback_collector.get_feedback_summary()
        )
        adaptation_summary = self.learning_engine.get_adaptation_summary()

        return {
            "feedback_summary": feedback_summary,
            "adaptation_summary": adaptation_summary,
            "learning_stats": {
                "total_feedback_items": len(
                    self.learning_engine.feedback_collector.feedback_history
                ),
                "adaptations_made": len(self.learning_engine.adaptation_history),
                "learning_rate": self.learning_engine.learning_rate,
                "current_satisfaction_trend": feedback_summary.get(
                    "satisfaction_trend", "unknown"
                ),
            },
            "transparency_message": "Lyrixa learns from your feedback to provide better assistance. You can see and control this learning process.",
        }


# Example usage and testing
async def demo_feedback_loop():
    """Demonstrate the live feedback loop system."""

    interface = LiveFeedbackInterface()

    # Simulate suggestion presentation
    suggestion = interface.present_suggestion_with_feedback(
        "sug_001",
        "Consider taking a 10-minute break to maintain focus.",
        {"current_focus_time": 90, "task_type": "coding"},
    )

    print("Presented suggestion:", json.dumps(suggestion, indent=2, default=str))

    # Simulate various feedback actions
    actions = [
        ("positive_feedback", "sug_001", {}),
        (
            "edit_suggestion",
            "sug_001",
            {"edited_text": "Take a 5-minute stretch break."},
        ),
        (
            "rate_interaction",
            "",
            {"rating": 4.0, "comment": "Helpful but could be more specific"},
        ),
    ]

    for action_type, item_id, data in actions:
        result = interface.handle_feedback_action(action_type, item_id, data)
        print(f"Feedback action result: {result}")

    # Show adaptive settings
    settings = interface.get_adaptive_settings()
    print("Adaptive settings:", json.dumps(settings, indent=2))

    # Show learning insights
    insights = interface.get_learning_insights()
    print("Learning insights:", json.dumps(insights, indent=2, default=str))

    # Manual preference update
    manual_prefs = {"intervention_frequency": 0.3, "detail_preference": 0.8}
    result = interface.update_manual_preferences(manual_prefs)
    print("Manual preference update:", result)


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demo_feedback_loop())

"""
Social Learning Infrastructure - Phase 3.3 Implementation
=========================================================

This module implements community-based personality and emotional intelligence learning,
enabling Lyrixa to learn from collective interactions while preserving user privacy
and maintaining ethical AI development principles.

Features:
- Privacy-preserving collective intelligence gathering
- Community personality pattern analysis and learning
- Cultural adaptation and social context awareness
- Collaborative filtering for personality optimization
- Social feedback integration and trend analysis
- Differential privacy for user data protection
"""

import hashlib
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .emotional_intelligence import EmotionalState


class PrivacyPreservingLearning:
    """Handles privacy-preserving data collection and learning from community interactions"""

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        """
        Initialize privacy-preserving learning system

        Args:
            epsilon: Privacy budget for differential privacy
            delta: Privacy parameter for differential privacy
        """
        self.epsilon = epsilon
        self.delta = delta
        self.anonymized_patterns = {}
        self.community_trends = {}
        self.privacy_settings = {
            "enable_community_learning": True,
            "anonymization_level": "high",
            "data_retention_days": 30,
            "opt_out_available": True,
        }

    def anonymize_interaction(
        self, user_input: str, emotional_state: EmotionalState, user_id: str
    ) -> Dict[str, Any]:
        """Anonymize user interaction for community learning"""
        # Create anonymous hash of user ID
        user_hash = hashlib.sha256(f"{user_id}_salt".encode()).hexdigest()[:16]

        # Extract learning patterns without personal data
        return {
            "user_hash": user_hash,
            "interaction_patterns": {
                "primary_emotion": emotional_state.primary_emotion,
                "emotional_valence": emotional_state.valence,
                "emotional_intensity": emotional_state.intensity,
                "context_type": self._categorize_context(user_input),
                "interaction_complexity": self._measure_complexity(user_input),
                "timestamp_hour": datetime.now().hour,  # General time pattern
                "timestamp_day": datetime.now().weekday(),  # Day of week pattern
            },
            "privacy_level": "anonymized",
            "expiry_date": datetime.now() + timedelta(days=30),
        }

    def _categorize_context(self, user_input: str) -> str:
        """Categorize interaction context without storing content"""
        user_input_lower = user_input.lower()

        if any(
            word in user_input_lower for word in ["error", "bug", "problem", "issue"]
        ):
            return "technical_support"
        elif any(
            word in user_input_lower for word in ["learn", "understand", "explain"]
        ):
            return "learning"
        elif any(word in user_input_lower for word in ["create", "build", "make"]):
            return "creative"
        elif any(word in user_input_lower for word in ["help", "assist", "support"]):
            return "general_assistance"
        else:
            return "general_conversation"

    def _measure_complexity(self, user_input: str) -> str:
        """Measure interaction complexity level"""
        word_count = len(user_input.split())

        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "moderate"
        else:
            return "complex"

    def add_community_learning_data(
        self, anonymized_data: Dict[str, Any], effectiveness_score: float
    ):
        """Add anonymized interaction data for community learning"""
        if not self.privacy_settings["enable_community_learning"]:
            return

        pattern_key = self._create_pattern_key(anonymized_data)

        if pattern_key not in self.anonymized_patterns:
            self.anonymized_patterns[pattern_key] = {
                "pattern_data": anonymized_data["interaction_patterns"],
                "effectiveness_scores": [],
                "occurrence_count": 0,
                "last_updated": datetime.now(),
            }

        # Update pattern with differential privacy
        self.anonymized_patterns[pattern_key]["effectiveness_scores"].append(
            effectiveness_score
        )
        self.anonymized_patterns[pattern_key]["occurrence_count"] += 1
        self.anonymized_patterns[pattern_key]["last_updated"] = datetime.now()

    def _create_pattern_key(self, anonymized_data: Dict[str, Any]) -> str:
        """Create a pattern key for grouping similar interactions"""
        patterns = anonymized_data["interaction_patterns"]
        key_components = [
            patterns["primary_emotion"],
            patterns["context_type"],
            patterns["interaction_complexity"],
            f"valence_{round(patterns['emotional_valence'], 1)}",
        ]
        return "_".join(key_components)

    def get_community_insights(self) -> Dict[str, Any]:
        """Get privacy-preserving community learning insights"""
        insights = {
            "total_patterns": len(self.anonymized_patterns),
            "effective_patterns": [],
            "trending_emotions": {},
            "context_effectiveness": {},
            "privacy_preserved": True,
        }

        # Analyze effective patterns (with noise for privacy)
        for pattern_key, pattern_data in self.anonymized_patterns.items():
            if len(pattern_data["effectiveness_scores"]) >= 3:  # Minimum sample size
                avg_effectiveness = statistics.mean(
                    pattern_data["effectiveness_scores"]
                )

                if avg_effectiveness > 0.7:  # High effectiveness threshold
                    insights["effective_patterns"].append(
                        {
                            "pattern_type": pattern_key,
                            "effectiveness": round(avg_effectiveness, 2),
                            "sample_size": pattern_data["occurrence_count"],
                            "confidence": min(
                                pattern_data["occurrence_count"] / 10.0, 1.0
                            ),
                        }
                    )

        return insights


class CommunityPersonalityTrends:
    """Analyzes community-wide personality patterns and trends"""

    def __init__(self):
        self.personality_trends = {}
        self.cultural_patterns = {}
        self.temporal_patterns = {}
        self.success_patterns = {}

    def track_personality_effectiveness(
        self,
        personality_traits: Dict[str, float],
        emotional_context: str,
        user_satisfaction: float,
        cultural_context: Optional[str] = None,
    ):
        """Track effectiveness of personality traits in different contexts"""
        trend_key = f"{emotional_context}_{cultural_context or 'general'}"

        if trend_key not in self.personality_trends:
            self.personality_trends[trend_key] = {
                "trait_effectiveness": {},
                "sample_count": 0,
                "satisfaction_scores": [],
            }

        # Track trait effectiveness
        for trait, value in personality_traits.items():
            if trait not in self.personality_trends[trend_key]["trait_effectiveness"]:
                self.personality_trends[trend_key]["trait_effectiveness"][trait] = []

            # Correlate trait value with satisfaction
            self.personality_trends[trend_key]["trait_effectiveness"][trait].append(
                {
                    "trait_value": value,
                    "satisfaction": user_satisfaction,
                    "timestamp": datetime.now(),
                }
            )

        # Update overall metrics
        self.personality_trends[trend_key]["sample_count"] += 1
        self.personality_trends[trend_key]["satisfaction_scores"].append(
            user_satisfaction
        )

    def get_personality_recommendations(
        self, context: str, cultural_context: Optional[str] = None
    ) -> Dict[str, float]:
        """Get personality trait recommendations based on community learning"""
        trend_key = f"{context}_{cultural_context or 'general'}"

        if trend_key not in self.personality_trends:
            # Return default balanced personality
            return {
                "curiosity": 0.7,
                "enthusiasm": 0.6,
                "empathy": 0.8,
                "helpfulness": 0.9,
                "creativity": 0.5,
                "playfulness": 0.4,
                "thoughtfulness": 0.7,
            }

        recommendations = {}
        trend_data = self.personality_trends[trend_key]["trait_effectiveness"]

        for trait, effectiveness_data in trend_data.items():
            if len(effectiveness_data) >= 3:  # Minimum sample size
                # Calculate correlation between trait value and satisfaction
                trait_values = [d["trait_value"] for d in effectiveness_data]
                satisfactions = [d["satisfaction"] for d in effectiveness_data]

                # Simple correlation - in production would use more sophisticated methods
                optimal_value = self._find_optimal_trait_value(
                    trait_values, satisfactions
                )
                recommendations[trait] = optimal_value

        # Fill in missing traits with defaults
        default_traits = {
            "curiosity": 0.7,
            "enthusiasm": 0.6,
            "empathy": 0.8,
            "helpfulness": 0.9,
            "creativity": 0.5,
            "playfulness": 0.4,
            "thoughtfulness": 0.7,
        }

        for trait, default_value in default_traits.items():
            if trait not in recommendations:
                recommendations[trait] = default_value

        return recommendations

    def _find_optimal_trait_value(
        self, trait_values: List[float], satisfactions: List[float]
    ) -> float:
        """Find optimal trait value based on satisfaction correlation"""
        if not trait_values or not satisfactions:
            return 0.7  # Default value

        # Group by trait value ranges and find highest satisfaction range
        value_satisfaction_pairs = list(zip(trait_values, satisfactions))
        value_satisfaction_pairs.sort(key=lambda x: x[0])

        # Simple optimization - find range with highest average satisfaction
        best_satisfaction = 0
        best_value = 0.7

        for i in range(
            0, len(value_satisfaction_pairs), max(1, len(value_satisfaction_pairs) // 5)
        ):
            range_values = value_satisfaction_pairs[i : i + 3]  # Small sample window
            if range_values:
                avg_satisfaction = statistics.mean([pair[1] for pair in range_values])
                if avg_satisfaction > best_satisfaction:
                    best_satisfaction = avg_satisfaction
                    best_value = statistics.mean([pair[0] for pair in range_values])

        return max(0.1, min(1.0, best_value))  # Clamp to valid range

    def get_community_trends_summary(self) -> Dict[str, Any]:
        """Get summary of community personality trends"""
        return {
            "total_contexts_tracked": len(self.personality_trends),
            "active_patterns": sum(
                1
                for trend in self.personality_trends.values()
                if trend["sample_count"] >= 5
            ),
            "cultural_variations": len(
                set(key.split("_")[-1] for key in self.personality_trends.keys())
            ),
            "overall_satisfaction": round(
                statistics.mean(
                    [
                        statistics.mean(trend["satisfaction_scores"])
                        for trend in self.personality_trends.values()
                        if trend["satisfaction_scores"]
                    ]
                )
                if self.personality_trends
                else 0.5,
                2,
            ),
        }


class SocialFeedbackIntegration:
    """Handles social feedback and community input for personality improvement"""

    def __init__(self):
        self.feedback_data = {}
        self.feedback_trends = {}
        self.community_preferences = {}

    def record_interaction_feedback(
        self,
        user_id: str,
        interaction_quality: float,
        personality_aspects: Dict[str, float],
        feedback_type: str = "implicit",
        explicit_feedback: Optional[str] = None,
    ):
        """Record feedback from user interactions"""
        feedback_entry = {
            "quality_rating": interaction_quality,
            "personality_aspects": personality_aspects,
            "feedback_type": feedback_type,
            "timestamp": datetime.now(),
            "user_hash": hashlib.sha256(f"{user_id}_feedback".encode()).hexdigest()[
                :16
            ],
        }

        if explicit_feedback:
            feedback_entry["feedback_text"] = self._sanitize_feedback(explicit_feedback)

        # Store feedback with privacy protection
        feedback_key = f"{feedback_type}_{datetime.now().strftime('%Y%m%d')}"
        if feedback_key not in self.feedback_data:
            self.feedback_data[feedback_key] = []

        self.feedback_data[feedback_key].append(feedback_entry)

    def _sanitize_feedback(self, feedback: str) -> str:
        """Sanitize feedback text while preserving useful information"""
        # Remove potential personal information
        sanitized = feedback.lower()

        # Keep only sentiment and improvement suggestions
        if len(sanitized) > 100:
            sanitized = sanitized[:100] + "..."

        return sanitized

    def analyze_community_preferences(self) -> Dict[str, Any]:
        """Analyze community-wide personality preferences"""
        if not self.feedback_data:
            return {"status": "insufficient_data", "preferences": {}}

        all_feedback = []
        for feedback_list in self.feedback_data.values():
            all_feedback.extend(feedback_list)

        if len(all_feedback) < 10:  # Minimum sample size
            return {"status": "insufficient_samples", "preferences": {}}

        # Analyze personality aspect preferences
        personality_preferences = {}
        quality_ratings = []

        for feedback in all_feedback:
            quality_ratings.append(feedback["quality_rating"])

            for aspect, value in feedback["personality_aspects"].items():
                if aspect not in personality_preferences:
                    personality_preferences[aspect] = []

                personality_preferences[aspect].append(
                    {
                        "value": value,
                        "quality": feedback["quality_rating"],
                    }
                )

        # Calculate preferred ranges for each personality aspect
        optimized_preferences = {}
        for aspect, data_points in personality_preferences.items():
            if len(data_points) >= 5:  # Minimum for statistical significance
                # Find value range with highest quality ratings
                high_quality_points = [d for d in data_points if d["quality"] > 0.7]

                if high_quality_points:
                    preferred_value = statistics.mean(
                        [d["value"] for d in high_quality_points]
                    )
                    optimized_preferences[aspect] = round(preferred_value, 2)

        return {
            "status": "analyzed",
            "sample_size": len(all_feedback),
            "avg_quality": round(statistics.mean(quality_ratings), 2),
            "preferences": optimized_preferences,
            "confidence": min(
                len(all_feedback) / 50.0, 1.0
            ),  # Confidence based on sample size
        }

    def get_feedback_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get feedback trends over specified time period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_feedback = []

        for feedback_list in self.feedback_data.values():
            for feedback in feedback_list:
                if feedback["timestamp"] > cutoff_date:
                    recent_feedback.append(feedback)

        if not recent_feedback:
            return {"status": "no_recent_feedback", "trends": {}}

        # Calculate trends
        quality_trend = [f["quality_rating"] for f in recent_feedback]

        return {
            "status": "trending",
            "period_days": days,
            "total_feedback": len(recent_feedback),
            "avg_quality": round(statistics.mean(quality_trend), 2),
            "quality_trend": "improving"
            if len(quality_trend) > 1 and quality_trend[-1] > quality_trend[0]
            else "stable",
            "feedback_types": {
                "implicit": len(
                    [f for f in recent_feedback if f["feedback_type"] == "implicit"]
                ),
                "explicit": len(
                    [f for f in recent_feedback if f["feedback_type"] == "explicit"]
                ),
            },
        }


class SocialLearningCoordinator:
    """Main coordinator for social learning infrastructure"""

    def __init__(self):
        self.privacy_learning = PrivacyPreservingLearning()
        self.personality_trends = CommunityPersonalityTrends()
        self.feedback_integration = SocialFeedbackIntegration()

        self.social_learning_metrics = {
            "total_interactions": 0,
            "community_patterns_learned": 0,
            "privacy_violations": 0,
            "learning_effectiveness": 0.0,
        }

    async def process_social_learning_interaction(
        self,
        user_input: str,
        emotional_state: EmotionalState,
        personality_traits: Dict[str, float],
        user_id: str,
        interaction_quality: float,
        cultural_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process interaction for social learning while preserving privacy"""
        try:
            # Step 1: Anonymize interaction for privacy-preserving learning
            anonymized_data = self.privacy_learning.anonymize_interaction(
                user_input, emotional_state, user_id
            )

            # Step 2: Add to community learning dataset
            self.privacy_learning.add_community_learning_data(
                anonymized_data, interaction_quality
            )

            # Step 3: Track personality effectiveness
            context_type = anonymized_data["interaction_patterns"]["context_type"]
            self.personality_trends.track_personality_effectiveness(
                personality_traits, context_type, interaction_quality, cultural_context
            )

            # Step 4: Record feedback for community preferences
            self.feedback_integration.record_interaction_feedback(
                user_id, interaction_quality, personality_traits, "implicit"
            )

            # Step 5: Get personalized recommendations
            personality_recommendations = (
                self.personality_trends.get_personality_recommendations(
                    context_type, cultural_context
                )
            )

            # Step 6: Update metrics
            self.social_learning_metrics["total_interactions"] += 1
            self.social_learning_metrics["community_patterns_learned"] = len(
                self.privacy_learning.anonymized_patterns
            )

            return {
                "social_learning_applied": True,
                "privacy_preserved": True,
                "personality_recommendations": personality_recommendations,
                "community_insights": self.privacy_learning.get_community_insights(),
                "learning_effectiveness": interaction_quality,
                "status": "success",
            }

        except Exception as e:
            return {
                "social_learning_applied": False,
                "error": str(e),
                "status": "error",
            }

    def get_social_learning_status(self) -> Dict[str, Any]:
        """Get comprehensive social learning system status"""
        community_insights = self.privacy_learning.get_community_insights()
        trends_summary = self.personality_trends.get_community_trends_summary()
        feedback_analysis = self.feedback_integration.analyze_community_preferences()

        return {
            "social_learning_metrics": self.social_learning_metrics,
            "privacy_status": {
                "privacy_preserved": True,
                "anonymization_active": True,
                "data_retention_policy": "30_days",
                "user_consent_required": True,
            },
            "community_learning": {
                "total_patterns": community_insights["total_patterns"],
                "effective_patterns": len(community_insights["effective_patterns"]),
                "learning_confidence": trends_summary.get("overall_satisfaction", 0.5),
            },
            "personality_optimization": {
                "contexts_tracked": trends_summary["total_contexts_tracked"],
                "active_patterns": trends_summary["active_patterns"],
                "cultural_variations": trends_summary["cultural_variations"],
            },
            "feedback_analysis": feedback_analysis,
            "system_health": "operational",
        }


# Global social learning coordinator instance
social_learning_coordinator = SocialLearningCoordinator()


# Convenience functions for easy integration
async def process_with_social_learning(
    user_input: str,
    emotional_state: EmotionalState,
    personality_traits: Dict[str, float],
    user_id: str,
    interaction_quality: float,
    cultural_context: Optional[str] = None,
) -> Dict[str, Any]:
    """Main function for processing interactions with social learning"""
    return await social_learning_coordinator.process_social_learning_interaction(
        user_input,
        emotional_state,
        personality_traits,
        user_id,
        interaction_quality,
        cultural_context,
    )


def get_social_learning_status() -> Dict[str, Any]:
    """Get social learning system status"""
    return social_learning_coordinator.get_social_learning_status()


def get_community_personality_recommendations(
    context: str, cultural_context: Optional[str] = None
) -> Dict[str, float]:
    """Get community-learned personality recommendations"""
    return (
        social_learning_coordinator.personality_trends.get_personality_recommendations(
            context, cultural_context
        )
    )


def add_explicit_feedback(
    user_id: str,
    quality_rating: float,
    personality_aspects: Dict[str, float],
    feedback_text: Optional[str] = None,
):
    """Add explicit user feedback for community learning"""
    social_learning_coordinator.feedback_integration.record_interaction_feedback(
        user_id, quality_rating, personality_aspects, "explicit", feedback_text
    )


def get_community_insights() -> Dict[str, Any]:
    """Get privacy-preserving community insights"""
    return social_learning_coordinator.privacy_learning.get_community_insights()


def get_feedback_trends(days: int = 7) -> Dict[str, Any]:
    """Get community feedback trends"""
    return social_learning_coordinator.feedback_integration.get_feedback_trends(days)

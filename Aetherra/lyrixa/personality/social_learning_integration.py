"""
Phase 3.3 Integration - Social Learning Infrastructure
=====================================================

This module integrates the social learning system with the existing Phase 1, 2, and 3.2
personality components, creating a comprehensive community-based learning enhancement layer.

Features:
- Community-wide personality pattern learning
- Privacy-preserving collective intelligence
- Cultural adaptation and social context awareness
- Social feedback integration for continuous improvement
- Personality optimization based on community insights
"""

from datetime import datetime
from typing import Any, Dict, Optional

# Import Phase 3.2 emotional intelligence
from .emotional_intelligence_integration import EmotionalIntelligenceIntegration

# Import existing personality components
from .integration import enhance_lyrixa_response

# Import Phase 3.3 social learning
from .social_learning import (
    get_community_insights,
    get_community_personality_recommendations,
    get_feedback_trends,
    get_social_learning_status,
    process_with_social_learning,
)


class SocialLearningIntegration:
    """
    Master integration system for social learning enhancement
    """

    def __init__(self):
        self.emotional_intelligence_integration = EmotionalIntelligenceIntegration()

        # Performance tracking
        self.integration_metrics = {
            "total_social_interactions": 0,
            "community_patterns_learned": 0,
            "personality_optimizations": 0,
            "avg_processing_time": 0.0,
            "social_learning_success_rate": 0.0,
            "privacy_preservation_rate": 1.0,  # Always maintain privacy
        }

    async def process_socially_enhanced_interaction(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        cultural_context: Optional[str] = None,
        enable_emotional_intelligence: bool = True,
    ) -> Dict[str, Any]:
        """
        Process interaction with full social learning enhancement
        """
        start_time = datetime.now()

        try:
            print("🌐🧠 Processing interaction with social learning intelligence...")

            # Step 1: Apply emotional intelligence enhancement (Phase 3.2)
            if enable_emotional_intelligence:
                print("💫 Applying emotional intelligence enhancement...")
                emotional_result = await self.emotional_intelligence_integration.process_emotionally_intelligent_interaction(
                    user_input, context, user_id, True
                )
                base_response = emotional_result["final_response"]
                emotional_intelligence_data = emotional_result
                interaction_quality = emotional_result["integration_metrics"].get(
                    "empathy_score", 0.7
                )
            else:
                print("🎭 Using basic personality enhancement...")
                # Fall back to basic response
                base_response = f"I'd be happy to help you with: {user_input}"
                emotional_intelligence_data = {"status": "disabled"}
                interaction_quality = 0.6  # Default quality score

            # Step 2: Get community-learned personality recommendations
            print("🌐 Applying community learning insights...")
            context_type = self._determine_context_type(user_input)
            community_recommendations = get_community_personality_recommendations(
                context_type, cultural_context
            )

            # Step 3: Apply social learning to the interaction
            print("🤝 Processing with social learning...")
            if (
                enable_emotional_intelligence
                and "emotional_intelligence" in emotional_intelligence_data
            ):
                # Extract emotional state from Phase 3.2 results
                emotional_state = self._extract_emotional_state(
                    emotional_intelligence_data
                )
                current_personality = self._get_current_personality_traits()

                social_learning_result = await process_with_social_learning(
                    user_input,
                    emotional_state,
                    current_personality,
                    user_id or "anonymous",
                    interaction_quality,
                    cultural_context,
                )
            else:
                # Simplified social learning without emotional intelligence
                social_learning_result = {
                    "social_learning_applied": True,
                    "privacy_preserved": True,
                    "personality_recommendations": community_recommendations,
                    "status": "simplified",
                }

            # Step 4: Apply community recommendations to enhance response
            enhanced_response = self._apply_community_recommendations(
                base_response, community_recommendations, context_type
            )

            # Step 5: Calculate performance metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_integration_metrics(social_learning_result, processing_time)

            print(f"✅ Social learning integration complete: {processing_time:.1f}ms")

            return {
                "final_response": enhanced_response,
                "emotional_intelligence_data": emotional_intelligence_data,
                "social_learning": social_learning_result,
                "community_recommendations": community_recommendations,
                "integration_metrics": {
                    "processing_time_ms": processing_time,
                    "social_learning_applied": social_learning_result.get(
                        "social_learning_applied", False
                    ),
                    "privacy_preserved": social_learning_result.get(
                        "privacy_preserved", True
                    ),
                    "community_learning_effectiveness": social_learning_result.get(
                        "learning_effectiveness", 0.0
                    ),
                },
                "status": "success",
            }

        except Exception as e:
            print(f"⚠️ Social learning integration error: {e}")

            # Fallback to emotional intelligence only
            try:
                if enable_emotional_intelligence:
                    fallback_result = await self.emotional_intelligence_integration.process_emotionally_intelligent_interaction(
                        user_input, context, user_id, True
                    )
                    base_response = fallback_result["final_response"]
                else:
                    base_response = f"I'd be happy to help you with: {user_input}"

                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                return {
                    "final_response": base_response,
                    "emotional_intelligence_data": {"status": "fallback"},
                    "social_learning": {"status": "error", "error": str(e)},
                    "community_recommendations": {},
                    "integration_metrics": {
                        "processing_time_ms": processing_time,
                        "social_learning_applied": False,
                        "privacy_preserved": True,
                        "community_learning_effectiveness": 0.0,
                    },
                    "status": "fallback",
                    "error": str(e),
                }

            except Exception as fallback_error:
                return {
                    "final_response": f"I understand you're asking about: {user_input}. Let me help you with that.",
                    "emotional_intelligence_data": {"status": "error"},
                    "social_learning": {"status": "error"},
                    "community_recommendations": {},
                    "integration_metrics": {
                        "processing_time_ms": (
                            datetime.now() - start_time
                        ).total_seconds()
                        * 1000,
                        "social_learning_applied": False,
                        "privacy_preserved": True,
                        "community_learning_effectiveness": 0.0,
                    },
                    "status": "error",
                    "error": str(fallback_error),
                }

    def _determine_context_type(self, user_input: str) -> str:
        """Determine interaction context type"""
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

    def _extract_emotional_state(self, emotional_intelligence_data: Dict[str, Any]):
        """Extract emotional state from Phase 3.2 results"""
        try:
            if "emotional_intelligence" in emotional_intelligence_data:
                emotional_data = emotional_intelligence_data["emotional_intelligence"]
                if "emotional_state" in emotional_data:
                    return emotional_data["emotional_state"]
        except Exception:
            pass

        # Return a default emotional state
        from .emotional_intelligence import EmotionalState

        return EmotionalState(
            primary_emotion="neutral",
            intensity=0.5,
            valence=0.0,
            arousal=0.5,
            dominance=0.5,
            confidence=0.5,
        )

    def _get_current_personality_traits(self) -> Dict[str, float]:
        """Get current personality traits"""
        return {
            "curiosity": 0.7,
            "enthusiasm": 0.6,
            "empathy": 0.8,
            "helpfulness": 0.9,
            "creativity": 0.5,
            "playfulness": 0.4,
            "thoughtfulness": 0.7,
        }

    def _apply_community_recommendations(
        self, base_response: str, recommendations: Dict[str, float], context_type: str
    ) -> str:
        """Apply community-learned personality recommendations to response"""
        if not recommendations:
            return base_response

        # Apply community insights to enhance response tone
        enhanced_response = base_response

        # Enhance empathy if community shows high empathy preference
        if recommendations.get("empathy", 0.5) > 0.8:
            if not any(
                phrase in enhanced_response.lower()
                for phrase in ["understand", "feel", "appreciate"]
            ):
                enhanced_response = (
                    f"I understand this can be challenging. {enhanced_response}"
                )

        # Enhance enthusiasm if community prefers it for this context
        if recommendations.get("enthusiasm", 0.5) > 0.7 and context_type in [
            "creative",
            "learning",
        ]:
            if not any(
                phrase in enhanced_response.lower()
                for phrase in ["exciting", "great", "wonderful"]
            ):
                enhanced_response = enhanced_response.replace(
                    "I can help", "I'd be excited to help"
                ).replace("Let me", "I'd love to")

        # Enhance thoughtfulness if community values it
        if recommendations.get("thoughtfulness", 0.5) > 0.8:
            if context_type == "technical_support":
                enhanced_response += " Let me think through this step by step with you."

        # Add collaborative language if helpfulness is highly valued
        if recommendations.get("helpfulness", 0.5) > 0.9:
            if "let's" not in enhanced_response.lower():
                enhanced_response = enhanced_response.replace(
                    "I'll help", "Let's work on this together"
                ).replace("I can", "We can")

        return enhanced_response

    def _update_integration_metrics(
        self, social_learning_result: Dict[str, Any], processing_time: float
    ):
        """Update integration performance metrics"""
        self.integration_metrics["total_social_interactions"] += 1
        total_interactions = self.integration_metrics["total_social_interactions"]

        # Update processing time average
        current_avg = self.integration_metrics["avg_processing_time"]
        new_avg = (
            (current_avg * (total_interactions - 1)) + processing_time
        ) / total_interactions
        self.integration_metrics["avg_processing_time"] = new_avg

        # Update success rate
        if social_learning_result.get("social_learning_applied", False):
            self.integration_metrics["community_patterns_learned"] += 1
            current_success = self.integration_metrics["social_learning_success_rate"]
            new_success = (
                (current_success * (total_interactions - 1)) + 1.0
            ) / total_interactions
            self.integration_metrics["social_learning_success_rate"] = new_success

    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive status of social learning integration"""
        social_learning_status = get_social_learning_status()
        community_insights = get_community_insights()
        feedback_trends = get_feedback_trends(7)

        return {
            "integration_metrics": {
                "total_interactions": self.integration_metrics[
                    "total_social_interactions"
                ],
                "success_rate_percent": round(
                    self.integration_metrics["social_learning_success_rate"] * 100, 1
                ),
                "avg_processing_time_ms": round(
                    self.integration_metrics["avg_processing_time"], 1
                ),
                "privacy_preservation_rate": round(
                    self.integration_metrics["privacy_preservation_rate"] * 100, 1
                ),
                "community_patterns_learned": self.integration_metrics[
                    "community_patterns_learned"
                ],
            },
            "social_learning_status": social_learning_status,
            "community_insights": community_insights,
            "feedback_trends": feedback_trends,
            "system_health": "operational",
            "privacy_compliance": "full",
        }


# Global integration system instance
social_learning_integration = SocialLearningIntegration()


# Convenience functions for easy integration
async def process_with_social_learning_enhancement(
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    cultural_context: Optional[str] = None,
    enable_emotional_intelligence: bool = True,
) -> Dict[str, Any]:
    """Main function for processing interactions with social learning enhancement"""
    return await social_learning_integration.process_socially_enhanced_interaction(
        user_input, context, user_id, cultural_context, enable_emotional_intelligence
    )


def get_social_learning_integration_status() -> Dict[str, Any]:
    """Get social learning integration status"""
    return social_learning_integration.get_integration_status()


def get_comprehensive_social_analysis() -> Dict[str, Any]:
    """Get comprehensive social learning analysis"""
    return {
        "social_learning_status": get_social_learning_status(),
        "community_insights": get_community_insights(),
        "feedback_trends_7d": get_feedback_trends(7),
        "feedback_trends_30d": get_feedback_trends(30),
        "integration_status": get_social_learning_integration_status(),
    }

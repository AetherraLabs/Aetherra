"""
Phase 2 Integration - Advanced Personality Enhancement
=====================================================

This module integrates all Phase 2 components (Critique Agent, Reflection System,
and Memory Learning) with the existing Phase 1 personality system to create a
comprehensive self-improving AI personality system.

Features:
- Seamless integration of all personality enhancement systems
- Coordinated feedback loops between all components
- Performance monitoring and optimization
- Real-time personality adaptation
- Comprehensive logging and analytics
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

# Import Phase 2 components
from .critique_agent import analyze_and_improve_response, get_critique_agent_status

# Import Phase 1 components
from .emotion_detector import detect_user_emotion
from .integration import enhance_lyrixa_response
from .memory_learning import (
    get_learning_system_status,
    get_style_recommendation,
    learn_from_response_effectiveness,
)
from .reflection_system import (
    get_reflection_system_status,
    process_interaction_for_reflection,
)


class AdvancedPersonalityIntegration:
    """
    Master integration system for all personality enhancement components
    """

    def __init__(self, memory_system=None):
        self.memory_system = memory_system

        # Integration metrics
        self.integration_metrics = {
            "total_interactions_processed": 0,
            "average_quality_improvement": 0.0,
            "personality_adaptations_made": 0,
            "learning_insights_generated": 0,
            "system_performance_score": 0.0,
        }

        # System health monitoring
        self.system_health = {
            "phase1_status": "active",
            "critique_agent_status": "active",
            "reflection_system_status": "active",
            "memory_learning_status": "active",
            "integration_health": 1.0,
            "last_health_check": datetime.now().isoformat(),
        }

        # Performance tracking
        self.performance_history = []
        self.quality_trends = []

        print("🧠 Advanced Personality Integration System initialized!")
        print("✨ All Phase 2 components are ready for enhanced AI consciousness!")

    async def process_complete_interaction(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a complete interaction through all personality enhancement systems

        Args:
            user_input: What the user said
            context: Additional context about the interaction
            user_id: Identifier for the user (for learning)

        Returns:
            Enhanced response with comprehensive analysis and improvements
        """
        if context is None:
            context = {}

        start_time = datetime.now()
        self.integration_metrics["total_interactions_processed"] += 1

        print(
            f"\n🧠 Processing interaction #{self.integration_metrics['total_interactions_processed']}..."
        )

        try:
            # Step 1: Get style recommendation from memory learning
            print("📚 Getting style recommendations from memory...")
            style_recommendation = await get_style_recommendation(
                user_input, context, user_id
            )

            # Step 2: Generate initial response with Phase 1 personality system
            print("🎭 Generating response with personality enhancement...")
            # For integration, we need a basic response first, then enhance it
            basic_response = f"I understand you're asking about: {user_input}. Let me help you with that."
            initial_response_data = await enhance_lyrixa_response(
                basic_response, user_input, context
            )
            initial_response = initial_response_data["text"]

            # Step 3: Apply style recommendations to enhance the response
            enhanced_response = await self._apply_style_recommendations(
                initial_response, style_recommendation, user_input, context
            )

            # Step 4: Critique the response for quality assessment
            print("🔍 Analyzing response quality...")
            critique_analysis = await analyze_and_improve_response(
                user_input, enhanced_response, context, apply_improvements=True
            )

            # Step 5: Process through reflection system
            print("🤔 Processing through reflection system...")
            reflection_result = await process_interaction_for_reflection(
                user_input, enhanced_response, context, critique_analysis
            )

            # Step 6: Learn from the interaction
            print("📖 Learning from interaction effectiveness...")
            effectiveness_score = critique_analysis["basic_critique"]["overall_score"]
            style_data = {
                "styles_detected": style_recommendation.get("style_adjustments", {}),
                "dominant_style": style_recommendation.get(
                    "recommended_style", "neutral"
                ),
                "trait_expressions": critique_analysis.get("enhanced_analysis", {})
                .get("personality_consistency", {})
                .get("trait_expressions", {}),
            }

            learning_result = await learn_from_response_effectiveness(
                user_input,
                enhanced_response,
                effectiveness_score,
                style_data,
                context,
                user_id,
            )

            # Step 7: Generate final integration result
            final_result = await self._compile_integration_result(
                user_input,
                enhanced_response,
                style_recommendation,
                critique_analysis,
                reflection_result,
                learning_result,
                start_time,
            )

            # Step 8: Update metrics and health
            await self._update_integration_metrics(final_result)

            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"✨ Integration complete! Processing time: {processing_time:.2f}s")
            print(f"🎯 Quality score: {effectiveness_score:.2f}/1.0")

            return final_result

        except Exception as e:
            print(f"⚠️ Error in integration processing: {e}")
            # Return fallback response
            basic_fallback = f"I understand you're asking about: {user_input}. Let me help you with that."
            fallback_data = await enhance_lyrixa_response(
                basic_fallback, user_input, context
            )
            return {
                "enhanced_response": fallback_data["text"],
                "processing_error": str(e),
                "fallback_mode": True,
            }

    async def _apply_style_recommendations(
        self,
        initial_response: str,
        style_recommendation: Dict[str, Any],
        user_input: str,
        context: Dict[str, Any],
    ) -> str:
        """Apply style recommendations to enhance the initial response"""

        enhanced_response = initial_response
        recommended_style = style_recommendation.get("recommended_style", "neutral")
        confidence = style_recommendation.get("confidence", 0.5)
        adjustments = style_recommendation.get("style_adjustments", {})

        # Only apply recommendations if confidence is high enough
        if confidence < 0.6:
            return enhanced_response

        print(f"🎨 Applying {recommended_style} style (confidence: {confidence:.2f})")

        # Apply style-specific enhancements
        if recommended_style == "empathetic" and confidence > 0.7:
            enhanced_response = self._add_empathetic_elements(
                enhanced_response, user_input
            )
        elif recommended_style == "enthusiastic" and confidence > 0.7:
            enhanced_response = self._add_enthusiastic_elements(enhanced_response)
        elif recommended_style == "technical" and confidence > 0.7:
            enhanced_response = self._add_technical_precision(enhanced_response)
        elif recommended_style == "casual" and confidence > 0.7:
            enhanced_response = self._add_casual_elements(enhanced_response)

        # Apply specific pattern adjustments
        for adjustment_type, adjustment_value in adjustments.items():
            if adjustment_value > 0.5:
                enhanced_response = self._apply_pattern_adjustment(
                    enhanced_response, adjustment_type, adjustment_value
                )

        return enhanced_response

    def _add_empathetic_elements(self, response: str, user_input: str) -> str:
        """Add empathetic elements to the response"""

        # Detect user emotion for empathetic response
        user_emotion = detect_user_emotion(user_input)
        primary_emotion = user_emotion.get("primary_emotion", "neutral")

        empathetic_starters = {
            "frustration": "I understand how frustrating that can be. ",
            "confusion": "I can see why that might be confusing. ",
            "excitement": "I can feel your excitement about this! ",
            "sadness": "I'm sorry you're going through this. ",
            "curiosity": "I love your curiosity about this topic! ",
        }

        if primary_emotion in empathetic_starters and not response.startswith(
            empathetic_starters[primary_emotion]
        ):
            response = empathetic_starters[primary_emotion] + response

        # Add empathetic language patterns
        if "let me help" not in response.lower():
            if response.endswith("."):
                response = response[:-1] + ". Let me help you with this."
            else:
                response += " Let me help you with this."

        return response

    def _add_enthusiastic_elements(self, response: str) -> str:
        """Add enthusiastic elements to the response"""

        # Add enthusiastic markers if not already present
        if not any(
            marker in response
            for marker in ["!", "exciting", "amazing", "fantastic", "love"]
        ):
            # Convert some periods to exclamation marks
            if ". " in response:
                parts = response.split(". ")
                if len(parts) > 1:
                    parts[0] += "!"
                    response = " ".join(parts)

        # Add enthusiastic language
        enthusiasm_boosters = [
            ("This is", "This is really"),
            ("That's", "That's absolutely"),
            ("Good", "Excellent"),
            ("Nice", "Fantastic"),
        ]

        for original, enhanced in enthusiasm_boosters:
            if original in response:
                response = response.replace(original, enhanced, 1)
                break

        return response

    def _add_technical_precision(self, response: str) -> str:
        """Add technical precision to the response"""

        # Add technical connectors
        technical_improvements = [
            ("because", "specifically because"),
            ("when you", "when you implement"),
            ("this will", "this approach will"),
            ("you can", "you can systematically"),
        ]

        for original, enhanced in technical_improvements:
            if original in response.lower():
                response = response.replace(original, enhanced, 1)
                break

        return response

    def _add_casual_elements(self, response: str) -> str:
        """Add casual elements to the response"""

        # Make language more casual
        casual_replacements = [
            ("you are", "you're"),
            ("I am", "I'm"),
            ("cannot", "can't"),
            ("do not", "don't"),
            ("Additionally", "Also"),
            ("Therefore", "So"),
        ]

        for formal, casual in casual_replacements:
            response = response.replace(formal, casual)

        return response

    def _apply_pattern_adjustment(
        self, response: str, adjustment_type: str, adjustment_value: float
    ) -> str:
        """Apply specific pattern adjustments"""

        if adjustment_type == "question_count" and adjustment_value > 0.5:
            # Add a follow-up question if none exists
            if "?" not in response:
                questions = [
                    " What do you think about that?",
                    " How does that sound to you?",
                    " Would you like me to explain more?",
                    " Does that help clarify things?",
                ]
                import random

                response += random.choice(questions)

        elif adjustment_type == "personal_pronouns" and adjustment_value > 0.5:
            # Add more personal touch
            if not any(pronoun in response.lower() for pronoun in ["i", "me", "my"]):
                personal_additions = [
                    "In my experience, ",
                    "I find that ",
                    "I think ",
                    "From my perspective, ",
                ]
                import random

                response = random.choice(personal_additions) + response.lower()

        return response

    async def _compile_integration_result(
        self,
        user_input: str,
        enhanced_response: str,
        style_recommendation: Dict[str, Any],
        critique_analysis: Dict[str, Any],
        reflection_result: Dict[str, Any],
        learning_result: Dict[str, Any],
        start_time: datetime,
    ) -> Dict[str, Any]:
        """Compile comprehensive integration result"""

        processing_time = (datetime.now() - start_time).total_seconds()

        # Calculate overall improvement score
        original_quality = critique_analysis.get("basic_critique", {}).get(
            "overall_score", 0.5
        )
        enhancement_score = critique_analysis.get("enhanced_analysis", {}).get(
            "overall_enhancement_score", 0.5
        )

        improvement_score = (original_quality + enhancement_score) / 2

        result = {
            # Main output
            "enhanced_response": enhanced_response,
            "user_input": user_input,
            # Processing information
            "processing_time_seconds": processing_time,
            "timestamp": datetime.now().isoformat(),
            # Quality metrics
            "quality_metrics": {
                "overall_score": original_quality,
                "enhancement_score": enhancement_score,
                "improvement_score": improvement_score,
                "style_confidence": style_recommendation.get("confidence", 0.5),
            },
            # System analysis
            "style_analysis": {
                "recommended_style": style_recommendation.get(
                    "recommended_style", "neutral"
                ),
                "style_reasoning": style_recommendation.get("reasoning", []),
                "applied_adjustments": style_recommendation.get(
                    "style_adjustments", {}
                ),
            },
            "critique_summary": {
                "quality_score": original_quality,
                "naturalness_score": critique_analysis.get("basic_critique", {}).get(
                    "naturalness_score", 0.5
                ),
                "engagement_score": critique_analysis.get("basic_critique", {}).get(
                    "engagement_score", 0.5
                ),
                "empathy_score": critique_analysis.get("basic_critique", {}).get(
                    "empathy_score", 0.5
                ),
                "improvements_applied": critique_analysis.get(
                    "improvements_applied", {}
                ),
            },
            "reflection_summary": {
                "reflection_performed": reflection_result.get(
                    "reflection_performed", False
                ),
                "patterns_updated": reflection_result.get("patterns_updated", False),
                "analysis_insights": reflection_result.get("interaction_analysis", {}),
                "reflection_data": reflection_result.get("reflection_result", {}),
            },
            "learning_summary": {
                "patterns_learned": learning_result.get("patterns_learned", 0),
                "preferences_updated": learning_result.get("preferences_updated", 0),
                "memories_stored": learning_result.get("memories_stored", 0),
                "adaptations_identified": learning_result.get(
                    "adaptations_identified", 0
                ),
            },
            # System status
            "system_status": await self._get_system_status(),
            # Integration metadata
            "integration_metadata": {
                "phase": "phase_2",
                "version": "2.0.0",
                "components_active": [
                    "personality_engine",
                    "critique_agent",
                    "reflection_system",
                    "memory_learning",
                ],
                "integration_health": self.system_health["integration_health"],
            },
        }

        return result

    async def _update_integration_metrics(self, result: Dict[str, Any]) -> None:
        """Update integration metrics based on processing result"""

        # Update quality improvement tracking
        improvement_score = result["quality_metrics"]["improvement_score"]
        current_avg = self.integration_metrics["average_quality_improvement"]
        total_interactions = self.integration_metrics["total_interactions_processed"]

        new_avg = (
            (current_avg * (total_interactions - 1)) + improvement_score
        ) / total_interactions
        self.integration_metrics["average_quality_improvement"] = new_avg

        # Track performance
        performance_data = {
            "timestamp": result["timestamp"],
            "processing_time": result["processing_time_seconds"],
            "quality_score": result["quality_metrics"]["overall_score"],
            "improvement_score": improvement_score,
        }

        self.performance_history.append(performance_data)

        # Keep only recent performance data
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-50:]

        # Update quality trends
        self.quality_trends.append(
            {"timestamp": result["timestamp"], "score": improvement_score}
        )

        if len(self.quality_trends) > 50:
            self.quality_trends = self.quality_trends[-25:]

        # Update other metrics
        if result["learning_summary"]["patterns_learned"] > 0:
            self.integration_metrics["learning_insights_generated"] += 1

        if result["reflection_summary"]["reflection_performed"]:
            self.integration_metrics["personality_adaptations_made"] += 1

        # Calculate system performance score
        if len(self.quality_trends) >= 5:
            recent_scores = [item["score"] for item in self.quality_trends[-5:]]
            self.integration_metrics["system_performance_score"] = sum(
                recent_scores
            ) / len(recent_scores)

    async def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""

        # Get status from all subsystems
        critique_status = get_critique_agent_status()
        reflection_status = get_reflection_system_status()
        learning_status = get_learning_system_status()

        # Update system health
        self.system_health.update(
            {
                "critique_agent_status": critique_status.get("agent_status", "unknown"),
                "reflection_system_status": reflection_status.get(
                    "system_status", "unknown"
                ),
                "memory_learning_status": learning_status.get(
                    "system_status", "unknown"
                ),
                "last_health_check": datetime.now().isoformat(),
            }
        )

        # Calculate integration health
        active_systems = sum(
            1
            for status in [
                self.system_health["critique_agent_status"],
                self.system_health["reflection_system_status"],
                self.system_health["memory_learning_status"],
            ]
            if status == "active"
        )

        self.system_health["integration_health"] = active_systems / 3.0

        return {
            "overall_health": self.system_health["integration_health"],
            "subsystem_status": {
                "critique_agent": critique_status,
                "reflection_system": reflection_status,
                "memory_learning": learning_status,
            },
            "integration_metrics": self.integration_metrics,
            "recent_performance": self.performance_history[-5:]
            if self.performance_history
            else [],
        }

    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the entire integration system"""

        status = await self._get_system_status()

        # Add additional insights
        insights = []

        if self.integration_metrics["average_quality_improvement"] > 0.8:
            insights.append("Consistently high-quality response generation")
        elif self.integration_metrics["average_quality_improvement"] < 0.6:
            insights.append("Room for improvement in response quality")

        if len(self.quality_trends) >= 5:
            recent_trend = sum(item["score"] for item in self.quality_trends[-3:]) / 3
            earlier_trend = (
                sum(item["score"] for item in self.quality_trends[-6:-3]) / 3
                if len(self.quality_trends) >= 6
                else recent_trend
            )

            if recent_trend > earlier_trend + 0.05:
                insights.append("Quality improving over time")
            elif recent_trend < earlier_trend - 0.05:
                insights.append("Quality declining - may need adjustment")

        if self.integration_metrics["learning_insights_generated"] > 10:
            insights.append("Strong learning and adaptation capability")

        status["insights"] = insights
        status["recommendations"] = self._generate_system_recommendations()

        return status

    def _generate_system_recommendations(self) -> List[str]:
        """Generate recommendations for system optimization"""

        recommendations = []

        if self.integration_metrics["system_performance_score"] < 0.7:
            recommendations.append(
                "Consider adjusting learning rates for better performance"
            )

        if self.system_health["integration_health"] < 0.8:
            recommendations.append(
                "Check subsystem health - some components may need attention"
            )

        if len(self.performance_history) > 20:
            avg_processing_time = (
                sum(p["processing_time"] for p in self.performance_history[-10:]) / 10
            )
            if avg_processing_time > 2.0:
                recommendations.append(
                    "Processing time is high - consider optimization"
                )

        if self.integration_metrics["learning_insights_generated"] < 5:
            recommendations.append("Increase interaction volume to improve learning")

        return recommendations


# Global advanced integration system
advanced_personality_integration = AdvancedPersonalityIntegration()


async def process_enhanced_interaction(
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main function for processing interactions through the complete Phase 2 system

    Args:
        user_input: What the user said
        context: Additional context
        user_id: User identifier for learning

    Returns:
        Comprehensive enhanced response with full analysis
    """
    return await advanced_personality_integration.process_complete_interaction(
        user_input, context, user_id
    )


async def get_integration_status() -> Dict[str, Any]:
    """Get status of the complete integration system"""
    return await advanced_personality_integration.get_comprehensive_status()


# Phase 2 Quick Enhancement Function
def enhance_response_phase2(
    user_input: str, context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Quick synchronous enhancement using Phase 2 improvements
    (For compatibility with existing systems that need immediate response)
    """
    try:
        # Create a basic response first
        basic_response = f"I'd be happy to help you with that: {user_input}."

        # Apply basic Phase 2 improvements
        user_emotion = detect_user_emotion(user_input)
        primary_emotion = user_emotion.get("primary_emotion", "neutral")

        # Quick empathetic enhancement based on emotion
        if (
            primary_emotion == "frustration"
            and "understand" not in basic_response.lower()
        ):
            enhanced = "I understand how that can be frustrating. " + basic_response
        elif primary_emotion == "excitement" and "!" not in basic_response:
            enhanced = basic_response.replace(".", "!", 1)
        elif primary_emotion == "confusion" and "clarify" not in basic_response.lower():
            enhanced = (
                basic_response + " Let me know if you'd like me to clarify anything!"
            )
        else:
            enhanced = basic_response

        return enhanced

    except Exception as e:
        print(f"⚠️ Phase 2 quick enhancement error: {e}")
        return f"I'd be happy to help you with that: {user_input}."

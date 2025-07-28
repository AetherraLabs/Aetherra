"""
Response Critique Agent - Phase 2 Implementation
===============================================

This module implements an autonomous agent that evaluates Lyrixa's communication
quality and provides feedback for continuous improvement. This agent works in
conjunction with the personality system to create a self-improving AI.

Features:
- Real-time response quality assessment
- Communication pattern analysis
- Adaptive improvement suggestions
- Performance tracking and metrics
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .emotion_detector import detect_user_emotion

# Import Phase 1 personality components
from .personality_engine import lyrixa_personality
from .response_critic import critique_response


class ResponseCritiqueAgent:
    """
    Autonomous agent that continuously evaluates and improves Lyrixa's responses
    """

    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.critique_history = []
        self.improvement_metrics = {
            "total_responses_analyzed": 0,
            "average_quality_score": 0.0,
            "quality_trend": [],
            "common_issues": {},
            "improvement_suggestions_applied": 0,
            "personality_adaptations_made": 0,
        }

        # Quality thresholds for different aspects
        self.quality_thresholds = {
            "overall_score": 0.7,
            "naturalness_score": 0.6,
            "engagement_score": 0.5,
            "empathy_score": 0.6,
            "enthusiasm_score": 0.5,
        }

        # Learning parameters
        self.learning_rate = 0.1
        self.adaptation_threshold = 3  # Number of similar issues before adapting

    async def analyze_response_quality(
        self,
        user_input: str,
        lyrixa_response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single response with improvement recommendations

        Args:
            user_input: What the user said
            lyrixa_response: Lyrixa's response
            context: Additional context about the interaction

        Returns:
            Detailed analysis with improvement suggestions
        """
        if context is None:
            context = {}

        # Step 1: Basic quality critique using Phase 1 system
        basic_critique = critique_response(lyrixa_response, user_input, context)

        # Step 2: Enhanced analysis by this agent
        enhanced_analysis = await self._perform_enhanced_analysis(
            user_input, lyrixa_response, basic_critique, context
        )

        # Step 3: Generate specific improvement recommendations
        improvements = await self._generate_improvement_recommendations(
            basic_critique, enhanced_analysis, context
        )

        # Step 4: Update metrics and history
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "lyrixa_response": lyrixa_response,
            "basic_critique": basic_critique,
            "enhanced_analysis": enhanced_analysis,
            "improvement_recommendations": improvements,
            "context": context,
        }

        await self._update_metrics(analysis_result)
        self.critique_history.append(analysis_result)

        # Keep only recent history
        if len(self.critique_history) > 100:
            self.critique_history = self.critique_history[-50:]

        return analysis_result

    async def _perform_enhanced_analysis(
        self,
        user_input: str,
        response: str,
        basic_critique: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform enhanced analysis beyond basic critique
        """
        # Analyze conversation flow
        flow_analysis = self._analyze_conversation_flow(user_input, response, context)

        # Analyze personality consistency
        personality_analysis = self._analyze_personality_consistency(response, context)

        # Analyze contextual appropriateness
        context_analysis = self._analyze_contextual_appropriateness(
            user_input, response, context
        )

        # Analyze learning opportunities
        learning_analysis = self._analyze_learning_opportunities(
            user_input, response, basic_critique
        )

        return {
            "conversation_flow": flow_analysis,
            "personality_consistency": personality_analysis,
            "contextual_appropriateness": context_analysis,
            "learning_opportunities": learning_analysis,
            "overall_enhancement_score": self._calculate_enhancement_score(
                flow_analysis, personality_analysis, context_analysis
            ),
        }

    def _analyze_conversation_flow(
        self, user_input: str, response: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze how well the response maintains conversation flow"""

        # Check for conversation continuity
        has_follow_up = "?" in response or any(
            phrase in response.lower()
            for phrase in [
                "what do you think",
                "how does that sound",
                "would you like",
                "let me know",
                "feel free",
                "anything else",
            ]
        )

        # Check for acknowledgment of user input
        acknowledges_user = any(
            phrase in response.lower()
            for phrase in [
                "i understand",
                "i see",
                "that makes sense",
                "good point",
                "interesting",
                "i hear you",
                "you're right",
            ]
        )

        # Check for natural transitions
        has_transitions = any(
            phrase in response.lower()
            for phrase in [
                "also",
                "additionally",
                "speaking of",
                "by the way",
                "on that note",
                "similarly",
                "meanwhile",
            ]
        )

        flow_score = (
            (0.4 if has_follow_up else 0)
            + (0.4 if acknowledges_user else 0)
            + (0.2 if has_transitions else 0)
        )

        return {
            "flow_score": flow_score,
            "has_follow_up": has_follow_up,
            "acknowledges_user": acknowledges_user,
            "has_transitions": has_transitions,
            "suggestions": self._generate_flow_suggestions(
                has_follow_up, acknowledges_user, has_transitions
            ),
        }

    def _analyze_personality_consistency(
        self, response: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze consistency with established personality traits"""

        current_traits = lyrixa_personality.get_personality_summary()

        # Check for trait expression in response
        trait_expressions = {
            "curiosity": any(
                word in response.lower()
                for word in ["curious", "wonder", "interesting", "explore", "discover"]
            ),
            "empathy": any(
                word in response.lower()
                for word in ["understand", "feel", "sorry", "challenging", "difficult"]
            ),
            "enthusiasm": any(
                word in response.lower()
                for word in ["exciting", "great", "amazing", "love", "fantastic"]
            ),
            "helpfulness": any(
                word in response.lower()
                for word in ["help", "assist", "support", "guide", "show you"]
            ),
        }

        # Calculate consistency score
        active_traits = current_traits.get("active_traits", [])
        consistency_score = 0.0

        if active_traits:
            expressed_traits = sum(
                1 for trait in active_traits if trait_expressions.get(trait, False)
            )
            consistency_score = expressed_traits / len(active_traits)

        return {
            "consistency_score": consistency_score,
            "trait_expressions": trait_expressions,
            "active_traits": active_traits,
            "missing_traits": [
                trait
                for trait in active_traits
                if not trait_expressions.get(trait, False)
            ],
        }

    def _analyze_contextual_appropriateness(
        self, user_input: str, response: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze if response is appropriate for the context"""

        # Detect user emotional state
        user_emotion = detect_user_emotion(user_input)

        # Check emotional alignment
        emotional_alignment = self._check_emotional_alignment(user_emotion, response)

        # Check response length appropriateness
        length_appropriateness = self._check_length_appropriateness(
            user_input, response, context
        )

        # Check technical level matching
        technical_matching = self._check_technical_level_matching(user_input, response)

        appropriateness_score = (
            emotional_alignment["score"] * 0.4
            + length_appropriateness["score"] * 0.3
            + technical_matching["score"] * 0.3
        )

        return {
            "appropriateness_score": appropriateness_score,
            "emotional_alignment": emotional_alignment,
            "length_appropriateness": length_appropriateness,
            "technical_matching": technical_matching,
            "user_emotion_detected": user_emotion["primary_emotion"],
        }

    def _check_emotional_alignment(
        self, user_emotion: Dict[str, Any], response: str
    ) -> Dict[str, Any]:
        """Check if response emotion matches user's emotional state"""

        primary_emotion = user_emotion.get("primary_emotion", "neutral")
        response_lower = response.lower()

        # Define expected response patterns for different emotions
        emotion_patterns = {
            "frustration": ["understand", "challenging", "help", "support"],
            "excitement": ["exciting", "great", "amazing", "wonderful"],
            "confusion": ["clarify", "explain", "break down", "understand"],
            "satisfaction": ["glad", "great", "excellent", "well done"],
            "curiosity": ["explore", "discover", "interesting", "learn"],
        }

        expected_patterns = emotion_patterns.get(primary_emotion, [])

        if expected_patterns:
            matches = sum(
                1 for pattern in expected_patterns if pattern in response_lower
            )
            alignment_score = min(1.0, matches / len(expected_patterns))
        else:
            alignment_score = 0.5  # Neutral score for unknown emotions

        return {
            "score": alignment_score,
            "expected_patterns": expected_patterns,
            "patterns_found": [
                pattern for pattern in expected_patterns if pattern in response_lower
            ],
            "primary_emotion": primary_emotion,
        }

    def _check_length_appropriateness(
        self, user_input: str, response: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if response length is appropriate"""

        user_length = len(user_input.split())
        response_length = len(response.split())

        # Simple heuristic: response should be proportional to user input
        # but not too short or too long
        ideal_ratio = 1.5  # Response should be ~1.5x user input length
        actual_ratio = response_length / max(user_length, 1)

        # Score based on how close to ideal ratio
        if 0.8 <= actual_ratio <= 2.5:
            length_score = 1.0
        elif 0.5 <= actual_ratio <= 4.0:
            length_score = 0.7
        else:
            length_score = 0.3

        return {
            "score": length_score,
            "user_length": user_length,
            "response_length": response_length,
            "ratio": actual_ratio,
            "ideal_ratio": ideal_ratio,
        }

    def _check_technical_level_matching(
        self, user_input: str, response: str
    ) -> Dict[str, Any]:
        """Check if technical complexity matches user's level"""

        # Simple technical complexity indicators
        user_technical_words = sum(
            1
            for word in user_input.lower().split()
            if word
            in [
                "code",
                "function",
                "class",
                "algorithm",
                "database",
                "api",
                "server",
                "framework",
                "library",
                "programming",
                "development",
                "technical",
            ]
        )

        response_technical_words = sum(
            1
            for word in response.lower().split()
            if word
            in [
                "code",
                "function",
                "class",
                "algorithm",
                "database",
                "api",
                "server",
                "framework",
                "library",
                "programming",
                "development",
                "technical",
            ]
        )

        user_total_words = max(len(user_input.split()), 1)
        response_total_words = max(len(response.split()), 1)

        user_technical_ratio = user_technical_words / user_total_words
        response_technical_ratio = response_technical_words / response_total_words

        # Score based on ratio similarity
        ratio_diff = abs(user_technical_ratio - response_technical_ratio)
        matching_score = max(0.0, 1.0 - ratio_diff * 2)

        return {
            "score": matching_score,
            "user_technical_ratio": user_technical_ratio,
            "response_technical_ratio": response_technical_ratio,
            "ratio_difference": ratio_diff,
        }

    def _analyze_learning_opportunities(
        self, user_input: str, response: str, basic_critique: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify specific learning opportunities"""

        opportunities = []

        # Check basic critique scores
        if (
            basic_critique["naturalness_score"]
            < self.quality_thresholds["naturalness_score"]
        ):
            opportunities.append(
                {
                    "type": "naturalness",
                    "issue": "Response sounds too robotic",
                    "suggestion": "Use more contractions and casual language",
                    "priority": "high",
                }
            )

        if (
            basic_critique["engagement_score"]
            < self.quality_thresholds["engagement_score"]
        ):
            opportunities.append(
                {
                    "type": "engagement",
                    "issue": "Response lacks engagement",
                    "suggestion": "Add questions or interactive elements",
                    "priority": "medium",
                }
            )

        if basic_critique["empathy_score"] < self.quality_thresholds["empathy_score"]:
            opportunities.append(
                {
                    "type": "empathy",
                    "issue": "Response lacks empathy",
                    "suggestion": "Acknowledge user's emotional state",
                    "priority": "high",
                }
            )

        return {
            "opportunities_count": len(opportunities),
            "opportunities": opportunities,
            "priority_distribution": {
                "high": len([o for o in opportunities if o["priority"] == "high"]),
                "medium": len([o for o in opportunities if o["priority"] == "medium"]),
                "low": len([o for o in opportunities if o["priority"] == "low"]),
            },
        }

    def _calculate_enhancement_score(
        self, flow_analysis: Dict, personality_analysis: Dict, context_analysis: Dict
    ) -> float:
        """Calculate overall enhancement score"""
        return (
            flow_analysis["flow_score"] * 0.3
            + personality_analysis["consistency_score"] * 0.3
            + context_analysis["appropriateness_score"] * 0.4
        )

    def _generate_flow_suggestions(
        self, has_follow_up: bool, acknowledges_user: bool, has_transitions: bool
    ) -> List[str]:
        """Generate specific suggestions for improving conversation flow"""
        suggestions = []

        if not has_follow_up:
            suggestions.append("Add a follow-up question to maintain conversation flow")

        if not acknowledges_user:
            suggestions.append(
                "Acknowledge the user's input before providing your response"
            )

        if not has_transitions:
            suggestions.append("Use transition words to connect ideas more smoothly")

        return suggestions

    async def _generate_improvement_recommendations(
        self,
        basic_critique: Dict[str, Any],
        enhanced_analysis: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate specific, actionable improvement recommendations"""

        recommendations = {
            "immediate_actions": [],
            "personality_adjustments": [],
            "long_term_improvements": [],
            "priority_score": 0.0,
        }

        # Immediate actions based on quality scores
        overall_score = basic_critique.get("overall_score", 0.5)

        if overall_score < 0.6:
            recommendations["immediate_actions"].extend(
                [
                    "Review response for robotic language patterns",
                    "Add more empathetic language",
                    "Include engaging elements like questions",
                ]
            )
            recommendations["priority_score"] = 0.9
        elif overall_score < 0.8:
            recommendations["immediate_actions"].extend(
                ["Fine-tune personality expression", "Improve conversation flow"]
            )
            recommendations["priority_score"] = 0.6

        # Personality adjustments
        personality_score = enhanced_analysis["personality_consistency"][
            "consistency_score"
        ]
        if personality_score < 0.7:
            missing_traits = enhanced_analysis["personality_consistency"][
                "missing_traits"
            ]
            for trait in missing_traits:
                recommendations["personality_adjustments"].append(
                    f"Increase expression of {trait} trait in responses"
                )

        # Long-term improvements based on learning opportunities
        opportunities = enhanced_analysis["learning_opportunities"]["opportunities"]
        for opportunity in opportunities:
            if opportunity["priority"] == "high":
                recommendations["long_term_improvements"].append(
                    f"Develop better {opportunity['type']} capabilities"
                )

        return recommendations

    async def _update_metrics(self, analysis_result: Dict[str, Any]) -> None:
        """Update performance metrics based on analysis results"""

        self.improvement_metrics["total_responses_analyzed"] += 1

        # Update average quality score
        overall_score = analysis_result["basic_critique"]["overall_score"]
        current_avg = self.improvement_metrics["average_quality_score"]
        total_count = self.improvement_metrics["total_responses_analyzed"]

        new_avg = ((current_avg * (total_count - 1)) + overall_score) / total_count
        self.improvement_metrics["average_quality_score"] = new_avg

        # Update quality trend
        self.improvement_metrics["quality_trend"].append(
            {"timestamp": analysis_result["timestamp"], "score": overall_score}
        )

        # Keep only recent trend data
        if len(self.improvement_metrics["quality_trend"]) > 50:
            self.improvement_metrics["quality_trend"] = self.improvement_metrics[
                "quality_trend"
            ][-25:]

        # Track common issues
        opportunities = analysis_result["enhanced_analysis"]["learning_opportunities"][
            "opportunities"
        ]
        for opportunity in opportunities:
            issue_type = opportunity["type"]
            if issue_type not in self.improvement_metrics["common_issues"]:
                self.improvement_metrics["common_issues"][issue_type] = 0
            self.improvement_metrics["common_issues"][issue_type] += 1

        # Store in memory system if available
        if self.memory_system:
            try:
                await self.memory_system.store_memory(
                    content=f"Response quality analysis: {overall_score:.2f}/1.0",
                    memory_type="quality_assessment",
                    tags=["critique", "quality", "improvement"],
                    confidence=0.8,
                    context={
                        "analysis_summary": {
                            "overall_score": overall_score,
                            "enhancement_score": analysis_result["enhanced_analysis"][
                                "overall_enhancement_score"
                            ],
                            "recommendations_count": len(
                                analysis_result["improvement_recommendations"][
                                    "immediate_actions"
                                ]
                            ),
                        }
                    },
                )
            except Exception as e:
                print(f"⚠️ Failed to store critique memory: {e}")

    async def apply_improvement_suggestions(
        self, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply improvement suggestions to personality system"""

        recommendations = analysis_result["improvement_recommendations"]
        applications = {
            "personality_adjustments_applied": 0,
            "threshold_updates": 0,
            "learning_rate_adjustments": 0,
        }

        # Apply personality adjustments
        for adjustment in recommendations["personality_adjustments"]:
            if "empathy" in adjustment.lower():
                await self._adjust_personality_trait("empathy", 0.05)
                applications["personality_adjustments_applied"] += 1
            elif "enthusiasm" in adjustment.lower():
                await self._adjust_personality_trait("enthusiasm", 0.03)
                applications["personality_adjustments_applied"] += 1
            elif "curiosity" in adjustment.lower():
                await self._adjust_personality_trait("curiosity", 0.02)
                applications["personality_adjustments_applied"] += 1

        # Update improvement metrics
        self.improvement_metrics["improvement_suggestions_applied"] += applications[
            "personality_adjustments_applied"
        ]

        return applications

    async def _adjust_personality_trait(
        self, trait_name: str, adjustment: float
    ) -> None:
        """Safely adjust a personality trait"""
        try:
            from .personality_engine import PersonalityTrait

            trait_map = {
                "empathy": PersonalityTrait.EMPATHY,
                "enthusiasm": PersonalityTrait.ENTHUSIASM,
                "curiosity": PersonalityTrait.CURIOSITY,
                "helpfulness": PersonalityTrait.HELPFULNESS,
                "creativity": PersonalityTrait.CREATIVITY,
                "playfulness": PersonalityTrait.PLAYFULNESS,
                "thoughtfulness": PersonalityTrait.THOUGHTFULNESS,
            }

            if trait_name in trait_map:
                trait = trait_map[trait_name]
                current_value = lyrixa_personality.base_traits[trait]
                new_value = min(1.0, max(0.0, current_value + adjustment))
                lyrixa_personality.base_traits[trait] = new_value

                self.improvement_metrics["personality_adaptations_made"] += 1

                print(
                    f"🎭 Adjusted {trait_name} trait: {current_value:.3f} → {new_value:.3f}"
                )

        except Exception as e:
            print(f"⚠️ Failed to adjust personality trait {trait_name}: {e}")

    def get_critique_summary(self) -> Dict[str, Any]:
        """Get a summary of critique agent performance"""

        recent_scores = [
            item["score"] for item in self.improvement_metrics["quality_trend"][-10:]
        ]

        trend_direction = "stable"
        if len(recent_scores) >= 3:
            if recent_scores[-1] > recent_scores[0]:
                trend_direction = "improving"
            elif recent_scores[-1] < recent_scores[0]:
                trend_direction = "declining"

        return {
            "agent_status": "active",
            "total_analyses": self.improvement_metrics["total_responses_analyzed"],
            "average_quality": self.improvement_metrics["average_quality_score"],
            "quality_trend": trend_direction,
            "common_issues": dict(
                sorted(
                    self.improvement_metrics["common_issues"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),
            "improvements_applied": self.improvement_metrics[
                "improvement_suggestions_applied"
            ],
            "personality_adaptations": self.improvement_metrics[
                "personality_adaptations_made"
            ],
            "recent_quality_scores": recent_scores,
        }


# Global critique agent instance
response_critique_agent = ResponseCritiqueAgent()


async def analyze_and_improve_response(
    user_input: str,
    lyrixa_response: str,
    context: Optional[Dict[str, Any]] = None,
    apply_improvements: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function for analyzing and improving responses

    Args:
        user_input: User's input
        lyrixa_response: Lyrixa's response
        context: Additional context
        apply_improvements: Whether to apply improvement suggestions

    Returns:
        Analysis results with improvement data
    """
    # Analyze response quality
    analysis = await response_critique_agent.analyze_response_quality(
        user_input, lyrixa_response, context
    )

    # Apply improvements if requested
    if apply_improvements:
        improvements_applied = (
            await response_critique_agent.apply_improvement_suggestions(analysis)
        )
        analysis["improvements_applied"] = improvements_applied

    return analysis


def get_critique_agent_status() -> Dict[str, Any]:
    """Get current status of the critique agent"""
    return response_critique_agent.get_critique_summary()

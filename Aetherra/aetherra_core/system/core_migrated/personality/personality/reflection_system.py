"""
Personality Reflection System - Phase 2 Implementation
======================================================

This module enables Lyrixa to analyze and reflect on her own communication style,
identifying patterns, strengths, and areas for improvement. It works with the
Response Critique Agent to create a comprehensive self-improvement loop.

Features:
- Communication pattern analysis
- Personality trait evolution tracking
- Self-awareness metrics
- Adaptive style adjustments
- Reflection-based learning
"""

import statistics
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .emotion_detector import detect_user_emotion

# Import Phase 1 and Phase 2 components
from .personality_engine import PersonalityTrait, lyrixa_personality


class PersonalityReflectionSystem:
    """
    System that enables Lyrixa to reflect on and improve her own personality expression
    """

    def __init__(self, memory_system=None):
        self.memory_system = memory_system

        # Reflection tracking
        self.reflection_history = deque(maxlen=200)
        self.trait_evolution_history = defaultdict(list)
        self.communication_patterns = defaultdict(int)
        self.self_awareness_metrics = {
            "reflection_count": 0,
            "successful_adaptations": 0,
            "failed_adaptations": 0,
            "pattern_recognitions": 0,
            "style_improvements": 0,
        }

        # Learning parameters
        self.reflection_frequency = 5  # Reflect every N interactions
        self.pattern_threshold = 3  # Minimum occurrences to recognize pattern
        self.adaptation_confidence = 0.7  # Minimum confidence for adaptation

        # Reflection triggers
        self.interaction_count = 0
        self.last_reflection_time = datetime.now()

        # Style tracking
        self.communication_styles = {
            "formal": 0.0,
            "casual": 0.0,
            "technical": 0.0,
            "empathetic": 0.0,
            "enthusiastic": 0.0,
            "analytical": 0.0,
            "creative": 0.0,
        }

    async def process_interaction(
        self,
        user_input: str,
        lyrixa_response: str,
        context: Optional[Dict[str, Any]] = None,
        critique_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a single interaction for reflection and learning

        Args:
            user_input: What the user said
            lyrixa_response: Lyrixa's response
            context: Additional context
            critique_data: Data from critique agent if available

        Returns:
            Reflection analysis and any adaptations made
        """
        if context is None:
            context = {}

        self.interaction_count += 1

        # Analyze current interaction
        interaction_analysis = await self._analyze_interaction(
            user_input, lyrixa_response, context, critique_data
        )

        # Update communication patterns
        await self._update_patterns(interaction_analysis)

        # Check if reflection is needed
        reflection_result = None
        if self._should_reflect():
            reflection_result = await self._perform_reflection()

        # Store interaction for future analysis
        interaction_record = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "lyrixa_response": lyrixa_response,
            "context": context,
            "analysis": interaction_analysis,
            "critique_data": critique_data,
            "reflection_triggered": reflection_result is not None,
        }

        self.reflection_history.append(interaction_record)

        result = {
            "interaction_analysis": interaction_analysis,
            "patterns_updated": True,
            "reflection_performed": reflection_result is not None,
        }

        if reflection_result:
            result["reflection_result"] = reflection_result

        return result

    async def _analyze_interaction(
        self,
        user_input: str,
        response: str,
        context: Dict[str, Any],
        critique_data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze a single interaction for patterns and insights"""

        # Analyze communication style used
        style_analysis = self._analyze_communication_style(response)

        # Analyze personality trait expression
        trait_analysis = self._analyze_trait_expression(response)

        # Analyze emotional resonance
        emotion_analysis = self._analyze_emotional_resonance(user_input, response)

        # Analyze effectiveness (if critique data available)
        effectiveness_analysis = self._analyze_effectiveness(critique_data)

        # Identify conversation elements
        conversation_elements = self._identify_conversation_elements(
            user_input, response
        )

        return {
            "style_analysis": style_analysis,
            "trait_analysis": trait_analysis,
            "emotion_analysis": emotion_analysis,
            "effectiveness_analysis": effectiveness_analysis,
            "conversation_elements": conversation_elements,
            "timestamp": datetime.now().isoformat(),
        }

    def _analyze_communication_style(self, response: str) -> Dict[str, Any]:
        """Analyze the communication style used in the response"""

        response_lower = response.lower()
        styles_detected = {}

        # Formal style indicators
        formal_indicators = [
            "therefore",
            "furthermore",
            "consequently",
            "moreover",
            "additionally",
        ]
        formal_score = sum(
            1 for indicator in formal_indicators if indicator in response_lower
        )
        styles_detected["formal"] = min(1.0, formal_score / 3)

        # Casual style indicators
        casual_indicators = ["hey", "yeah", "cool", "awesome", "gonna", "wanna", "!"]
        casual_score = sum(
            1 for indicator in casual_indicators if indicator in response_lower
        )
        styles_detected["casual"] = min(1.0, casual_score / 3)

        # Technical style indicators
        technical_indicators = [
            "function",
            "algorithm",
            "implement",
            "optimize",
            "architecture",
        ]
        technical_score = sum(
            1 for indicator in technical_indicators if indicator in response_lower
        )
        styles_detected["technical"] = min(1.0, technical_score / 2)

        # Empathetic style indicators
        empathetic_indicators = [
            "understand",
            "feel",
            "sorry",
            "challenging",
            "difficult",
            "care",
        ]
        empathetic_score = sum(
            1 for indicator in empathetic_indicators if indicator in response_lower
        )
        styles_detected["empathetic"] = min(1.0, empathetic_score / 3)

        # Enthusiastic style indicators
        enthusiastic_indicators = [
            "exciting",
            "amazing",
            "fantastic",
            "love",
            "brilliant",
            "wonderful",
        ]
        enthusiastic_score = sum(
            1 for indicator in enthusiastic_indicators if indicator in response_lower
        )
        styles_detected["enthusiastic"] = min(1.0, enthusiastic_score / 2)

        # Analytical style indicators
        analytical_indicators = [
            "analyze",
            "consider",
            "examine",
            "evaluate",
            "assess",
            "compare",
        ]
        analytical_score = sum(
            1 for indicator in analytical_indicators if indicator in response_lower
        )
        styles_detected["analytical"] = min(1.0, analytical_score / 2)

        # Creative style indicators
        creative_indicators = [
            "imagine",
            "creative",
            "innovative",
            "unique",
            "artistic",
            "inspiring",
        ]
        creative_score = sum(
            1 for indicator in creative_indicators if indicator in response_lower
        )
        styles_detected["creative"] = min(1.0, creative_score / 2)

        # Determine dominant style
        dominant_style = max(styles_detected.items(), key=lambda x: x[1])

        return {
            "styles_detected": styles_detected,
            "dominant_style": dominant_style[0],
            "dominant_score": dominant_style[1],
            "style_diversity": len([s for s in styles_detected.values() if s > 0.3]),
        }

    def _analyze_trait_expression(self, response: str) -> Dict[str, Any]:
        """Analyze which personality traits are expressed in the response"""

        response_lower = response.lower()
        trait_expressions = {}

        # Map traits to their indicators
        trait_indicators = {
            PersonalityTrait.EMPATHY: [
                "understand",
                "feel",
                "care",
                "support",
                "sorry",
            ],
            PersonalityTrait.ENTHUSIASM: [
                "exciting",
                "great",
                "amazing",
                "love",
                "fantastic",
            ],
            PersonalityTrait.CURIOSITY: [
                "curious",
                "wonder",
                "explore",
                "discover",
                "learn",
            ],
            PersonalityTrait.HELPFULNESS: [
                "help",
                "assist",
                "support",
                "guide",
                "show",
            ],
            PersonalityTrait.CREATIVITY: [
                "creative",
                "innovative",
                "imagine",
                "unique",
                "artistic",
            ],
            PersonalityTrait.PLAYFULNESS: ["fun", "playful", "silly", "joke", "laugh"],
            PersonalityTrait.THOUGHTFULNESS: [
                "think",
                "consider",
                "reflect",
                "ponder",
                "careful",
            ],
        }

        for trait, indicators in trait_indicators.items():
            expression_count = sum(
                1 for indicator in indicators if indicator in response_lower
            )
            trait_expressions[trait.name.lower()] = min(
                1.0, expression_count / len(indicators)
            )

        # Compare with current trait levels
        current_traits = lyrixa_personality.get_personality_summary()["trait_levels"]
        trait_alignment = {}

        for trait_name, expressed_level in trait_expressions.items():
            current_level = current_traits.get(trait_name, 0.5)
            alignment = 1.0 - abs(expressed_level - current_level)
            trait_alignment[trait_name] = alignment

        return {
            "trait_expressions": trait_expressions,
            "trait_alignment": trait_alignment,
            "average_alignment": statistics.mean(trait_alignment.values())
            if trait_alignment
            else 0.5,
            "strongest_trait_expressed": max(
                trait_expressions.items(), key=lambda x: x[1]
            )
            if trait_expressions
            else ("none", 0.0),
        }

    def _analyze_emotional_resonance(
        self, user_input: str, response: str
    ) -> Dict[str, Any]:
        """Analyze how well the response resonates with the user's emotional state"""

        # Detect user emotion
        user_emotion = detect_user_emotion(user_input)

        # Analyze response emotion
        response_emotion = detect_user_emotion(
            response
        )  # Can be reused for response analysis

        # Calculate emotional alignment
        user_primary = user_emotion.get("primary_emotion", "neutral")
        response_primary = response_emotion.get("primary_emotion", "neutral")

        # Define emotion compatibility matrix
        emotion_compatibility = {
            "excitement": ["excitement", "satisfaction", "curiosity"],
            "frustration": ["empathy", "understanding", "support"],
            "curiosity": ["curiosity", "excitement", "enthusiasm"],
            "confusion": ["patience", "clarity", "understanding"],
            "satisfaction": ["satisfaction", "excitement", "validation"],
            "neutral": ["neutral", "curiosity", "helpfulness"],
        }

        compatible_emotions = emotion_compatibility.get(user_primary, ["neutral"])
        resonance_score = 1.0 if response_primary in compatible_emotions else 0.3

        return {
            "user_emotion": user_emotion,
            "response_emotion": response_emotion,
            "resonance_score": resonance_score,
            "emotional_match": response_primary == user_primary,
            "compatible_response": response_primary in compatible_emotions,
        }

    def _analyze_effectiveness(
        self, critique_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze interaction effectiveness based on critique data"""

        if not critique_data:
            return {
                "overall_effectiveness": 0.5,
                "quality_score": 0.5,
                "improvement_needed": True,
                "critique_available": False,
            }

        basic_critique = critique_data.get("basic_critique", {})
        enhanced_analysis = critique_data.get("enhanced_analysis", {})

        overall_score = basic_critique.get("overall_score", 0.5)
        enhancement_score = enhanced_analysis.get("overall_enhancement_score", 0.5)

        # Calculate combined effectiveness
        effectiveness = (overall_score * 0.6) + (enhancement_score * 0.4)

        # Determine improvement areas
        improvement_areas = []
        if basic_critique.get("naturalness_score", 1.0) < 0.7:
            improvement_areas.append("naturalness")
        if basic_critique.get("engagement_score", 1.0) < 0.7:
            improvement_areas.append("engagement")
        if basic_critique.get("empathy_score", 1.0) < 0.7:
            improvement_areas.append("empathy")

        return {
            "overall_effectiveness": effectiveness,
            "quality_score": overall_score,
            "enhancement_score": enhancement_score,
            "improvement_needed": effectiveness < 0.7,
            "improvement_areas": improvement_areas,
            "critique_available": True,
        }

    def _identify_conversation_elements(
        self, user_input: str, response: str
    ) -> Dict[str, Any]:
        """Identify key elements of the conversation"""

        user_lower = user_input.lower()
        response_lower = response.lower()

        elements = {
            "question_asked": "?" in user_input,
            "question_answered": any(
                word in response_lower
                for word in ["yes", "no", "here's", "the answer", "i think"]
            ),
            "follow_up_question": "?" in response,
            "acknowledgment": any(
                word in response_lower
                for word in ["i understand", "i see", "that makes sense"]
            ),
            "personal_reference": any(
                word in response_lower for word in ["i", "me", "my", "myself"]
            ),
            "user_reference": any(
                word in response_lower for word in ["you", "your", "yourself"]
            ),
            "emotional_expression": any(
                word in response_lower
                for word in ["feel", "emotion", "excited", "frustrated"]
            ),
            "code_discussion": any(
                word in user_lower
                for word in ["code", "function", "class", "programming"]
            ),
            "help_request": any(
                word in user_lower for word in ["help", "assist", "support", "guide"]
            ),
        }

        # Calculate conversation engagement level
        engagement_indicators = [
            "follow_up_question",
            "acknowledgment",
            "emotional_expression",
        ]
        engagement_score = sum(
            1 for indicator in engagement_indicators if elements[indicator]
        ) / len(engagement_indicators)

        # Add non-boolean elements
        result: Dict[str, Any] = dict(elements)
        result["engagement_score"] = engagement_score
        result["conversation_type"] = self._classify_conversation_type(elements)

        return result

    def _classify_conversation_type(self, elements: Dict[str, bool]) -> str:
        """Classify the type of conversation based on elements"""

        if elements["code_discussion"]:
            return "technical"
        elif elements["help_request"]:
            return "assistance"
        elif elements["emotional_expression"]:
            return "personal"
        elif elements["question_asked"]:
            return "inquiry"
        else:
            return "general"

    async def _update_patterns(self, interaction_analysis: Dict[str, Any]) -> None:
        """Update communication patterns based on interaction analysis"""

        # Update style usage
        style_analysis = interaction_analysis["style_analysis"]
        for style, score in style_analysis["styles_detected"].items():
            if score > 0.3:  # Only count significant style usage
                self.communication_patterns[f"style_{style}"] += 1

        # Update trait expression patterns
        trait_analysis = interaction_analysis["trait_analysis"]
        for trait, score in trait_analysis["trait_expressions"].items():
            if score > 0.3:
                self.communication_patterns[f"trait_{trait}"] += 1

        # Update conversation element patterns
        elements = interaction_analysis["conversation_elements"]
        for element, present in elements.items():
            if (
                present
                and element != "engagement_score"
                and element != "conversation_type"
            ):
                self.communication_patterns[f"element_{element}"] += 1

        # Update conversation type patterns
        conv_type = elements["conversation_type"]
        self.communication_patterns[f"conversation_{conv_type}"] += 1

        # Update style tracking with exponential moving average
        alpha = 0.1  # Learning rate for style tracking
        for style, score in style_analysis["styles_detected"].items():
            current_value = self.communication_styles[style]
            self.communication_styles[style] = (
                1 - alpha
            ) * current_value + alpha * score

    def _should_reflect(self) -> bool:
        """Determine if reflection should be triggered"""

        # Frequency-based trigger
        if self.interaction_count % self.reflection_frequency == 0:
            return True

        # Time-based trigger (reflect at least once per hour)
        time_since_last = datetime.now() - self.last_reflection_time
        if time_since_last > timedelta(hours=1):
            return True

        # Pattern-based trigger (significant change in communication patterns)
        if self._detect_significant_pattern_change():
            return True

        return False

    def _detect_significant_pattern_change(self) -> bool:
        """Detect if there's been a significant change in communication patterns"""

        if len(self.reflection_history) < 10:
            return False

        # Compare recent interactions with historical average
        recent_interactions = list(self.reflection_history)[-5:]
        older_interactions = list(self.reflection_history)[-15:-5]

        if not older_interactions:
            return False

        # Calculate style diversity change
        recent_diversity = statistics.mean(
            [
                interaction["analysis"]["style_analysis"]["style_diversity"]
                for interaction in recent_interactions
            ]
        )

        older_diversity = statistics.mean(
            [
                interaction["analysis"]["style_analysis"]["style_diversity"]
                for interaction in older_interactions
            ]
        )

        diversity_change = abs(recent_diversity - older_diversity)

        # Trigger reflection if significant change
        return diversity_change > 1.0  # Threshold for significant change

    async def _perform_reflection(self) -> Dict[str, Any]:
        """Perform a comprehensive reflection on recent interactions"""

        self.last_reflection_time = datetime.now()
        self.self_awareness_metrics["reflection_count"] += 1

        print("🤔 Lyrixa is reflecting on her communication patterns...")

        # Analyze recent interaction history
        recent_history = (
            list(self.reflection_history)[-20:]
            if len(self.reflection_history) >= 20
            else list(self.reflection_history)
        )

        if not recent_history:
            return {
                "reflection_type": "initial",
                "insights": ["Starting communication pattern analysis"],
            }

        # Perform different types of reflection
        pattern_insights = await self._reflect_on_patterns(recent_history)
        effectiveness_insights = await self._reflect_on_effectiveness(recent_history)
        evolution_insights = await self._reflect_on_evolution()
        adaptation_insights = await self._plan_adaptations(
            pattern_insights, effectiveness_insights
        )

        reflection_result = {
            "reflection_type": "comprehensive",
            "timestamp": datetime.now().isoformat(),
            "interactions_analyzed": len(recent_history),
            "pattern_insights": pattern_insights,
            "effectiveness_insights": effectiveness_insights,
            "evolution_insights": evolution_insights,
            "adaptation_plan": adaptation_insights,
            "self_awareness_level": self._calculate_self_awareness_level(),
        }

        # Apply adaptations if confidence is high enough
        if adaptation_insights["confidence"] >= self.adaptation_confidence:
            adaptation_results = await self._apply_adaptations(adaptation_insights)
            reflection_result["adaptations_applied"] = adaptation_results

        # Store reflection in memory if available
        if self.memory_system:
            try:
                await self.memory_system.store_memory(
                    content=f"Personality reflection: {len(pattern_insights['key_patterns'])} patterns identified",
                    memory_type="self_reflection",
                    tags=["reflection", "personality", "communication"],
                    confidence=0.9,
                    context={"reflection_summary": reflection_result},
                )
            except Exception as e:
                print(f"⚠️ Failed to store reflection memory: {e}")

        print(
            f"✨ Reflection complete! Identified {len(pattern_insights['key_patterns'])} key patterns"
        )

        return reflection_result

    async def _reflect_on_patterns(
        self, recent_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Reflect on communication patterns in recent interactions"""

        # Analyze style usage patterns
        style_usage = defaultdict(list)
        for interaction in recent_history:
            style_analysis = interaction["analysis"]["style_analysis"]
            for style, score in style_analysis["styles_detected"].items():
                style_usage[style].append(score)

        # Calculate average style usage
        avg_style_usage = {
            style: statistics.mean(scores) for style, scores in style_usage.items()
        }

        # Identify dominant patterns
        dominant_styles = sorted(
            avg_style_usage.items(), key=lambda x: x[1], reverse=True
        )[:3]

        # Analyze trait expression consistency
        trait_consistency = self._analyze_trait_consistency(recent_history)

        # Identify conversation type preferences
        conv_types = [
            interaction["analysis"]["conversation_elements"]["conversation_type"]
            for interaction in recent_history
        ]
        conv_type_counts = {t: conv_types.count(t) for t in set(conv_types)}

        key_patterns = []

        # Generate insights
        if dominant_styles[0][1] > 0.4:
            key_patterns.append(
                f"Consistently using {dominant_styles[0][0]} communication style"
            )

        if trait_consistency["most_consistent"]:
            trait_name, consistency = trait_consistency["most_consistent"]
            if consistency > 0.7:
                key_patterns.append(
                    f"Strong consistency in {trait_name} trait expression"
                )

        most_common_conv_type = max(conv_type_counts.items(), key=lambda x: x[1])
        if most_common_conv_type[1] > len(recent_history) * 0.4:
            key_patterns.append(f"Frequent {most_common_conv_type[0]} conversations")

        return {
            "key_patterns": key_patterns,
            "style_usage": avg_style_usage,
            "dominant_styles": dominant_styles,
            "trait_consistency": trait_consistency,
            "conversation_preferences": conv_type_counts,
            "pattern_strength": len(key_patterns) / 5.0,  # Normalize to 0-1
        }

    def _analyze_trait_consistency(
        self, recent_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze consistency of trait expression"""

        trait_scores = defaultdict(list)

        for interaction in recent_history:
            trait_analysis = interaction["analysis"]["trait_analysis"]
            for trait, score in trait_analysis["trait_expressions"].items():
                trait_scores[trait].append(score)

        # Calculate consistency (inverse of standard deviation)
        trait_consistency = {}
        for trait, scores in trait_scores.items():
            if len(scores) > 1:
                std_dev = statistics.stdev(scores)
                consistency = max(
                    0.0, 1.0 - std_dev
                )  # Higher consistency = lower std dev
                trait_consistency[trait] = consistency
            else:
                trait_consistency[trait] = 1.0

        most_consistent = (
            max(trait_consistency.items(), key=lambda x: x[1])
            if trait_consistency
            else None
        )
        least_consistent = (
            min(trait_consistency.items(), key=lambda x: x[1])
            if trait_consistency
            else None
        )

        return {
            "trait_consistency": trait_consistency,
            "most_consistent": most_consistent,
            "least_consistent": least_consistent,
            "average_consistency": statistics.mean(trait_consistency.values())
            if trait_consistency
            else 0.5,
        }

    async def _reflect_on_effectiveness(
        self, recent_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Reflect on the effectiveness of recent interactions"""

        effectiveness_scores = []
        quality_scores = []
        improvement_areas = defaultdict(int)

        for interaction in recent_history:
            effectiveness_analysis = interaction["analysis"]["effectiveness_analysis"]

            if effectiveness_analysis["critique_available"]:
                effectiveness_scores.append(
                    effectiveness_analysis["overall_effectiveness"]
                )
                quality_scores.append(effectiveness_analysis["quality_score"])

                for area in effectiveness_analysis.get("improvement_areas", []):
                    improvement_areas[area] += 1

        insights = []

        if effectiveness_scores:
            avg_effectiveness = statistics.mean(effectiveness_scores)
            avg_quality = statistics.mean(quality_scores)

            if avg_effectiveness > 0.8:
                insights.append("Consistently high-quality interactions")
            elif avg_effectiveness < 0.6:
                insights.append("Room for improvement in interaction quality")

            # Trend analysis
            if len(effectiveness_scores) >= 5:
                recent_trend = statistics.mean(effectiveness_scores[-3:])
                earlier_trend = (
                    statistics.mean(effectiveness_scores[-6:-3])
                    if len(effectiveness_scores) >= 6
                    else avg_effectiveness
                )

                if recent_trend > earlier_trend + 0.1:
                    insights.append("Improving effectiveness trend")
                elif recent_trend < earlier_trend - 0.1:
                    insights.append("Declining effectiveness trend")
        else:
            avg_effectiveness = 0.5
            avg_quality = 0.5
            insights.append("Limited effectiveness data available")

        # Most common improvement areas
        if improvement_areas:
            most_common_area = max(improvement_areas.items(), key=lambda x: x[1])
            if most_common_area[1] > 2:
                insights.append(f"Frequent need to improve {most_common_area[0]}")

        return {
            "effectiveness_insights": insights,
            "average_effectiveness": avg_effectiveness,
            "average_quality": avg_quality,
            "effectiveness_trend": self._calculate_trend(effectiveness_scores),
            "common_improvement_areas": dict(improvement_areas),
            "effectiveness_stability": self._calculate_stability(effectiveness_scores),
        }

    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction from a list of scores"""
        if len(scores) < 3:
            return "insufficient_data"

        recent_avg = statistics.mean(scores[-3:])
        earlier_avg = (
            statistics.mean(scores[:-3]) if len(scores) > 3 else statistics.mean(scores)
        )

        diff = recent_avg - earlier_avg

        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"

    def _calculate_stability(self, scores: List[float]) -> float:
        """Calculate stability (consistency) of scores"""
        if len(scores) < 2:
            return 1.0

        std_dev = statistics.stdev(scores)
        stability = max(
            0.0, 1.0 - std_dev
        )  # Higher stability = lower standard deviation
        return stability

    async def _reflect_on_evolution(self) -> Dict[str, Any]:
        """Reflect on personality evolution over time"""

        current_traits = lyrixa_personality.get_personality_summary()["trait_levels"]

        # Track trait evolution
        for trait_name, current_level in current_traits.items():
            self.trait_evolution_history[trait_name].append(
                {"timestamp": datetime.now().isoformat(), "level": current_level}
            )

            # Keep only recent history
            if len(self.trait_evolution_history[trait_name]) > 50:
                self.trait_evolution_history[trait_name] = self.trait_evolution_history[
                    trait_name
                ][-25:]

        evolution_insights = []
        trait_changes = {}

        # Analyze trait changes
        for trait_name, history in self.trait_evolution_history.items():
            if len(history) >= 2:
                initial_level = history[0]["level"]
                current_level = history[-1]["level"]
                change = current_level - initial_level
                trait_changes[trait_name] = change

                if abs(change) > 0.05:
                    direction = "increased" if change > 0 else "decreased"
                    evolution_insights.append(
                        f"{trait_name.title()} trait has {direction} over time"
                    )

        # Identify most evolved traits
        if trait_changes:
            most_increased = max(trait_changes.items(), key=lambda x: x[1])
            most_decreased = min(trait_changes.items(), key=lambda x: x[1])

            if most_increased[1] > 0.05:
                evolution_insights.append(
                    f"Strongest growth in {most_increased[0]} trait"
                )

            if most_decreased[1] < -0.05:
                evolution_insights.append(
                    f"Notable decline in {most_decreased[0]} trait"
                )

        return {
            "evolution_insights": evolution_insights,
            "trait_changes": trait_changes,
            "total_evolution_magnitude": sum(
                abs(change) for change in trait_changes.values()
            )
            if trait_changes
            else 0.0,
            "growth_traits": [
                trait for trait, change in trait_changes.items() if change > 0.02
            ],
            "declining_traits": [
                trait for trait, change in trait_changes.items() if change < -0.02
            ],
        }

    async def _plan_adaptations(
        self, pattern_insights: Dict[str, Any], effectiveness_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Plan personality adaptations based on reflection insights"""

        adaptations = []
        confidence = 0.5

        # Plan adaptations based on effectiveness
        avg_effectiveness = effectiveness_insights["average_effectiveness"]

        if avg_effectiveness < 0.6:
            adaptations.append(
                {
                    "type": "trait_adjustment",
                    "target": "empathy",
                    "adjustment": 0.05,
                    "reason": "Low effectiveness suggests need for more empathy",
                }
            )
            confidence += 0.2

        # Plan adaptations based on patterns
        dominant_styles = pattern_insights["dominant_styles"]
        if len(dominant_styles) > 0 and dominant_styles[0][1] > 0.7:
            # Too much focus on one style
            adaptations.append(
                {
                    "type": "style_diversification",
                    "current_dominant": dominant_styles[0][0],
                    "adjustment": -0.1,
                    "reason": "Over-reliance on single communication style",
                }
            )
            confidence += 0.1

        # Plan adaptations based on common improvement areas
        improvement_areas = effectiveness_insights.get("common_improvement_areas", {})
        if "naturalness" in improvement_areas and improvement_areas["naturalness"] > 2:
            adaptations.append(
                {
                    "type": "trait_adjustment",
                    "target": "playfulness",
                    "adjustment": 0.03,
                    "reason": "Frequent naturalness issues suggest need for more playful language",
                }
            )
            confidence += 0.1

        if "engagement" in improvement_areas and improvement_areas["engagement"] > 2:
            adaptations.append(
                {
                    "type": "trait_adjustment",
                    "target": "curiosity",
                    "adjustment": 0.04,
                    "reason": "Frequent engagement issues suggest need for more curiosity",
                }
            )
            confidence += 0.1

        # Normalize confidence
        confidence = min(1.0, confidence)

        return {
            "adaptations": adaptations,
            "confidence": confidence,
            "adaptation_count": len(adaptations),
            "reasoning": [adaptation["reason"] for adaptation in adaptations],
        }

    async def _apply_adaptations(
        self, adaptation_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply the planned personality adaptations"""

        adaptations = adaptation_plan["adaptations"]
        applied_adaptations = []
        failed_adaptations = []

        for adaptation in adaptations:
            try:
                if adaptation["type"] == "trait_adjustment":
                    success = await self._apply_trait_adjustment(
                        adaptation["target"], adaptation["adjustment"]
                    )

                    if success:
                        applied_adaptations.append(adaptation)
                        self.self_awareness_metrics["successful_adaptations"] += 1
                    else:
                        failed_adaptations.append(adaptation)
                        self.self_awareness_metrics["failed_adaptations"] += 1

                elif adaptation["type"] == "style_diversification":
                    # For style diversification, we adjust related traits
                    success = await self._apply_style_diversification(adaptation)

                    if success:
                        applied_adaptations.append(adaptation)
                        self.self_awareness_metrics["successful_adaptations"] += 1
                    else:
                        failed_adaptations.append(adaptation)
                        self.self_awareness_metrics["failed_adaptations"] += 1

            except Exception as e:
                print(f"⚠️ Failed to apply adaptation: {e}")
                failed_adaptations.append(adaptation)
                self.self_awareness_metrics["failed_adaptations"] += 1

        result = {
            "applied_count": len(applied_adaptations),
            "failed_count": len(failed_adaptations),
            "applied_adaptations": applied_adaptations,
            "failed_adaptations": failed_adaptations,
            "success_rate": len(applied_adaptations) / len(adaptations)
            if adaptations
            else 0.0,
        }

        if applied_adaptations:
            print(f"🎭 Applied {len(applied_adaptations)} personality adaptations")
            self.self_awareness_metrics["style_improvements"] += len(
                applied_adaptations
            )

        return result

    async def _apply_trait_adjustment(self, trait_name: str, adjustment: float) -> bool:
        """Apply a trait adjustment"""
        try:
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

                print(
                    f"🎭 Adjusted {trait_name}: {current_value:.3f} → {new_value:.3f}"
                )
                return True

            return False

        except Exception as e:
            print(f"⚠️ Failed to adjust trait {trait_name}: {e}")
            return False

    async def _apply_style_diversification(self, adaptation: Dict[str, Any]) -> bool:
        """Apply style diversification by adjusting related traits"""
        try:
            dominant_style = adaptation["current_dominant"]

            # Map styles to traits that should be reduced/increased
            style_trait_map = {
                "formal": ("thoughtfulness", -0.02),
                "casual": ("playfulness", -0.02),
                "technical": ("creativity", 0.03),
                "empathetic": ("curiosity", 0.02),
                "enthusiastic": ("thoughtfulness", 0.02),
                "analytical": ("creativity", 0.03),
            }

            if dominant_style in style_trait_map:
                trait_to_adjust, adjustment = style_trait_map[dominant_style]
                success = await self._apply_trait_adjustment(
                    trait_to_adjust, adjustment
                )
                return success

            return False

        except Exception as e:
            print(f"⚠️ Failed to apply style diversification: {e}")
            return False

    def _calculate_self_awareness_level(self) -> float:
        """Calculate current level of self-awareness"""

        metrics = self.self_awareness_metrics

        # Base score from reflection count
        reflection_score = min(1.0, metrics["reflection_count"] / 20.0)

        # Success rate score
        total_adaptations = (
            metrics["successful_adaptations"] + metrics["failed_adaptations"]
        )
        success_rate = metrics["successful_adaptations"] / max(total_adaptations, 1)

        # Pattern recognition score
        pattern_score = min(1.0, metrics["pattern_recognitions"] / 10.0)

        # Improvement score
        improvement_score = min(1.0, metrics["style_improvements"] / 15.0)

        # Combined score
        self_awareness = (
            reflection_score * 0.3
            + success_rate * 0.3
            + pattern_score * 0.2
            + improvement_score * 0.2
        )

        return self_awareness

    def get_reflection_summary(self) -> Dict[str, Any]:
        """Get a summary of the reflection system's current state"""

        return {
            "system_status": "active",
            "total_interactions_processed": self.interaction_count,
            "reflections_performed": self.self_awareness_metrics["reflection_count"],
            "self_awareness_level": self._calculate_self_awareness_level(),
            "successful_adaptations": self.self_awareness_metrics[
                "successful_adaptations"
            ],
            "current_communication_styles": dict(self.communication_styles),
            "most_common_patterns": dict(
                sorted(
                    self.communication_patterns.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5]
            ),
            "recent_reflection": self.last_reflection_time.isoformat(),
            "next_reflection_trigger": self.interaction_count
            + (
                self.reflection_frequency
                - (self.interaction_count % self.reflection_frequency)
            ),
        }


# Global reflection system instance
personality_reflection_system = PersonalityReflectionSystem()


async def process_interaction_for_reflection(
    user_input: str,
    lyrixa_response: str,
    context: Optional[Dict[str, Any]] = None,
    critique_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function for processing interactions through reflection system

    Args:
        user_input: User's input
        lyrixa_response: Lyrixa's response
        context: Additional context
        critique_data: Data from critique agent

    Returns:
        Reflection processing results
    """
    return await personality_reflection_system.process_interaction(
        user_input, lyrixa_response, context, critique_data
    )


def get_reflection_system_status() -> Dict[str, Any]:
    """Get current status of the reflection system"""
    return personality_reflection_system.get_reflection_summary()

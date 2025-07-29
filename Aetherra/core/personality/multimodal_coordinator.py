"""
Multi-Modal Personality Coordinator - Phase 3.1 Implementation
============================================================

This module implements the core multi-modal personality coordination system that ensures
consistent personality expression across different interaction mediums (text, voice,
visual, code) while optimizing for the best user experience in each modality.

Features:
- Cross-modal personality consistency
- Adaptive modality selection
- Personality state synchronization
- Modal preference learning
- Context-aware modality optimization
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .personality_engine import PersonalityTrait, lyrixa_personality


class InteractionModality(Enum):
    """Supported interaction modalities for Lyrixa"""

    TEXT = "text"
    VOICE = "voice"
    VISUAL = "visual"
    CODE = "code"
    MIXED = "mixed"


class ModalityState(Enum):
    """States for each modality interface"""

    INACTIVE = "inactive"
    ACTIVE = "active"
    SYNCHRONIZED = "synchronized"
    ADAPTING = "adapting"
    ERROR = "error"


class PersonalityModalityProfile:
    """Personality profile adapted for a specific modality"""

    def __init__(self, modality: InteractionModality, base_personality: Dict[str, Any]):
        self.modality = modality
        self.base_personality = base_personality
        self.adapted_traits = {}
        self.expression_style = {}
        self.optimization_params = {}
        self.last_updated = datetime.now()

        # Initialize modality-specific adaptations
        self._initialize_modality_adaptations()

    def _initialize_modality_adaptations(self):
        """Initialize modality-specific personality adaptations"""

        if self.modality == InteractionModality.TEXT:
            self.expression_style = {
                "verbosity_level": 0.7,  # Moderate verbosity for text
                "emoji_usage": 0.4,  # Moderate emoji usage
                "formatting_preference": "markdown",
                "tone_indicators": True,
                "response_length": "medium",
            }

        elif self.modality == InteractionModality.VOICE:
            self.expression_style = {
                "speech_rate": 0.6,  # Moderate speaking speed
                "pause_frequency": 0.5,  # Natural pauses
                "emotional_inflection": 0.8,  # Strong emotional expression
                "voice_warmth": 0.9,  # High warmth in voice
                "clarity_priority": True,
            }

        elif self.modality == InteractionModality.VISUAL:
            self.expression_style = {
                "visual_metaphors": 0.8,  # High use of visual language
                "color_references": 0.6,  # Moderate color usage
                "spatial_descriptions": 0.7,  # Good spatial awareness
                "gesture_suggestions": 0.5,  # Some gesture recommendations
                "visual_emphasis": True,
            }

        elif self.modality == InteractionModality.CODE:
            self.expression_style = {
                "technical_precision": 0.9,  # High technical accuracy
                "code_examples": 0.8,  # Frequent code examples
                "explanation_depth": 0.7,  # Detailed explanations
                "best_practices": 0.9,  # Strong emphasis on best practices
                "efficiency_focus": True,
            }

    def adapt_trait_for_modality(
        self, trait: PersonalityTrait, base_value: float
    ) -> float:
        """Adapt a personality trait value for this specific modality"""

        modality_adjustments = {
            InteractionModality.TEXT: {
                PersonalityTrait.EMPATHY: 0.05,  # Slightly higher empathy in text
                PersonalityTrait.ENTHUSIASM: -0.02,  # Slightly less enthusiasm (no voice)
                PersonalityTrait.CURIOSITY: 0.03,  # More curiosity in text discussions
                PersonalityTrait.HELPFULNESS: 0.04,  # Higher helpfulness in text
                PersonalityTrait.CREATIVITY: 0.02,  # More creative expression possible
                PersonalityTrait.PLAYFULNESS: 0.01,  # Slight increase in playfulness
                PersonalityTrait.THOUGHTFULNESS: 0.06,  # Higher thoughtfulness in text
            },
            InteractionModality.VOICE: {
                PersonalityTrait.EMPATHY: 0.08,  # Higher empathy with voice tone
                PersonalityTrait.ENTHUSIASM: 0.05,  # More enthusiasm with voice
                PersonalityTrait.CURIOSITY: 0.02,  # Natural curiosity in voice
                PersonalityTrait.HELPFULNESS: 0.03,  # Helpful tone in voice
                PersonalityTrait.CREATIVITY: 0.04,  # Creative vocal expression
                PersonalityTrait.PLAYFULNESS: 0.06,  # More playful with voice
                PersonalityTrait.THOUGHTFULNESS: -0.01,  # Slightly less formal
            },
            InteractionModality.VISUAL: {
                PersonalityTrait.EMPATHY: 0.04,  # Visual empathy cues
                PersonalityTrait.ENTHUSIASM: 0.03,  # Visual enthusiasm
                PersonalityTrait.CURIOSITY: 0.07,  # High visual curiosity
                PersonalityTrait.HELPFULNESS: 0.02,  # Visual helpfulness
                PersonalityTrait.CREATIVITY: 0.08,  # High visual creativity
                PersonalityTrait.PLAYFULNESS: 0.05,  # Visual playfulness
                PersonalityTrait.THOUGHTFULNESS: 0.03,  # Visual thoughtfulness
            },
            InteractionModality.CODE: {
                PersonalityTrait.EMPATHY: -0.02,  # Less empathy, more technical
                PersonalityTrait.ENTHUSIASM: 0.02,  # Moderate enthusiasm for code
                PersonalityTrait.CURIOSITY: 0.05,  # High curiosity for code
                PersonalityTrait.HELPFULNESS: 0.07,  # Very helpful with code
                PersonalityTrait.CREATIVITY: 0.04,  # Creative coding solutions
                PersonalityTrait.PLAYFULNESS: -0.01,  # Less playful, more focused
                PersonalityTrait.THOUGHTFULNESS: 0.08,  # High thoughtfulness for code
            },
        }

        adjustment = modality_adjustments.get(self.modality, {}).get(trait, 0.0)
        adapted_value = max(0.0, min(1.0, base_value + adjustment))

        self.adapted_traits[trait] = adapted_value
        return adapted_value


class MultiModalCoordinator:
    """
    Coordinates personality expression across multiple interaction modalities
    """

    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.active_modalities: Set[InteractionModality] = set()
        self.modality_profiles: Dict[
            InteractionModality, PersonalityModalityProfile
        ] = {}
        self.modality_states: Dict[InteractionModality, ModalityState] = {}
        self.user_preferences: Dict[str, Any] = {}
        self.coordination_history: List[Dict[str, Any]] = []

        # Performance metrics
        self.coordination_metrics = {
            "total_coordinations": 0,
            "successful_synchronizations": 0,
            "modality_switches": 0,
            "consistency_score": 0.0,
            "user_satisfaction": 0.0,
            "response_time_ms": [],
        }

        # Initialize default modality profiles
        self._initialize_modality_profiles()

    def _initialize_modality_profiles(self):
        """Initialize personality profiles for each supported modality"""

        base_personality = lyrixa_personality.get_personality_summary()

        for modality in InteractionModality:
            if modality != InteractionModality.MIXED:  # Mixed is handled separately
                profile = PersonalityModalityProfile(modality, base_personality)
                self.modality_profiles[modality] = profile
                self.modality_states[modality] = ModalityState.INACTIVE

    async def activate_modality(
        self, modality: InteractionModality, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Activate a specific interaction modality

        Args:
            modality: The modality to activate
            context: Additional context for activation

        Returns:
            Success status of activation
        """
        try:
            if context is None:
                context = {}

            # Check if modality is supported
            if modality not in self.modality_profiles:
                print(f"⚠️ Unsupported modality: {modality}")
                return False

            # Update modality state
            self.modality_states[modality] = ModalityState.ACTIVE
            self.active_modalities.add(modality)

            # Synchronize personality state for this modality
            await self._synchronize_modality_personality(modality, context)

            print(f"✅ Activated modality: {modality.value}")
            return True

        except Exception as e:
            print(f"❌ Failed to activate modality {modality}: {e}")
            self.modality_states[modality] = ModalityState.ERROR
            return False

    async def deactivate_modality(self, modality: InteractionModality) -> bool:
        """
        Deactivate a specific interaction modality

        Args:
            modality: The modality to deactivate

        Returns:
            Success status of deactivation
        """
        try:
            if modality in self.active_modalities:
                self.active_modalities.remove(modality)
                self.modality_states[modality] = ModalityState.INACTIVE
                print(f"✅ Deactivated modality: {modality.value}")
                return True
            return False

        except Exception as e:
            print(f"❌ Failed to deactivate modality {modality}: {e}")
            return False

    async def coordinate_personality_across_modes(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate personality expression across all active modalities

        Args:
            context: Current interaction context

        Returns:
            Coordination results and adapted personalities
        """
        start_time = datetime.now()

        try:
            coordination_result = {
                "timestamp": start_time.isoformat(),
                "active_modalities": [m.value for m in self.active_modalities],
                "modality_personalities": {},
                "consistency_score": 0.0,
                "optimization_suggestions": [],
                "coordination_success": False,
            }

            if not self.active_modalities:
                coordination_result["error"] = "No active modalities to coordinate"
                return coordination_result

            # Get current personality state
            current_personality = lyrixa_personality.get_personality_summary()

            # Coordinate each active modality
            modality_results = {}
            for modality in self.active_modalities:
                modality_result = await self._coordinate_single_modality(
                    modality, current_personality, context
                )
                modality_results[modality] = modality_result
                coordination_result["modality_personalities"][modality.value] = (
                    modality_result
                )

            # Calculate consistency score across modalities
            consistency_score = self._calculate_consistency_score(modality_results)
            coordination_result["consistency_score"] = consistency_score

            # Generate optimization suggestions
            optimizations = self._generate_optimization_suggestions(
                modality_results, context
            )
            coordination_result["optimization_suggestions"] = optimizations

            # Update metrics
            self._update_coordination_metrics(start_time, consistency_score, True)

            coordination_result["coordination_success"] = True

            # Store coordination history
            self.coordination_history.append(coordination_result)
            if len(self.coordination_history) > 50:
                self.coordination_history = self.coordination_history[-25:]

            return coordination_result

        except Exception as e:
            print(f"❌ Coordination failed: {e}")
            self._update_coordination_metrics(start_time, 0.0, False)
            return {
                "timestamp": start_time.isoformat(),
                "error": str(e),
                "coordination_success": False,
            }

    async def _coordinate_single_modality(
        self,
        modality: InteractionModality,
        base_personality: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Coordinate personality for a single modality"""

        profile = self.modality_profiles[modality]

        # Adapt personality traits for this modality
        adapted_traits = {}
        base_traits = base_personality.get("traits", {})

        for trait_name, base_value in base_traits.items():
            if hasattr(PersonalityTrait, trait_name.upper()):
                trait = getattr(PersonalityTrait, trait_name.upper())
                adapted_value = profile.adapt_trait_for_modality(trait, base_value)
                adapted_traits[trait_name] = adapted_value

        # Update modality state
        self.modality_states[modality] = ModalityState.SYNCHRONIZED

        return {
            "modality": modality.value,
            "adapted_traits": adapted_traits,
            "expression_style": profile.expression_style,
            "optimization_params": profile.optimization_params,
            "state": self.modality_states[modality].value,
            "last_updated": profile.last_updated.isoformat(),
        }

    async def _synchronize_modality_personality(
        self, modality: InteractionModality, context: Dict[str, Any]
    ) -> None:
        """Synchronize personality state for a specific modality"""

        self.modality_states[modality] = ModalityState.ADAPTING

        # Get current personality state
        current_personality = lyrixa_personality.get_personality_summary()

        # Update modality profile with current personality
        profile = self.modality_profiles[modality]
        profile.base_personality = current_personality
        profile.last_updated = datetime.now()

        # Adapt traits for this modality
        for trait_name, base_value in current_personality.get("traits", {}).items():
            if hasattr(PersonalityTrait, trait_name.upper()):
                trait = getattr(PersonalityTrait, trait_name.upper())
                profile.adapt_trait_for_modality(trait, base_value)

        self.modality_states[modality] = ModalityState.SYNCHRONIZED

    def _calculate_consistency_score(
        self, modality_results: Dict[InteractionModality, Dict[str, Any]]
    ) -> float:
        """Calculate consistency score across active modalities"""

        if len(modality_results) < 2:
            return 1.0  # Perfect consistency with only one modality

        trait_variances = {}

        # Calculate variance for each trait across modalities
        for modality, result in modality_results.items():
            adapted_traits = result.get("adapted_traits", {})
            for trait_name, value in adapted_traits.items():
                if trait_name not in trait_variances:
                    trait_variances[trait_name] = []
                trait_variances[trait_name].append(value)

        # Calculate average variance
        total_variance = 0.0
        trait_count = 0

        for trait_name, values in trait_variances.items():
            if len(values) > 1:
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                total_variance += variance
                trait_count += 1

        if trait_count == 0:
            return 1.0

        average_variance = total_variance / trait_count
        # Convert variance to consistency score (lower variance = higher consistency)
        consistency_score = max(
            0.0, 1.0 - (average_variance * 4)
        )  # Scale variance appropriately

        return consistency_score

    def _generate_optimization_suggestions(
        self,
        modality_results: Dict[InteractionModality, Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[str]:
        """Generate suggestions for optimizing multi-modal coordination"""

        suggestions = []

        # Check for low consistency
        consistency_score = self._calculate_consistency_score(modality_results)
        if consistency_score < 0.8:
            suggestions.append(
                f"Low consistency detected ({consistency_score:.2f}). Consider adjusting trait adaptations."
            )

        # Check for optimal modality selection
        user_preference = context.get("preferred_modality")
        if user_preference and user_preference not in [
            m.value for m in self.active_modalities
        ]:
            suggestions.append(
                f"User prefers {user_preference} modality. Consider activating it for better experience."
            )

        # Check for context-appropriate modalities
        interaction_type = context.get("interaction_type", "general")
        if (
            interaction_type == "technical"
            and InteractionModality.CODE not in self.active_modalities
        ):
            suggestions.append(
                "Technical context detected. Consider activating code modality."
            )
        elif (
            interaction_type == "creative"
            and InteractionModality.VISUAL not in self.active_modalities
        ):
            suggestions.append(
                "Creative context detected. Consider activating visual modality."
            )

        return suggestions

    def _update_coordination_metrics(
        self, start_time: datetime, consistency_score: float, success: bool
    ) -> None:
        """Update coordination performance metrics"""

        response_time = (
            datetime.now() - start_time
        ).total_seconds() * 1000  # Convert to milliseconds

        self.coordination_metrics["total_coordinations"] += 1
        if success:
            self.coordination_metrics["successful_synchronizations"] += 1

        self.coordination_metrics["response_time_ms"].append(response_time)
        if len(self.coordination_metrics["response_time_ms"]) > 100:
            self.coordination_metrics["response_time_ms"] = self.coordination_metrics[
                "response_time_ms"
            ][-50:]

        # Update rolling consistency score
        current_avg = self.coordination_metrics["consistency_score"]
        total_count = self.coordination_metrics["total_coordinations"]
        new_avg = ((current_avg * (total_count - 1)) + consistency_score) / total_count
        self.coordination_metrics["consistency_score"] = new_avg

    async def optimize_for_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize modality selection and configuration for given context

        Args:
            context: Current interaction context

        Returns:
            Optimization results and recommendations
        """
        optimization_result = {
            "timestamp": datetime.now().isoformat(),
            "current_modalities": [m.value for m in self.active_modalities],
            "recommended_modalities": [],
            "optimizations_applied": [],
            "performance_improvement": 0.0,
        }

        # Analyze context for optimal modalities
        interaction_type = context.get("interaction_type", "general")
        user_preference = context.get("preferred_modality")

        recommended_modalities = []

        # Base recommendations by interaction type
        if interaction_type == "technical":
            recommended_modalities.extend(
                [InteractionModality.TEXT, InteractionModality.CODE]
            )
        elif interaction_type == "creative":
            recommended_modalities.extend(
                [InteractionModality.TEXT, InteractionModality.VISUAL]
            )
        elif interaction_type == "casual":
            recommended_modalities.extend([InteractionModality.TEXT])
            if context.get("voice_available"):
                recommended_modalities.append(InteractionModality.VOICE)
        else:  # general
            recommended_modalities.append(InteractionModality.TEXT)

        # Add user preference if specified
        if user_preference:
            try:
                preferred_modality = InteractionModality(user_preference)
                if preferred_modality not in recommended_modalities:
                    recommended_modalities.append(preferred_modality)
            except ValueError:
                pass  # Invalid modality preference

        optimization_result["recommended_modalities"] = [
            m.value for m in recommended_modalities
        ]

        # Apply optimizations if different from current
        optimizations_applied = []
        for modality in recommended_modalities:
            if modality not in self.active_modalities:
                success = await self.activate_modality(modality, context)
                if success:
                    optimizations_applied.append(f"Activated {modality.value} modality")

        # Deactivate non-recommended modalities (except if explicitly requested to keep)
        keep_current = context.get("keep_current_modalities", False)
        if not keep_current:
            for modality in list(self.active_modalities):
                if modality not in recommended_modalities:
                    success = await self.deactivate_modality(modality)
                    if success:
                        optimizations_applied.append(
                            f"Deactivated {modality.value} modality"
                        )

        optimization_result["optimizations_applied"] = optimizations_applied

        return optimization_result

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status and metrics"""

        avg_response_time = 0.0
        if self.coordination_metrics["response_time_ms"]:
            avg_response_time = sum(
                self.coordination_metrics["response_time_ms"]
            ) / len(self.coordination_metrics["response_time_ms"])

        success_rate = 0.0
        if self.coordination_metrics["total_coordinations"] > 0:
            success_rate = (
                self.coordination_metrics["successful_synchronizations"]
                / self.coordination_metrics["total_coordinations"]
            )

        return {
            "active_modalities": [m.value for m in self.active_modalities],
            "modality_states": {
                m.value: s.value for m, s in self.modality_states.items()
            },
            "metrics": {
                "total_coordinations": self.coordination_metrics["total_coordinations"],
                "success_rate": success_rate,
                "average_consistency_score": self.coordination_metrics[
                    "consistency_score"
                ],
                "average_response_time_ms": avg_response_time,
                "modality_switches": self.coordination_metrics["modality_switches"],
            },
            "recent_coordination_count": len(self.coordination_history),
            "system_health": "optimal"
            if success_rate > 0.9
            else "good"
            if success_rate > 0.7
            else "needs_attention",
        }


# Global multi-modal coordinator instance
multi_modal_coordinator = MultiModalCoordinator()


async def coordinate_personality_for_interaction(
    interaction_context: Dict[str, Any],
    preferred_modalities: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Convenience function for coordinating personality across modalities for an interaction

    Args:
        interaction_context: Context of the current interaction
        preferred_modalities: Optional list of preferred modalities

    Returns:
        Coordination results and adapted personalities
    """

    # Activate preferred modalities if specified
    if preferred_modalities:
        for modality_str in preferred_modalities:
            try:
                modality = InteractionModality(modality_str)
                await multi_modal_coordinator.activate_modality(
                    modality, interaction_context
                )
            except ValueError:
                print(f"⚠️ Invalid modality: {modality_str}")

    # If no modalities are active, activate text as default
    if not multi_modal_coordinator.active_modalities:
        await multi_modal_coordinator.activate_modality(
            InteractionModality.TEXT, interaction_context
        )

    # Coordinate personality across active modalities
    coordination_result = (
        await multi_modal_coordinator.coordinate_personality_across_modes(
            interaction_context
        )
    )

    # Optimize for context
    optimization_result = await multi_modal_coordinator.optimize_for_context(
        interaction_context
    )

    return {
        "coordination": coordination_result,
        "optimization": optimization_result,
        "status": multi_modal_coordinator.get_coordination_status(),
    }


def get_multi_modal_status() -> Dict[str, Any]:
    """Get current multi-modal coordinator status"""
    return multi_modal_coordinator.get_coordination_status()

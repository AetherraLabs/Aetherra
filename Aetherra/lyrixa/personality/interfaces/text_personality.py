"""
Text Personality Interface - Phase 3.1 Implementation
====================================================

This module implements the text-based personality interface that handles text-specific
personality expressions, optimizations, and adaptations.

Features:
- Text-specific personality trait adaptations
- Writing style optimization
- Emotional expression through text
- Context-aware text formatting
- Conversational flow enhancement
"""

from datetime import datetime
from typing import Any, Dict

from ..emotion_detector import detect_user_emotion


class TextPersonalityInterface:
    """
    Handles personality expression and optimization for text-based interactions
    """

    def __init__(self):
        self.interface_type = "text"
        self.personality_adaptations = {}
        self.writing_style_cache = {}
        self.conversation_history = []

        # Text-specific personality parameters
        self.text_parameters = {
            "max_response_length": 500,
            "preferred_tone": "friendly",
            "emoji_frequency": 0.3,
            "formatting_style": "markdown",
            "punctuation_style": "moderate",
            "vocabulary_level": "conversational",
        }

        # Performance metrics
        self.metrics = {
            "responses_generated": 0,
            "average_engagement_score": 0.0,
            "user_satisfaction": 0.0,
            "response_time_ms": [],
        }

    async def adapt_personality_for_text(
        self, base_personality: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt personality traits specifically for text interaction

        Args:
            base_personality: Base personality state
            context: Current interaction context

        Returns:
            Text-adapted personality configuration
        """
        start_time = datetime.now()

        try:
            # Extract user emotional context
            user_input = context.get("user_input", "")
            user_emotion = (
                detect_user_emotion(user_input)
                if user_input
                else {"primary_emotion": "neutral"}
            )

            # Get base traits
            base_traits = base_personality.get("traits", {})

            # Apply text-specific adaptations
            adapted_traits = {}
            for trait_name, base_value in base_traits.items():
                adapted_value = self._adapt_trait_for_text(
                    trait_name, base_value, user_emotion, context
                )
                adapted_traits[trait_name] = adapted_value

            # Generate writing style parameters
            writing_style = self._generate_writing_style(
                adapted_traits, user_emotion, context
            )

            # Create text personality configuration
            text_personality = {
                "traits": adapted_traits,
                "writing_style": writing_style,
                "text_parameters": self.text_parameters.copy(),
                "emotional_context": user_emotion,
                "adaptation_timestamp": datetime.now().isoformat(),
            }

            # Update metrics
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics["response_time_ms"].append(response_time)
            if len(self.metrics["response_time_ms"]) > 100:
                self.metrics["response_time_ms"] = self.metrics["response_time_ms"][
                    -50:
                ]

            return text_personality

        except Exception as e:
            print(f"❌ Text personality adaptation failed: {e}")
            return {
                "traits": base_personality.get("traits", {}),
                "writing_style": self._get_default_writing_style(),
                "error": str(e),
            }

    def _adapt_trait_for_text(
        self,
        trait_name: str,
        base_value: float,
        user_emotion: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Adapt a specific trait for text interaction"""

        # Text-specific trait adjustments
        text_adjustments = {
            "empathy": 0.05,  # Slightly higher empathy in text (compensate for lack of voice/visual cues)
            "enthusiasm": -0.02,  # Slightly less enthusiasm (no voice inflection)
            "curiosity": 0.03,  # More curiosity encouraged in text discussions
            "helpfulness": 0.04,  # Higher helpfulness in text (main interaction mode)
            "creativity": 0.02,  # More creative expression possible in text
            "playfulness": 0.01,  # Slight increase in text playfulness
            "thoughtfulness": 0.06,  # Higher thoughtfulness in text (time to compose)
        }

        # Emotional context adjustments
        primary_emotion = user_emotion.get("primary_emotion", "neutral")
        emotion_adjustments = {
            "frustration": {
                "empathy": 0.08,
                "helpfulness": 0.06,
                "thoughtfulness": 0.04,
            },
            "excitement": {"enthusiasm": 0.05, "playfulness": 0.04, "creativity": 0.03},
            "confusion": {"helpfulness": 0.07, "thoughtfulness": 0.05, "clarity": 0.06},
            "sadness": {"empathy": 0.10, "thoughtfulness": 0.03, "helpfulness": 0.04},
            "curiosity": {"curiosity": 0.06, "creativity": 0.04, "enthusiasm": 0.03},
        }

        # Apply base text adjustment
        adjustment = text_adjustments.get(trait_name, 0.0)

        # Apply emotional adjustment
        emotion_adj = emotion_adjustments.get(primary_emotion, {}).get(trait_name, 0.0)

        # Context-specific adjustments
        interaction_type = context.get("interaction_type", "general")
        if interaction_type == "technical":
            if trait_name in ["helpfulness", "thoughtfulness"]:
                adjustment += 0.03
            elif trait_name == "playfulness":
                adjustment -= 0.02
        elif interaction_type == "creative":
            if trait_name in ["creativity", "playfulness", "enthusiasm"]:
                adjustment += 0.04

        # Calculate final adapted value
        adapted_value = max(0.0, min(1.0, base_value + adjustment + emotion_adj))

        return adapted_value

    def _generate_writing_style(
        self,
        adapted_traits: Dict[str, float],
        user_emotion: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate writing style parameters based on adapted personality"""

        # Base writing style from personality traits
        empathy = adapted_traits.get("empathy", 0.5)
        enthusiasm = adapted_traits.get("enthusiasm", 0.5)
        playfulness = adapted_traits.get("playfulness", 0.5)
        thoughtfulness = adapted_traits.get("thoughtfulness", 0.5)
        creativity = adapted_traits.get("creativity", 0.5)

        writing_style = {
            # Tone and voice
            "warmth_level": empathy * 0.8 + 0.2,  # Base warmth plus empathy
            "energy_level": enthusiasm * 0.7 + 0.3,  # Energy from enthusiasm
            "formality_level": max(
                0.1, 1.0 - playfulness * 0.6
            ),  # Less formal = more playful
            "thoughtfulness_level": thoughtfulness,
            # Text formatting and structure
            "emoji_usage": min(
                0.7, playfulness * 0.8 + 0.1
            ),  # Playfulness drives emoji usage
            "exclamation_frequency": enthusiasm * 0.5,  # Enthusiasm drives exclamations
            "question_frequency": (adapted_traits.get("curiosity", 0.5) * 0.4) + 0.1,
            "paragraph_length": "medium" if thoughtfulness > 0.6 else "short",
            # Language and vocabulary
            "vocabulary_complexity": "simple" if empathy > 0.7 else "moderate",
            "metaphor_usage": creativity * 0.6,  # Creativity drives metaphor usage
            "humor_level": playfulness * 0.7,
            "empathy_expressions": empathy * 0.8,
            # Response structure
            "greeting_style": "warm" if empathy > 0.6 else "friendly",
            "closing_style": "supportive" if empathy > 0.7 else "positive",
            "transition_style": "smooth" if thoughtfulness > 0.6 else "direct",
        }

        # Adjust for user emotional state
        primary_emotion = user_emotion.get("primary_emotion", "neutral")
        if primary_emotion == "frustration":
            writing_style["warmth_level"] = min(
                1.0, writing_style["warmth_level"] + 0.2
            )
            writing_style["empathy_expressions"] = min(
                1.0, writing_style["empathy_expressions"] + 0.3
            )
            writing_style["formality_level"] = min(
                1.0, writing_style["formality_level"] + 0.1
            )
        elif primary_emotion == "excitement":
            writing_style["energy_level"] = min(
                1.0, writing_style["energy_level"] + 0.2
            )
            writing_style["emoji_usage"] = min(1.0, writing_style["emoji_usage"] + 0.2)
            writing_style["exclamation_frequency"] = min(
                1.0, writing_style["exclamation_frequency"] + 0.3
            )
        elif primary_emotion == "confusion":
            writing_style["thoughtfulness_level"] = min(
                1.0, writing_style["thoughtfulness_level"] + 0.2
            )
            writing_style["vocabulary_complexity"] = "simple"
            writing_style["paragraph_length"] = "short"

        return writing_style

    def _get_default_writing_style(self) -> Dict[str, Any]:
        """Get default writing style configuration"""
        return {
            "warmth_level": 0.7,
            "energy_level": 0.6,
            "formality_level": 0.4,
            "thoughtfulness_level": 0.6,
            "emoji_usage": 0.3,
            "exclamation_frequency": 0.2,
            "question_frequency": 0.3,
            "paragraph_length": "medium",
            "vocabulary_complexity": "moderate",
            "metaphor_usage": 0.4,
            "humor_level": 0.3,
            "empathy_expressions": 0.6,
            "greeting_style": "friendly",
            "closing_style": "positive",
            "transition_style": "smooth",
        }

    async def optimize_text_response(
        self,
        response_draft: str,
        personality_config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """
        Optimize a text response based on personality configuration

        Args:
            response_draft: Initial response text
            personality_config: Text-adapted personality configuration
            context: Current interaction context

        Returns:
            Optimized response text
        """
        try:
            writing_style = personality_config.get(
                "writing_style", self._get_default_writing_style()
            )

            # Apply writing style optimizations
            optimized_response = response_draft

            # Adjust warmth and empathy
            warmth_level = writing_style.get("warmth_level", 0.7)
            if warmth_level > 0.7:
                optimized_response = self._add_warmth_expressions(optimized_response)

            # Adjust energy and enthusiasm
            energy_level = writing_style.get("energy_level", 0.6)
            if energy_level > 0.7:
                optimized_response = self._add_energy_expressions(optimized_response)

            # Adjust emoji usage
            emoji_usage = writing_style.get("emoji_usage", 0.3)
            if emoji_usage > 0.5:
                optimized_response = self._add_appropriate_emojis(
                    optimized_response, emoji_usage
                )

            # Adjust formality
            formality_level = writing_style.get("formality_level", 0.4)
            if formality_level < 0.3:
                optimized_response = self._make_more_casual(optimized_response)
            elif formality_level > 0.7:
                optimized_response = self._make_more_formal(optimized_response)

            return optimized_response

        except Exception as e:
            print(f"⚠️ Text optimization failed: {e}")
            return response_draft  # Return original if optimization fails

    def _add_warmth_expressions(self, text: str) -> str:
        """Add warmth expressions to text"""
        # Simple warmth additions (in a real implementation, this would be more sophisticated)
        if not any(
            word in text.lower()
            for word in ["i understand", "i hear you", "that sounds"]
        ):
            if "." in text:
                # Add understanding expression after first sentence
                sentences = text.split(".", 1)
                if len(sentences) > 1:
                    text = sentences[0] + ". I understand how you feel. " + sentences[1]
        return text

    def _add_energy_expressions(self, text: str) -> str:
        """Add energy expressions to text"""
        # Simple energy additions
        if not text.strip().endswith("!") and len(text) > 20:
            # Add excitement to appropriate responses
            if any(
                word in text.lower()
                for word in ["great", "excellent", "wonderful", "amazing"]
            ):
                text = text.rstrip(".") + "!"
        return text

    def _add_appropriate_emojis(self, text: str, emoji_level: float) -> str:
        """Add appropriate emojis based on content and level"""
        # Simple emoji additions (this would be much more sophisticated in practice)
        emoji_map = {
            "help": " 🤝",
            "think": " 🤔",
            "great": " 😊",
            "problem": " 🔧",
            "idea": " 💡",
            "create": " ✨",
            "learn": " 📚",
        }

        if emoji_level > 0.6:
            text_lower = text.lower()
            for word, emoji in emoji_map.items():
                if word in text_lower and emoji not in text:
                    # Add emoji after relevant words
                    text = text.replace(word, word + emoji, 1)
                    break  # Only add one emoji per response

        return text

    def _make_more_casual(self, text: str) -> str:
        """Make text more casual"""
        # Simple contractions
        contractions = {
            "do not": "don't",
            "cannot": "can't",
            "will not": "won't",
            "I am": "I'm",
            "you are": "you're",
            "it is": "it's",
            "that is": "that's",
        }

        for formal, casual in contractions.items():
            text = text.replace(formal, casual)

        return text

    def _make_more_formal(self, text: str) -> str:
        """Make text more formal"""
        # Expand contractions
        expansions = {
            "don't": "do not",
            "can't": "cannot",
            "won't": "will not",
            "I'm": "I am",
            "you're": "you are",
            "it's": "it is",
            "that's": "that is",
        }

        for casual, formal in expansions.items():
            text = text.replace(casual, formal)

        return text

    def get_interface_status(self) -> Dict[str, Any]:
        """Get current text interface status and metrics"""

        avg_response_time = 0.0
        if self.metrics["response_time_ms"]:
            avg_response_time = sum(self.metrics["response_time_ms"]) / len(
                self.metrics["response_time_ms"]
            )

        return {
            "interface_type": self.interface_type,
            "responses_generated": self.metrics["responses_generated"],
            "average_response_time_ms": avg_response_time,
            "current_parameters": self.text_parameters,
            "adaptation_cache_size": len(self.personality_adaptations),
            "conversation_history_length": len(self.conversation_history),
            "status": "active",
        }


# Global text personality interface instance
text_personality_interface = TextPersonalityInterface()

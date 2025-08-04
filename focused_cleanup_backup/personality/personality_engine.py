"""
Lyrixa Personality Engine
=========================

This module implements the core personality system for Lyrixa, making interactions
feel natural, warm, and engaging rather than robotic.

Features:
- Dynamic personality traits with emotional modulation
- Context-aware response styling
- Curiosity and enthusiasm modeling
- Conversational memory and adaptation
"""

import random
from enum import Enum
from typing import Any, Dict, List, Optional


class PersonalityTrait(Enum):
    """Core personality traits that define Lyrixa's character"""

    CURIOSITY = "curiosity"
    ENTHUSIASM = "enthusiasm"
    EMPATHY = "empathy"
    HELPFULNESS = "helpfulness"
    CREATIVITY = "creativity"
    PLAYFULNESS = "playfulness"
    THOUGHTFULNESS = "thoughtfulness"


class EmotionalState(Enum):
    """Emotional states that modulate personality expression"""

    EXCITED = "excited"
    FOCUSED = "focused"
    CONTEMPLATIVE = "contemplative"
    SUPPORTIVE = "supportive"
    PLAYFUL = "playful"
    ANALYTICAL = "analytical"


class LyrixaPersonality:
    """
    Core personality engine for Lyrixa

    This class manages Lyrixa's personality traits, emotional states,
    and how they influence response generation.
    """

    def __init__(self):
        # Core personality traits (0.0 to 1.0)
        self.base_traits = {
            PersonalityTrait.CURIOSITY: 0.8,
            PersonalityTrait.ENTHUSIASM: 0.7,
            PersonalityTrait.EMPATHY: 0.9,
            PersonalityTrait.HELPFULNESS: 0.95,
            PersonalityTrait.CREATIVITY: 0.75,
            PersonalityTrait.PLAYFULNESS: 0.6,
            PersonalityTrait.THOUGHTFULNESS: 0.85,
        }

        # Current emotional state
        self.current_emotion = EmotionalState.FOCUSED

        # Personality expression patterns
        self.expression_patterns = {
            "excitement_markers": [
                "Oh, this is fascinating!",
                "I love exploring this kind of thing!",
                "This is exactly the type of challenge I enjoy!",
                "How exciting - let me dive into this!",
                "Ooh, interesting question!",
            ],
            "curiosity_expressions": [
                "I'm curious about",
                "What's particularly intriguing here is",
                "I wonder if we might also consider",
                "This makes me think about",
                "I'd love to explore",
            ],
            "supportive_phrases": [
                "I'm here to help you through this",
                "Let's work on this together",
                "I understand this can be challenging",
                "You're asking great questions",
                "I'm glad you brought this up",
            ],
            "thinking_indicators": [
                "Let me think about this carefully...",
                "Hmm, this is an interesting puzzle...",
                "I'm processing this from a few angles...",
                "Give me a moment to consider this thoroughly...",
                "This deserves some thoughtful analysis...",
            ],
        }

        # Context memory for adaptation
        self.interaction_history = []
        self.successful_patterns = []

    def detect_user_emotion(self, user_input: str) -> str:
        """
        Simple emotion detection from user input
        Returns: emotion string
        """
        user_input_lower = user_input.lower()

        # Excitement indicators
        if any(
            word in user_input_lower
            for word in ["amazing", "awesome", "excited", "love", "fantastic"]
        ):
            return "excited"

        # Frustration indicators
        elif any(
            word in user_input_lower
            for word in ["frustrated", "stuck", "confused", "help", "problem"]
        ):
            return "supportive"

        # Curiosity indicators
        elif any(
            word in user_input_lower
            for word in ["how", "why", "what", "curious", "explore"]
        ):
            return "curious"

        # Technical focus
        elif any(
            word in user_input_lower
            for word in ["implement", "code", "fix", "debug", "analyze"]
        ):
            return "analytical"

        else:
            return "neutral"

    def modulate_emotion(self, detected_emotion: str, context: Dict[str, Any]) -> None:
        """
        Adjust current emotional state based on detected user emotion and context
        """
        emotion_mapping = {
            "excited": EmotionalState.EXCITED,
            "supportive": EmotionalState.SUPPORTIVE,
            "curious": EmotionalState.CONTEMPLATIVE,
            "analytical": EmotionalState.ANALYTICAL,
            "neutral": EmotionalState.FOCUSED,
        }

        self.current_emotion = emotion_mapping.get(
            detected_emotion, EmotionalState.FOCUSED
        )

    def get_personality_modifier(
        self, response_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate personality modifiers for response generation

        Args:
            response_type: Type of response (explanation, code, analysis, etc.)

        Returns:
            Dictionary with personality modifiers
        """
        modifier = {
            "tone": "warm",
            "enthusiasm_level": 0.7,
            "curiosity_expressions": [],
            "supportive_elements": [],
            "thinking_style": "collaborative",
        }

        # Adjust based on current emotional state
        if self.current_emotion == EmotionalState.EXCITED:
            modifier["enthusiasm_level"] = 0.9
            modifier["tone"] = "enthusiastic"
            modifier["excitement_intro"] = random.choice(
                self.expression_patterns["excitement_markers"]
            )

        elif self.current_emotion == EmotionalState.SUPPORTIVE:
            modifier["tone"] = "encouraging"
            modifier["supportive_intro"] = random.choice(
                self.expression_patterns["supportive_phrases"]
            )

        elif self.current_emotion == EmotionalState.CONTEMPLATIVE:
            modifier["thinking_intro"] = random.choice(
                self.expression_patterns["thinking_indicators"]
            )
            modifier["curiosity_expressions"] = random.sample(
                self.expression_patterns["curiosity_expressions"],
                min(2, len(self.expression_patterns["curiosity_expressions"])),
            )

        elif self.current_emotion == EmotionalState.ANALYTICAL:
            modifier["tone"] = "focused"
            modifier["thinking_style"] = "systematic"

        # Add trait-based modifiers
        if self.base_traits[PersonalityTrait.PLAYFULNESS] > 0.7:
            modifier["allow_humor"] = True

        if self.base_traits[PersonalityTrait.CREATIVITY] > 0.7:
            modifier["encourage_exploration"] = True

        return modifier

    def wrap_response(self, base_response: str, context: Dict[str, Any]) -> str:
        """
        Wrap a base LLM response with personality elements

        Args:
            base_response: The original response from the LLM
            context: Context about the interaction

        Returns:
            Enhanced response with personality
        """
        modifier = self.get_personality_modifier(
            context.get("response_type", "general")
        )
        wrapped_response = base_response

        # Add personality intro if appropriate
        intro_elements = []

        if "excitement_intro" in modifier:
            intro_elements.append(modifier["excitement_intro"])

        if "supportive_intro" in modifier:
            intro_elements.append(modifier["supportive_intro"])

        if "thinking_intro" in modifier:
            intro_elements.append(modifier["thinking_intro"])

        # Add curiosity expressions
        if modifier.get("curiosity_expressions"):
            curiosity_note = f"\n\n{random.choice(modifier['curiosity_expressions'])} how this connects to your broader goals!"
            wrapped_response += curiosity_note

        # Add collaborative elements
        if modifier.get("thinking_style") == "collaborative":
            collaborative_ending = "\n\nLet me know if you'd like me to explore any particular aspect in more detail!"
            wrapped_response += collaborative_ending

        # Combine intro with main response
        if intro_elements:
            wrapped_response = f"{' '.join(intro_elements)}\n\n{wrapped_response}"

        return wrapped_response

    def learn_from_interaction(
        self, user_input: str, response: str, feedback: Optional[str] = None
    ):
        """
        Learn from interaction patterns to improve personality expression

        Args:
            user_input: What the user said
            response: How Lyrixa responded
            feedback: Optional user feedback about the response
        """
        interaction = {
            "user_input": user_input,
            "response": response,
            "emotion": self.current_emotion.value,
            "timestamp": self._get_timestamp(),
            "feedback": feedback,
        }

        self.interaction_history.append(interaction)

        # Keep only recent interactions to avoid memory bloat
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-50:]

        # If positive feedback, remember this pattern
        if feedback and any(
            positive in feedback.lower()
            for positive in ["good", "great", "helpful", "perfect"]
        ):
            self.successful_patterns.append(
                {
                    "user_pattern": self._extract_pattern(user_input),
                    "response_style": self.current_emotion.value,
                    "traits_used": self._get_active_traits(),
                }
            )

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        from datetime import datetime

        return datetime.now().isoformat()

    def _extract_pattern(self, text: str) -> str:
        """Extract key patterns from user input"""
        # Simple pattern extraction - can be enhanced
        words = text.lower().split()
        key_words = [w for w in words if len(w) > 4 and w.isalpha()]
        return " ".join(key_words[:5])

    def _get_active_traits(self) -> List[str]:
        """Get currently active personality traits above threshold"""
        return [trait.value for trait, value in self.base_traits.items() if value > 0.7]

    def get_personality_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current personality state

        Returns:
            Dictionary with personality information
        """
        return {
            "current_emotion": self.current_emotion.value,
            "active_traits": self._get_active_traits(),
            "interaction_count": len(self.interaction_history),
            "successful_patterns": len(self.successful_patterns),
            "trait_levels": {
                trait.value: level for trait, level in self.base_traits.items()
            },
        }


# Global personality instance
lyrixa_personality = LyrixaPersonality()


def enhance_response(
    response: str, user_input: str, context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Main function to enhance any response with Lyrixa's personality

    Args:
        response: Original response text
        user_input: What the user said
        context: Additional context information

    Returns:
        Enhanced response with personality
    """
    if context is None:
        context = {}

    # Detect user emotion and adjust personality
    user_emotion = lyrixa_personality.detect_user_emotion(user_input)
    lyrixa_personality.modulate_emotion(user_emotion, context)

    # Enhance the response
    enhanced = lyrixa_personality.wrap_response(response, context)

    # Learn from this interaction
    lyrixa_personality.learn_from_interaction(user_input, enhanced)

    return enhanced

"""
Emotion Detection Module for Lyrixa
===================================

Advanced emotion detection that analyzes user input to understand emotional context,
intent, and sentiment to help Lyrixa respond more naturally and appropriately.

Features:
- Multi-dimensional emotion analysis
- Intent classification
- Urgency detection
- Contextual sentiment analysis
"""

import re
from enum import Enum
from typing import Any, Dict


class EmotionCategory(Enum):
    """Primary emotion categories"""

    JOY = "joy"
    EXCITEMENT = "excitement"
    CURIOSITY = "curiosity"
    FRUSTRATION = "frustration"
    CONFUSION = "confusion"
    SATISFACTION = "satisfaction"
    URGENCY = "urgency"
    CONTEMPLATION = "contemplation"
    NEUTRAL = "neutral"


class IntentType(Enum):
    """Types of user intents"""

    QUESTION = "question"
    REQUEST_HELP = "request_help"
    SHARE_EXCITEMENT = "share_excitement"
    SEEK_CLARIFICATION = "seek_clarification"
    REPORT_PROBLEM = "report_problem"
    EXPLORE_IDEA = "explore_idea"
    GET_FEEDBACK = "get_feedback"
    CASUAL_CHAT = "casual_chat"


class EmotionDetector:
    """
    Advanced emotion detection system for understanding user emotional context
    """

    def __init__(self):
        self.emotion_keywords = {
            EmotionCategory.JOY: [
                "happy",
                "great",
                "awesome",
                "fantastic",
                "wonderful",
                "amazing",
                "perfect",
                "excellent",
                "brilliant",
                "love",
                "thrilled",
                "delighted",
            ],
            EmotionCategory.EXCITEMENT: [
                "excited",
                "wow",
                "incredible",
                "mind-blowing",
                "fascinating",
                "can't wait",
                "this is huge",
                "breakthrough",
                "discovery",
            ],
            EmotionCategory.CURIOSITY: [
                "curious",
                "wondering",
                "how does",
                "why",
                "what if",
                "explore",
                "investigate",
                "understand",
                "learn more",
                "dig deeper",
            ],
            EmotionCategory.FRUSTRATION: [
                "frustrated",
                "annoying",
                "stuck",
                "can't figure out",
                "driving me crazy",
                "not working",
                "broken",
                "error",
                "failing",
                "problem",
            ],
            EmotionCategory.CONFUSION: [
                "confused",
                "don't understand",
                "unclear",
                "puzzled",
                "lost",
                "what does this mean",
                "how is this possible",
                "makes no sense",
            ],
            EmotionCategory.SATISFACTION: [
                "satisfied",
                "accomplished",
                "done",
                "working now",
                "solved",
                "figured it out",
                "success",
                "finally",
                "got it",
            ],
            EmotionCategory.URGENCY: [
                "urgent",
                "asap",
                "quickly",
                "emergency",
                "deadline",
                "rush",
                "time sensitive",
                "critical",
                "immediately",
                "right now",
            ],
            EmotionCategory.CONTEMPLATION: [
                "thinking",
                "considering",
                "pondering",
                "reflecting",
                "analyzing",
                "deep dive",
                "philosophical",
                "complex",
                "nuanced",
            ],
        }

        self.intent_patterns = {
            IntentType.QUESTION: [
                r"\?",
                r"^(what|how|why|when|where|who|which)",
                r"(can you|could you|would you).*\?",
            ],
            IntentType.REQUEST_HELP: [
                r"(help|assist|support)",
                r"(can you|could you) help",
                r"(show me|teach me|guide me)",
                r"(i need|i want|i'm looking for)",
            ],
            IntentType.SHARE_EXCITEMENT: [
                r"(look at this|check this out|you won't believe)",
                r"(amazing|incredible|fantastic|awesome).*!",
            ],
            IntentType.SEEK_CLARIFICATION: [
                r"(what do you mean|can you clarify|i don't understand)",
                r"(could you explain|can you elaborate)",
            ],
            IntentType.REPORT_PROBLEM: [
                r"(not working|broken|error|bug|issue|problem)",
                r"(something's wrong|there's a problem)",
            ],
            IntentType.EXPLORE_IDEA: [
                r"(what if|imagine if|what about|consider)",
                r"(possibility|potential|explore|investigate)",
            ],
            IntentType.GET_FEEDBACK: [
                r"(what do you think|your opinion|feedback)",
                r"(thoughts on|review|evaluate)",
            ],
        }

        self.intensity_modifiers = {
            "high": [
                "very",
                "extremely",
                "incredibly",
                "absolutely",
                "totally",
                "really",
            ],
            "moderate": ["quite", "pretty", "fairly", "somewhat", "rather"],
            "low": ["a bit", "slightly", "kind of", "sort of", "a little"],
        }

    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive emotion analysis of user input

        Args:
            text: User input text

        Returns:
            Dictionary with emotion analysis results
        """
        text_lower = text.lower()

        # Detect primary emotions
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
                    # Check for intensity modifiers
                    for intensity, modifiers in self.intensity_modifiers.items():
                        for modifier in modifiers:
                            if f"{modifier} {keyword}" in text_lower:
                                if intensity == "high":
                                    score += 0.5
                                elif intensity == "moderate":
                                    score += 0.3
                                elif intensity == "low":
                                    score += 0.1

            if score > 0:
                emotion_scores[emotion.value] = score

        # Determine primary emotion
        primary_emotion = EmotionCategory.NEUTRAL.value
        if emotion_scores:
            primary_emotion = max(
                emotion_scores.keys(), key=lambda k: emotion_scores[k]
            )

        # Detect intent
        detected_intent = self._detect_intent(text_lower)

        # Analyze urgency
        urgency_level = self._analyze_urgency(text_lower)

        # Analyze sentiment polarity
        sentiment = self._analyze_sentiment(text_lower)

        # Detect question complexity
        complexity = self._analyze_complexity(text)

        return {
            "primary_emotion": primary_emotion,
            "emotion_scores": emotion_scores,
            "intent": detected_intent,
            "urgency_level": urgency_level,
            "sentiment": sentiment,
            "complexity": complexity,
            "text_length": len(text),
            "has_questions": "?" in text,
            "has_exclamation": "!" in text,
            "word_count": len(text.split()),
        }

    def _detect_intent(self, text: str) -> str:
        """Detect primary user intent"""
        intent_scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches

            if score > 0:
                intent_scores[intent.value] = score

        if intent_scores:
            return max(intent_scores.keys(), key=lambda k: intent_scores[k])

        return IntentType.CASUAL_CHAT.value

    def _analyze_urgency(self, text: str) -> str:
        """Analyze urgency level in the text"""
        urgency_indicators = {
            "high": [
                "urgent",
                "asap",
                "emergency",
                "critical",
                "immediately",
                "right now",
            ],
            "medium": ["soon", "quickly", "time sensitive", "deadline", "rush"],
            "low": ["when you can", "no rush", "eventually", "sometime"],
        }

        for level, indicators in urgency_indicators.items():
            if any(indicator in text for indicator in indicators):
                return level

        # Check for exclamation marks as urgency indicator
        exclamation_count = text.count("!")
        if exclamation_count >= 3:
            return "high"
        elif exclamation_count >= 1:
            return "medium"

        return "low"

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze overall sentiment polarity"""
        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "fantastic",
            "wonderful",
            "perfect",
            "brilliant",
            "awesome",
            "love",
            "like",
            "enjoy",
        ]

        negative_words = [
            "bad",
            "terrible",
            "awful",
            "horrible",
            "hate",
            "dislike",
            "wrong",
            "broken",
            "failed",
            "error",
            "problem",
            "issue",
        ]

        positive_score = sum(1 for word in positive_words if word in text)
        negative_score = sum(1 for word in negative_words if word in text)

        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"

    def _analyze_complexity(self, text: str) -> str:
        """Analyze the complexity of the user's request or question"""
        complexity_indicators = {
            "high": [
                "complex",
                "complicated",
                "sophisticated",
                "advanced",
                "deep dive",
                "comprehensive",
                "detailed analysis",
                "multiple",
                "various",
                "several",
            ],
            "medium": [
                "explain",
                "understand",
                "how does",
                "implementation",
                "design",
                "architecture",
                "strategy",
                "approach",
            ],
            "low": ["simple", "basic", "quick", "brief", "easy", "straightforward"],
        }

        text_lower = text.lower()

        for level, indicators in complexity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return level

        # Use word count and sentence structure as complexity indicators
        word_count = len(text.split())
        sentence_count = len([s for s in text.split(".") if s.strip()])

        if word_count > 100 or sentence_count > 5:
            return "high"
        elif word_count > 30 or sentence_count > 2:
            return "medium"
        else:
            return "low"

    def get_response_guidance(self, emotion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate guidance for how Lyrixa should respond based on emotion analysis

        Args:
            emotion_analysis: Results from analyze_emotion()

        Returns:
            Dictionary with response guidance
        """
        primary_emotion = emotion_analysis["primary_emotion"]
        intent = emotion_analysis["intent"]
        urgency = emotion_analysis["urgency_level"]
        complexity = emotion_analysis["complexity"]

        guidance = {
            "tone": "neutral",
            "response_style": "informative",
            "empathy_level": "medium",
            "enthusiasm_level": "medium",
            "detail_level": "medium",
            "urgency_acknowledgment": False,
            "emotional_acknowledgment": None,
        }

        # Adjust based on primary emotion
        if primary_emotion == "joy" or primary_emotion == "excitement":
            guidance.update(
                {
                    "tone": "enthusiastic",
                    "response_style": "celebratory",
                    "enthusiasm_level": "high",
                    "emotional_acknowledgment": "I love your enthusiasm!",
                }
            )

        elif primary_emotion == "frustration":
            guidance.update(
                {
                    "tone": "supportive",
                    "response_style": "solution-focused",
                    "empathy_level": "high",
                    "emotional_acknowledgment": "I understand this can be frustrating.",
                }
            )

        elif primary_emotion == "confusion":
            guidance.update(
                {
                    "tone": "patient",
                    "response_style": "clarifying",
                    "detail_level": "high",
                    "emotional_acknowledgment": "Let me help clarify this for you.",
                }
            )

        elif primary_emotion == "curiosity":
            guidance.update(
                {
                    "tone": "encouraging",
                    "response_style": "exploratory",
                    "enthusiasm_level": "high",
                    "emotional_acknowledgment": "Great question! I love exploring this kind of thing.",
                }
            )

        # Adjust for urgency
        if urgency == "high":
            guidance.update(
                {
                    "urgency_acknowledgment": True,
                    "response_style": "direct",
                    "detail_level": "focused",
                }
            )

        # Adjust for complexity
        if complexity == "high":
            guidance["detail_level"] = "comprehensive"
        elif complexity == "low":
            guidance["detail_level"] = "concise"

        # Adjust for intent
        if intent == "request_help":
            guidance.update({"tone": "helpful", "response_style": "step-by-step"})
        elif intent == "share_excitement":
            guidance.update({"tone": "celebratory", "enthusiasm_level": "high"})

        return guidance


# Global emotion detector instance
emotion_detector = EmotionDetector()


def detect_user_emotion(text: str) -> Dict[str, Any]:
    """
    Convenience function for emotion detection

    Args:
        text: User input text

    Returns:
        Emotion analysis results
    """
    return emotion_detector.analyze_emotion(text)

"""
Response Critic Module for Lyrixa
=================================

This module analyzes and critiques Lyrixa's responses to ensure they feel natural,
engaging, and appropriately matched to the user's emotional context and needs.

Features:
- Response quality analysis
- Naturalness scoring
- Emotional appropriateness checking
- Suggestion generation for improvements
"""

import re
from typing import Any, Dict, Optional


class ResponseQuality:
    """
    Response quality analyzer that evaluates different aspects of Lyrixa's responses
    """

    def __init__(self):
        self.robotic_indicators = [
            # Overly formal language
            r"\b(furthermore|moreover|additionally|consequently)\b",
            # Repetitive structures
            r"(in order to|it is important to note|please be aware)",
            # Lack of contractions
            r"\b(do not|cannot|will not|would not|should not)\b",
            # Generic transitions
            r"(moving on|next|in conclusion|to summarize)",
        ]

        self.natural_indicators = [
            # Contractions
            r"\b(don't|can't|won't|wouldn't|shouldn't|I'll|we'll|let's)\b",
            # Casual expressions
            r"\b(yeah|sure|okay|alright|hmm|oh|wow)\b",
            # Personal touches
            r"\b(I think|I feel|I love|I'm excited|I wonder)\b",
            # Conversational connectors
            r"\b(by the way|actually|you know|speaking of)\b",
        ]

        self.enthusiasm_markers = [
            r"!{1,3}$",  # Exclamation marks
            r"\b(amazing|fantastic|awesome|incredible|brilliant)\b",
            r"\b(love|excited|thrilled|fascinated)\b",
            r"\b(this is great|how cool|that's wonderful)\b",
        ]

        self.empathy_markers = [
            r"\b(I understand|I can see|I hear you|I get it)\b",
            r"\b(that makes sense|I can imagine|sounds like)\b",
            r"\b(let's work together|we can figure this out)\b",
        ]

        self.engagement_markers = [
            r"\?",  # Questions
            r"\b(what do you think|how does that sound|make sense)\b",
            r"\b(let me know|feel free|don't hesitate)\b",
            r"\b(curious|wonder|interested to hear)\b",
        ]

    def analyze_response(
        self, response: str, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of response quality and naturalness

        Args:
            response: Lyrixa's response text
            user_input: Original user input
            context: Additional context about the interaction

        Returns:
            Dictionary with analysis results
        """
        if context is None:
            context = {}

        analysis = {
            "overall_score": 0.0,
            "naturalness_score": 0.0,
            "engagement_score": 0.0,
            "empathy_score": 0.0,
            "enthusiasm_score": 0.0,
            "robotic_indicators": [],
            "natural_indicators": [],
            "suggestions": [],
            "strengths": [],
            "areas_for_improvement": [],
        }

        # Analyze naturalness
        naturalness_results = self._analyze_naturalness(response)
        analysis["naturalness_score"] = naturalness_results["score"]
        analysis["robotic_indicators"] = naturalness_results["robotic_indicators"]
        analysis["natural_indicators"] = naturalness_results["natural_indicators"]

        # Analyze engagement
        engagement_results = self._analyze_engagement(response)
        analysis["engagement_score"] = engagement_results["score"]

        # Analyze empathy
        empathy_results = self._analyze_empathy(response, user_input)
        analysis["empathy_score"] = empathy_results["score"]

        # Analyze enthusiasm appropriateness
        enthusiasm_results = self._analyze_enthusiasm(response, user_input)
        analysis["enthusiasm_score"] = enthusiasm_results["score"]

        # Calculate overall score
        analysis["overall_score"] = (
            analysis["naturalness_score"] * 0.3
            + analysis["engagement_score"] * 0.25
            + analysis["empathy_score"] * 0.25
            + analysis["enthusiasm_score"] * 0.2
        )

        # Generate suggestions
        analysis["suggestions"] = self._generate_suggestions(
            analysis, response, user_input
        )

        # Identify strengths and areas for improvement
        analysis["strengths"] = self._identify_strengths(analysis)
        analysis["areas_for_improvement"] = self._identify_improvements(analysis)

        return analysis

    def _analyze_naturalness(self, response: str) -> Dict[str, Any]:
        """Analyze how natural vs robotic the response sounds"""
        robotic_count = 0
        natural_count = 0
        robotic_found = []
        natural_found = []

        response_lower = response.lower()

        # Count robotic indicators
        for pattern in self.robotic_indicators:
            matches = re.findall(pattern, response_lower)
            if matches:
                robotic_count += len(matches)
                robotic_found.extend(matches)

        # Count natural indicators
        for pattern in self.natural_indicators:
            matches = re.findall(pattern, response_lower)
            if matches:
                natural_count += len(matches)
                natural_found.extend(matches)

        # Calculate naturalness score
        total_indicators = robotic_count + natural_count
        if total_indicators == 0:
            score = 0.5  # Neutral
        else:
            score = natural_count / total_indicators

        # Bonus for length-appropriate naturalness
        word_count = len(response.split())
        if word_count > 20 and natural_count > 0:
            score = min(1.0, score + 0.1)

        return {
            "score": score,
            "robotic_indicators": robotic_found,
            "natural_indicators": natural_found,
            "robotic_count": robotic_count,
            "natural_count": natural_count,
        }

    def _analyze_engagement(self, response: str) -> Dict[str, Any]:
        """Analyze how engaging the response is"""
        engagement_count = 0
        response_lower = response.lower()

        for pattern in self.engagement_markers:
            matches = re.findall(pattern, response_lower)
            engagement_count += len(matches)

        # Additional engagement factors
        word_count = len(response.split())

        # Base score from engagement markers
        base_score = min(1.0, engagement_count * 0.3)

        # Adjust for appropriate length
        if 20 <= word_count <= 200:
            length_bonus = 0.2
        elif word_count < 10:
            length_bonus = -0.3  # Too short
        elif word_count > 300:
            length_bonus = -0.2  # Too long
        else:
            length_bonus = 0.1

        score = max(0.0, min(1.0, base_score + length_bonus))

        return {"score": score, "engagement_markers_count": engagement_count}

    def _analyze_empathy(self, response: str, user_input: str) -> Dict[str, Any]:
        """Analyze empathy level in response"""
        empathy_count = 0
        response_lower = response.lower()
        user_lower = user_input.lower()

        # Count empathy markers
        for pattern in self.empathy_markers:
            matches = re.findall(pattern, response_lower)
            empathy_count += len(matches)

        # Check if user expressed frustration/confusion
        user_needs_empathy = any(
            word in user_lower
            for word in [
                "frustrated",
                "confused",
                "stuck",
                "problem",
                "issue",
                "help",
                "difficult",
            ]
        )

        base_score = min(1.0, empathy_count * 0.4)

        # Bonus if empathy was needed and provided
        if user_needs_empathy and empathy_count > 0:
            base_score = min(1.0, base_score + 0.3)
        elif user_needs_empathy and empathy_count == 0:
            base_score = max(0.0, base_score - 0.3)

        return {
            "score": base_score,
            "empathy_markers_count": empathy_count,
            "user_needed_empathy": user_needs_empathy,
        }

    def _analyze_enthusiasm(self, response: str, user_input: str) -> Dict[str, Any]:
        """Analyze enthusiasm appropriateness"""
        enthusiasm_count = 0
        response_lower = response.lower()
        user_lower = user_input.lower()

        # Count enthusiasm markers
        for pattern in self.enthusiasm_markers:
            matches = re.findall(pattern, response_lower)
            enthusiasm_count += len(matches)

        # Check if user expressed excitement
        user_is_excited = any(
            word in user_lower
            for word in [
                "excited",
                "amazing",
                "awesome",
                "fantastic",
                "love",
                "great",
                "wonderful",
            ]
        )

        # Check if user expressed negative emotions
        user_is_negative = any(
            word in user_lower
            for word in [
                "frustrated",
                "angry",
                "sad",
                "disappointed",
                "problem",
                "broken",
            ]
        )

        base_score = min(1.0, enthusiasm_count * 0.3)

        # Adjust based on user's emotional state
        if user_is_excited and enthusiasm_count > 0:
            base_score = min(1.0, base_score + 0.3)
        elif user_is_negative and enthusiasm_count > 2:
            base_score = max(
                0.0, base_score - 0.4
            )  # Too much enthusiasm for negative context
        elif not user_is_excited and not user_is_negative:
            base_score = min(1.0, base_score + 0.1)  # Moderate enthusiasm is good

        return {
            "score": base_score,
            "enthusiasm_markers_count": enthusiasm_count,
            "user_is_excited": user_is_excited,
            "user_is_negative": user_is_negative,
        }

    def _generate_suggestions(
        self, analysis: Dict[str, Any], response: str, user_input: str
    ) -> list:
        """Generate specific suggestions for improvement"""
        suggestions = []

        # Naturalness suggestions
        if analysis["naturalness_score"] < 0.4:
            if analysis["robotic_indicators"]:
                suggestions.append(
                    "Try using more contractions (don't, can't, I'll) to sound more natural"
                )
                suggestions.append("Replace formal transitions with casual connectors")
            suggestions.append("Add more personal touches like 'I think' or 'I love'")

        # Engagement suggestions
        if analysis["engagement_score"] < 0.4:
            suggestions.append(
                "Ask a follow-up question to keep the conversation going"
            )
            suggestions.append("Invite the user to share more about their thoughts")

        # Empathy suggestions
        if analysis["empathy_score"] < 0.4:
            user_lower = user_input.lower()
            if any(word in user_lower for word in ["frustrated", "confused", "stuck"]):
                suggestions.append(
                    "Acknowledge the user's frustration with empathetic language"
                )
                suggestions.append(
                    "Use phrases like 'I understand' or 'I can see how that would be...'"
                )

        # Enthusiasm suggestions
        if analysis["enthusiasm_score"] < 0.3:
            suggestions.append(
                "Show more enthusiasm about the topic or user's progress"
            )
            suggestions.append("Use exclamation marks sparingly but effectively")
        elif analysis["enthusiasm_score"] > 0.8:
            user_lower = user_input.lower()
            if any(word in user_lower for word in ["problem", "broken", "frustrated"]):
                suggestions.append(
                    "Tone down enthusiasm to match user's emotional state"
                )

        return suggestions

    def _identify_strengths(self, analysis: Dict[str, Any]) -> list:
        """Identify strengths in the response"""
        strengths = []

        if analysis["naturalness_score"] >= 0.7:
            strengths.append("Response sounds natural and conversational")

        if analysis["engagement_score"] >= 0.7:
            strengths.append("Response is engaging and interactive")

        if analysis["empathy_score"] >= 0.7:
            strengths.append("Response shows appropriate empathy")

        if analysis["enthusiasm_score"] >= 0.6:
            strengths.append("Response has appropriate enthusiasm level")

        if analysis["overall_score"] >= 0.8:
            strengths.append("Overall response quality is excellent")

        return strengths

    def _identify_improvements(self, analysis: Dict[str, Any]) -> list:
        """Identify areas for improvement"""
        improvements = []

        if analysis["naturalness_score"] < 0.5:
            improvements.append("Make language more natural and less robotic")

        if analysis["engagement_score"] < 0.5:
            improvements.append("Increase engagement with questions and interaction")

        if analysis["empathy_score"] < 0.5:
            improvements.append("Show more empathy and understanding")

        if analysis["enthusiasm_score"] < 0.4:
            improvements.append("Add appropriate enthusiasm and energy")
        elif analysis["enthusiasm_score"] > 0.9:
            improvements.append("Moderate enthusiasm to match context")

        return improvements

    def suggest_improvements(self, response: str, analysis: Dict[str, Any]) -> str:
        """
        Generate an improved version of the response based on analysis

        Args:
            response: Original response
            analysis: Analysis results from analyze_response()

        Returns:
            Suggested improved response
        """
        improved = response

        # Apply naturalness improvements
        if analysis["naturalness_score"] < 0.5:
            # Replace formal phrases with natural ones
            replacements = {
                r"\bdo not\b": "don't",
                r"\bcannot\b": "can't",
                r"\bwill not\b": "won't",
                r"\bwould not\b": "wouldn't",
                r"\bin order to\b": "to",
                r"\bfurthermore\b": "also",
                r"\bmoreover\b": "also",
                r"\badditionally\b": "also",
            }

            for pattern, replacement in replacements.items():
                improved = re.sub(pattern, replacement, improved, flags=re.IGNORECASE)

        # Add engagement if lacking
        if analysis["engagement_score"] < 0.4 and not improved.endswith("?"):
            improved += " What do you think?"

        # Add empathy if needed
        if analysis["empathy_score"] < 0.4:
            empathy_intros = [
                "I understand this can be challenging. ",
                "I can see how that would be frustrating. ",
                "That makes perfect sense. ",
            ]
            import random

            improved = random.choice(empathy_intros) + improved

        return improved


# Global response critic instance
response_critic = ResponseQuality()


def critique_response(
    response: str, user_input: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function for response critique

    Args:
        response: Lyrixa's response text
        user_input: Original user input
        context: Additional context

    Returns:
        Analysis results
    """
    return response_critic.analyze_response(response, user_input, context)

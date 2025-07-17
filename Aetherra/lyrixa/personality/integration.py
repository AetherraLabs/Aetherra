"""
Lyrixa Personality Integration Module
====================================

This module integrates the new personality system with the existing Lyrixa
conversation engine to make responses feel more natural and engaging.

Features:
- Seamless integration with existing conversation flow
- Enhanced response processing with personality modulation
- Emotion-aware response generation
- Quality assessment and improvement suggestions
"""

from typing import Any, Dict, Optional

from .emotion_detector import detect_user_emotion

# Import the new personality components
from .personality_engine import PersonalityTrait, enhance_response, lyrixa_personality
from .response_critic import critique_response


class PersonalityIntegration:
    """
    Integration layer between the personality system and existing Lyrixa components
    """

    def __init__(self, enable_critique: bool = True, enable_learning: bool = True):
        self.enable_critique = enable_critique
        self.enable_learning = enable_learning
        self.integration_metrics = {
            "responses_enhanced": 0,
            "responses_critiqued": 0,
            "learning_events": 0,
            "personality_adaptations": 0,
        }

    async def enhance_conversation_response(
        self,
        original_response: str,
        user_input: str,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Main integration function that enhances conversation responses
        with personality and emotional intelligence

        Args:
            original_response: Response from existing conversation engine
            user_input: Original user input
            conversation_context: Additional context from conversation engine

        Returns:
            Enhanced response with personality data
        """
        if conversation_context is None:
            conversation_context = {}

        # Step 1: Detect user emotion and intent
        emotion_analysis = detect_user_emotion(user_input)

        # Step 2: Enhance response with personality
        enhanced_text = enhance_response(
            response=original_response,
            user_input=user_input,
            context={
                "emotion_analysis": emotion_analysis,
                "conversation_context": conversation_context,
                "response_type": self._determine_response_type(
                    original_response, user_input
                ),
            },
        )

        self.integration_metrics["responses_enhanced"] += 1

        # Step 3: Critique response if enabled
        critique_data = None
        if self.enable_critique:
            critique_data = critique_response(
                response=enhanced_text,
                user_input=user_input,
                context={
                    "emotion_analysis": emotion_analysis,
                    "conversation_context": conversation_context,
                },
            )
            self.integration_metrics["responses_critiqued"] += 1

        # Step 4: Create comprehensive response
        enhanced_response = {
            "text": enhanced_text,
            "original_text": original_response,
            "personality_data": {
                "emotion_detected": emotion_analysis["primary_emotion"],
                "personality_state": lyrixa_personality.get_personality_summary(),
                "enhancement_applied": True,
                "emotion_analysis": emotion_analysis,
            },
            "quality_metrics": critique_data,
            "integration_info": {
                "personality_version": "1.0.0",
                "enhancement_timestamp": self._get_timestamp(),
                "metrics": self.integration_metrics.copy(),
            },
        }

        # Step 5: Learn from interaction if enabled
        if self.enable_learning:
            await self._learn_from_interaction(
                user_input=user_input,
                enhanced_response=enhanced_response,
                emotion_analysis=emotion_analysis,
            )

        return enhanced_response

    def _determine_response_type(self, response: str, user_input: str) -> str:
        """Determine the type of response for appropriate personality modulation"""
        response_lower = response.lower()
        user_lower = user_input.lower()

        # Technical/coding response
        if any(
            word in response_lower
            for word in ["code", "function", "class", "variable", "syntax"]
        ):
            return "technical"

        # Explanation response
        elif any(
            word in response_lower
            for word in ["because", "explanation", "understand", "reason"]
        ):
            return "explanation"

        # Help/guidance response
        elif any(word in user_lower for word in ["help", "how", "guide", "tutorial"]):
            return "guidance"

        # Problem-solving response
        elif any(
            word in user_lower for word in ["problem", "issue", "error", "bug", "fix"]
        ):
            return "problem_solving"

        # Creative/exploratory response
        elif any(
            word in user_lower for word in ["idea", "creative", "explore", "imagine"]
        ):
            return "creative"

        else:
            return "general"

    async def _learn_from_interaction(
        self,
        user_input: str,
        enhanced_response: Dict[str, Any],
        emotion_analysis: Dict[str, Any],
    ) -> None:
        """Learn from the interaction to improve future responses"""
        try:
            # Store learning data in personality system
            lyrixa_personality.learn_from_interaction(
                user_input=user_input,
                response=enhanced_response["text"],
                feedback=None,  # Could be enhanced later with user feedback
            )

            # Update metrics
            self.integration_metrics["learning_events"] += 1

            # Adapt personality based on patterns
            if self._should_adapt_personality(emotion_analysis):
                await self._adapt_personality_traits(emotion_analysis)
                self.integration_metrics["personality_adaptations"] += 1

        except Exception as e:
            print(f"⚠️ Learning error in personality integration: {e}")

    def _should_adapt_personality(self, emotion_analysis: Dict[str, Any]) -> bool:
        """Determine if personality should be adapted based on interaction"""
        # Simple adaptation logic - can be enhanced
        return (
            emotion_analysis.get("urgency_level") == "high"
            or emotion_analysis.get("primary_emotion") in ["frustration", "confusion"]
            or emotion_analysis.get("complexity") == "high"
        )

    async def _adapt_personality_traits(self, emotion_analysis: Dict[str, Any]) -> None:
        """Adapt personality traits based on user needs"""
        try:
            # Increase empathy for frustrated users
            if emotion_analysis.get("primary_emotion") == "frustration":
                current_empathy = lyrixa_personality.base_traits[
                    PersonalityTrait.EMPATHY
                ]
                lyrixa_personality.base_traits[PersonalityTrait.EMPATHY] = min(
                    1.0, current_empathy + 0.05
                )

            # Increase enthusiasm for excited users
            elif emotion_analysis.get("primary_emotion") == "excitement":
                current_enthusiasm = lyrixa_personality.base_traits[
                    PersonalityTrait.ENTHUSIASM
                ]
                lyrixa_personality.base_traits[PersonalityTrait.ENTHUSIASM] = min(
                    1.0, current_enthusiasm + 0.03
                )

            # Increase thoughtfulness for complex queries
            elif emotion_analysis.get("complexity") == "high":
                current_thoughtfulness = lyrixa_personality.base_traits[
                    PersonalityTrait.THOUGHTFULNESS
                ]
                lyrixa_personality.base_traits[PersonalityTrait.THOUGHTFULNESS] = min(
                    1.0, current_thoughtfulness + 0.02
                )

        except Exception as e:
            print(f"⚠️ Personality adaptation error: {e}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status and metrics of personality integration"""
        return {
            "status": "active",
            "personality_system_active": True,
            "emotion_detection_active": True,
            "response_critique_active": self.enable_critique,
            "learning_active": self.enable_learning,
            "metrics": self.integration_metrics.copy(),
            "personality_summary": lyrixa_personality.get_personality_summary(),
        }

    async def test_integration(self) -> Dict[str, Any]:
        """Test the personality integration with sample data"""
        test_user_input = (
            "I'm having trouble understanding this code and it's really frustrating!"
        )
        test_original_response = (
            "Let me help you understand the code structure and functionality."
        )

        try:
            enhanced_response = await self.enhance_conversation_response(
                original_response=test_original_response,
                user_input=test_user_input,
                conversation_context={"test": True},
            )

            return {
                "test_status": "passed",
                "original_response": test_original_response,
                "enhanced_response": enhanced_response["text"],
                "emotion_detected": enhanced_response["personality_data"][
                    "emotion_detected"
                ],
                "quality_score": enhanced_response["quality_metrics"]["overall_score"]
                if enhanced_response["quality_metrics"]
                else None,
            }

        except Exception as e:
            return {"test_status": "failed", "error": str(e)}


# Global integration instance
personality_integration = PersonalityIntegration()


async def enhance_lyrixa_response(
    original_response: str,
    user_input: str,
    conversation_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function for enhancing Lyrixa responses with personality

    Args:
        original_response: Response from existing conversation engine
        user_input: Original user input
        conversation_context: Additional context

    Returns:
        Enhanced response with personality
    """
    return await personality_integration.enhance_conversation_response(
        original_response=original_response,
        user_input=user_input,
        conversation_context=conversation_context,
    )


def get_personality_status() -> Dict[str, Any]:
    """Get current personality system status"""
    return personality_integration.get_integration_status()

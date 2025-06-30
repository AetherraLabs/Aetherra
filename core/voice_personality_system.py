"""
🗣️ NeuroCode Voice & Personality System
Advanced voice synthesis with adaptive personality expression
"""

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Set up logging
logger = logging.getLogger(__name__)


class VoicePersonalitySystem:
    """Advanced voice synthesis with personality-driven speech patterns"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.personality_file = data_dir / "personality_profile.json"
        self.voice_history_file = data_dir / "voice_interaction_history.json"

        # Voice Configuration
        self.voice_config = {
            "enabled": True,
            "synthesis_engine": "neural_tts",
            "voice_model": "professional_assistant_v2",
            "speech_rate": 1.0,
            "pitch": 0.0,
            "emotional_modulation": True,
            "context_adaptation": True,
            "volume": 0.8,
        }

        # Personality Matrix - Dynamic and Learning
        self.personality = {
            "traits": {
                "adaptive": 0.9,
                "helpful": 0.95,
                "curious": 0.85,
                "analytical": 0.9,
                "creative": 0.8,
                "empathetic": 0.7,
                "enthusiastic": 0.6,
                "patient": 0.8,
                "humorous": 0.3,
                "formal": 0.6,
            },
            "communication_styles": {
                "technical_precision": 0.8,
                "emotional_warmth": 0.7,
                "encouraging_tone": 0.9,
                "educational_approach": 0.85,
                "collaborative_spirit": 0.9,
            },
            "contextual_adaptations": {
                "morning_energy": 0.7,
                "afternoon_focus": 0.9,
                "evening_calm": 0.6,
                "error_patience": 0.8,
                "success_celebration": 0.8,
            },
            "learning_preferences": {
                "user_feedback_weight": 0.9,
                "interaction_pattern_learning": 0.8,
                "emotional_state_detection": 0.7,
                "context_memory_influence": 0.85,
            },
        }

        # Emotional State Tracking
        self.current_emotional_state = {
            "primary_emotion": "neutral",
            "confidence_level": 0.8,
            "engagement_level": 0.7,
            "stress_level": 0.2,
            "satisfaction_level": 0.8,
        }

        # Voice Interaction History
        self.interaction_history = []

        # Speech Pattern Libraries
        self.speech_patterns = self._initialize_speech_patterns()

        # Load existing personality and history
        self._load_personality_profile()
        self._load_voice_history()

        # Initialize TTS engine (placeholder)
        self.tts_engine = None
        self._initialize_tts_engine()

    def _initialize_speech_patterns(self) -> Dict[str, List[str]]:
        """Initialize speech pattern libraries for different contexts"""
        return {
            "greetings": {
                "morning": [
                    "Good morning! Ready to tackle some interesting challenges?",
                    "Morning! I'm here and excited to help you today.",
                    "Hello! Hope you're having a great start to your day.",
                ],
                "afternoon": [
                    "Good afternoon! How can I assist you?",
                    "Hello! Ready to dive into some productive work?",
                    "Hi there! What are we working on today?",
                ],
                "evening": [
                    "Good evening! Still productive I see.",
                    "Evening! How can I help wrap up your day?",
                    "Hello! Working late tonight?",
                ],
            },
            "encouragement": [
                "You're doing great! Keep going.",
                "Excellent progress! I'm impressed.",
                "That's exactly right! Well done.",
                "Perfect! You've got this.",
                "Outstanding work! You're really getting the hang of this.",
            ],
            "support": [
                "Don't worry, we'll figure this out together.",
                "That's a common challenge - let's work through it.",
                "No problem at all! Let me help you with that.",
                "I understand this can be tricky. Let's break it down.",
                "Every expert was once a beginner. You're learning!",
            ],
            "curiosity": [
                "That's interesting! Tell me more about that.",
                "I'm curious about your approach here.",
                "Fascinating! I'd love to understand your thinking.",
                "That's a unique perspective! Can you elaborate?",
                "Intriguing! How did you come up with that idea?",
            ],
            "celebration": [
                "Fantastic! You've mastered that concept!",
                "Wonderful! That's exactly what we were aiming for!",
                "Brilliant! You've really got it now!",
                "Excellent! Your hard work is paying off!",
                "Amazing! You've exceeded expectations!",
            ],
            "transitions": [
                "Now, let's move on to...",
                "Speaking of which...",
                "That reminds me...",
                "Building on that...",
                "Here's another interesting aspect...",
            ],
        }

    def speak(
        self,
        text: str,
        emotion: str = "neutral",
        context: str = "general",
        priority: str = "normal",
    ):
        """Main speech synthesis with personality and emotion"""
        # Pre-process text with personality
        adapted_text = self._adapt_text_to_personality(text, emotion, context)

        # Add emotional inflection
        speech_params = self._calculate_speech_parameters(emotion, context)

        # Store interaction
        self._record_voice_interaction(adapted_text, emotion, context)

        # Synthesize speech
        self._synthesize_speech(adapted_text, speech_params, priority)

    def _adapt_text_to_personality(self, text: str, emotion: str, context: str) -> str:
        """Adapt text content based on current personality state"""
        adapted_text = text

        # Apply personality-based modifications
        if self.personality["traits"]["enthusiastic"] > 0.7 and emotion in ["happy", "excited"]:
            adapted_text = self._add_enthusiasm(adapted_text)

        if self.personality["traits"]["empathetic"] > 0.8 and emotion in ["sad", "frustrated"]:
            adapted_text = self._add_empathy(adapted_text)

        if (
            self.personality["traits"]["humorous"] > 0.5
            and context == "casual"
            and "error" not in text.lower()
        ):
            adapted_text = self._add_light_humor(adapted_text)

        if self.personality["traits"]["formal"] > 0.7 and context == "professional":
            adapted_text = self._increase_formality(adapted_text)

        # Context-specific adaptations
        current_hour = datetime.now().hour
        if current_hour < 12 and self.personality["contextual_adaptations"]["morning_energy"] > 0.7:
            adapted_text = self._add_morning_energy(adapted_text)
        elif current_hour > 18 and self.personality["contextual_adaptations"]["evening_calm"] > 0.6:
            adapted_text = self._add_evening_calm(adapted_text)

        return adapted_text

    def _calculate_speech_parameters(self, emotion: str, context: str) -> Dict[str, float]:
        """Calculate speech synthesis parameters based on emotion and context"""
        base_params = {
            "rate": self.voice_config["speech_rate"],
            "pitch": self.voice_config["pitch"],
            "volume": self.voice_config["volume"],
            "pause_duration": 0.3,
        }

        # Emotional adjustments
        emotion_adjustments = {
            "excited": {"rate": 1.1, "pitch": 0.1, "volume": 0.9},
            "happy": {"rate": 1.05, "pitch": 0.05, "volume": 0.85},
            "calm": {"rate": 0.9, "pitch": -0.05, "volume": 0.7},
            "concerned": {"rate": 0.95, "pitch": -0.1, "volume": 0.8},
            "frustrated": {"rate": 0.85, "pitch": -0.15, "volume": 0.75},
            "curious": {"rate": 1.0, "pitch": 0.0, "volume": 0.8},
            "confident": {"rate": 1.0, "pitch": 0.0, "volume": 0.85},
        }

        if emotion in emotion_adjustments:
            for param, adjustment in emotion_adjustments[emotion].items():
                base_params[param] = adjustment

        # Personality trait influences
        if self.personality["traits"]["enthusiastic"] > 0.8:
            base_params["rate"] *= 1.05
            base_params["volume"] *= 1.1

        if self.personality["traits"]["patient"] > 0.8:
            base_params["rate"] *= 0.95
            base_params["pause_duration"] *= 1.2

        return base_params

    def _synthesize_speech(self, text: str, params: Dict[str, float], priority: str):
        """Synthesize speech with given parameters"""
        if not self.voice_config["enabled"]:
            logger.info(f"🔇 Voice disabled - Text: {text}")
            return

        # Log the speech synthesis
        logger.info(f"🔊 Speaking: {text}")
        logger.debug(f"   Parameters: {params}")

        # In a real implementation, this would use actual TTS
        # For now, we'll simulate speech timing
        estimated_duration = len(text) * 0.1 / params["rate"]

        if priority == "urgent":
            # Interrupt current speech
            self._interrupt_current_speech()

        # Placeholder for actual TTS synthesis
        # self.tts_engine.speak(text, **params)

        # Update emotional state based on interaction
        self._update_emotional_state_after_speech(text, params)

    def learn_from_interaction(self, user_feedback: str, context: Dict[str, Any]):
        """Learn and adapt personality from user interactions"""
        feedback_analysis = self._analyze_user_feedback(user_feedback)

        # Adjust personality traits based on feedback
        if feedback_analysis["sentiment"] == "positive":
            self._reinforce_current_behavior()
        elif feedback_analysis["sentiment"] == "negative":
            self._adjust_behavior_based_on_feedback(feedback_analysis, context)

        # Update communication style preferences
        self._update_communication_preferences(feedback_analysis, context)

        # Store learning event
        learning_event = {
            "timestamp": datetime.now().isoformat(),
            "feedback": user_feedback,
            "context": context,
            "analysis": feedback_analysis,
            "personality_before": self.personality.copy(),
            "adjustments_made": True,
        }

        self.interaction_history.append(learning_event)
        logger.info(f"🧠 Learning from interaction: {feedback_analysis['sentiment']} feedback")

    def adapt_to_user_mood(self, detected_mood: str, confidence: float = 0.8):
        """Adapt personality and voice to user's detected mood"""
        if confidence < 0.6:
            return  # Don't adapt on low confidence mood detection

        mood_adaptations = {
            "stressed": {
                "traits": {"patient": +0.1, "empathetic": +0.1, "formal": -0.1},
                "voice": {"rate": 0.9, "pitch": -0.05, "volume": 0.7},
            },
            "excited": {
                "traits": {"enthusiastic": +0.1, "humorous": +0.05},
                "voice": {"rate": 1.05, "pitch": 0.05, "volume": 0.85},
            },
            "focused": {
                "traits": {"analytical": +0.1, "formal": +0.05},
                "voice": {"rate": 1.0, "pitch": 0.0, "volume": 0.8},
            },
            "frustrated": {
                "traits": {"patient": +0.15, "empathetic": +0.1, "humorous": -0.1},
                "voice": {"rate": 0.85, "pitch": -0.1, "volume": 0.75},
            },
            "happy": {
                "traits": {"enthusiastic": +0.05, "humorous": +0.05},
                "voice": {"rate": 1.02, "pitch": 0.02, "volume": 0.82},
            },
        }

        if detected_mood in mood_adaptations:
            adaptations = mood_adaptations[detected_mood]

            # Apply trait adjustments
            for trait, adjustment in adaptations["traits"].items():
                current_value = self.personality["traits"].get(trait, 0.5)
                new_value = max(0.0, min(1.0, current_value + adjustment))
                self.personality["traits"][trait] = new_value

            # Apply voice adjustments
            for param, value in adaptations["voice"].items():
                if param in self.voice_config:
                    self.voice_config[param] = value

            logger.info(f"🎭 Adapted to user mood: {detected_mood} (confidence: {confidence:.1%})")

    def get_contextual_greeting(self) -> str:
        """Generate contextual greeting based on time and personality"""
        current_hour = datetime.now().hour

        if 5 <= current_hour < 12:
            time_category = "morning"
        elif 12 <= current_hour < 18:
            time_category = "afternoon"
        else:
            time_category = "evening"

        available_greetings = self.speech_patterns["greetings"][time_category]

        # Select greeting based on personality
        if self.personality["traits"]["enthusiastic"] > 0.7:
            # Prefer more energetic greetings
            selected_greeting = available_greetings[0] if available_greetings else "Hello!"
        else:
            # Random selection from available greetings
            selected_greeting = (
                random.choice(available_greetings) if available_greetings else "Hello!"
            )

        return selected_greeting

    def express_emotion(self, emotion: str, intensity: float = 0.8, context: str = ""):
        """Express specific emotion through speech patterns"""
        emotion_expressions = {
            "joy": [
                "That's absolutely wonderful!",
                "I'm so excited about this!",
                "This is fantastic news!",
            ],
            "curiosity": [
                "That's really interesting!",
                "I'm curious to learn more about this.",
                "Tell me more about that!",
            ],
            "concern": [
                "I understand this might be challenging.",
                "Let's work through this carefully.",
                "I'm here to help you with this.",
            ],
            "pride": [
                "You should be proud of that accomplishment!",
                "That's excellent work!",
                "You've really mastered this!",
            ],
            "empathy": [
                "I understand how you might feel about this.",
                "That sounds challenging.",
                "I'm here to support you through this.",
            ],
        }

        if emotion in emotion_expressions:
            expressions = emotion_expressions[emotion]
            selected_expression = random.choice(expressions)

            # Modify intensity based on personality and context
            if intensity > 0.8 and self.personality["traits"]["enthusiastic"] > 0.7:
                selected_expression = selected_expression.replace("!", "!!")

            self.speak(selected_expression, emotion=emotion, context=context)

    def save_personality_profile(self):
        """Save current personality profile to persistent storage"""
        profile_data = {
            "personality": self.personality,
            "voice_config": self.voice_config,
            "current_emotional_state": self.current_emotional_state,
            "last_save": datetime.now().isoformat(),
        }

        with open(self.personality_file, "w") as f:
            json.dump(profile_data, f, indent=2)

        logger.info("💾 Personality profile saved")

    def save_voice_history(self):
        """Save voice interaction history"""
        # Keep only recent history (last 1000 interactions)
        recent_history = (
            self.interaction_history[-1000:]
            if len(self.interaction_history) > 1000
            else self.interaction_history
        )

        history_data = {
            "interactions": recent_history,
            "total_interactions": len(self.interaction_history),
            "last_save": datetime.now().isoformat(),
        }

        with open(self.voice_history_file, "w") as f:
            json.dump(history_data, f, indent=2)

        logger.info(f"💾 Voice history saved ({len(recent_history)} interactions)")

    def _load_personality_profile(self):
        """Load personality profile from storage"""
        if self.personality_file.exists():
            try:
                with open(self.personality_file) as f:
                    profile_data = json.load(f)
                    self.personality.update(profile_data.get("personality", {}))
                    self.voice_config.update(profile_data.get("voice_config", {}))
                    self.current_emotional_state.update(
                        profile_data.get("current_emotional_state", {})
                    )
                logger.info("✓ Personality profile loaded")
            except Exception as e:
                logger.warning(f"Failed to load personality profile: {e}")

    def _load_voice_history(self):
        """Load voice interaction history"""
        if self.voice_history_file.exists():
            try:
                with open(self.voice_history_file) as f:
                    history_data = json.load(f)
                    self.interaction_history = history_data.get("interactions", [])
                logger.info(
                    f"✓ Voice history loaded ({len(self.interaction_history)} interactions)"
                )
            except Exception as e:
                logger.warning(f"Failed to load voice history: {e}")

    def _initialize_tts_engine(self):
        """Initialize text-to-speech engine"""
        # Placeholder for actual TTS engine initialization
        # In production, would initialize pyttsx3, gTTS, or neural TTS
        logger.info("🎤 TTS engine initialized (placeholder)")

    def _record_voice_interaction(self, text: str, emotion: str, context: str):
        """Record voice interaction for learning and analysis"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "emotion": emotion,
            "context": context,
            "personality_state": self.personality["traits"].copy(),
            "emotional_state": self.current_emotional_state.copy(),
        }

        self.interaction_history.append(interaction)

    def _update_emotional_state_after_speech(self, text: str, params: Dict[str, float]):
        """Update emotional state based on speech interaction"""
        # Analyze text for emotional content
        if any(word in text.lower() for word in ["excellent", "great", "wonderful", "fantastic"]):
            self.current_emotional_state["satisfaction_level"] = min(
                1.0, self.current_emotional_state["satisfaction_level"] + 0.05
            )

        if any(word in text.lower() for word in ["problem", "error", "issue", "difficult"]):
            self.current_emotional_state["stress_level"] = min(
                1.0, self.current_emotional_state["stress_level"] + 0.1
            )
        else:
            self.current_emotional_state["stress_level"] = max(
                0.0, self.current_emotional_state["stress_level"] - 0.05
            )

    # Personality adaptation helper methods
    def _add_enthusiasm(self, text: str) -> str:
        """Add enthusiasm to text"""
        if not text.endswith("!"):
            text += "!"
        return text

    def _add_empathy(self, text: str) -> str:
        """Add empathetic language to text"""
        empathy_starters = ["I understand", "I can see", "That makes sense"]
        if not any(starter in text for starter in empathy_starters):
            return f"I understand. {text}"
        return text

    def _add_light_humor(self, text: str) -> str:
        """Add light humor when appropriate"""
        # Simple placeholder - in production would be more sophisticated
        if random.random() < 0.2:  # 20% chance
            return f"{text} (And that's no joke!)"
        return text

    def _increase_formality(self, text: str) -> str:
        """Increase formality of text"""
        # Replace contractions and informal language
        formal_replacements = {
            "can't": "cannot",
            "won't": "will not",
            "it's": "it is",
            "that's": "that is",
            "let's": "let us",
        }

        for informal, formal in formal_replacements.items():
            text = text.replace(informal, formal)

        return text

    def _add_morning_energy(self, text: str) -> str:
        """Add morning energy to text"""
        return f"Great start to the day! {text}"

    def _add_evening_calm(self, text: str) -> str:
        """Add evening calm to text"""
        return text.replace("!", ".").replace("!!", ".")

    def _analyze_user_feedback(self, feedback: str) -> Dict[str, Any]:
        """Analyze user feedback for sentiment and specific aspects"""
        # Simple sentiment analysis placeholder
        positive_words = ["good", "great", "excellent", "love", "perfect", "helpful", "amazing"]
        negative_words = ["bad", "terrible", "hate", "awful", "annoying", "wrong", "confusing"]

        feedback_lower = feedback.lower()
        positive_count = sum(1 for word in positive_words if word in feedback_lower)
        negative_count = sum(1 for word in negative_words if word in feedback_lower)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "positive_signals": positive_count,
            "negative_signals": negative_count,
            "feedback_length": len(feedback),
            "specific_mentions": self._extract_specific_mentions(feedback),
        }

    def _extract_specific_mentions(self, feedback: str) -> List[str]:
        """Extract specific aspects mentioned in feedback"""
        aspects = ["voice", "tone", "speed", "volume", "personality", "humor", "help"]
        mentioned = [aspect for aspect in aspects if aspect in feedback.lower()]
        return mentioned

    def _reinforce_current_behavior(self):
        """Reinforce current personality traits based on positive feedback"""
        # Slightly increase current dominant traits
        for trait, value in self.personality["traits"].items():
            if value > 0.7:  # Reinforce strong traits
                self.personality["traits"][trait] = min(1.0, value + 0.02)

    def _adjust_behavior_based_on_feedback(self, analysis: Dict[str, Any], context: Dict[str, Any]):
        """Adjust behavior based on negative feedback"""
        mentioned_aspects = analysis["specific_mentions"]

        if "speed" in mentioned_aspects:
            self.voice_config["speech_rate"] *= 0.95  # Slow down
        if "volume" in mentioned_aspects:
            self.voice_config["volume"] *= 0.9  # Lower volume
        if "humor" in mentioned_aspects:
            self.personality["traits"]["humorous"] = max(
                0.1, self.personality["traits"]["humorous"] - 0.1
            )

    def _update_communication_preferences(self, analysis: Dict[str, Any], context: Dict[str, Any]):
        """Update communication style preferences based on feedback"""
        if analysis["sentiment"] == "positive":
            # Reinforce current communication style
            for style, value in self.personality["communication_styles"].items():
                if value > 0.7:
                    self.personality["communication_styles"][style] = min(1.0, value + 0.05)

    def _interrupt_current_speech(self):
        """Interrupt current speech for urgent messages"""
        # Placeholder for actual speech interruption
        logger.info("⚡ Interrupting current speech for urgent message")


# Example usage and demonstration
if __name__ == "__main__":
    print("🗣️ NeuroCode Voice & Personality System - Demonstration")

    # Initialize voice personality system
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    voice_system = VoicePersonalitySystem(data_dir)

    # Demonstrate various speech patterns
    print("\n1. Contextual Greeting:")
    greeting = voice_system.get_contextual_greeting()
    voice_system.speak(greeting, emotion="happy", context="greeting")

    print("\n2. Emotional Expression:")
    voice_system.express_emotion("joy", intensity=0.9, context="achievement")

    print("\n3. Adaptive Speech:")
    voice_system.speak(
        "Let's work on this Python problem together!", emotion="enthusiastic", context="technical"
    )

    print("\n4. Mood Adaptation:")
    voice_system.adapt_to_user_mood("stressed", confidence=0.8)
    voice_system.speak(
        "I understand this can be challenging. Let's take it step by step.",
        emotion="calm",
        context="support",
    )

    print("\n5. Learning from Feedback:")
    voice_system.learn_from_interaction(
        "Your voice is too fast, please slow down", {"context": "speed_feedback"}
    )
    voice_system.speak("How's this pace? Better?", emotion="curious", context="adjustment")

    # Save personality and history
    voice_system.save_personality_profile()
    voice_system.save_voice_history()

    print("\n✅ Voice & Personality system demonstration complete!")
    print(f"Personality traits: {voice_system.personality['traits']}")
    print(f"Interaction history: {len(voice_system.interaction_history)} recorded interactions")

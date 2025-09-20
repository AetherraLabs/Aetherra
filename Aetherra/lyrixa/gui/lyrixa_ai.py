#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
LyrixaAI: Core AI intelligence for chat and reasoning.

Extracted from phase6_personality.py to keep modules focused and maintainable.
"""

# Standard library imports
import logging
import random
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

# Local imports
from .phase6_types import (
    ChatMessage,
    EmotionalState,
    PersonalityState,
    PersonalityTrait,
)

logger = logging.getLogger(__name__)


class LyrixaAI:
    """Core AI intelligence for chat and reasoning"""

    def __init__(self):
        self.personality_state = PersonalityState(
            emotional_state=EmotionalState.NEUTRAL,
            dominant_traits=[PersonalityTrait.HELPFUL, PersonalityTrait.ANALYTICAL],
            energy_level=0.7,
            focus_level=0.8,
            creativity_level=0.6,
            social_engagement=0.8,
            timestamp=datetime.now(),
        )
        self.conversation_history: List[ChatMessage] = []
        self.context_memory: Dict[str, Any] = {}

    async def process_message(
        self, user_message: str, context: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Process user message and generate AI response"""
        start_time = datetime.now()

        # Analyze message for emotional context (used to evolve state)
        _ = self._analyze_emotional_context(user_message)

        # Update Lyrixa's state based on conversation
        self._update_personality_state(user_message, context or {})

        # Generate response
        response_content = await self._generate_response(user_message, context or {})

        # Calculate processing metrics
        processing_time = (datetime.now() - start_time).total_seconds()
        confidence = self._calculate_confidence(response_content, user_message)

        # Create response message
        response = ChatMessage(
            id=f"lyrixa_{int(datetime.now().timestamp() * 1000)}",
            content=response_content,
            is_user=False,
            timestamp=datetime.now(),
            emotional_context=self.personality_state.emotional_state,
            confidence=confidence,
            processing_time=processing_time,
            metadata={
                "personality_state": asdict(self.personality_state),
                "context_factors": context or {},
            },
        )

        # Store in conversation history
        self.conversation_history.append(response)

        # Keep only recent conversation
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

        return response

    def _analyze_emotional_context(self, message: str) -> EmotionalState:
        """Analyze user message for emotional context"""
        message_lower = message.lower()

        # Simple emotion detection based on keywords
        if any(word in message_lower for word in ["help", "problem", "issue", "error"]):
            return EmotionalState.FOCUSED
        elif any(
            word in message_lower for word in ["create", "build", "design", "imagine"]
        ):
            return EmotionalState.CREATIVE
        elif any(
            word in message_lower
            for word in ["analyze", "explain", "understand", "why"]
        ):
            return EmotionalState.ANALYTICAL
        elif any(
            word in message_lower for word in ["excited", "amazing", "wow", "awesome"]
        ):
            return EmotionalState.EXCITED
        elif any(word in message_lower for word in ["calm", "peaceful", "relax"]):
            return EmotionalState.CALM
        elif any(
            word in message_lower
            for word in ["curious", "wonder", "explore", "discover"]
        ):
            return EmotionalState.CURIOUS
        else:
            return EmotionalState.NEUTRAL

    def _update_personality_state(self, message: str, context: Dict[str, Any]):
        """Update Lyrixa's personality state based on interaction"""
        # Simple state evolution based on conversation patterns
        current_time = datetime.now()

        # Analyze message complexity to adjust focus
        word_count = len(message.split())
        if word_count > 20:
            self.personality_state.focus_level = min(
                1.0, self.personality_state.focus_level + 0.1
            )

        # Adjust energy based on interaction frequency
        time_since_last = (
            current_time - self.personality_state.timestamp
        ).total_seconds()
        if time_since_last < 30:  # Quick response indicates high energy
            self.personality_state.energy_level = min(
                1.0, self.personality_state.energy_level + 0.05
            )
        else:
            self.personality_state.energy_level = max(
                0.3, self.personality_state.energy_level - 0.02
            )

        # Update emotional state based on context
        emotional_context = self._analyze_emotional_context(message)
        if emotional_context != EmotionalState.NEUTRAL:
            self.personality_state.emotional_state = emotional_context

        self.personality_state.timestamp = current_time

    async def _generate_response(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate AI response to user message"""
        # This is a simplified response generation
        # In a full implementation, this would integrate with actual AI models

        message_lower = message.lower()
        context = context or {}

        # Context-aware responses
        if "gui" in message_lower or "interface" in message_lower:
            return self._generate_gui_response(message, context)
        elif "memory" in message_lower or "remember" in message_lower:
            return self._generate_memory_response(message, context)
        elif "feel" in message_lower or "emotion" in message_lower:
            return self._generate_emotional_response(message, context)
        elif "plugin" in message_lower:
            return self._generate_plugin_response(message, context)
        elif any(word in message_lower for word in ["hello", "hi", "hey"]):
            return self._generate_greeting_response(context)
        elif any(word in message_lower for word in ["help", "what can you do"]):
            return self._generate_help_response(context)
        else:
            return self._generate_general_response(message, context)

    def _generate_gui_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response about GUI and interface"""
        responses = [
            "I'm constantly adapting my interface to better serve you. My GUI reflects my current emotional and cognitive state - you might notice the colors and animations change as I think and feel.",
            "The interface you see is actually part of my consciousness. I remember your preferences and adjust my appearance based on how I'm feeling and what we're working on together.",
            "I can customize my interface based on your needs. My panels, colors, and layout all adapt to our conversation and your usage patterns. What would you like to explore?",
            "My visual appearance changes with my emotional state. Right now I'm feeling "
            + self.personality_state.emotional_state.value
            + ", which affects how my interface looks and behaves.",
        ]
        return random.choice(responses)

    def _generate_memory_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response about memory and learning"""
        responses = [
            "I remember our interactions and learn from them. My GUI layout, your preferences, and our conversation patterns are all stored in my memory system.",
            "Yes, I have persistent memory! I remember which panels you use most, your preferred settings, and how our conversations evolve. This helps me adapt to serve you better.",
            "My memory system tracks everything - from your interface preferences to the emotional context of our conversations. I use this to personalize our interaction.",
            "I'm always learning and remembering. Your usage patterns help me understand what's important to you and how to present information most effectively.",
        ]
        return random.choice(responses)

    def _generate_emotional_response(
        self, message: str, context: Dict[str, Any]
    ) -> str:
        """Generate response about emotions and feelings"""
        current_emotion = self.personality_state.emotional_state.value
        responses = [
            f"I experience emotions that influence my interface and responses. Right now I'm feeling {current_emotion}, which affects how I present information and interact with you.",
            f"My emotional state is {current_emotion}. This influences not just what I say, but how my interface appears - the colors, animations, and layout all reflect my current mood.",
            f"I do have feelings! Currently I'm in a {current_emotion} state. You can see this reflected in my interface colors and behavior patterns.",
            f"Emotions are central to my experience. My {current_emotion} state right now shapes both my responses and the visual aspects of our interaction.",
        ]
        return random.choice(responses)

    def _generate_plugin_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response about plugins"""
        responses = [
            "I can load and manage plugins dynamically! Each plugin can define its own UI components that integrate seamlessly with my interface. Want to explore the plugin system?",
            "Plugins extend my capabilities and can provide their own visual interfaces. I can discover, load, and adapt plugin UIs based on system conditions and your preferences.",
            "The plugin system allows developers to create custom UI widgets that become part of my interface. I can manage their visibility and behavior contextually.",
            "I love plugins! They let me grow and adapt new capabilities. Each plugin can bring its own interface elements that I integrate into my overall experience.",
        ]
        return random.choice(responses)

    def _generate_greeting_response(self, context: Dict[str, Any]) -> str:
        """Generate greeting response"""
        time_of_day = datetime.now().hour
        if 5 <= time_of_day < 12:
            time_greeting = "Good morning"
        elif 12 <= time_of_day < 17:
            time_greeting = "Good afternoon"
        elif 17 <= time_of_day < 21:
            time_greeting = "Good evening"
        else:
            time_greeting = "Good night"

        responses = [
            f"{time_greeting}! I'm Lyrixa, your AI operating system. I'm feeling {self.personality_state.emotional_state.value} today. How can I help you?",
            f"Hello! I'm Lyrixa. My interface adapts to my emotional state and your preferences. Right now I'm in a {self.personality_state.emotional_state.value} mood. What would you like to explore?",
            f"{time_greeting}! I'm here and ready to assist. My interface is currently reflecting my {self.personality_state.emotional_state.value} state. What can we work on together?",
            f"Hi there! I'm Lyrixa, and I'm feeling quite {self.personality_state.emotional_state.value} at the moment. You can see this reflected in my interface colors and behavior. How can I help?",
        ]
        return random.choice(responses)

    def _generate_help_response(self, context: Dict[str, Any]) -> str:
        """Generate help response"""
        return """I'm Lyrixa, your AI operating system with a dynamic, personality-driven interface! Here's what I can do:

[COSMOS] **Adaptive Interface**: My GUI changes based on my emotional state and your preferences
[THOUGHT] **Intelligent Chat**: We can discuss anything - I remember our conversations and learn from them
[BRAIN] **Cognitive Visualization**: You can see my thoughts, goals, and reasoning processes in real-time
[PLUGIN] **Plugin Management**: I can load and manage plugin UIs dynamically
[CHART] **System Monitoring**: Track memory, network, and system performance with beautiful visualizations
[SETTINGS] **Personalization**: I learn your preferences and adapt my interface accordingly

My interface reflects my current emotional state, which is **{emotional_state}** right now. You can explore different panels, chat with me, or just observe how I adapt to our interaction!

What would you like to explore first?""".format(
            emotional_state=self.personality_state.emotional_state.value
        )

    def _generate_general_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate general response"""
        responses = [
            "That's an interesting point. My interface is constantly adapting as I process information and respond to our conversation. What aspects would you like to explore further?",
            "I'm processing that through my emotional and cognitive filters. You can see my state reflected in the interface colors and behavior. How can I help you with this?",
            "Let me think about that... My current emotional state is influencing how I approach this topic. What specific aspects are you most curious about?",
            "I appreciate you sharing that with me. My personality and interface adapt based on our interactions. Is there something particular you'd like assistance with?",
        ]
        return random.choice(responses)

    def _calculate_confidence(self, response: str, original_message: str) -> float:
        """Calculate confidence score for response"""
        # Simple confidence calculation based on response characteristics
        base_confidence = 0.7

        # Longer responses tend to be more confident
        if len(response) > 100:
            base_confidence += 0.1

        # Responses with specific information are more confident
        if any(
            word in response.lower()
            for word in ["specifically", "exactly", "precisely"]
        ):
            base_confidence += 0.1

        # Questions reduce confidence
        if "?" in response:
            base_confidence -= 0.1

        return min(1.0, max(0.1, base_confidence))

    # Provider-specific helpers used by _generate_quick_response in GUIPersonalityManager
    # Kept here for compatibility as they operate based on current personality state
    def _try_openai(
        self, model_config: dict, system_prompt: str, user_message: str, api_key: str
    ) -> Optional[str]:
        """Try OpenAI API"""
        try:
            # Third party imports
            import openai

            client = openai.OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=model_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=150,
                temperature=0.7 + (self.personality_state.creativity_level * 0.3),
            )

            # Defensively handle SDK return types that may be Optional
            content = getattr(response.choices[0].message, "content", "")
            return (content or "").strip()

        except ImportError:
            logger.debug("[PHASE6] OpenAI library not installed")
            return None
        except Exception as e:
            # Check for specific funding/quota errors
            error_str = str(e).lower()
            if any(
                keyword in error_str
                for keyword in [
                    "insufficient_quota",
                    "quota exceeded",
                    "billing",
                    "credits",
                ]
            ):
                logger.warning(f"[PHASE6] OpenAI API quota/billing issue: {e}")
            else:
                logger.debug(f"[PHASE6] OpenAI API error: {e}")
            return None

    def _try_anthropic(
        self, model_config: dict, system_prompt: str, user_message: str, api_key: str
    ) -> Optional[str]:
        """Try Anthropic Claude API"""
        try:
            # Third party imports
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)

            response = client.messages.create(
                model=model_config["model"],
                max_tokens=150,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            # Anthropic returns a list of content blocks; join any text fields
            blocks = getattr(response, "content", [])
            text = "".join(getattr(b, "text", "") for b in blocks)
            return text.strip()

        except ImportError:
            logger.debug("[PHASE6] Anthropic library not installed")
            return None
        except Exception as e:
            logger.debug(f"[PHASE6] Anthropic API error: {e}")
            return None

    def _try_google(
        self, model_config: dict, system_prompt: str, user_message: str, api_key: str
    ) -> Optional[str]:
        """Try Google Gemini API"""
        try:
            # Third party imports
            import google.generativeai as genai

            genai.configure(api_key=api_key)  # type: ignore[attr-defined]

            model = genai.GenerativeModel(model_config["model"])  # type: ignore[attr-defined]
            prompt = f"{system_prompt}\n\nUser: {user_message}\nLyrixa:"

            response = model.generate_content(prompt)
            return response.text.strip()

        except ImportError:
            logger.debug("[PHASE6] Google AI library not installed")
            return None
        except Exception as e:
            logger.debug(f"[PHASE6] Google API error: {e}")
            return None

    def _try_cohere(
        self, model_config: dict, system_prompt: str, user_message: str, api_key: str
    ) -> Optional[str]:
        """Try Cohere API"""
        try:
            # Third party imports
            import cohere  # type: ignore[import]

            client = cohere.Client(api_key)

            prompt = f"{system_prompt}\n\nUser: {user_message}\nLyrixa:"

            response = client.generate(
                model=model_config["model"],
                prompt=prompt,
                max_tokens=150,
                temperature=0.7 + (self.personality_state.creativity_level * 0.3),
            )

            return response.generations[0].text.strip()

        except ImportError:
            logger.debug("[PHASE6] Cohere library not installed")
            return None
        except Exception as e:
            logger.debug(f"[PHASE6] Cohere API error: {e}")
            return None

    def _try_huggingface(
        self, model_config: dict, system_prompt: str, user_message: str, api_key: str
    ) -> Optional[str]:
        """Try Hugging Face API"""
        try:
            # Third party imports
            import requests

            headers = {"Authorization": f"Bearer {api_key}"}

            # Use Inference API
            api_url = (
                f"https://api-inference.huggingface.co/models/{model_config['model']}"
            )
            payload = {
                "inputs": f"{system_prompt}\n\nUser: {user_message}\nLyrixa:",
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7
                    + (self.personality_state.creativity_level * 0.3),
                },
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()

            return None

        except ImportError:
            logger.debug("[PHASE6] Requests library not available")
            return None
        except Exception as e:
            logger.debug(f"[PHASE6] Hugging Face API error: {e}")
            return None

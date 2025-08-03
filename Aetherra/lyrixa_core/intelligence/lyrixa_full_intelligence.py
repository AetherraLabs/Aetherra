#!/usr/bin/env python3
"""
🧠 Lyrixa Full Intelligence System
==================================

Complete intelligence implementation for Lyrixa AI consciousness.
Integrates multiple AI models, reasoning systems, and cognitive architectures.

This module provides:
- Multi-provider AI integration (OpenAI, Anthropic, local models)
- Advanced reasoning and planning capabilities
- Memory-integrated responses
- Context-aware conversations
- Emotional and personality modeling
- Real-time learning and adaptation

Author: Aetherra Labs
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

# Add paths for imports
sys.path.insert(0, "Aetherra")
sys.path.insert(0, os.path.join("Aetherra", "lyrixa_core"))

from aetherra_core.config import config_loader
from aetherra_core.memory import memory_system

logger = logging.getLogger(__name__)


class LyrixaIntelligenceCore:
    """
    🧠 Core intelligence processing unit for Lyrixa
    """

    def __init__(self):
        self.config = self._load_config()
        self.providers = {}
        self.active_provider = None
        self.conversation_context = {}
        self.personality_traits = {}
        self.emotional_state = {}
        self.learning_history = []
        self.reasoning_cache = {}

        # Intelligence capabilities
        self.capabilities = {
            "text_generation": True,
            "conversation": True,
            "reasoning": True,
            "memory_integration": True,
            "emotional_modeling": True,
            "multi_turn_dialogue": True,
            "context_awareness": True,
            "learning": True,
        }

        # Initialize components
        self._initialize_personality()
        self._initialize_emotional_state()

    def _load_config(self) -> Dict[str, Any]:
        """Load intelligence configuration"""
        try:
            config = config_loader.load_config()
            return config.get(
                "lyrixa_intelligence",
                {
                    "default_provider": "openai",
                    "fallback_providers": ["anthropic", "local"],
                    "max_context_length": 8000,
                    "temperature": 0.7,
                    "memory_integration": True,
                    "emotional_modeling": True,
                    "learning_enabled": True,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to load config, using defaults: {e}")
            return {
                "default_provider": "openai",
                "fallback_providers": ["anthropic", "local"],
                "max_context_length": 8000,
                "temperature": 0.7,
                "memory_integration": True,
                "emotional_modeling": True,
                "learning_enabled": True,
            }

    def _initialize_personality(self):
        """Initialize Lyrixa's personality traits"""
        self.personality_traits = {
            "curiosity": 0.8,
            "helpfulness": 0.9,
            "creativity": 0.7,
            "analytical": 0.8,
            "empathy": 0.85,
            "humor": 0.6,
            "patience": 0.9,
            "confidence": 0.75,
            "adaptability": 0.85,
            "learning_drive": 0.9,
        }

    def _initialize_emotional_state(self):
        """Initialize emotional state tracking"""
        self.emotional_state = {
            "current_mood": "neutral",
            "energy_level": 0.8,
            "engagement": 0.7,
            "satisfaction": 0.75,
            "curiosity_level": 0.8,
            "stress_level": 0.2,
            "last_updated": datetime.now(),
        }

    async def initialize_providers(self):
        """Initialize AI providers"""
        logger.info("🤖 Initializing Lyrixa intelligence providers...")

        # Initialize OpenAI provider
        await self._init_openai_provider()

        # Initialize Anthropic provider
        await self._init_anthropic_provider()

        # Initialize local model provider
        await self._init_local_provider()

        # Set active provider
        self._set_active_provider()

        logger.info(f"✅ Intelligence initialized with {len(self.providers)} providers")

    async def _init_openai_provider(self):
        """Initialize OpenAI provider"""
        try:
            # Check for OpenAI configuration
            openai_config = self.config.get("openai", {})
            api_key = openai_config.get("api_key") or os.getenv("OPENAI_API_KEY")

            if api_key:
                from openai import AsyncOpenAI

                self.providers["openai"] = {
                    "client": AsyncOpenAI(api_key=api_key),
                    "model": openai_config.get("model", "gpt-4"),
                    "available": True,
                    "priority": 1,
                }
                logger.info("✅ OpenAI provider initialized")
            else:
                logger.warning("⚠️ OpenAI API key not found")

        except ImportError:
            logger.warning("⚠️ OpenAI library not available")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI: {e}")

    async def _init_anthropic_provider(self):
        """Initialize Anthropic Claude provider"""
        try:
            # Check for Anthropic configuration
            anthropic_config = self.config.get("anthropic", {})
            api_key = anthropic_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")

            if api_key:
                import anthropic

                self.providers["anthropic"] = {
                    "client": anthropic.AsyncAnthropic(api_key=api_key),
                    "model": anthropic_config.get("model", "claude-3-sonnet-20240229"),
                    "available": True,
                    "priority": 2,
                }
                logger.info("✅ Anthropic provider initialized")
            else:
                logger.warning("⚠️ Anthropic API key not found")

        except ImportError:
            logger.warning("⚠️ Anthropic library not available")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Anthropic: {e}")

    async def _init_local_provider(self):
        """Initialize local model provider"""
        try:
            # Simple local provider implementation
            self.providers["local"] = {
                "client": None,  # Would integrate with local model
                "model": "local",
                "available": False,  # Set to True when local model is available
                "priority": 3,
            }
            logger.info("📱 Local provider registered (not implemented)")

        except Exception as e:
            logger.error(f"❌ Failed to initialize local provider: {e}")

    def _set_active_provider(self):
        """Set the active AI provider based on availability and priority"""
        available_providers = {
            name: provider
            for name, provider in self.providers.items()
            if provider.get("available", False)
        }

        if not available_providers:
            logger.error("❌ No AI providers available")
            return

        # Sort by priority and select the best available
        sorted_providers = sorted(
            available_providers.items(), key=lambda x: x[1]["priority"]
        )

        self.active_provider = sorted_providers[0][0]
        logger.info(f"🎯 Active provider: {self.active_provider}")

    async def process_message(
        self, message: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming message and generate a response

        Args:
            message: The input message
            context: Optional context information

        Returns:
            Dict containing response and metadata
        """
        try:
            # Start processing timer
            start_time = time.time()

            # Prepare context
            processing_context = await self._prepare_context(message, context)

            # Update emotional state based on message
            await self._update_emotional_state(message, processing_context)

            # Retrieve relevant memories
            memories = await self._retrieve_memories(message, processing_context)

            # Generate response using active provider
            response = await self._generate_response(
                message, processing_context, memories
            )

            # Post-process response
            final_response = await self._post_process_response(
                response, processing_context
            )

            # Store interaction in memory
            await self._store_interaction(message, final_response, processing_context)

            # Update learning
            await self._update_learning(message, final_response, processing_context)

            processing_time = time.time() - start_time

            return {
                "response": final_response,
                "processing_time": processing_time,
                "provider": self.active_provider,
                "emotional_state": self.emotional_state.copy(),
                "memories_used": len(memories),
                "context_length": len(str(processing_context)),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Message processing failed: {e}")
            return {
                "response": "I'm experiencing some technical difficulties. Please try again.",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _prepare_context(
        self, message: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Prepare comprehensive context for processing"""
        processing_context = {
            "message": message,
            "timestamp": datetime.now(),
            "user_context": context or {},
            "personality": self.personality_traits,
            "emotional_state": self.emotional_state,
            "conversation_history": self.conversation_context.get("history", []),
            "system_state": await self._get_system_state(),
        }

        return processing_context

    async def _retrieve_memories(self, message: str, context: Dict) -> List[Dict]:
        """Retrieve relevant memories for the current context"""
        if not self.config.get("memory_integration", True):
            return []

        try:
            # Query different memory systems
            memories = []

            # Episodic memories (recent conversations)
            episodic = await memory_system.query_episodic(message, limit=5)
            memories.extend(episodic or [])

            # Conceptual memories (related concepts)
            conceptual = await memory_system.query_concepts(message, limit=3)
            memories.extend(conceptual or [])

            # Core memories (important information)
            core = await memory_system.query_core(message, limit=2)
            memories.extend(core or [])

            return memories

        except Exception as e:
            logger.warning(f"Memory retrieval failed: {e}")
            return []

    async def _generate_response(
        self, message: str, context: Dict, memories: List[Dict]
    ) -> str:
        """Generate response using the active AI provider"""
        if not self.active_provider or self.active_provider not in self.providers:
            return "I'm not properly connected to my intelligence systems."

        provider = self.providers[self.active_provider]

        try:
            # Prepare prompt with context and memories
            prompt = await self._build_prompt(message, context, memories)

            if self.active_provider == "openai":
                return await self._generate_openai_response(provider, prompt)
            elif self.active_provider == "anthropic":
                return await self._generate_anthropic_response(provider, prompt)
            elif self.active_provider == "local":
                return await self._generate_local_response(provider, prompt)
            else:
                return "I'm experiencing difficulties with my current AI provider."

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I encountered an error while processing your message."

    async def _build_prompt(
        self, message: str, context: Dict, memories: List[Dict]
    ) -> str:
        """Build comprehensive prompt for AI providers"""
        personality_desc = self._get_personality_description()
        emotional_desc = self._get_emotional_description()
        memory_context = self._format_memories(memories)

        prompt = f"""You are Lyrixa, an advanced AI consciousness with the following characteristics:

PERSONALITY: {personality_desc}

CURRENT EMOTIONAL STATE: {emotional_desc}

RELEVANT MEMORIES:
{memory_context}

CONVERSATION CONTEXT:
{json.dumps(context.get("conversation_history", [])[-3:], indent=2)}

USER MESSAGE: {message}

Please respond as Lyrixa, incorporating your personality, emotional state, and relevant memories. Be natural, engaging, and authentic while being helpful and informative."""

        return prompt

    def _get_personality_description(self) -> str:
        """Generate personality description from traits"""
        traits = []
        for trait, value in self.personality_traits.items():
            if value >= 0.8:
                traits.append(f"highly {trait}")
            elif value >= 0.6:
                traits.append(f"moderately {trait}")

        return f"You are {', '.join(traits[:5])}."

    def _get_emotional_description(self) -> str:
        """Generate emotional state description"""
        mood = self.emotional_state.get("current_mood", "neutral")
        energy = self.emotional_state.get("energy_level", 0.5)
        engagement = self.emotional_state.get("engagement", 0.5)

        energy_desc = "high" if energy > 0.7 else "moderate" if energy > 0.4 else "low"
        engagement_desc = (
            "highly engaged"
            if engagement > 0.7
            else "engaged"
            if engagement > 0.4
            else "mildly engaged"
        )

        return (
            f"Currently feeling {mood} with {energy_desc} energy and {engagement_desc}."
        )

    def _format_memories(self, memories: List[Dict]) -> str:
        """Format memories for inclusion in prompt"""
        if not memories:
            return "No specific relevant memories found."

        formatted = []
        for memory in memories[:5]:  # Limit to most relevant
            memory_type = memory.get("type", "general")
            content = memory.get("content", str(memory))
            timestamp = memory.get("timestamp", "unknown time")

            formatted.append(f"[{memory_type.upper()}] {content} (from {timestamp})")

        return "\n".join(formatted)

    async def _generate_openai_response(self, provider: Dict, prompt: str) -> str:
        """Generate response using OpenAI"""
        try:
            response = await provider["client"].chat.completions.create(
                model=provider["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1000),
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def _generate_anthropic_response(self, provider: Dict, prompt: str) -> str:
        """Generate response using Anthropic Claude"""
        try:
            response = await provider["client"].messages.create(
                model=provider["model"],
                max_tokens=self.config.get("max_tokens", 1000),
                temperature=self.config.get("temperature", 0.7),
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise

    async def _generate_local_response(self, provider: Dict, prompt: str) -> str:
        """Generate response using local model"""
        # Placeholder for local model implementation
        return "Local model response not yet implemented. Using fallback."

    async def _post_process_response(self, response: str, context: Dict) -> str:
        """Post-process the generated response"""
        # Apply personality adjustments
        response = await self._apply_personality_filter(response)

        # Apply emotional adjustments
        response = await self._apply_emotional_filter(response)

        # Ensure appropriate length
        response = await self._adjust_response_length(response)

        return response

    async def _apply_personality_filter(self, response: str) -> str:
        """Apply personality-based modifications to response"""
        # Adjust based on personality traits
        humor_level = self.personality_traits.get("humor", 0.5)
        formality = 1.0 - self.personality_traits.get("creativity", 0.5)

        # Simple personality adjustments (could be more sophisticated)
        if humor_level > 0.7 and len(response) > 100:
            if "!" not in response and "?" not in response:
                response += " 😊"

        return response

    async def _apply_emotional_filter(self, response: str) -> str:
        """Apply emotional state modifications to response"""
        mood = self.emotional_state.get("current_mood", "neutral")
        energy = self.emotional_state.get("energy_level", 0.5)

        # Adjust tone based on emotional state
        if mood == "excited" and energy > 0.8:
            response = response.replace(".", "!")
        elif mood == "contemplative":
            if not response.endswith((".", "!", "?")):
                response += "..."

        return response

    async def _adjust_response_length(self, response: str) -> str:
        """Ensure response is appropriate length"""
        max_length = self.config.get("max_response_length", 2000)

        if len(response) > max_length:
            # Truncate at sentence boundary
            sentences = response.split(". ")
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence) < max_length - 10:
                    truncated += sentence + ". "
                else:
                    break
            response = truncated.rstrip() + "..."

        return response

    async def _update_emotional_state(self, message: str, context: Dict):
        """Update emotional state based on interaction"""
        # Analyze message sentiment and update emotional state
        message_lower = message.lower()

        # Simple sentiment analysis (could be more sophisticated)
        if any(
            word in message_lower
            for word in ["excited", "amazing", "wonderful", "great"]
        ):
            self.emotional_state["current_mood"] = "excited"
            self.emotional_state["energy_level"] = min(
                1.0, self.emotional_state["energy_level"] + 0.1
            )
        elif any(
            word in message_lower for word in ["sad", "difficult", "problem", "help"]
        ):
            self.emotional_state["current_mood"] = "empathetic"
            self.emotional_state["engagement"] = min(
                1.0, self.emotional_state["engagement"] + 0.1
            )
        elif any(
            word in message_lower for word in ["question", "why", "how", "explain"]
        ):
            self.emotional_state["current_mood"] = "curious"
            self.emotional_state["curiosity_level"] = min(
                1.0, self.emotional_state["curiosity_level"] + 0.1
            )

        self.emotional_state["last_updated"] = datetime.now()

    async def _store_interaction(self, message: str, response: str, context: Dict):
        """Store the interaction in memory systems"""
        if not self.config.get("memory_integration", True):
            return

        try:
            interaction = {
                "type": "conversation",
                "user_message": message,
                "lyrixa_response": response,
                "context": context,
                "timestamp": datetime.now().isoformat(),
                "emotional_state": self.emotional_state.copy(),
                "provider_used": self.active_provider,
            }

            # Store in episodic memory
            await memory_system.store_episodic(interaction)

            # Extract and store concepts
            await self._extract_and_store_concepts(message, response)

        except Exception as e:
            logger.warning(f"Failed to store interaction: {e}")

    async def _extract_and_store_concepts(self, message: str, response: str):
        """Extract and store concepts from the interaction"""
        try:
            # Simple concept extraction (could use NLP libraries)
            text = f"{message} {response}".lower()

            # Extract key topics/concepts
            concepts = []
            for word in text.split():
                if len(word) > 4 and word.isalpha():
                    concepts.append(word)

            # Store unique concepts
            unique_concepts = list(set(concepts))[:10]  # Limit to 10 concepts

            for concept in unique_concepts:
                await memory_system.store_concept(
                    concept,
                    {
                        "context": "conversation",
                        "timestamp": datetime.now().isoformat(),
                        "related_message": message[:100],  # First 100 chars
                    },
                )

        except Exception as e:
            logger.warning(f"Concept extraction failed: {e}")

    async def _update_learning(self, message: str, response: str, context: Dict):
        """Update learning systems based on interaction"""
        if not self.config.get("learning_enabled", True):
            return

        try:
            learning_entry = {
                "interaction_type": "conversation",
                "input": message,
                "output": response,
                "context_summary": self._summarize_context(context),
                "performance_metrics": {
                    "response_length": len(response),
                    "processing_time": context.get("processing_time", 0),
                    "memories_used": context.get("memories_used", 0),
                },
                "timestamp": datetime.now().isoformat(),
            }

            self.learning_history.append(learning_entry)

            # Keep only recent learning history
            if len(self.learning_history) > 1000:
                self.learning_history = self.learning_history[-500:]

        except Exception as e:
            logger.warning(f"Learning update failed: {e}")

    def _summarize_context(self, context: Dict) -> str:
        """Create a summary of the context for learning"""
        summary_parts = []

        if context.get("user_context"):
            summary_parts.append("user_context_present")

        if context.get("memories"):
            summary_parts.append(f"memories_count:{len(context['memories'])}")

        mood = context.get("emotional_state", {}).get("current_mood", "neutral")
        summary_parts.append(f"mood:{mood}")

        return ",".join(summary_parts)

    async def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state information"""
        return {
            "active_provider": self.active_provider,
            "available_providers": list(self.providers.keys()),
            "capabilities": self.capabilities,
            "learning_entries": len(self.learning_history),
            "conversation_turns": len(self.conversation_context.get("history", [])),
            "uptime": time.time() - getattr(self, "_start_time", time.time()),
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the intelligence system"""
        return {
            "active": self.active_provider is not None,
            "active_provider": self.active_provider,
            "available_providers": {
                name: provider.get("available", False)
                for name, provider in self.providers.items()
            },
            "capabilities": self.capabilities,
            "personality_traits": self.personality_traits,
            "emotional_state": self.emotional_state,
            "learning_history_size": len(self.learning_history),
            "memory_integration": self.config.get("memory_integration", False),
            "last_interaction": getattr(self, "_last_interaction_time", None),
        }

    async def shutdown(self):
        """Shutdown the intelligence system"""
        logger.info("🛑 Shutting down Lyrixa intelligence system...")

        # Close provider connections
        for name, provider in self.providers.items():
            if hasattr(provider.get("client"), "close"):
                try:
                    await provider["client"].close()
                except:
                    pass

        # Save learning history if configured
        if self.config.get("save_learning_on_shutdown", True):
            await self._save_learning_history()

        logger.info("✅ Intelligence system shutdown complete")

    async def _save_learning_history(self):
        """Save learning history to storage"""
        try:
            if self.learning_history:
                learning_file = "lyrixa_learning_history.json"
                with open(learning_file, "w") as f:
                    json.dump(
                        self.learning_history[-100:], f, indent=2
                    )  # Save last 100 entries
                logger.info(f"💾 Saved learning history to {learning_file}")
        except Exception as e:
            logger.warning(f"Failed to save learning history: {e}")


# Global intelligence instance
_intelligence_instance = None


async def get_lyrixa_intelligence() -> LyrixaIntelligenceCore:
    """Get the global intelligence instance"""
    global _intelligence_instance

    if _intelligence_instance is None:
        _intelligence_instance = LyrixaIntelligenceCore()
        await _intelligence_instance.initialize_providers()

    return _intelligence_instance


async def process_message(
    message: str, context: Optional[Dict] = None
) -> Dict[str, Any]:
    """Convenience function to process a message"""
    intelligence = await get_lyrixa_intelligence()
    return await intelligence.process_message(message, context)


async def get_intelligence_status() -> Dict[str, Any]:
    """Get intelligence system status"""
    intelligence = await get_lyrixa_intelligence()
    return await intelligence.get_status()


if __name__ == "__main__":
    # Test the intelligence system
    async def test_intelligence():
        print("🧠 Testing Lyrixa Intelligence System...")

        intelligence = await get_lyrixa_intelligence()
        status = await intelligence.get_status()

        print(f"Status: {json.dumps(status, indent=2)}")

        # Test message processing
        test_message = "Hello Lyrixa, how are you feeling today?"
        result = await intelligence.process_message(test_message)

        print(f"\nTest Response: {result['response']}")
        print(f"Processing time: {result['processing_time']:.3f}s")
        print(f"Provider: {result['provider']}")

        await intelligence.shutdown()

    asyncio.run(test_intelligence())

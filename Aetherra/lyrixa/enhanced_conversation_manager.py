"""
🤖 ENHANCED CONVERSATION MANAGER WITH ADVANCED MEMORY
=====================================================

This module provides an enhanced conversation manager that integrates
with the Advanced Memory Systems for sophisticated context-aware conversations.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
    logger.info("✅ OpenAI library available")
except ImportError as e:
    OPENAI_AVAILABLE = False
    logger.warning(f"[WARN] OpenAI library not available: {e}")
    OpenAI = None

# Import our advanced memory system
try:
    from Aetherra.lyrixa.advanced_memory_integration import (
        AdvancedMemoryManager,
        create_advanced_memory_manager,
    )

    MEMORY_INTEGRATION_AVAILABLE = True
    logger.info("✅ Advanced Memory Integration available")
except ImportError as e:
    MEMORY_INTEGRATION_AVAILABLE = False
    logger.warning(f"[WARN] Advanced Memory Integration not available: {e}")
    AdvancedMemoryManager = None
    create_advanced_memory_manager = None


class EnhancedConversationManager:
    """
    🤖 Enhanced Conversation Manager with Advanced Memory Integration

    Features:
    - OpenAI GPT integration with advanced prompting
    - Quantum-enhanced memory recall and storage
    - Context-aware conversation handling
    - Pattern-based response optimization
    - Conversation flow analysis
    - Intelligent memory-driven responses
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # OpenAI configuration
        self.openai_client = None
        self.api_key = self.config.get("openai_api_key", "")
        self.model = self.config.get("openai_model", "gpt-3.5-turbo")
        self.max_tokens = self.config.get("max_tokens", 1500)
        self.temperature = self.config.get("temperature", 0.7)

        # Advanced memory integration
        self.memory_manager = None
        self.memory_enabled = self.config.get("memory_enabled", True)

        # Conversation statistics
        self.conversation_stats = {
            "total_conversations": 0,
            "memory_enhanced_responses": 0,
            "openai_api_calls": 0,
            "fallback_responses": 0,
            "average_response_time": 0.0,
            "memory_recall_successes": 0,
        }

        # Enhanced prompting system
        self.base_system_prompt = self.config.get(
            "system_prompt",
            "You are Aetherra, an advanced AI OS with quantum-enhanced memory capabilities. "
            "You have access to sophisticated memory systems that allow you to recall past "
            "conversations, recognize patterns, and provide contextually aware responses. "
            "Be helpful, intelligent, and leverage your memory capabilities when relevant.",
        )

        # Response enhancement settings
        self.memory_context_weight = self.config.get("memory_context_weight", 0.3)
        self.pattern_enhancement = self.config.get("pattern_enhancement", True)
        self.conversation_flow_analysis = self.config.get(
            "conversation_flow_analysis", True
        )

        logger.info("🤖 EnhancedConversationManager initialized")

    async def initialize(self) -> bool:
        """Initialize the enhanced conversation manager"""
        try:
            # Initialize OpenAI client
            if OPENAI_AVAILABLE and self.api_key and OpenAI:
                self.openai_client = OpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI client initialized")
            else:
                logger.warning("[WARN] OpenAI not available, using fallback responses")

            # Initialize advanced memory manager
            if (
                MEMORY_INTEGRATION_AVAILABLE
                and self.memory_enabled
                and create_advanced_memory_manager
            ):
                memory_config = self.config.get("memory_config", {})
                self.memory_manager = create_advanced_memory_manager(memory_config)
                await self.memory_manager.initialize()
                logger.info("✅ Advanced memory manager initialized")
            else:
                logger.warning("[WARN] Advanced memory not available")

            return True

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False

    async def generate_response(
        self,
        message: str,
        user_id: str = "default",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an enhanced response using memory-augmented conversation
        """

        try:
            response_start = time.time()
            context = context or {}

            # Step 1: Memory recall to gather relevant context
            memory_context = {}
            if self.memory_manager:
                memory_results = await self._recall_relevant_memories(message, user_id)
                memory_context = self._process_memory_results(memory_results)

            # Step 2: Generate enhanced response
            response_data = await self._generate_memory_enhanced_response(
                message, user_id, memory_context, context
            )

            # Step 3: Store conversation in memory systems
            if self.memory_manager:
                storage_result = await self.memory_manager.store_conversation_memory(
                    message=message,
                    response=response_data["response"],
                    user_id=user_id,
                    context={
                        **context,
                        "memory_enhanced": memory_context.get("memory_enhanced", False),
                        "patterns_used": memory_context.get("patterns_discovered", []),
                        "response_confidence": response_data.get("confidence", 0.5),
                    },
                )
                memory_context["storage_result"] = storage_result

            # Step 4: Update statistics
            response_time = time.time() - response_start
            await self._update_conversation_stats(response_time, memory_context)

            # Prepare final response
            final_response = {
                "response": response_data["response"],
                "confidence": response_data.get("confidence", 0.5),
                "source": response_data.get("source", "unknown"),
                "memory_enhanced": memory_context.get("memory_enhanced", False),
                "memory_context": memory_context,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
            }

            logger.info(
                f"💬 Enhanced response generated (memory: {memory_context.get('memory_enhanced', False)})"
            )
            return final_response

        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            return await self._generate_fallback_response(message, user_id, str(e))

    async def _recall_relevant_memories(
        self, message: str, user_id: str
    ) -> Dict[str, Any]:
        """Recall relevant memories for the current conversation"""

        try:
            if not self.memory_manager:
                return {"results": [], "memory_enhanced": False}

            # Use quantum-hybrid strategy for best results
            memory_results = await self.memory_manager.recall_memory(
                query=message, user_id=user_id, strategy="quantum_hybrid", limit=5
            )

            # Analyze memory quality
            high_relevance_results = [
                r
                for r in memory_results.get("results", [])
                if r.get("relevance", 0.0) > 0.6
            ]

            memory_results["memory_enhanced"] = len(high_relevance_results) > 0
            memory_results["high_relevance_count"] = len(high_relevance_results)

            if memory_results["memory_enhanced"]:
                self.conversation_stats["memory_recall_successes"] += 1

            return memory_results

        except Exception as e:
            logger.error(f"Memory recall failed: {e}")
            return {"results": [], "memory_enhanced": False, "error": str(e)}

    def _process_memory_results(self, memory_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process memory results for response enhancement"""

        try:
            results = memory_results.get("results", [])

            # Categorize memories by type and relevance
            categorized_memories = {
                "quantum_memories": [],
                "episodic_memories": [],
                "pattern_memories": [],
                "context_memories": [],
            }

            for result in results:
                memory_type = result.get("type", "unknown")
                relevance = result.get("relevance", 0.0)

                if relevance > 0.5:  # Only use high-relevance memories
                    if "quantum" in memory_type:
                        categorized_memories["quantum_memories"].append(result)
                    elif "conversation" in memory_type or "episodic" in memory_type:
                        categorized_memories["episodic_memories"].append(result)
                    elif "pattern" in memory_type:
                        categorized_memories["pattern_memories"].append(result)
                    elif "context" in memory_type:
                        categorized_memories["context_memories"].append(result)

            # Extract patterns and topics
            patterns_discovered = []
            for pattern_memory in categorized_memories["pattern_memories"]:
                if "pattern" in pattern_memory.get("content", "").lower():
                    patterns_discovered.append(
                        {
                            "pattern": pattern_memory.get("content", ""),
                            "frequency": pattern_memory.get("frequency", 1),
                            "strength": pattern_memory.get("pattern_strength", 0.5),
                        }
                    )

            # Create memory context summary
            memory_context = {
                "memory_enhanced": len(results) > 0
                and any(r.get("relevance", 0) > 0.6 for r in results),
                "categorized_memories": categorized_memories,
                "patterns_discovered": patterns_discovered,
                "total_memories": len(results),
                "high_relevance_memories": len(
                    [r for r in results if r.get("relevance", 0) > 0.6]
                ),
                "memory_sources": list(
                    set(r.get("source", "unknown") for r in results)
                ),
                "recall_metadata": memory_results.get("metadata", {}),
            }

            return memory_context

        except Exception as e:
            logger.error(f"Memory processing failed: {e}")
            return {"memory_enhanced": False, "error": str(e)}

    async def _generate_memory_enhanced_response(
        self,
        message: str,
        user_id: str,
        memory_context: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate response enhanced with memory context"""

        try:
            # Construct enhanced prompt with memory context
            enhanced_prompt = await self._build_memory_enhanced_prompt(
                message, memory_context, context
            )

            # Try OpenAI first if available
            if self.openai_client:
                return await self._generate_openai_response(
                    enhanced_prompt, memory_context
                )
            else:
                return await self._generate_intelligent_fallback(
                    message, memory_context
                )

        except Exception as e:
            logger.error(f"Enhanced response generation failed: {e}")
            return {
                "response": "I encountered an issue generating a response, but I'm still here to help!",
                "source": "error_fallback",
                "confidence": 0.3,
                "error": str(e),
            }

    async def _build_memory_enhanced_prompt(
        self, message: str, memory_context: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Build enhanced prompt with memory context"""

        messages = [{"role": "system", "content": self.base_system_prompt}]

        # Add memory context if available
        if memory_context.get("memory_enhanced", False):
            memory_summary = await self._create_memory_summary(memory_context)

            memory_prompt = (
                f"MEMORY CONTEXT:\n{memory_summary}\n\n"
                f"Use this memory context to provide a more informed and contextual response. "
                f"Reference relevant past conversations or patterns when appropriate, but don't "
                f"over-reference memory unless directly relevant."
            )

            messages.append({"role": "system", "content": memory_prompt})

            # If we discovered patterns, add pattern guidance
            patterns = memory_context.get("patterns_discovered", [])
            if patterns and self.pattern_enhancement:
                pattern_prompt = (
                    f"DISCOVERED PATTERNS:\n"
                    + "\n".join(
                        [
                            f"- {p['pattern']} (frequency: {p['frequency']})"
                            for p in patterns[:3]
                        ]
                    )
                    + "\n\nConsider these patterns when crafting your response."
                )
                messages.append({"role": "system", "content": pattern_prompt})

        # Add conversation flow context
        if self.conversation_flow_analysis and memory_context.get(
            "categorized_memories"
        ):
            recent_conversations = memory_context["categorized_memories"].get(
                "episodic_memories", []
            )
            if recent_conversations:
                flow_context = "RECENT CONVERSATION FLOW:\n"
                for conv in recent_conversations[:2]:  # Last 2 conversations
                    content = conv.get("content", "")
                    if len(content) > 100:
                        content = content[:100] + "..."
                    flow_context += f"- {content}\n"

                messages.append({"role": "system", "content": flow_context})

        # Add the user message
        messages.append({"role": "user", "content": message})

        return messages

    async def _create_memory_summary(self, memory_context: Dict[str, Any]) -> str:
        """Create a concise summary of memory context"""

        summary_parts = []

        # Quantum memories
        quantum_memories = memory_context.get("categorized_memories", {}).get(
            "quantum_memories", []
        )
        if quantum_memories:
            summary_parts.append(
                f"Quantum-enhanced memories ({len(quantum_memories)} entries):"
            )
            for qm in quantum_memories[:2]:  # Top 2
                content = qm.get("content", "")[:80]
                summary_parts.append(f"  - {content}...")

        # Episodic memories
        episodic_memories = memory_context.get("categorized_memories", {}).get(
            "episodic_memories", []
        )
        if episodic_memories:
            summary_parts.append(
                f"Past conversations ({len(episodic_memories)} relevant):"
            )
            for em in episodic_memories[:2]:  # Top 2
                content = em.get("content", "")[:80]
                summary_parts.append(f"  - {content}...")

        # Patterns
        patterns = memory_context.get("patterns_discovered", [])
        if patterns:
            summary_parts.append(f"Conversation patterns:")
            for pattern in patterns[:2]:  # Top 2
                summary_parts.append(
                    f"  - {pattern['pattern']} (×{pattern['frequency']})"
                )

        return (
            "\n".join(summary_parts)
            if summary_parts
            else "No significant memory context found."
        )

    async def _generate_openai_response(
        self, messages: List[Dict[str, str]], memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate response using OpenAI with memory enhancement"""

        try:
            if not self.openai_client:
                return await self._generate_intelligent_fallback(
                    messages[-1]["content"], memory_context
                )

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model,
                messages=messages,  # type: ignore
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            response_text = response.choices[0].message.content

            # Calculate confidence based on memory enhancement
            base_confidence = 0.8
            memory_bonus = 0.1 if memory_context.get("memory_enhanced", False) else 0.0
            pattern_bonus = 0.05 * len(memory_context.get("patterns_discovered", []))

            confidence = min(base_confidence + memory_bonus + pattern_bonus, 1.0)

            self.conversation_stats["openai_api_calls"] += 1
            if memory_context.get("memory_enhanced", False):
                self.conversation_stats["memory_enhanced_responses"] += 1

            # Safe access to usage statistics
            token_usage = {}
            if hasattr(response, "usage") and response.usage:
                token_usage = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(
                        response.usage, "completion_tokens", 0
                    ),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                }

            return {
                "response": response_text,
                "source": "openai_memory_enhanced"
                if memory_context.get("memory_enhanced")
                else "openai",
                "confidence": confidence,
                "token_usage": token_usage,
            }

        except Exception as e:
            logger.error(f"OpenAI response generation failed: {e}")
            return await self._generate_intelligent_fallback(
                messages[-1]["content"], memory_context
            )

    async def _generate_intelligent_fallback(
        self, message: str, memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate intelligent fallback response using memory context"""

        try:
            # Analyze message for intent
            message_lower = message.lower()

            # Check if we have relevant memory context
            if memory_context.get("memory_enhanced", False):
                # Try to use memory context for response
                episodic_memories = memory_context.get("categorized_memories", {}).get(
                    "episodic_memories", []
                )

                if episodic_memories:
                    # Reference a relevant past conversation
                    response = (
                        f"Based on our previous conversations, I remember we discussed similar topics. "
                        f"Let me build on that context to help you with '{message}'. "
                        f"I'm continuously learning from our interactions to provide better assistance."
                    )

                    return {
                        "response": response,
                        "source": "memory_fallback",
                        "confidence": 0.6,
                    }

            # Pattern-based responses
            patterns = memory_context.get("patterns_discovered", [])
            if patterns:
                pattern = patterns[0]  # Most frequent pattern
                response = (
                    f"I notice a pattern in our conversations around '{pattern['pattern']}'. "
                    f"Regarding '{message}', I'm here to help you explore this topic further. "
                    f"What specific aspect would you like to focus on?"
                )

                return {
                    "response": response,
                    "source": "pattern_fallback",
                    "confidence": 0.5,
                }

            # Basic intelligent responses
            intelligent_responses = {
                "hello": "Hello! I'm Aetherra, your AI assistant with advanced memory capabilities. How can I help you today?",
                "help": "I'm here to assist you! I have access to quantum-enhanced memory systems that allow me to remember our conversations and provide contextual help. What would you like to know?",
                "memory": "I use advanced memory systems including quantum-enhanced storage to remember our conversations and provide better, more contextual responses. Is there something specific about my memory capabilities you'd like to know?",
                "quantum": "I utilize quantum-enhanced memory processing that allows for sophisticated pattern recognition and contextual understanding. This helps me provide more intelligent responses based on our conversation history.",
                "aetherra": "I am Aetherra, an advanced AI operating system with quantum-enhanced capabilities. I'm designed to learn, remember, and adapt to provide you with the best possible assistance.",
            }

            # Find matching response
            for keyword, response in intelligent_responses.items():
                if keyword in message_lower:
                    return {
                        "response": response,
                        "source": "intelligent_fallback",
                        "confidence": 0.7,
                    }

            # Default fallback
            self.conversation_stats["fallback_responses"] += 1
            return {
                "response": (
                    f"I understand you're asking about '{message}'. While I'm processing your request "
                    f"through my advanced memory systems, I want to ensure I give you the most helpful response. "
                    f"Could you provide a bit more context about what specific aspect you're interested in?"
                ),
                "source": "default_fallback",
                "confidence": 0.4,
            }

        except Exception as e:
            logger.error(f"Fallback generation failed: {e}")
            return {
                "response": "I'm here to help! Please tell me more about what you need assistance with.",
                "source": "error_fallback",
                "confidence": 0.3,
                "error": str(e),
            }

    async def _generate_fallback_response(
        self, message: str, user_id: str, error: str
    ) -> Dict[str, Any]:
        """Generate fallback response when main generation fails"""

        return {
            "response": "I encountered a technical issue, but I'm still here to help! Please try rephrasing your question.",
            "confidence": 0.2,
            "source": "system_fallback",
            "memory_enhanced": False,
            "memory_context": {"error": error},
            "response_time": 0.0,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "error": error,
        }

    async def _update_conversation_stats(
        self, response_time: float, memory_context: Dict[str, Any]
    ):
        """Update conversation statistics"""

        self.conversation_stats["total_conversations"] += 1

        # Update average response time
        total = self.conversation_stats["total_conversations"]
        current_avg = self.conversation_stats["average_response_time"]
        self.conversation_stats["average_response_time"] = (
            current_avg * (total - 1) + response_time
        ) / total

        # Update memory enhancement stats
        if memory_context.get("memory_enhanced", False):
            self.conversation_stats["memory_enhanced_responses"] += 1

    def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive conversation statistics"""

        stats = self.conversation_stats.copy()

        # Add memory statistics if available
        if self.memory_manager:
            memory_stats = self.memory_manager.get_memory_statistics()
            stats["memory_system_stats"] = memory_stats

        # Calculate percentages
        total = stats["total_conversations"]
        if total > 0:
            stats["memory_enhancement_rate"] = (
                stats["memory_enhanced_responses"] / total
            )
            stats["fallback_rate"] = stats["fallback_responses"] / total
            stats["openai_usage_rate"] = stats["openai_api_calls"] / total

        # Add system status
        stats["system_status"] = {
            "openai_available": self.openai_client is not None,
            "memory_system_available": self.memory_manager is not None,
            "memory_enabled": self.memory_enabled,
            "model": self.model,
        }

        return stats

    async def cleanup_old_conversations(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old conversation data"""

        cleanup_result: Dict[str, Any] = {"conversation_manager": "no cleanup needed"}

        if self.memory_manager:
            memory_cleanup = await self.memory_manager.cleanup_old_memories(days_old)
            cleanup_result["memory_system"] = memory_cleanup

        return cleanup_result


# Convenience function for easy integration
def create_enhanced_conversation_manager(
    config: Optional[Dict[str, Any]] = None,
) -> EnhancedConversationManager:
    """Create and initialize an enhanced conversation manager"""
    return EnhancedConversationManager(config)


__all__ = ["EnhancedConversationManager", "create_enhanced_conversation_manager"]

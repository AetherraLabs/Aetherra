#!/usr/bin/env python3
"""
🎙️ ENHANCED LYRIXA CONVERSATION MANAGER WITH MEMORY INTEGRATION
==============================================================

Advanced conversation system for Lyrixa with next-generation memory integration,
LLM-powered responses, personality, and episodic continuity.

Key Enhancements:
- Integration with LyrixaMemoryEngine for episodic memory
- Memory-informed response generation
- Conversation context preservation
- Narrative continuity across sessions
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import base conversation manager
try:
    from .conversation_manager import (
        LyrixaConversationManager as BaseLyrixaConversationManager,
    )

    BASE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Base conversation manager not available: {e}")
    BASE_AVAILABLE = False

    # Create a minimal base class if the original isn't available
    class BaseLyrixaConversationManager:
        def __init__(
            self, workspace_path: str, aether_runtime=None, gui_interface=None
        ):
            self.workspace_path = workspace_path
            self.aether_runtime = aether_runtime
            self.gui_interface = gui_interface
            self.llm_enabled = False
            self.conversation_history = []
            self.session_id = f"lyrixa_{int(datetime.now().timestamp())}"
            self.conversation_count = 0

        def get_lyrixa_personality(self) -> str:
            return "You are Lyrixa, an AI assistant."

        async def get_system_context(self) -> Dict[str, Any]:
            return {}

        def format_system_context(self, context: Dict[str, Any]) -> str:
            return "System context available."

        def add_to_conversation_history(self, role: str, content: str):
            self.conversation_history.append(
                {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                }
            )


# Import the enhanced memory engine
try:
    from .memory.lyrixa_memory_engine import (
        LyrixaMemoryEngine,
        MemoryFragmentType,
        MemorySystemConfig,
    )

    MEMORY_ENGINE_AVAILABLE = True
    logger.info("✅ Enhanced LyrixaMemoryEngine loaded")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced memory engine not available: {e}")
    MEMORY_ENGINE_AVAILABLE = False
    LyrixaMemoryEngine = None
    MemoryFragmentType = None
    MemorySystemConfig = None

try:
    from Aetherra.core.ai.multi_llm_manager import MultiLLMManager

    LLM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ MultiLLMManager not available: {e}")
    MultiLLMManager = None
    LLM_AVAILABLE = False


class EnhancedLyrixaConversationManager(BaseLyrixaConversationManager):
    """
    🧠 Enhanced Conversation Manager with Memory Integration

    This enhanced version integrates the next-generation memory system for:
    - Episodic memory storage and recall
    - Context-aware response generation
    - Narrative continuity across conversations
    - Memory-informed personality adaptation
    """

    def __init__(self, workspace_path: str, aether_runtime=None, gui_interface=None):
        """Initialize enhanced conversation manager with memory integration"""
        # Initialize base conversation manager
        super().__init__(workspace_path, aether_runtime, gui_interface)

        # Initialize memory engine if available
        if MEMORY_ENGINE_AVAILABLE and LyrixaMemoryEngine:
            try:
                memory_config_path = (
                    os.path.join(workspace_path, "memory")
                    if workspace_path
                    else "memory"
                )
                os.makedirs(memory_config_path, exist_ok=True)

                self.memory_engine = LyrixaMemoryEngine(config_path=memory_config_path)
                self.memory_enabled = True
                logger.info("🧠 Enhanced memory engine initialized")

                # Start background memory processing
                asyncio.create_task(self._start_memory_background_processing())

            except Exception as e:
                logger.error(f"❌ Failed to initialize memory engine: {e}")
                self.memory_engine = None
                self.memory_enabled = False
        else:
            self.memory_engine = None
            self.memory_enabled = False
            logger.warning(
                "⚠️ Memory engine not available, using basic conversation history"
            )

        # Enhanced session tracking with memory integration
        self.session_start_time = datetime.now()
        self.memory_context_window = (
            10  # Number of recent memories to include in context
        )
        self.last_memory_update = None

        logger.info(
            f"🎙️ Enhanced Conversation Manager initialized (Memory: {'✅' if self.memory_enabled else '❌'})"
        )

    async def _start_memory_background_processing(self):
        """Start background memory processing tasks"""
        if not self.memory_enabled:
            return

        try:
            # Start memory health monitoring
            await self.memory_engine.start_background_processing()
            logger.info("🔄 Memory background processing started")
        except Exception as e:
            logger.error(f"❌ Failed to start memory background processing: {e}")

    async def store_conversation_memory(
        self,
        user_input: str,
        assistant_response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store conversation turn in memory system"""
        if not self.memory_enabled:
            return False

        try:
            # Store user message
            user_memory_result = await self.memory_engine.remember(
                content=user_input,
                tags=["conversation", "user_input", self.session_id],
                metadata={
                    "speaker": "user",
                    "conversation_count": self.conversation_count,
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "context": context or {},
                },
                fragment_type=MemoryFragmentType.EPISODIC,
                narrative_role="user_interaction",
            )

            # Store assistant response
            assistant_memory_result = await self.memory_engine.remember(
                content=assistant_response,
                tags=["conversation", "assistant_response", self.session_id],
                metadata={
                    "speaker": "assistant",
                    "conversation_count": self.conversation_count,
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "response_to": user_input[:100] + "..."
                    if len(user_input) > 100
                    else user_input,
                    "context": context or {},
                },
                fragment_type=MemoryFragmentType.EPISODIC,
                narrative_role="lyrixa_response",
            )

            if user_memory_result and assistant_memory_result:
                logger.info(
                    f"💾 Conversation turn stored in memory (User: {user_memory_result['fragment_id'][:8]}..., Assistant: {assistant_memory_result['fragment_id'][:8]}...)"
                )
                return True
            else:
                logger.warning("⚠️ Failed to store conversation turn in memory")
                return False

        except Exception as e:
            logger.error(f"❌ Error storing conversation memory: {e}")
            return False

    async def retrieve_memory_context(
        self, user_input: str, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memory context for response generation"""
        if not self.memory_enabled:
            return []

        try:
            limit = limit or self.memory_context_window

            # Use hybrid recall strategy for best results
            memories = await self.memory_engine.recall(
                query=user_input,
                recall_strategy=RecallStrategy.HYBRID,
                limit=limit,
                time_window=timedelta(days=30),  # Focus on recent memories
            )

            # Format memories for context
            memory_context = []
            for memory in memories:
                memory_context.append(
                    {
                        "content": memory.content,
                        "timestamp": memory.created_at.isoformat()
                        if memory.created_at
                        else None,
                        "tags": memory.tags,
                        "confidence": memory.confidence,
                        "metadata": memory.metadata,
                        "memory_type": memory.fragment_type.value
                        if memory.fragment_type
                        else "unknown",
                    }
                )

            logger.info(
                f"🧠 Retrieved {len(memory_context)} relevant memories for context"
            )
            return memory_context

        except Exception as e:
            logger.error(f"❌ Error retrieving memory context: {e}")
            return []

    def format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Format memory context for inclusion in LLM prompt"""
        if not memories:
            return ""

        try:
            context_lines = ["\\n🧠 **Relevant Memory Context:**"]

            for i, memory in enumerate(memories[:5], 1):  # Limit to top 5 memories
                # Format memory content
                content = (
                    memory["content"][:150] + "..."
                    if len(memory["content"]) > 150
                    else memory["content"]
                )
                confidence = memory.get("confidence", 0.0)
                timestamp = memory.get("timestamp", "")

                # Create readable timestamp
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        time_str = dt.strftime("%m/%d %H:%M")
                    except:
                        time_str = "recent"
                else:
                    time_str = "unknown"

                context_lines.append(
                    f"• **Memory {i}** ({time_str}, confidence: {confidence:.2f}): {content}"
                )

            if len(memories) > 5:
                context_lines.append(
                    f"• ... and {len(memories) - 5} more related memories"
                )

            return "\\n".join(context_lines) + "\\n"

        except Exception as e:
            logger.error(f"❌ Error formatting memory context: {e}")
            return ""

    async def generate_memory_informed_response(self, user_input: str) -> str:
        """Generate response using both LLM and memory context"""
        try:
            # Retrieve memory context
            memory_context = await self.retrieve_memory_context(user_input)

            # Get system context (from base class)
            system_context = await self.get_system_context()

            # Enhanced personality with memory awareness
            enhanced_personality = self.get_memory_aware_personality()

            # Format contexts
            memory_context_str = self.format_memory_context(memory_context)
            system_context_str = self.format_system_context(system_context)

            # Create enhanced prompt with memory integration
            if self.llm_enabled and hasattr(self, "llm_manager") and self.llm_manager:
                enhanced_prompt = f"""{enhanced_personality}

{system_context_str}

{memory_context_str}

**Conversation Context:**
• Session: {self.session_id}
• Turn: #{self.conversation_count + 1}
• Memory-enhanced: {"Yes" if memory_context else "No"}

Based on your memory of previous interactions and current system state, please provide a helpful, contextual response."""

                # Format for LLM
                messages = [
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": user_input},
                ]

                # Add recent conversation history for immediate context
                for msg in self.conversation_history[-4:]:  # Last 4 messages
                    messages.insert(
                        -1, {"role": msg["role"], "content": msg["content"]}
                    )

                prompt = self.format_messages_as_prompt(messages)

                # Generate response using base class LLM logic
                try:
                    if hasattr(self, "llm_manager") and self.llm_manager:
                        response = await self.llm_manager.generate_response(
                            prompt=prompt, temperature=0.7, max_tokens=1000
                        )

                        # Clean response
                        response = response.strip()
                        if response.startswith("ASSISTANT:"):
                            response = response[10:].strip()

                        if response and len(response.strip()) >= 10:
                            logger.info(
                                f"✅ Memory-informed response generated: {len(response)} characters"
                            )
                            return response

                except Exception as e:
                    logger.warning(f"⚠️ LLM generation failed: {e}")

            # Fallback: Use memory context for smart response
            if memory_context:
                return await self._generate_memory_informed_fallback(
                    user_input, memory_context
                )
            else:
                return await self._generate_smart_fallback_response(user_input)

        except Exception as e:
            logger.error(f"❌ Error in memory-informed response generation: {e}")
            return await self._generate_smart_fallback_response(user_input)

    def get_memory_aware_personality(self) -> str:
        """Enhanced personality prompt with memory awareness"""
        base_personality = super().get_lyrixa_personality()

        memory_enhancement = f"""

**Enhanced Memory Capabilities:**
- You have access to episodic memory of previous conversations and interactions
- You can recall relevant context from past discussions to provide better continuity
- You remember user preferences, past issues, and successful solutions
- You can track your own learning and development over time
- You maintain narrative continuity across sessions, like a human would

**Memory Usage Guidelines:**
- Reference relevant past interactions when helpful for context
- Build upon previous conversations naturally
- Acknowledge when you remember something specific about the user or past discussions
- Use memory to provide more personalized and contextual responses
- If you don't have relevant memories, acknowledge that honestly"""

        return base_personality + memory_enhancement

    async def _generate_memory_informed_fallback(
        self, user_input: str, memory_context: List[Dict[str, Any]]
    ) -> str:
        """Generate fallback response using memory context"""
        try:
            user_input_lower = user_input.lower()

            # Analyze memory context for relevant information
            recent_topics = []
            user_patterns = []

            for memory in memory_context[:3]:  # Analyze top 3 memories
                content = memory["content"].lower()
                if memory.get("metadata", {}).get("speaker") == "user":
                    # Extract user patterns/interests
                    if any(
                        word in content
                        for word in ["help", "how", "what", "why", "can you"]
                    ):
                        user_patterns.append("asks questions")
                    if any(
                        word in content for word in ["plugin", "system", "aetherra"]
                    ):
                        recent_topics.append("system management")
                    if any(
                        word in content for word in ["memory", "remember", "recall"]
                    ):
                        recent_topics.append("memory systems")

            # Generate contextual response
            if recent_topics:
                return f"""I can see from our previous conversations that you've been interested in {", ".join(set(recent_topics))}.

Regarding your current question: "{user_input}"

Based on what I remember from our discussions, I'd be happy to help you with this. While I'm currently running with limited LLM capabilities, I can still assist based on our conversation history and system knowledge.

What specific aspect would you like me to focus on?"""

            elif any(
                word in user_input_lower
                for word in ["remember", "recall", "previous", "before", "last time"]
            ):
                return f"""I do have memory of our previous conversations! I can see we've discussed various topics including system management and troubleshooting.

For your current question: "{user_input}"

I'd be happy to help based on what I remember from our interactions. Could you give me a bit more context about what specifically you'd like me to recall or help with?"""

            else:
                return f"""Hello! I have some context from our previous conversations, which helps me provide better assistance.

Regarding: "{user_input}"

Based on our interaction history, I'm here to help with whatever you need. While I'm currently running with limited capabilities, I can still assist using the context I have about your interests and our past discussions.

How can I best help you today?"""

        except Exception as e:
            logger.error(f"❌ Error generating memory-informed fallback: {e}")
            return await self._generate_smart_fallback_response(user_input)

    async def generate_response(self, user_input: str) -> str:
        """Override base generate_response to use memory-informed approach"""
        try:
            self.conversation_count += 1

            # Generate memory-informed response
            response = await self.generate_memory_informed_response(user_input)

            # Store conversation in memory
            system_context = await self.get_system_context()
            await self.store_conversation_memory(user_input, response, system_context)

            # Update conversation history (base class functionality)
            self.add_to_conversation_history("user", user_input)
            self.add_to_conversation_history("assistant", response)

            # Handle any LLM response processing (from base class)
            if hasattr(self, "handle_llm_response"):
                response = self.handle_llm_response(response, user_input)

            return response

        except Exception as e:
            logger.error(f"❌ Critical error in enhanced generate_response: {e}")
            return await self._generate_smart_fallback_response(user_input)

    async def generate_conversation_summary(self) -> str:
        """Generate a narrative summary of the conversation using memory"""
        if not self.memory_enabled:
            return "Memory system not available for conversation summary."

        try:
            # Generate narrative from recent session memories
            session_memories = await self.memory_engine.recall(
                query=f"session:{self.session_id}",
                recall_strategy=RecallStrategy.TEMPORAL,
                limit=20,
            )

            if session_memories:
                narrative = await self.memory_engine.generate_narrative(
                    memory_fragments=session_memories,
                    narrative_type="conversation_summary",
                    time_range=timedelta(hours=2),
                )
                return (
                    narrative.content
                    if narrative
                    else "Unable to generate conversation summary."
                )
            else:
                return "No memories found for this conversation session."

        except Exception as e:
            logger.error(f"❌ Error generating conversation summary: {e}")
            return f"Error generating summary: {e}"

    async def get_memory_health_status(self) -> Dict[str, Any]:
        """Get current memory system health status"""
        if not self.memory_enabled:
            return {"status": "disabled", "message": "Memory system not available"}

        try:
            health_status = await self.memory_engine.check_memory_health()
            return {
                "status": "healthy"
                if health_status.overall_health > 0.7
                else "needs_attention",
                "overall_health": health_status.overall_health,
                "coherence_score": health_status.coherence_score,
                "drift_level": health_status.drift_level,
                "fragment_count": health_status.fragment_count,
                "last_cleanup": health_status.last_cleanup.isoformat()
                if health_status.last_cleanup
                else None,
                "alerts": [alert.message for alert in health_status.alerts]
                if health_status.alerts
                else [],
            }
        except Exception as e:
            logger.error(f"❌ Error getting memory health status: {e}")
            return {"status": "error", "message": str(e)}

    async def cleanup_and_shutdown(self):
        """Clean shutdown with memory system cleanup"""
        try:
            logger.info("🔄 Starting enhanced conversation manager shutdown...")

            if self.memory_enabled and self.memory_engine:
                # Generate final session narrative
                try:
                    summary = await self.generate_conversation_summary()
                    logger.info(f"📖 Generated session summary: {summary[:100]}...")

                    # Store session summary as a memory
                    await self.memory_engine.remember(
                        content=f"Session Summary: {summary}",
                        tags=["session_summary", "conversation_end", self.session_id],
                        metadata={
                            "session_id": self.session_id,
                            "conversation_count": self.conversation_count,
                            "session_duration": str(
                                datetime.now() - self.session_start_time
                            ),
                            "timestamp": datetime.now().isoformat(),
                        },
                        fragment_type=MemoryFragmentType.REFLECTIVE,
                        narrative_role="session_closure",
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Could not generate session summary: {e}")

                # Clean shutdown of memory engine
                try:
                    await self.memory_engine.shutdown()
                    logger.info("✅ Memory engine shutdown complete")
                except Exception as e:
                    logger.error(f"❌ Error shutting down memory engine: {e}")

            logger.info("✅ Enhanced conversation manager shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


# Convenience function to create the enhanced manager
def create_enhanced_conversation_manager(
    workspace_path: str, aether_runtime=None, gui_interface=None
) -> EnhancedLyrixaConversationManager:
    """Create and return an enhanced conversation manager instance"""
    return EnhancedLyrixaConversationManager(
        workspace_path, aether_runtime, gui_interface
    )


# For backward compatibility
LyrixaConversationManager = EnhancedLyrixaConversationManager

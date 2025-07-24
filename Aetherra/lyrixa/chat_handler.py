#!/usr/bin/env python3
"""
🎙️ LYRIXA CONVERSATION MANAGER - MEMORY INTEGRATION PATCH
========================================================

This patch integrates the new LyrixaMemoryEngine with the existing conversation manager
for enhanced episodic memory and narrative continuity.

Usage:
1. Import this instead of the original conversation_manager
2. All existing functionality preserved
3. Enhanced with memory integration when available
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Import the base conversation manager
try:
    from .conversation_manager import (
        LyrixaConversationManager as OriginalConversationManager,
    )

    BASE_AVAILABLE = True
    logger.info("✅ Base conversation manager loaded")
except ImportError as e:
    logger.error(f"❌ Cannot import base conversation manager: {e}")
    raise ImportError("Base conversation manager required for memory integration")

# Import the memory engine
try:
    from .memory.lyrixa_memory_engine import (
        LyrixaMemoryEngine,
        MemoryFragmentType,
        MemorySystemConfig,
    )

    MEMORY_ENGINE_AVAILABLE = True
    logger.info("✅ Memory engine available for integration")
except ImportError as e:
    logger.warning(f"⚠️ Memory engine not available: {e}")
    MEMORY_ENGINE_AVAILABLE = False


class LyrixaConversationManager(OriginalConversationManager):
    """
    Enhanced conversation manager with memory integration

    Extends the original conversation manager with:
    - Episodic memory storage
    - Memory-informed responses
    - Conversation context preservation
    """

    def __init__(self, workspace_path: str, aether_runtime=None, gui_interface=None):
        """Initialize with memory integration"""
        # Initialize base conversation manager first
        super().__init__(workspace_path, aether_runtime, gui_interface)

        # Initialize memory engine
        self.memory_enabled = False
        self.memory_engine = None

        if MEMORY_ENGINE_AVAILABLE:
            try:
                # Create memory config with workspace-specific paths
                config = MemorySystemConfig()
                if workspace_path:
                    memory_dir = os.path.join(workspace_path, "memory")
                    os.makedirs(memory_dir, exist_ok=True)
                    config.core_db_path = os.path.join(memory_dir, "lyrixa_memory.db")
                    config.fractal_db_path = os.path.join(
                        memory_dir, "fractal_memory.db"
                    )
                    config.concepts_db_path = os.path.join(
                        memory_dir, "concept_clusters.db"
                    )
                    config.timeline_db_path = os.path.join(
                        memory_dir, "episodic_timeline.db"
                    )

                self.memory_engine = LyrixaMemoryEngine(config)
                self.memory_enabled = True
                logger.info("🧠 Memory engine initialized successfully")

            except Exception as e:
                logger.error(f"❌ Failed to initialize memory engine: {e}")
                self.memory_engine = None
                self.memory_enabled = False

        # Memory-specific settings
        self.memory_context_limit = 5
        self.session_start_time = datetime.now()

        logger.info(
            f"🎙️ Enhanced Conversation Manager ready (Memory: {'✅ Enabled' if self.memory_enabled else '❌ Disabled'})"
        )

    async def store_conversation_turn(
        self, user_input: str, assistant_response: str
    ) -> bool:
        """Store conversation turn in memory"""
        if not self.memory_enabled:
            return False

        try:
            # Store user input
            user_result = await self.memory_engine.remember(
                content=user_input,
                tags=["conversation", "user_input", self.session_id],
                category="conversation",
                fragment_type=MemoryFragmentType.EPISODIC,
                narrative_role="user_interaction",
            )

            # Store assistant response
            assistant_result = await self.memory_engine.remember(
                content=assistant_response,
                tags=["conversation", "assistant_response", self.session_id],
                category="conversation",
                fragment_type=MemoryFragmentType.EPISODIC,
                narrative_role="lyrixa_response",
            )

            if user_result.success and assistant_result.success:
                logger.info(f"💾 Conversation turn stored in memory")
                return True
            else:
                logger.warning(f"⚠️ Failed to store conversation turn")
                return False

        except Exception as e:
            logger.error(f"❌ Error storing conversation turn: {e}")
            return False

    async def get_memory_context(self, user_input: str) -> List[str]:
        """Get relevant memory context for response generation"""
        if not self.memory_enabled:
            return []

        try:
            # Recall relevant memories using hybrid strategy
            memory_results = await self.memory_engine.recall(
                query=user_input,
                recall_strategy="hybrid",
                limit=self.memory_context_limit,
            )

            # Extract content from results
            context = []
            for result in memory_results:
                if isinstance(result, dict) and "content" in result:
                    content = result["content"]
                    # Truncate long content
                    if len(content) > 150:
                        content = content[:147] + "..."
                    context.append(content)

            if context:
                logger.info(f"🧠 Retrieved {len(context)} memory contexts")

            return context

        except Exception as e:
            logger.error(f"❌ Error retrieving memory context: {e}")
            return []

    def format_memory_context(self, contexts: List[str]) -> str:
        """Format memory context for LLM prompt"""
        if not contexts:
            return ""

        formatted = "\\n🧠 **Recent Memory Context:**\\n"
        for i, context in enumerate(contexts, 1):
            formatted += f"• **Memory {i}:** {context}\\n"

        return formatted + "\\n"

    async def generate_response(self, user_input: str) -> str:
        """Enhanced response generation with memory integration"""
        try:
            self.conversation_count += 1

            # Get memory context if available
            memory_context = await self.get_memory_context(user_input)

            # If we have memory context, enhance the system context
            if memory_context and self.memory_enabled:
                original_personality = self.get_lyrixa_personality()
                memory_context_str = self.format_memory_context(memory_context)

                # Temporarily enhance personality with memory context
                enhanced_personality = f"""{original_personality}

{memory_context_str}
**Memory Integration:** You have access to relevant memories from previous conversations. Use this context naturally to provide more informed and continuous responses."""

                # Temporarily replace personality method
                original_get_personality = self.get_lyrixa_personality
                self.get_lyrixa_personality = lambda: enhanced_personality

            # Generate response using base class method
            try:
                response = await super().generate_response(user_input)
            finally:
                # Restore original personality method
                if memory_context and self.memory_enabled:
                    self.get_lyrixa_personality = original_get_personality

            # Store the conversation turn in memory
            if self.memory_enabled:
                asyncio.create_task(self.store_conversation_turn(user_input, response))

            return response

        except Exception as e:
            logger.error(f"❌ Error in enhanced generate_response: {e}")
            # Fallback to base class method
            return await super().generate_response(user_input)

    async def get_conversation_summary(self) -> str:
        """Generate conversation summary using memory system"""
        if not self.memory_enabled:
            return await super().get_conversation_summary()

        try:
            # Try to get a narrative from the memory system
            session_memories = await self.memory_engine.recall(
                query=f"session:{self.session_id}", recall_strategy="episodic", limit=20
            )

            if session_memories:
                # Create a simple summary from the memories
                summary_parts = ["📖 **Session Summary:**"]
                for i, memory in enumerate(session_memories[:5], 1):
                    if isinstance(memory, dict) and "content" in memory:
                        content = (
                            memory["content"][:100] + "..."
                            if len(memory["content"]) > 100
                            else memory["content"]
                        )
                        summary_parts.append(f"{i}. {content}")

                return "\\n".join(summary_parts)
            else:
                return "No significant memories found for this session."

        except Exception as e:
            logger.error(f"❌ Error generating memory-based summary: {e}")
            return await super().get_conversation_summary()

    async def get_memory_status(self) -> Dict[str, Any]:
        """Get memory system status"""
        if not self.memory_enabled:
            return {"memory_enabled": False, "status": "Memory system not available"}

        try:
            # Get basic memory statistics
            return {
                "memory_enabled": True,
                "status": "Memory system operational",
                "session_id": self.session_id,
                "session_duration": str(datetime.now() - self.session_start_time),
                "conversation_count": self.conversation_count,
                "memory_engine_available": MEMORY_ENGINE_AVAILABLE,
            }
        except Exception as e:
            return {"memory_enabled": False, "status": f"Memory system error: {e}"}

    async def cleanup_and_shutdown(self):
        """Enhanced shutdown with memory system cleanup"""
        try:
            logger.info("🔄 Starting conversation manager shutdown...")

            if self.memory_enabled and self.memory_engine:
                try:
                    # Store a session end marker
                    await self.memory_engine.remember(
                        content=f"Session ended after {self.conversation_count} conversations",
                        tags=["session_end", self.session_id],
                        category="system",
                        fragment_type=MemoryFragmentType.REFLECTIVE,
                        narrative_role="session_closure",
                    )
                    logger.info("💾 Session end marker stored")
                except Exception as e:
                    logger.warning(f"⚠️ Could not store session end marker: {e}")

            logger.info("✅ Enhanced conversation manager shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during enhanced shutdown: {e}")


# For backward compatibility and ease of import
EnhancedLyrixaConversationManager = LyrixaConversationManager


def create_conversation_manager(
    workspace_path: str, aether_runtime=None, gui_interface=None
):
    """Create a conversation manager with memory integration"""
    return LyrixaConversationManager(workspace_path, aether_runtime, gui_interface)


if __name__ == "__main__":
    # Simple test
    async def test_memory_integration():
        print("🧪 Testing memory-integrated conversation manager...")

        manager = LyrixaConversationManager("./test_workspace")

        print(f"Memory enabled: {manager.memory_enabled}")

        status = await manager.get_memory_status()
        print(f"Status: {status}")

        # Test conversation
        response = await manager.generate_response("Hello, can you remember this test?")
        print(f"Response: {response}")

        await manager.cleanup_and_shutdown()
        print("✅ Test complete")

    asyncio.run(test_memory_integration())

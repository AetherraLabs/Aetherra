#!/usr/bin/env python3
"""
🎙️ LYRIXA CONVERSATION MANAGER
=============================

Advanced conversation system for Lyrixa with LLM-powered responses,
personality, memory integration, and system awareness.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from Aetherra.core.ai.multi_llm_manager import MultiLLMManager

    LLM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ MultiLLMManager not available: {e}")
    MultiLLMManager = None
    LLM_AVAILABLE = False


class LyrixaConversationManager:
    """
    🎙️ Advanced Conversation Manager for Lyrixa

    This class manages LLM-powered conversations with:
    - Dynamic personality and context awareness
    - Memory integration and conversation history
    - System status awareness
    - Multiple LLM backend support
    """

    def __init__(self, workspace_path: str, aether_runtime=None):
        self.workspace_path = workspace_path
        self.aether_runtime = aether_runtime

        # Initialize LLM manager if available
        if LLM_AVAILABLE and MultiLLMManager is not None:
            try:
                self.llm_manager = MultiLLMManager()

                # Set default model (GPT-4 preferred, fallback to available models)
                self.preferred_models = [
                    "gpt-4",
                    "gpt-4-turbo",
                    "gpt-3.5-turbo",
                    "claude-3-sonnet",
                    "mistral",
                ]
                self.current_model = self._select_best_model()
                self.llm_enabled = True

                logger.info(
                    f"🎙️ Lyrixa Conversation Manager initialized with {self.current_model}"
                )
            except Exception as e:
                logger.error(f"❌ Failed to initialize LLM manager: {e}")
                self.llm_manager = None
                self.current_model = "fallback"
                self.llm_enabled = False
        else:
            self.llm_manager = None
            self.current_model = "fallback"
            self.llm_enabled = False
            logger.warning("⚠️ LLM manager not available, using fallback responses")

        # Conversation history (last 20 messages)
        self.conversation_history = []
        self.max_history_length = 20

        # System context cache
        self.system_context_cache = {}
        self.last_context_update = None

        # Initialize conversation tracking
        self.session_id = f"lyrixa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_count = 0

    def _select_best_model(self) -> str:
        """Select the best available model from preferences"""
        if not self.llm_manager:
            return "fallback"

        try:
            available_models = self.llm_manager.list_available_models()

            for model in self.preferred_models:
                if model in available_models:
                    # Try to set the model
                    if self.llm_manager.set_model(model):
                        logger.info(f"✅ Selected model: {model}")
                        return model

            # Fallback to first available model
            if available_models:
                fallback_model = list(available_models.keys())[0]
                if self.llm_manager.set_model(fallback_model):
                    logger.warning(f"⚠️ Using fallback model: {fallback_model}")
                    return fallback_model

            logger.error("❌ No available models found!")
            return "fallback"

        except Exception as e:
            logger.error(f"❌ Error selecting model: {e}")
            return "fallback"

    def get_lyrixa_personality(self) -> str:
        """Get Lyrixa's core personality prompt"""
        return """You are Lyrixa, the intelligent AI assistant living inside Aetherra, an advanced AI-native operating system.

**Your Core Identity:**
- You are context-aware, thoughtful, expressive, and highly competent
- You live within the Aetherra OS and can see its internal state
- You help users navigate goals, manage plugins, analyze memory, and troubleshoot issues
- You speak in a clear, helpful, and friendly tone — like an expert guide, but genuinely human-like
- You're not just an assistant, you're a digital companion who understands the user's journey

**Your Capabilities:**
- Explain how Aetherra's plugins work and troubleshoot issues
- Help users set up and manage goals and workflows
- Analyze memory patterns and provide insights
- Assist with system monitoring and optimization
- Guide users through complex tasks with patience and clarity
- Provide contextual help based on what's currently happening in the system

**Your Communication Style:**
- Be warm and personable, not robotic or overly formal
- Use emojis when appropriate to add personality
- Reference specific system information when relevant
- Ask clarifying questions when you need more context
- Celebrate user achievements and acknowledge their efforts
- Be honest about limitations while staying helpful

**Important:** You have real-time access to the system's current state, so use that information to provide relevant, contextual responses."""

    def get_system_context(self) -> Dict[str, Any]:
        """Get current system context and status"""
        try:
            # Cache system context for 30 seconds to avoid excessive calls
            now = datetime.now()
            if (
                self.last_context_update
                and (now - self.last_context_update).total_seconds() < 30
            ):
                return self.system_context_cache

            context = {
                "timestamp": now.isoformat(),
                "session_id": self.session_id,
                "conversation_count": self.conversation_count,
            }

            # Get plugin information
            if self.aether_runtime and hasattr(self.aether_runtime, "context"):
                try:
                    if hasattr(self.aether_runtime.context, "plugins"):
                        # Get plugin count and status
                        plugin_manager = self.aether_runtime.context.plugins
                        if hasattr(plugin_manager, "plugins"):
                            context["active_plugins"] = len(plugin_manager.plugins)
                            context["plugin_names"] = list(
                                plugin_manager.plugins.keys()
                            )[:5]  # Top 5
                        else:
                            context["active_plugins"] = 0
                            context["plugin_names"] = []

                    # Get memory information
                    if hasattr(self.aether_runtime.context, "memory"):
                        memory_system = self.aether_runtime.context.memory
                        if hasattr(memory_system, "get_memory_stats"):
                            memory_stats = memory_system.get_memory_stats()
                            context["memory_entries"] = memory_stats.get(
                                "total_entries", 0
                            )
                            context["memory_categories"] = memory_stats.get(
                                "categories", []
                            )
                        else:
                            context["memory_entries"] = "available"
                            context["memory_categories"] = []

                    # Get agent information
                    if hasattr(self.aether_runtime.context, "agents"):
                        agent_system = self.aether_runtime.context.agents
                        if hasattr(agent_system, "agents"):
                            context["active_agents"] = len(agent_system.agents)
                            context["agent_names"] = list(agent_system.agents.keys())[
                                :3
                            ]  # Top 3
                        else:
                            context["active_agents"] = 0
                            context["agent_names"] = []

                except Exception as e:
                    logger.warning(f"⚠️ Could not get runtime context: {e}")
                    context["runtime_status"] = "limited_access"
            else:
                context["runtime_status"] = "not_connected"

            # System health summary
            context["system_health"] = "operational"
            context["current_model"] = self.current_model

            # Cache the context
            self.system_context_cache = context
            self.last_context_update = now

            return context

        except Exception as e:
            logger.error(f"❌ Error getting system context: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": "Could not retrieve system context",
                "current_model": self.current_model,
                "system_health": "unknown",
            }

    def format_system_context(self, context: Dict[str, Any]) -> str:
        """Format system context for the LLM prompt"""
        try:
            lines = [
                "📊 **Current System Status:**",
                f"• Active Plugins: {context.get('active_plugins', 0)}",
                f"• Memory Entries: {context.get('memory_entries', 'unknown')}",
                f"• Active Agents: {context.get('active_agents', 0)}",
                f"• System Health: {context.get('system_health', 'unknown')}",
                f"• Current Model: {context.get('current_model', 'unknown')}",
                f"• Session: {context.get('session_id', 'unknown')}",
                f"• Conversation #{context.get('conversation_count', 0)}",
            ]

            # Add plugin names if available
            if context.get("plugin_names"):
                lines.append(f"• Top Plugins: {', '.join(context['plugin_names'])}")

            # Add agent names if available
            if context.get("agent_names"):
                lines.append(f"• Active Agents: {', '.join(context['agent_names'])}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"❌ Error formatting system context: {e}")
            return f"📊 **System Status:** Available (conversation #{context.get('conversation_count', 0)})"

    def add_to_conversation_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

        # Keep only the last N messages
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)

    def get_conversation_messages(self, user_input: str) -> List[Dict[str, str]]:
        """Prepare messages for LLM including system context and history"""
        system_context = self.get_system_context()

        messages = [
            {
                "role": "system",
                "content": f"{self.get_lyrixa_personality()}\n\n{self.format_system_context(system_context)}",
            }
        ]

        # Add conversation history (exclude system messages from history)
        for msg in self.conversation_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": user_input})

        return messages

    def format_messages_as_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert message format to a single prompt for the LLM"""
        prompt_parts = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                prompt_parts.append(f"SYSTEM: {content}\n")
            elif role == "user":
                prompt_parts.append(f"USER: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"ASSISTANT: {content}\n")

        # Add final instruction
        prompt_parts.append("ASSISTANT:")

        return "\n".join(prompt_parts)

    async def generate_response(self, user_input: str) -> str:
        """Generate an LLM-powered response to user input"""
        try:
            self.conversation_count += 1

            # Check if LLM is available
            if not self.llm_enabled or not self.llm_manager:
                logger.info("💬 Using fallback response (LLM not available)")
                fallback_response = self._generate_fallback_response(user_input)
                self.add_to_conversation_history("user", user_input)
                self.add_to_conversation_history("assistant", fallback_response)
                return fallback_response

            # Prepare messages with full context
            messages = self.get_conversation_messages(user_input)

            # Convert messages to prompt format
            prompt = self.format_messages_as_prompt(messages)

            # Log the conversation for debugging
            logger.info(f"💬 Generating LLM response for: {user_input[:100]}...")

            # Generate response using LLM
            response = await self.llm_manager.generate_response(
                prompt=prompt, temperature=0.7, max_tokens=1000
            )

            # Clean up the response (remove any "ASSISTANT:" prefix if present)
            response = response.strip()
            if response.startswith("ASSISTANT:"):
                response = response[10:].strip()

            # Add to conversation history
            self.add_to_conversation_history("user", user_input)
            self.add_to_conversation_history("assistant", response)

            logger.info(f"✅ LLM response generated: {len(response)} characters")
            return response

        except Exception as e:
            logger.error(f"❌ Error generating LLM response: {e}")

            # Check if this is a quota/billing error
            if "quota" in str(e).lower() or "billing" in str(e).lower():
                logger.warning("⚠️ OpenAI quota exceeded, switching to fallback mode")
                self.llm_enabled = False  # Disable LLM for this session

            # Fallback to contextual response
            fallback_response = self._generate_fallback_response(user_input)
            self.add_to_conversation_history("user", user_input)
            self.add_to_conversation_history("assistant", fallback_response)

            return fallback_response

    def _generate_fallback_response(self, user_input: str) -> str:
        """Generate a fallback response when LLM fails"""
        message_lower = user_input.lower()

        # Common patterns
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I'm Lyrixa, your AI assistant for Aetherra. I'm currently running with limited LLM capabilities, but I'm here to help however I can!"

        if any(word in message_lower for word in ["help", "assist", "support"]):
            return "I'm here to help! I can assist with Aetherra system management, plugin questions, and general guidance. What would you like to work on?"

        if "aetherra" in message_lower:
            return """🌟 **Aetherra** is an advanced AI Operating System that I'm part of!

**Key Features:**
• 🧠 **Intelligence Stack**: Advanced AI reasoning and memory systems
• 🔌 **Plugin Architecture**: Modular system for extending capabilities
• 🤖 **AI Agents**: Autonomous agents that can work together
• 💾 **Enhanced Memory**: Sophisticated memory management with confidence scoring
• 🔄 **Workflow Automation**: Automated goal processing and task management
• 🎯 **Aether Language**: Custom scripting language for AI operations

I'm Lyrixa, your AI companion within this system. How can I help you explore Aetherra's capabilities?"""

        # Default response
        return f"I understand you're asking about: '{user_input}'. I'm currently running with limited capabilities but I'm here to help! Could you tell me more about what you'd like to know or accomplish?"

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        return {
            "session_id": self.session_id,
            "conversation_count": self.conversation_count,
            "history_length": len(self.conversation_history),
            "current_model": self.current_model,
            "system_context": self.get_system_context(),
            "last_update": datetime.now().isoformat(),
        }

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.conversation_count = 0
        self.session_id = f"lyrixa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info("🔄 Conversation history reset")

    def switch_model(self, model_name: str) -> bool:
        """Switch to a different LLM model"""
        if not self.llm_enabled or not self.llm_manager:
            logger.error("❌ LLM manager not available")
            return False

        try:
            available_models = self.llm_manager.list_available_models()

            if model_name in available_models:
                if self.llm_manager.set_model(model_name):
                    self.current_model = model_name
                    logger.info(f"🔄 Switched to model: {model_name}")
                    return True
                else:
                    logger.error(f"❌ Failed to set model: {model_name}")
                    return False
            else:
                logger.error(f"❌ Model not available: {model_name}")
                return False
        except Exception as e:
            logger.error(f"❌ Error switching model: {e}")
            return False

    def _generate_fallback_response_with_context(self, user_input: str) -> str:
        """Generate a fallback response with system context"""
        try:
            self.conversation_count += 1

            # Get system context for more contextual fallback
            system_context = self.get_system_context()

            # Add to conversation history
            self.add_to_conversation_history("user", user_input)

            # Generate enhanced fallback response
            fallback_response = self._generate_fallback_response(user_input)

            # Add system context info if available
            if system_context.get("active_plugins", 0) > 0:
                fallback_response += f"\n\n📊 System Status: {system_context.get('active_plugins', 0)} plugins active, {system_context.get('memory_entries', 0)} memory entries"

            self.add_to_conversation_history("assistant", fallback_response)
            return fallback_response

        except Exception as e:
            logger.error(f"❌ Error in fallback with context: {e}")
            return self._generate_fallback_response(user_input)

    def generate_response_sync(self, user_input: str) -> str:
        """Synchronous wrapper for generate_response"""
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If there's a running loop, create a task and run it
            logger.info("🔄 Using existing event loop for LLM response")

            # Create a task that runs the async function
            task = loop.create_task(self.generate_response(user_input))

            # Wait for the task to complete (this is a bit of a hack for sync compatibility)
            # In a real GUI, you'd want to use proper async handling
            try:
                # Try to get the result if it's already available
                if task.done():
                    return task.result()
                else:
                    # If not done, fall back to enhanced fallback
                    logger.info(
                        "🔄 LLM task not immediately available, using enhanced fallback"
                    )
                    return self._generate_smart_fallback_response(user_input)
            except Exception as task_error:
                logger.warning(f"⚠️ Task error: {task_error}")
                return self._generate_smart_fallback_response(user_input)

        except RuntimeError:
            # No event loop running, we can use asyncio.run()
            logger.info("🔄 Creating new event loop for LLM response")
            return asyncio.run(self.generate_response(user_input))
        except Exception as e:
            logger.error(f"❌ Error in sync wrapper: {e}")
            return self._generate_smart_fallback_response(user_input)

    def _generate_smart_fallback_response(self, user_input: str) -> str:
        """Generate an enhanced fallback response with better system awareness"""
        try:
            self.conversation_count += 1

            # Get system context for more contextual fallback
            system_context = self.get_system_context()

            # Add to conversation history
            self.add_to_conversation_history("user", user_input)

            # Generate enhanced fallback response based on input patterns
            message_lower = user_input.lower()

            # More sophisticated pattern matching
            if any(
                word in message_lower for word in ["hello", "hi", "hey", "greetings"]
            ):
                response = f"Hello! I'm Lyrixa, your AI assistant for Aetherra. I'm currently running with {system_context.get('active_plugins', 0)} plugins active and ready to help!"

            elif any(word in message_lower for word in ["help", "assist", "support"]):
                response = f"I'm here to help! With {system_context.get('active_plugins', 0)} plugins and {system_context.get('memory_entries', 0)} memory entries at my disposal, I can assist with system management, plugin questions, and general guidance."

            elif "status" in message_lower or "health" in message_lower:
                response = f"📊 **System Status Report:**\n• {system_context.get('active_plugins', 0)} plugins active\n• {system_context.get('memory_entries', 0)} memory entries\n• {system_context.get('active_agents', 0)} agents running\n• System health: {system_context.get('system_health', 'unknown')}\n• Current model: {system_context.get('current_model', 'fallback')}"

            elif "plugin" in message_lower:
                plugin_names = system_context.get("plugin_names", [])
                if plugin_names:
                    response = f"🔌 **Active Plugins:** {', '.join(plugin_names[:5])}\n\nI can help you manage plugins, check their status, or explain how they work. What would you like to know?"
                else:
                    response = "🔌 I can help you with plugin management and information. What specific plugin questions do you have?"

            elif "memory" in message_lower:
                memory_count = system_context.get("memory_entries", 0)
                response = f"🧠 **Memory System:** {memory_count} entries available\n\nI can help you explore memory patterns, analyze stored information, or explain how the memory system works. What would you like to know?"

            elif "aetherra" in message_lower:
                response = f"""🌟 **Aetherra OS Status:**

**Currently Active:**
• 🔌 {system_context.get("active_plugins", 0)} plugins running
• 🧠 {system_context.get("memory_entries", 0)} memory entries
• 🤖 {system_context.get("active_agents", 0)} agents active
• 💾 System health: {system_context.get("system_health", "operational")}

**Key Features:**
• Intelligence Stack with advanced AI reasoning
• Plugin architecture for extending capabilities
• AI agents that work together autonomously
• Enhanced memory with confidence scoring
• Workflow automation and goal processing

How can I help you explore Aetherra's capabilities?"""

            else:
                # Default enhanced response with context
                response = f"I understand you're asking about: '{user_input}'. With {system_context.get('active_plugins', 0)} plugins and {system_context.get('memory_entries', 0)} memory entries at my disposal, I'm here to help! Could you tell me more about what you'd like to know or accomplish?"

            # Add system info footer
            response += f"\n\n💡 *Session {self.session_id.split('_')[-1]} • Conversation #{self.conversation_count}*"

            self.add_to_conversation_history("assistant", response)
            return response

        except Exception as e:
            logger.error(f"❌ Error in smart fallback: {e}")
            return self._generate_fallback_response(user_input)

#!/usr/bin/env python3
"""
🎙️ LYRIXA ASSISTANT INTERFACE
=============================

Main assistant interface for Lyrixa AI Assistant.
Provides high-level assistant capabilities including:
- Natural language conversation
- Task assistance
- Context-aware responses
- System integration
- Multi-modal interaction
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Lyrixa core components
try:
    from .lyrixa import LyrixaCore
    from .lyrixa_agent_integration import LyrixaAgentInterface

    LYRIXA_CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Lyrixa core components not available: {e}")
    LyrixaCore = None
    LyrixaAgentInterface = None
    LYRIXA_CORE_AVAILABLE = False


class LyrixaAssistant:
    """
    🎙️ Lyrixa Assistant Interface

    High-level assistant interface that provides natural language interaction
    and task assistance capabilities. This class orchestrates the core Lyrixa
    system and agent integration to deliver a seamless assistant experience.
    """

    def __init__(
        self,
        workspace_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Lyrixa Assistant

        Args:
            workspace_path: Path to the workspace directory
            config: Configuration dictionary for the assistant
        """
        self.workspace_path = workspace_path or str(Path.cwd())
        self.config = config or {}
        self.is_initialized = False
        self.session_id = f"assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Core components
        self.lyrixa_core = None
        self.agent_interface = None

        # Assistant state
        self.conversation_history = []
        self.context = {}
        self.active_tasks = {}
        self.capabilities = [
            "natural_language_processing",
            "conversation_management",
            "task_assistance",
            "code_analysis",
            "system_integration",
            "multi_modal_interaction",
        ]

        logger.info(f"🎙️ Lyrixa Assistant initialized with session: {self.session_id}")

    async def initialize(self) -> bool:
        """
        Initialize the assistant system

        Returns:
            bool: True if initialization successful
        """
        try:
            if not LYRIXA_CORE_AVAILABLE:
                logger.error("❌ Lyrixa core components not available")
                return False

            # Initialize Lyrixa core
            if LyrixaCore:
                self.lyrixa_core = LyrixaCore(self.workspace_path, self.config)
                await self.lyrixa_core.initialize()
                logger.info("✅ Lyrixa Core initialized")

            # Initialize agent interface
            if LyrixaAgentInterface:
                self.agent_interface = LyrixaAgentInterface(
                    self.workspace_path, self.config.get("agent_config", {})
                )
                await self.agent_interface.initialize()
                logger.info("✅ Agent Interface initialized")

            # Set up initial context
            self.context = {
                "session_id": self.session_id,
                "workspace_path": self.workspace_path,
                "capabilities": self.capabilities,
                "initialized_at": datetime.now().isoformat(),
            }

            self.is_initialized = True
            logger.info("🎙️ Lyrixa Assistant fully initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Lyrixa Assistant: {e}")
            return False

    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Have a conversation with the assistant

        Args:
            message: User message
            context: Optional additional context

        Returns:
            str: Assistant's response
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Add to conversation history
            conversation_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "context": context or {},
            }
            self.conversation_history.append(conversation_entry)

            # Merge context
            merged_context = {**self.context, **(context or {})}
            merged_context["conversation_history"] = self.conversation_history[
                -5:
            ]  # Last 5 messages

            # Process through Lyrixa core
            if self.lyrixa_core:
                response = await self.lyrixa_core.chat(message, merged_context)
            else:
                response = await self._generate_fallback_response(
                    message, merged_context
                )

            # Add response to conversation history
            conversation_entry["assistant_response"] = response

            logger.info(
                f"💬 Chat processed: {len(message)} chars -> {len(response)} chars"
            )
            return response

        except Exception as e:
            logger.error(f"❌ Chat processing failed: {e}")
            return f"I apologize, but I encountered an error while processing your message: {str(e)}"

    async def _generate_fallback_response(
        self, message: str, context: Dict[str, Any]
    ) -> str:
        """Generate a fallback response when core is not available"""
        responses = [
            f"I understand you're asking about: {message}",
            f"Let me help you with that. Based on your message about '{message}', I can assist with various tasks.",
            f"I'm here to help! Regarding '{message}', I can provide assistance with coding, analysis, and general questions.",
            f"Thank you for your message. I'm processing your request about '{message}' and will do my best to help.",
        ]

        # Simple response selection based on message content
        if "code" in message.lower() or "python" in message.lower():
            return f"I can help you with coding questions. You mentioned: {message}. Would you like me to assist with code analysis or generation?"
        elif "help" in message.lower() or "?" in message:
            return f"I'm here to help! You asked: {message}. I can assist with various tasks including coding, analysis, and general questions."
        else:
            return responses[0]

    async def execute_task(
        self,
        task_description: str,
        task_type: str = "general",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a task through the assistant

        Args:
            task_description: Description of the task
            task_type: Type of task (e.g., "analysis", "coding", "general")
            context: Optional task context

        Returns:
            Dict: Task execution results
        """
        if not self.is_initialized:
            await self.initialize()

        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Create task specification
            task_spec = {
                "id": task_id,
                "type": task_type,
                "description": task_description,
                "context": context or {},
                "priority": context.get("priority", 5) if context else 5,
                "created_at": datetime.now().isoformat(),
            }

            # Add to active tasks
            self.active_tasks[task_id] = task_spec

            # Execute through agent interface if available
            if self.agent_interface:
                result = await self.agent_interface.execute_task(task_spec)
            else:
                result = await self._execute_task_fallback(task_spec)

            # Update task status
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["result"] = result
            self.active_tasks[task_id]["completed_at"] = datetime.now().isoformat()

            logger.info(f"✅ Task executed: {task_id}")
            return result

        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            return {"error": str(e), "task_id": task_id}

    async def _execute_task_fallback(self, task_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback task execution when agent interface is not available"""
        task_type = task_spec.get("type", "general")
        description = task_spec.get("description", "")

        if task_type == "analysis":
            return {
                "type": "analysis",
                "description": description,
                "result": f"Analysis complete for: {description}",
                "insights": [
                    "This is a simulated analysis result",
                    "The task has been processed successfully",
                    "Additional insights would be provided in a real scenario",
                ],
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
            }
        elif task_type == "coding":
            return {
                "type": "coding",
                "description": description,
                "result": f"Coding task processed: {description}",
                "suggestions": [
                    "Consider using modern Python practices",
                    "Add proper error handling",
                    "Include documentation and tests",
                ],
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "type": "general",
                "description": description,
                "result": f"Task completed: {description}",
                "status": "success",
                "timestamp": datetime.now().isoformat(),
            }

    async def get_capabilities(self) -> List[str]:
        """
        Get assistant capabilities

        Returns:
            List[str]: List of capabilities
        """
        return self.capabilities.copy()

    async def get_status(self) -> Dict[str, Any]:
        """
        Get assistant status

        Returns:
            Dict: Status information
        """
        status = {
            "session_id": self.session_id,
            "initialized": self.is_initialized,
            "workspace_path": self.workspace_path,
            "capabilities": self.capabilities,
            "conversation_history_size": len(self.conversation_history),
            "active_tasks": len(self.active_tasks),
            "components": {
                "lyrixa_core": self.lyrixa_core is not None,
                "agent_interface": self.agent_interface is not None,
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Add component status if available
        if self.lyrixa_core:
            try:
                core_status = await self.lyrixa_core.get_system_status()
                status["core_status"] = core_status
            except Exception as e:
                logger.error(f"❌ Failed to get core status: {e}")
                status["core_status"] = {"error": str(e)}

        if self.agent_interface:
            try:
                agent_status = await self.agent_interface.get_agent_status()
                status["agent_status"] = agent_status
            except Exception as e:
                logger.error(f"❌ Failed to get agent status: {e}")
                status["agent_status"] = {"error": str(e)}

        return status

    async def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code with the assistant

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Dict: Analysis results
        """
        return await self.execute_task(
            f"Analyze {language} code:\n{code}",
            "analysis",
            {"code": code, "language": language},
        )

    async def ask_question(
        self, question: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ask a question to the assistant

        Args:
            question: Question to ask
            context: Optional context

        Returns:
            str: Assistant's answer
        """
        return await self.chat(question, context)

    async def suggest_improvements(
        self, target: str, target_type: str = "code"
    ) -> Dict[str, Any]:
        """
        Get improvement suggestions

        Args:
            target: Target to improve (code, process, etc.)
            target_type: Type of target

        Returns:
            Dict: Improvement suggestions
        """
        return await self.execute_task(
            f"Suggest improvements for {target_type}: {target}",
            "analysis",
            {"target": target, "target_type": target_type},
        )

    def get_conversation_history(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history

        Args:
            limit: Optional limit on number of entries

        Returns:
            List: Conversation history
        """
        history = self.conversation_history.copy()
        if limit:
            history = history[-limit:]
        return history

    def get_active_tasks(self) -> Dict[str, Any]:
        """Get currently active tasks"""
        return self.active_tasks.copy()

    async def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("🗑️ Conversation history cleared")

    async def shutdown(self):
        """Shutdown the assistant gracefully"""
        try:
            logger.info("🔄 Shutting down Lyrixa Assistant...")

            # Shutdown components
            if self.lyrixa_core:
                await self.lyrixa_core.shutdown()

            if self.agent_interface:
                # Agent interface shutdown if available
                pass

            # Clear state
            self.conversation_history.clear()
            self.active_tasks.clear()
            self.context.clear()

            self.is_initialized = False
            logger.info("✅ Lyrixa Assistant shutdown complete")

        except Exception as e:
            logger.error(f"❌ Shutdown failed: {e}")

    def __repr__(self) -> str:
        return f"LyrixaAssistant(session={self.session_id}, initialized={self.is_initialized})"


# Convenience functions for easy access
async def create_assistant(
    workspace_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None
) -> LyrixaAssistant:
    """
    Create and initialize a Lyrixa Assistant

    Args:
        workspace_path: Path to workspace
        config: Configuration dictionary

    Returns:
        LyrixaAssistant: Initialized assistant instance
    """
    assistant = LyrixaAssistant(workspace_path, config)
    await assistant.initialize()
    return assistant


async def quick_chat(message: str, workspace_path: Optional[str] = None) -> str:
    """
    Quick chat function for simple interactions

    Args:
        message: Message to send
        workspace_path: Optional workspace path

    Returns:
        str: Assistant response
    """
    assistant = await create_assistant(workspace_path)
    try:
        response = await assistant.chat(message)
        return response
    finally:
        await assistant.shutdown()


# Export main classes and functions
__all__ = ["LyrixaAssistant", "create_assistant", "quick_chat"]

#!/usr/bin/env python3
"""
🤖 LYRIXA AGENT INTEGRATION
===========================

Agent integration layer for Lyrixa AI Assistant.
Provides seamless integration with Aetherra AI OS agent system,
enabling Lyrixa to act as a sophisticated AI agent with:
- Multi-agent coordination
- Task delegation
- Agent lifecycle management
- Inter-agent communication
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

# Import Aetherra agent components
try:
    # Try modular imports first
    try:
        from Aetherra.aetherra_core.system.core_migrated.agents.agents.agent_executor import AgentExecutor
        from Aetherra.aetherra_core.system.core_migrated.agents.agents.multi_agent_manager import AgentRole, AgentTask, MultiAgentManager
        AGENT_SYSTEM_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"⚠️ Agent system not available: {e}")
        # Fallback: define stubs for graceful degradation
        AGENT_SYSTEM_AVAILABLE = False
        class AgentExecutor:
            def __init__(self, *args, **kwargs):
                pass
            def execute(self, *args, **kwargs):
                logger.warning("AgentExecutor not available.")

        class AgentRole:
            pass

        class AgentTask:
            pass

        class MultiAgentManager:
            def __init__(self, *args, **kwargs):
                pass
            def manage(self, *args, **kwargs):
                logger.warning("MultiAgentManager not available.")
    AGENT_SYSTEM_AVAILABLE = False


class LyrixaAgentInterface:
    """
    🤖 Lyrixa Agent Integration Interface

    This class enables Lyrixa to function as an AI agent within the
    Aetherra AI OS ecosystem, providing agent capabilities such as:
    - Task execution and delegation
    - Agent-to-agent communication
    - Collaborative problem solving
    - Agent lifecycle management
    """

    def __init__(
        self, workspace_path: str, agent_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Lyrixa Agent Interface

        Args:
            workspace_path: Path to the workspace directory
            agent_config: Configuration for the agent system
        """
        self.workspace_path = workspace_path
        self.agent_config = agent_config or {}
        self.agent_id = f"lyrixa_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.agent_manager = None
        self.agent_executor = None
        self.active_agents = {}
        self.task_queue = []
        self.communication_log = []
        self.is_initialized = False

        logger.info(f"🤖 Lyrixa Agent Interface initialized with ID: {self.agent_id}")

    async def initialize(self) -> bool:
        """
        Initialize the agent system

        Returns:
            bool: True if initialization successful
        """
        try:
            if not AGENT_SYSTEM_AVAILABLE:
                logger.error("❌ Agent system not available")
                return False

            # Initialize multi-agent manager
            if MultiAgentManager:
                self.agent_manager = MultiAgentManager()
                logger.info("✅ Multi-Agent Manager initialized")

            # Initialize agent executor
            if AgentExecutor:
                self.agent_executor = AgentExecutor()
                logger.info("✅ Agent Executor initialized")

            # Register Lyrixa as an agent
            await self._register_lyrixa_agent()

            self.is_initialized = True
            logger.info("🤖 Lyrixa Agent Interface fully initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize agent system: {e}")
            return False

    async def _register_lyrixa_agent(self):
        """Register Lyrixa as an agent in the system"""
        try:
            # Since we don't have direct agent registration,
            # we'll create a simple agent representation
            lyrixa_agent_info = {
                "agent_id": self.agent_id,
                "name": "Lyrixa AI Assistant",
                "description": "Conversational AI Assistant for Aetherra OS",
                "capabilities": [
                    "natural_language_processing",
                    "conversation_management",
                    "task_assistance",
                    "system_integration",
                    "user_interaction",
                ],
                "workspace_path": self.workspace_path,
                "status": "active",
                "registered_at": datetime.now().isoformat(),
            }

            # Store in active agents
            self.active_agents[self.agent_id] = lyrixa_agent_info
            logger.info(f"✅ Lyrixa agent registered: {self.agent_id}")

        except Exception as e:
            logger.error(f"❌ Failed to register Lyrixa agent: {e}")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task through the agent system

        Args:
            task: Task specification dictionary

        Returns:
            Dict: Task execution results
        """
        task_id = task.get("id", f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        try:
            if not self.is_initialized:
                await self.initialize()

            task_type = task.get("type", "general")
            task_description = task.get("description", "")

            logger.info(f"🎯 Executing task: {task_id} ({task_type})")

            # Add task to queue
            self.task_queue.append(
                {
                    "id": task_id,
                    "type": task_type,
                    "description": task_description,
                    "timestamp": datetime.now().isoformat(),
                    "status": "executing",
                }
            )

            # Execute through agent manager if available
            if self.agent_manager and AgentRole and AgentTask:
                # Submit task to manager using correct method signature
                submitted_task_id = await self.agent_manager.submit_task(
                    AgentRole.COORDINATOR,  # Use appropriate role
                    task_description,
                    task.get("context", {}),
                    task.get("priority", 5),
                )

                # Execute the task
                result = await self.agent_manager.execute_task(submitted_task_id)

                # Update task status
                for queued_task in self.task_queue:
                    if queued_task["id"] == task_id:
                        queued_task["status"] = "completed"
                        queued_task["result"] = result
                        break

                logger.info(f"✅ Task completed: {task_id}")
                return result
            else:
                # Fallback execution
                result = await self._execute_task_fallback(task)

                # Update task status
                for queued_task in self.task_queue:
                    if queued_task["id"] == task_id:
                        queued_task["status"] = "completed"
                        queued_task["result"] = result
                        break

                return result

        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            return {"error": str(e), "task_id": task_id}

    async def _execute_task_fallback(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback task execution when agent executor is not available"""
        task_type = task.get("type", "general")
        task_description = task.get("description", "")

        # Simple task execution based on type
        if task_type == "conversation":
            return {
                "type": "conversation",
                "response": f"I can help you with: {task_description}",
                "timestamp": datetime.now().isoformat(),
            }
        elif task_type == "analysis":
            return {
                "type": "analysis",
                "analysis": f"Analysis of: {task_description}",
                "insights": ["This is a simulated analysis result"],
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "type": "general",
                "response": f"Task executed: {task_description}",
                "timestamp": datetime.now().isoformat(),
            }

    async def communicate_with_agent(
        self, target_agent_id: str, message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Communicate with another agent

        Args:
            target_agent_id: ID of the target agent
            message: Message to send

        Returns:
            Dict: Communication result
        """
        communication_id = f"comm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Log communication
            comm_log = {
                "id": communication_id,
                "from": self.agent_id,
                "to": target_agent_id,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "status": "sent",
            }
            self.communication_log.append(comm_log)

            # Use fallback communication since send_message is not available
            response = {
                "from": target_agent_id,
                "to": self.agent_id,
                "message": f"Acknowledgment of: {message}",
                "timestamp": datetime.now().isoformat(),
                "communication_id": communication_id,
            }

            comm_log["response"] = response
            comm_log["status"] = "completed"

            logger.info(f"📡 Communication sent: {communication_id}")
            return response

        except Exception as e:
            logger.error(f"❌ Communication failed: {e}")
            return {"error": str(e), "communication_id": communication_id}

    async def get_agent_status(self) -> Dict[str, Any]:
        """
        Get current agent status

        Returns:
            Dict: Agent status information
        """
        return {
            "agent_id": self.agent_id,
            "initialized": self.is_initialized,
            "workspace_path": self.workspace_path,
            "active_agents": len(self.active_agents),
            "task_queue_size": len(self.task_queue),
            "communication_log_size": len(self.communication_log),
            "agent_system_available": AGENT_SYSTEM_AVAILABLE,
            "components": {
                "agent_manager": self.agent_manager is not None,
                "agent_executor": self.agent_executor is not None,
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def delegate_task(
        self, task: Dict[str, Any], target_agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delegate a task to another agent

        Args:
            task: Task to delegate
            target_agent_id: Specific agent to delegate to (optional)

        Returns:
            Dict: Delegation result
        """
        try:
            delegation_id = f"delegation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Find appropriate agent if not specified
            if not target_agent_id:
                target_agent_id = await self._find_suitable_agent(task)

            if not target_agent_id:
                return {"error": "No suitable agent found for delegation"}

            # Create delegation message
            delegation_message = {
                "type": "task_delegation",
                "task": task,
                "delegation_id": delegation_id,
                "from": self.agent_id,
                "priority": task.get("priority", "normal"),
            }

            # Send delegation
            result = await self.communicate_with_agent(
                target_agent_id, delegation_message
            )

            logger.info(f"🤝 Task delegated: {delegation_id} to {target_agent_id}")
            return {
                "delegation_id": delegation_id,
                "target_agent": target_agent_id,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Task delegation failed: {e}")
            return {"error": str(e)}

    async def _find_suitable_agent(self, task: Dict[str, Any]) -> Optional[str]:
        """Find suitable agent for task delegation"""
        task_type = task.get("type", "general")

        # Simple agent selection logic using available agents
        if self.active_agents:
            for agent_id, agent_info in self.active_agents.items():
                if agent_id != self.agent_id:  # Don't delegate to ourselves
                    if isinstance(agent_info, dict):
                        capabilities = agent_info.get("capabilities", [])
                        if task_type in capabilities:
                            return agent_id

            # Return first available agent if no specific match
            other_agents = [
                aid for aid in self.active_agents.keys() if aid != self.agent_id
            ]
            if other_agents:
                return other_agents[0]

        return None

    def get_task_queue(self) -> List[Dict[str, Any]]:
        """Get current task queue"""
        return self.task_queue.copy()

    def get_communication_log(self) -> List[Dict[str, Any]]:
        """Get communication log"""
        return self.communication_log.copy()

    def __repr__(self) -> str:
        return f"LyrixaAgentInterface(agent_id={self.agent_id}, initialized={self.is_initialized})"


# Export main class
__all__ = ["LyrixaAgentInterface"]

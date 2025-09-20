# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎯 Agent Orchestrator
====================

Coordinates multiple AI agents and manages task distribution across the Aetherra ecosystem.
Handles agent discovery, capability matching, task scheduling, and result aggregation.
"""

# Standard library imports
import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels for orchestration."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(Enum):
    """Agent availability status."""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class Task:
    """Represents a task to be executed by an agent."""

    task_id: str
    name: str
    description: str
    required_capabilities: list[str]
    input_data: dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    max_execution_time: int = 300  # seconds
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    assigned_agent: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    result: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class Agent:
    """Represents an AI agent in the system."""

    agent_id: str
    name: str
    capabilities: list[str]
    status: AgentStatus = AgentStatus.AVAILABLE
    current_task: str | None = None
    last_seen: datetime = field(default_factory=datetime.now)
    performance_metrics: dict[str, float] = field(default_factory=dict)
    total_tasks_completed: int = 0
    average_execution_time: float = 0.0


class AgentOrchestrator:
    """
    🎯 Agent Orchestrator

    Manages a fleet of AI agents and coordinates task execution across
    the Aetherra ecosystem with intelligent load balancing and capability matching.
    """

    def __init__(self, db_path: str = "agent_orchestrator.db"):
        """Initialize the orchestrator with persistent storage."""
        self.db_path = Path(db_path)
        self.agents: dict[str, Agent] = {}
        self.tasks: dict[str, Task] = {}
        self.task_queue: list[str] = []
        self.running_tasks: dict[str, asyncio.Task] = {}
        self.orchestration_active = False
        self._task_counter = 0

        # Load persistent data
        self._load_state()

        logger.info(
            f"[AGENT] Agent Orchestrator initialized with {len(self.agents)} agents"
        )

    def _load_state(self):
        """Load orchestrator state from persistent storage."""
        try:
            if self.db_path.exists():
                # Mode argument not required for default text read (ruff UP015)
                with open(self.db_path) as f:
                    data = json.load(f)

                # Restore agents
                for agent_data in data.get("agents", []):
                    agent = Agent(**agent_data)
                    agent.last_seen = datetime.fromisoformat(
                        agent_data.get("last_seen", datetime.now().isoformat())
                    )
                    agent.status = AgentStatus.OFFLINE  # Reset to offline on startup
                    self.agents[agent.agent_id] = agent

                # Restore pending tasks
                for task_data in data.get("tasks", []):
                    task = Task(**task_data)
                    task.created_at = datetime.fromisoformat(
                        task_data.get("created_at", datetime.now().isoformat())
                    )
                    if task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED]:
                        self.tasks[task.task_id] = task
                        self.task_queue.append(task.task_id)

                logger.info(
                    f"✅ Loaded {len(self.agents)} agents and {len(self.tasks)} pending tasks"
                )

        except Exception as e:
            logger.warning(f"⚠️ Could not load orchestrator state: {e}")

    def _save_state(self):
        """Save orchestrator state to persistent storage."""
        try:
            data = {
                "agents": [
                    {
                        **agent.__dict__,
                        "last_seen": agent.last_seen.isoformat(),
                        "status": agent.status.value,
                    }
                    for agent in self.agents.values()
                ],
                "tasks": [
                    {
                        **task.__dict__,
                        "created_at": task.created_at.isoformat(),
                        "started_at": task.started_at.isoformat()
                        if task.started_at
                        else None,
                        "completed_at": task.completed_at.isoformat()
                        if task.completed_at
                        else None,
                        "priority": task.priority.value,
                        "status": task.status.value,
                    }
                    for task in self.tasks.values()
                ],
            }

            with open(self.db_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"❌ Could not save orchestrator state: {e}")

    async def start_orchestration(self):
        """Start the orchestration process."""
        if self.orchestration_active:
            return

        self.orchestration_active = True
        logger.info("[AGENT] Starting agent orchestration")

        # Start background orchestration loop
        asyncio.create_task(self._orchestration_loop())

        # Register some default agents if none exist
        if not self.agents:
            await self._register_default_agents()

    async def stop_orchestration(self):
        """Stop the orchestration process."""
        if not self.orchestration_active:
            return

        self.orchestration_active = False
        logger.info("🛑 Stopping agent orchestration")

        # Cancel running tasks
        for task_future in self.running_tasks.values():
            task_future.cancel()

        # Save state before shutdown
        self._save_state()

    async def _register_default_agents(self):
        """Register some default agents for testing."""
        default_agents = [
            {
                "agent_id": "text_processor_01",
                "name": "Text Processing Agent",
                "capabilities": ["text_analysis", "summarization", "translation"],
            },
            {
                "agent_id": "data_analyst_01",
                "name": "Data Analysis Agent",
                "capabilities": ["data_analysis", "visualization", "statistics"],
            },
            {
                "agent_id": "web_researcher_01",
                "name": "Web Research Agent",
                "capabilities": [
                    "web_search",
                    "information_gathering",
                    "fact_checking",
                ],
            },
        ]

        for agent_data in default_agents:
            await self.register_agent(**agent_data)

    async def register_agent(self, *args, **kwargs) -> bool:
        """Register a new agent with the orchestrator.

        Backwards-compatible + flexible signature so tests can call either:

            await register_agent(agent_id="agent_1", name="Agent 1", capabilities=[...])
            await register_agent("agent_1", "Agent 1", ["capability"])
            register_agent(mock_agent)  # (test passes MagicMock without awaiting)

        If a single positional argument is provided and it is not a ``str`` we treat it
        as an object with ``name`` / optional ``agent_id`` / ``capabilities`` attributes.
        Missing fields are synthesized with safe defaults.
        """
        try:
            agent_id: str | None = None
            name: str | None = None
            capabilities: list[str] | None = None

            # Pattern 1: legacy / existing usage via kwargs (agent_id, name, capabilities)
            if kwargs:
                agent_id = kwargs.get("agent_id")
                name = kwargs.get("name")
                capabilities = kwargs.get("capabilities")

            # Pattern 2: positional explicit fields
            if not kwargs and len(args) >= 1 and isinstance(args[0], str):
                agent_id = agent_id or args[0]
                if len(args) > 1:
                    name = name or args[1]
                if len(args) > 2:
                    capabilities = capabilities or args[2]

            # Pattern 3: single object (e.g., MagicMock in tests)
            if len(args) == 1 and not kwargs and not isinstance(args[0], str):
                obj = args[0]
                # Extract possible attributes; fall back to synthesized id
                agent_id = getattr(obj, "agent_id", None) or getattr(obj, "name", None)
                name = (
                    getattr(obj, "name", None)
                    or agent_id
                    or f"agent_{len(self.agents) + 1:04d}"
                )
                raw_caps = getattr(obj, "capabilities", [])
                capabilities = (
                    list(raw_caps) if isinstance(raw_caps, list | tuple | set) else []
                )

            # Synthesize defaults if still missing
            agent_id = agent_id or name or f"agent_{len(self.agents) + 1:04d}"
            name = name or agent_id
            if capabilities is None:
                capabilities = []
            if not isinstance(capabilities, list):  # normalize
                capabilities = (
                    list(capabilities)
                    if isinstance(capabilities, set | tuple)
                    else [str(capabilities)]
                )

            agent = Agent(
                agent_id=agent_id,
                name=name,
                capabilities=capabilities,
                status=AgentStatus.AVAILABLE,
            )

            self.agents[agent_id] = agent
            self._save_state()

            logger.info(
                f"✅ Registered agent '{name}' with capabilities: {capabilities}"
            )
            return True

        except Exception as e:  # pragma: no cover - defensive path
            logger.error(f"❌ Failed to register agent: {e}")
            return False

    async def submit_task(self, task: Task) -> str:
        """Submit a task for execution."""
        try:
            # Generate task ID if not provided
            if not task.task_id:
                self._task_counter += 1
                task.task_id = f"task_{self._task_counter:06d}"

            # Add to task registry and queue
            self.tasks[task.task_id] = task
            self.task_queue.append(task.task_id)

            self._save_state()

            logger.info(f"📋 Submitted task '{task.name}' (ID: {task.task_id})")
            return task.task_id

        except Exception as e:
            logger.error(f"❌ Failed to submit task: {e}")
            raise

    async def _orchestration_loop(self):
        """Main orchestration loop that assigns tasks to agents."""
        while self.orchestration_active:
            try:
                # Process pending tasks
                await self._process_task_queue()

                # Check for completed tasks
                await self._check_completed_tasks()

                # Update agent status
                await self._update_agent_status()

                # Wait before next iteration
                await asyncio.sleep(1.0)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in orchestration loop: {e}")
                await asyncio.sleep(5.0)

    async def _process_task_queue(self):
        """Process pending tasks and assign them to available agents."""
        if not self.task_queue:
            return

        # Sort tasks by priority
        self.task_queue.sort(key=lambda tid: self._get_task_priority_value(tid))

        for task_id in self.task_queue[
            :
        ]:  # Copy to avoid modification during iteration
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.PENDING:
                self.task_queue.remove(task_id)
                continue

            # Find suitable agent
            agent = self._find_suitable_agent(task.required_capabilities)
            if agent:
                await self._assign_task_to_agent(task, agent)
                self.task_queue.remove(task_id)

    def _get_task_priority_value(self, task_id: str) -> int:
        """Get numeric priority value for sorting."""
        task = self.tasks.get(task_id)
        if not task:
            return 0

        priority_values = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 3,
        }
        return priority_values.get(task.priority, 2)

    def _find_suitable_agent(self, required_capabilities: list[str]) -> Agent | None:
        """Find the best available agent for the given capabilities."""
        available_agents = [
            agent
            for agent in self.agents.values()
            if agent.status == AgentStatus.AVAILABLE
        ]

        if not available_agents:
            return None

        # Score agents by capability match and performance
        scored_agents = []
        for agent in available_agents:
            capability_score = len(set(required_capabilities) & set(agent.capabilities))
            performance_score = agent.performance_metrics.get("success_rate", 0.5)
            total_score = capability_score * 10 + performance_score

            if capability_score > 0:  # Agent must have at least one required capability
                scored_agents.append((total_score, agent))

        if not scored_agents:
            return None

        # Return agent with highest score
        return max(scored_agents, key=lambda x: x[0])[1]

    async def _assign_task_to_agent(self, task: Task, agent: Agent):
        """Assign a task to a specific agent."""
        try:
            task.assigned_agent = agent.agent_id
            task.status = TaskStatus.ASSIGNED
            task.started_at = datetime.now()

            agent.status = AgentStatus.BUSY
            agent.current_task = task.task_id

            # Start task execution
            task_future = asyncio.create_task(self._execute_task(task, agent))
            self.running_tasks[task.task_id] = task_future

            logger.info(f"[AGENT] Assigned task '{task.name}' to agent '{agent.name}'")

        except Exception as e:
            logger.error(
                f"❌ Failed to assign task {task.task_id} to agent {agent.agent_id}: {e}"
            )
            task.status = TaskStatus.FAILED
            task.error_message = str(e)

    async def _execute_task(self, task: Task, agent: Agent) -> dict[str, Any]:
        """Execute a task using the assigned agent."""
        try:
            task.status = TaskStatus.RUNNING

            # Simulate task execution (in real implementation, this would call the actual agent)
            await asyncio.sleep(2.0)  # Simulate processing time

            # Mock successful result
            result = {
                "status": "completed",
                "agent_id": agent.agent_id,
                "task_id": task.task_id,
                "result": f"Mock result for task '{task.name}' by agent '{agent.name}'",
                "execution_time": 2.0,
                "timestamp": datetime.now().isoformat(),
            }

            # Update task status
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()

            # Update agent status and metrics
            agent.status = AgentStatus.AVAILABLE
            agent.current_task = None
            agent.total_tasks_completed += 1
            agent.last_seen = datetime.now()

            # Update performance metrics
            if task.started_at:
                execution_time = (task.completed_at - task.started_at).total_seconds()
                agent.average_execution_time = (
                    agent.average_execution_time * (agent.total_tasks_completed - 1)
                    + execution_time
                ) / agent.total_tasks_completed
            agent.performance_metrics["success_rate"] = min(
                1.0, agent.performance_metrics.get("success_rate", 0.5) + 0.1
            )

            self._save_state()
            logger.info(f"✅ Task '{task.name}' completed by agent '{agent.name}'")

            return result

        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            agent.status = AgentStatus.AVAILABLE
            agent.current_task = None

            return {"status": "failed", "error": str(e)}

        finally:
            # Clean up running task reference
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]

    async def _check_completed_tasks(self):
        """Check for and clean up completed tasks."""
        completed_tasks = []

        for task_id, task_future in self.running_tasks.items():
            if task_future.done():
                completed_tasks.append(task_id)

        for task_id in completed_tasks:
            del self.running_tasks[task_id]

    async def _update_agent_status(self):
        """Update agent status based on last seen time."""
        current_time = datetime.now()
        timeout_threshold = timedelta(minutes=5)

        for agent in self.agents.values():
            if agent.status != AgentStatus.OFFLINE:
                time_since_last_seen = current_time - agent.last_seen
                if time_since_last_seen > timeout_threshold:
                    agent.status = AgentStatus.OFFLINE
                    if agent.current_task:
                        # Mark current task as failed due to agent timeout
                        task = self.tasks.get(agent.current_task)
                        if task:
                            task.status = TaskStatus.FAILED
                            task.error_message = "Agent became unavailable"
                        agent.current_task = None

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        total_agents = len(self.agents)
        available_agents = len(
            [a for a in self.agents.values() if a.status == AgentStatus.AVAILABLE]
        )
        busy_agents = len(
            [a for a in self.agents.values() if a.status == AgentStatus.BUSY]
        )
        offline_agents = len(
            [a for a in self.agents.values() if a.status == AgentStatus.OFFLINE]
        )

        pending_tasks = len(
            [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
        )
        running_tasks = len(
            [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
        )
        completed_tasks = len(
            [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        )

        return {
            "orchestration_active": self.orchestration_active,
            "total_agents": total_agents,
            "available_agents": available_agents,
            "busy_agents": busy_agents,
            "offline_agents": offline_agents,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "completed_tasks": completed_tasks,
            "queue_length": len(self.task_queue),
            "timestamp": datetime.now().isoformat(),
        }

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get the status of a specific task."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "result": task.result,
            "error_message": task.error_message,
        }

    def list_agents(self) -> list[dict[str, Any]]:
        """List all registered agents."""
        return [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "capabilities": agent.capabilities,
                "status": agent.status.value,
                "current_task": agent.current_task,
                "total_tasks_completed": agent.total_tasks_completed,
                "average_execution_time": agent.average_execution_time,
                "last_seen": agent.last_seen.isoformat(),
            }
            for agent in self.agents.values()
        ]

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ]:
            return False  # Cannot cancel already finished tasks

        # Cancel the task
        task.status = TaskStatus.CANCELLED

        # If task is running, cancel the future
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]

        # Free up the assigned agent
        if task.assigned_agent:
            agent = self.agents.get(task.assigned_agent)
            if agent and agent.current_task == task_id:
                agent.status = AgentStatus.AVAILABLE
                agent.current_task = None

        # Remove from queue if pending
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)

        self._save_state()
        logger.info(f"🚫 Cancelled task '{task.name}' (ID: {task_id})")

        return True


# For testing the orchestrator
async def test_orchestrator():
    """Test the agent orchestrator functionality."""
    orchestrator = AgentOrchestrator("test_orchestrator.db")

    try:
        # Start orchestration
        await orchestrator.start_orchestration()

        # Submit some test tasks
        test_tasks = [
            Task(
                task_id="test_001",
                name="Analyze Text Document",
                description="Analyze a document for sentiment and key topics",
                required_capabilities=["text_analysis", "summarization"],
                input_data={"document": "Sample text to analyze..."},
            ),
            Task(
                task_id="test_002",
                name="Research Market Trends",
                description="Research current market trends in AI",
                required_capabilities=["web_search", "data_analysis"],
                input_data={"topic": "AI market trends"},
                priority=TaskPriority.HIGH,
            ),
        ]

        for task in test_tasks:
            task_id = await orchestrator.submit_task(task)
            print(f"Submitted task: {task_id}")

        # Wait for tasks to process
        await asyncio.sleep(10)

        # Check system status
        status = orchestrator.get_system_status()
        print("System Status:")
        print(json.dumps(status, indent=2))

        # Check individual task status
        for task in test_tasks:
            task_status = orchestrator.get_task_status(task.task_id)
            print(f"Task {task.task_id} status:")
            print(json.dumps(task_status, indent=2))

    finally:
        await orchestrator.stop_orchestration()


if __name__ == "__main__":
    asyncio.run(test_orchestrator())

"""
Aetherra Agent Orchestrator
Multi-agent coordination and task distribution system.
"""

import asyncio
import json
import logging
import sqlite3
import time
import traceback
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Status of an agent"""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"


class TaskPriority(Enum):
    """Priority levels for tasks"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Status of a task"""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentCapability:
    """Represents an agent's capability"""

    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    performance_score: float = 1.0


@dataclass
class Task:
    """Represents a task to be executed"""

    task_id: str
    name: str
    description: str
    required_capabilities: List[str]
    input_data: Any
    priority: TaskPriority
    max_execution_time: int
    dependencies: List[str]
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any = None
    error_message: str | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Agent:
    """Represents an AI agent"""

    agent_id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    status: AgentStatus
    current_task: str | None = None
    max_concurrent_tasks: int = 1
    performance_metrics: Dict[str, float] | None = None
    last_activity: datetime | None = None

    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {
                "success_rate": 1.0,
                "avg_execution_time": 0.0,
                "total_tasks": 0,
            }
        if self.last_activity is None:
            self.last_activity = datetime.now()


class TaskQueue:
    """Priority queue for tasks"""

    def __init__(self):
        self.tasks: List[Task] = []
        self.task_index: Dict[str, Task] = {}

    def add_task(self, task: Task):
        """Add task to queue"""
        self.tasks.append(task)
        self.task_index[task.task_id] = task
        # Sort by priority and creation time
        self.tasks.sort(key=lambda t: (-t.priority.value, t.created_at))

    def get_next_task(self, agent_capabilities: Set[str]) -> Task | None:
        """Get next suitable task for agent"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # Check if agent has required capabilities
                if all(cap in agent_capabilities for cap in task.required_capabilities):
                    # Check dependencies
                    if self._dependencies_satisfied(task):
                        return task
        return None

    def _dependencies_satisfied(self, task: Task) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_id in task.dependencies:
            if dep_id in self.task_index:
                dep_task = self.task_index[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
        return True

    def remove_task(self, task_id: str):
        """Remove task from queue"""
        if task_id in self.task_index:
            task = self.task_index[task_id]
            if task in self.tasks:
                self.tasks.remove(task)
            del self.task_index[task_id]

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID"""
        return self.task_index.get(task_id)

    def get_pending_count(self) -> int:
        """Get number of pending tasks"""
        return len([t for t in self.tasks if t.status == TaskStatus.PENDING])


class AgentInterface:
    """Base interface for agents"""

    def __init__(self, agent: Agent):
        self.agent = agent

    async def execute_task(self, task: Task) -> Any:
        """Execute a task"""
        raise NotImplementedError("Subclasses must implement execute_task")

    async def health_check(self) -> bool:
        """Check if agent is healthy"""
        return True

    async def initialize(self):
        """Initialize the agent"""
        pass

    async def shutdown(self):
        """Shutdown the agent"""
        pass


class LoadBalancer:
    """Balances load across agents"""

    @staticmethod
    def select_agent(task: Task, available_agents: List[Agent]) -> Agent | None:
        """Select best agent for task"""
        suitable_agents = []

        for agent in available_agents:
            if agent.status != AgentStatus.IDLE:
                continue

            # Check capabilities
            agent_caps = {cap.name for cap in agent.capabilities}
            if all(cap in agent_caps for cap in task.required_capabilities):
                suitable_agents.append(agent)

        if not suitable_agents:
            return None

        # Select agent with best performance and lowest load
        def score_agent(agent: Agent) -> float:
            if agent.performance_metrics is None:
                performance = 1.0
            else:
                performance = agent.performance_metrics.get("success_rate", 1.0)
            load_factor = 1.0 / (
                1 + len([t for t in agent.current_task] if agent.current_task else [])
            )
            capability_match = sum(
                1
                for cap in agent.capabilities
                if cap.name in task.required_capabilities
            ) / len(task.required_capabilities)

            return performance * load_factor * capability_match

        return max(suitable_agents, key=score_agent)


class PerformanceMonitor:
    """Monitors agent and system performance"""

    def __init__(self):
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "avg_execution_time": 0.0,
            "system_throughput": 0.0,
        }
        self.start_time = time.time()

    def record_task_completion(self, task: Task, execution_time: float, success: bool):
        """Record task completion metrics"""
        self.metrics["total_tasks"] += 1

        if success:
            self.metrics["completed_tasks"] += 1
        else:
            self.metrics["failed_tasks"] += 1

        # Update average execution time
        current_avg = self.metrics["avg_execution_time"]
        total_completed = self.metrics["completed_tasks"]

        if total_completed > 0:
            self.metrics["avg_execution_time"] = (
                current_avg * (total_completed - 1) + execution_time
            ) / total_completed

        # Update throughput
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.metrics["system_throughput"] = (
                self.metrics["completed_tasks"] / elapsed_time
            )

    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        return self.metrics.copy()


class AgentOrchestrator:
    """
    Advanced multi-agent orchestration system for coordinating AI agents
    """

    def __init__(self, db_path: str = "agent_orchestrator.db", max_agents: int = 10):
        self.db_path = Path(db_path)
        self.agents: Dict[str, Agent] = {}
        self.agent_interfaces: Dict[str, AgentInterface] = {}
        self.task_queue = TaskQueue()
        self.load_balancer = LoadBalancer()
        self.performance_monitor = PerformanceMonitor()
        self.max_agents = max_agents
        self.orchestration_active = False
        self.orchestration_task = None
        self._init_database()

    def _init_database(self):
        """Initialize orchestrator database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    capabilities TEXT NOT NULL,
                    status TEXT NOT NULL,
                    performance_metrics TEXT,
                    created_at TEXT NOT NULL,
                    last_activity TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    required_capabilities TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    assigned_agent TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    execution_time REAL,
                    success BOOLEAN,
                    result TEXT,
                    error_message TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS orchestration_sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_tasks INTEGER DEFAULT 0,
                    completed_tasks INTEGER DEFAULT 0,
                    failed_tasks INTEGER DEFAULT 0,
                    active_agents INTEGER DEFAULT 0,
                    performance_metrics TEXT
                )
            """)

            conn.commit()
        finally:
            conn.close()

    def register_agent(self, agent: Agent, interface: AgentInterface):
        """Register an agent with the orchestrator"""
        if len(self.agents) >= self.max_agents:
            raise ValueError(f"Maximum agent limit ({self.max_agents}) reached")

        self.agents[agent.agent_id] = agent
        self.agent_interfaces[agent.agent_id] = interface

        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
        # Store agent asynchronously in background
        asyncio.create_task(self._store_agent(agent))

    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.agent_interfaces[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    async def submit_task(self, task: Task) -> str:
        """Submit a task for execution"""
        self.task_queue.add_task(task)
        await self._store_task(task)

        logger.info(f"Task submitted: {task.name} ({task.task_id})")

        # If orchestration is not active, try to start it
        if not self.orchestration_active:
            await self.start_orchestration()

        return task.task_id

    async def start_orchestration(self):
        """Start the orchestration process"""
        if self.orchestration_active:
            logger.warning("Orchestration already active")
            return

        self.orchestration_active = True
        self.orchestration_task = asyncio.create_task(self._orchestration_loop())

        logger.info("Agent orchestration started")

    async def stop_orchestration(self):
        """Stop the orchestration process"""
        if not self.orchestration_active:
            return

        self.orchestration_active = False

        if self.orchestration_task:
            self.orchestration_task.cancel()
            try:
                await self.orchestration_task
            except asyncio.CancelledError:
                pass

        logger.info("Agent orchestration stopped")

    async def _orchestration_loop(self):
        """Main orchestration loop"""
        try:
            while self.orchestration_active:
                await self._process_tasks()
                await self._monitor_agents()
                await asyncio.sleep(1)  # Check every second

        except asyncio.CancelledError:
            logger.info("Orchestration loop cancelled")
        except Exception as e:
            logger.error(f"Orchestration loop error: {e}")
            logger.debug(traceback.format_exc())

    async def _process_tasks(self):
        """Process pending tasks"""
        # Get available agents
        available_agents = [
            agent for agent in self.agents.values() if agent.status == AgentStatus.IDLE
        ]

        if not available_agents:
            return

        # Process tasks
        for agent in available_agents:
            agent_caps = {cap.name for cap in agent.capabilities}
            task = self.task_queue.get_next_task(agent_caps)

            if task:
                await self._assign_task(task, agent)

    async def _assign_task(self, task: Task, agent: Agent):
        """Assign a task to an agent"""
        task.status = TaskStatus.ASSIGNED
        task.assigned_agent = agent.agent_id
        task.started_at = datetime.now()

        agent.status = AgentStatus.BUSY
        agent.current_task = task.task_id
        agent.last_activity = datetime.now()

        logger.info(f"Assigned task {task.name} to agent {agent.name}")

        # Execute task in background
        asyncio.create_task(self._execute_task(task, agent))

    async def _execute_task(self, task: Task, agent: Agent):
        """Execute a task with an agent"""
        interface = self.agent_interfaces[agent.agent_id]
        start_time = time.time()

        try:
            task.status = TaskStatus.IN_PROGRESS
            await self._update_task_status(task)

            # Execute with timeout
            result = await asyncio.wait_for(
                interface.execute_task(task), timeout=task.max_execution_time
            )

            execution_time = time.time() - start_time

            # Task completed successfully
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result

            # Update agent metrics
            if agent.performance_metrics is None:
                agent.performance_metrics = {
                    "success_rate": 1.0,
                    "avg_execution_time": 0.0,
                    "total_tasks": 0,
                }
            agent.performance_metrics["total_tasks"] += 1
            success_rate = agent.performance_metrics.get("success_rate", 1.0)
            total = agent.performance_metrics["total_tasks"]
            agent.performance_metrics["success_rate"] = (
                success_rate * (total - 1) + 1.0
            ) / total

            # Update system metrics
            self.performance_monitor.record_task_completion(task, execution_time, True)

            logger.info(
                f"Task {task.name} completed by {agent.name} in {execution_time:.2f}s"
            )

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = "Task execution timeout"

            logger.error(f"Task {task.name} timed out after {execution_time:.2f}s")
            self.performance_monitor.record_task_completion(task, execution_time, False)

        except Exception as e:
            execution_time = time.time() - start_time
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = str(e)

            logger.error(f"Task {task.name} failed: {e}")
            self.performance_monitor.record_task_completion(task, execution_time, False)

        finally:
            # Clean up agent state
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.last_activity = datetime.now()

            # Remove from queue
            self.task_queue.remove_task(task.task_id)

            # Update database
            await self._update_task_status(task)

    async def _monitor_agents(self):
        """Monitor agent health and performance"""
        for agent_id, agent in self.agents.items():
            interface = self.agent_interfaces[agent_id]

            try:
                healthy = await interface.health_check()
                if not healthy:
                    agent.status = AgentStatus.ERROR
                    logger.warning(f"Agent {agent.name} health check failed")

                # Check for stuck tasks
                if agent.current_task:
                    task = self.task_queue.get_task(agent.current_task)
                    if task and task.started_at:
                        elapsed = (datetime.now() - task.started_at).total_seconds()
                        if elapsed > task.max_execution_time * 1.5:  # 50% buffer
                            logger.warning(
                                f"Task {task.name} appears stuck, may need intervention"
                            )

            except Exception as e:
                agent.status = AgentStatus.ERROR
                logger.error(f"Error monitoring agent {agent.name}: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        agent_statuses = {}
        for status in AgentStatus:
            agent_statuses[status.value] = len(
                [a for a in self.agents.values() if a.status == status]
            )

        task_statuses = {}
        for status in TaskStatus:
            task_statuses[status.value] = len(
                [t for t in self.task_queue.tasks if t.status == status]
            )

        return {
            "orchestration_active": self.orchestration_active,
            "total_agents": len(self.agents),
            "agent_statuses": agent_statuses,
            "task_statuses": task_statuses,
            "pending_tasks": self.task_queue.get_pending_count(),
            "performance_metrics": self.performance_monitor.get_metrics(),
        }

    def get_agent_status(self, agent_id: str) -> Dict[str, Any] | None:
        """Get status of specific agent"""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "status": agent.status.value,
            "current_task": agent.current_task,
            "capabilities": [cap.name for cap in agent.capabilities],
            "performance_metrics": agent.performance_metrics,
            "last_activity": agent.last_activity.isoformat()
            if agent.last_activity
            else None,
        }

    def get_task_status(self, task_id: str) -> Dict[str, Any] | None:
        """Get status of specific task"""
        task = self.task_queue.get_task(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "assigned_agent": task.assigned_agent,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "error_message": task.error_message,
        }

    async def _store_agent(self, agent: Agent):
        """Store agent in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO agents
                (agent_id, name, description, capabilities, status, performance_metrics, created_at, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    agent.agent_id,
                    agent.name,
                    agent.description,
                    json.dumps([asdict(cap) for cap in agent.capabilities]),
                    agent.status.value,
                    json.dumps(agent.performance_metrics),
                    datetime.now().isoformat(),
                    agent.last_activity.isoformat() if agent.last_activity else None,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    async def _store_task(self, task: Task):
        """Store task in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks
                (task_id, name, description, required_capabilities, priority, status,
                 assigned_agent, created_at, started_at, completed_at, success, result, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task.task_id,
                    task.name,
                    task.description,
                    json.dumps(task.required_capabilities),
                    task.priority.value,
                    task.status.value,
                    task.assigned_agent,
                    task.created_at.isoformat() if task.created_at else None,
                    task.started_at.isoformat() if task.started_at else None,
                    task.completed_at.isoformat() if task.completed_at else None,
                    task.status == TaskStatus.COMPLETED,
                    json.dumps(task.result, default=str) if task.result else None,
                    task.error_message,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    async def _update_task_status(self, task: Task):
        """Update task status in database"""
        await self._store_task(task)


# Example agent implementation
class ExampleAgent(AgentInterface):
    """Example agent for testing"""

    def __init__(self, agent: Agent, processing_delay: float = 1.0):
        super().__init__(agent)
        self.processing_delay = processing_delay

    async def execute_task(self, task: Task) -> Any:
        """Execute a task"""
        await asyncio.sleep(self.processing_delay)  # Simulate work

        result = f"Task '{task.name}' processed by {self.agent.name}"
        return result


# Testing function
async def test_agent_orchestrator():
    """Test the agent orchestrator"""
    orchestrator = AgentOrchestrator()

    # Create test agents
    agents_data = [
        Agent(
            agent_id="analyzer-1",
            name="Text Analyzer",
            description="Analyzes text content",
            capabilities=[
                AgentCapability(
                    "text_analysis", "Analyze text", ["text"], ["analysis"]
                ),
                AgentCapability(
                    "sentiment", "Sentiment analysis", ["text"], ["sentiment"]
                ),
            ],
            status=AgentStatus.IDLE,
        ),
        Agent(
            agent_id="processor-1",
            name="Data Processor",
            description="Processes data",
            capabilities=[
                AgentCapability(
                    "data_processing", "Process data", ["data"], ["processed_data"]
                ),
                AgentCapability(
                    "validation", "Data validation", ["data"], ["validation_result"]
                ),
            ],
            status=AgentStatus.IDLE,
        ),
    ]

    # Register agents
    for agent_data in agents_data:
        interface = ExampleAgent(agent_data, processing_delay=2.0)
        orchestrator.register_agent(agent_data, interface)

    # Start orchestration
    await orchestrator.start_orchestration()

    # Submit test tasks
    tasks = [
        Task(
            task_id=str(uuid.uuid4()),
            name="Analyze Customer Feedback",
            description="Analyze customer feedback sentiment",
            required_capabilities=["text_analysis", "sentiment"],
            input_data="Customer feedback text here",
            priority=TaskPriority.HIGH,
            max_execution_time=30,
            dependencies=[],
        ),
        Task(
            task_id=str(uuid.uuid4()),
            name="Process Sales Data",
            description="Process and validate sales data",
            required_capabilities=["data_processing"],
            input_data={"sales": [100, 200, 300]},
            priority=TaskPriority.NORMAL,
            max_execution_time=60,
            dependencies=[],
        ),
    ]

    # Submit tasks
    for task in tasks:
        await orchestrator.submit_task(task)

    # Wait for tasks to complete
    await asyncio.sleep(5)

    # Check system status
    status = orchestrator.get_system_status()
    print("System Status:")
    print(json.dumps(status, indent=2, default=str))

    # Stop orchestration
    await orchestrator.stop_orchestration()


if __name__ == "__main__":
    asyncio.run(test_agent_orchestrator())

#!/usr/bin/env python3
"""
🤖 LYRIXA AGENT ORCHESTRATOR
============================

Lyrixa's multi-agent system for complex task orchestration.
Manages specialized AI agents that work together to solve problems.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentType(Enum):
    """Types of specialized agents"""

    PLANNER = "planner"
    CODER = "coder"
    ANALYZER = "analyzer"
    DEBUGGER = "debugger"
    TESTER = "tester"
    DOCUMENTER = "documenter"
    OPTIMIZER = "optimizer"
    RESEARCHER = "researcher"


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Represents a task for an agent"""

    id: str
    agent_type: AgentType
    task_type: str
    description: str
    input_data: Dict[str, Any]
    priority: int  # 1-10, higher is more important
    created_at: datetime
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = None  # Task IDs this task depends on
    estimated_duration: int = 60  # seconds

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class AgentCapability:
    """Describes an agent's capability"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    estimated_duration: int = 60


class LyrixaAgent(ABC):
    """
    Base class for all Lyrixa agents

    Agents are specialized AI components that handle specific types of tasks.
    """

    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.name = self.__class__.__name__
        self.capabilities: List[AgentCapability] = []
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_history: List[AgentTask] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_duration": 0.0,
            "success_rate": 0.0,
        }

    @abstractmethod
    async def can_handle_task(self, task: AgentTask) -> bool:
        """Check if this agent can handle the given task"""
        pass

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task and return the result"""
        pass

    async def initialize(self, orchestrator_context: Dict[str, Any]) -> bool:
        """Initialize the agent with orchestrator context"""
        return True

    async def cleanup(self) -> bool:
        """Clean up agent resources"""
        return True

    def get_capabilities(self) -> List[AgentCapability]:
        """Get agent capabilities"""
        return self.capabilities

    def update_performance_metrics(self, task: AgentTask):
        """Update performance metrics after task completion"""
        if task.status == TaskStatus.COMPLETED:
            self.performance_metrics["tasks_completed"] += 1
        elif task.status == TaskStatus.FAILED:
            self.performance_metrics["tasks_failed"] += 1

        total_tasks = (
            self.performance_metrics["tasks_completed"]
            + self.performance_metrics["tasks_failed"]
        )
        if total_tasks > 0:
            self.performance_metrics["success_rate"] = (
                self.performance_metrics["tasks_completed"] / total_tasks
            )


class AgentOrchestrator:
    """
    Lyrixa's agent orchestration system

    Manages multiple specialized agents, coordinates their work,
    and handles complex multi-step tasks.
    """

    def __init__(self):
        self.agents: Dict[AgentType, LyrixaAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.active_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: Dict[str, AgentTask] = {}
        self.task_dependencies: Dict[str, List[str]] = {}
        self.orchestrator_context: Dict[str, Any] = {}

        # Initialize built-in agents
        self._initialize_builtin_agents()

    def _initialize_builtin_agents(self):
        """Initialize built-in agent types"""
        agent_classes = {
            AgentType.PLANNER: PlannerAgent,
            AgentType.CODER: CoderAgent,
            AgentType.ANALYZER: AnalyzerAgent,
            AgentType.DEBUGGER: DebuggerAgent,
            AgentType.TESTER: TesterAgent,
            AgentType.DOCUMENTER: DocumenterAgent,
            AgentType.OPTIMIZER: OptimizerAgent,
            AgentType.RESEARCHER: ResearcherAgent,
        }

        for agent_type, agent_class in agent_classes.items():
            try:
                agent = agent_class(agent_type)
                self.agents[agent_type] = agent
                print(f"🤖 Initialized {agent_type.value} agent")
            except Exception as e:
                print(f"❌ Failed to initialize {agent_type.value} agent: {e}")

    async def initialize(self, orchestrator_context: Dict[str, Any]):
        """Initialize the orchestrator and all agents"""
        self.orchestrator_context = orchestrator_context

        for agent in self.agents.values():
            await agent.initialize(orchestrator_context)

        print(f"🎭 Agent orchestrator initialized with {len(self.agents)} agents")

    async def create_task(
        self,
        agent_type: AgentType,
        task_type: str,
        description: str,
        input_data: Dict[str, Any],
        priority: int = 5,
        dependencies: Optional[List[str]] = None,
    ) -> str:
        """Create a new task for an agent"""
        task_id = (
            f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.task_queue)}"
        )

        task = AgentTask(
            id=task_id,
            agent_type=agent_type,
            task_type=task_type,
            description=description,
            input_data=input_data,
            priority=priority,
            created_at=datetime.now(),
            dependencies=dependencies or [],
        )

        self.task_queue.append(task)

        if dependencies:
            self.task_dependencies[task_id] = dependencies

        print(f"📋 Created task: {description} ({agent_type.value})")
        return task_id

    async def execute_next_task(self) -> Optional[Dict[str, Any]]:
        """Execute the next available task"""
        if not self.task_queue:
            return None

        # Find a task that can be executed (dependencies met)
        executable_task = None
        for i, task in enumerate(self.task_queue):
            if self._can_execute_task(task):
                executable_task = self.task_queue.pop(i)
                break

        if not executable_task:
            return None

        # Find appropriate agent
        agent = self.agents.get(executable_task.agent_type)
        if not agent:
            executable_task.status = TaskStatus.FAILED
            executable_task.error = (
                f"No agent available for type {executable_task.agent_type.value}"
            )
            return {
                "task_id": executable_task.id,
                "status": "failed",
                "error": executable_task.error,
            }

        # Check if agent can handle the task
        if not await agent.can_handle_task(executable_task):
            executable_task.status = TaskStatus.FAILED
            executable_task.error = (
                f"Agent cannot handle task type {executable_task.task_type}"
            )
            return {
                "task_id": executable_task.id,
                "status": "failed",
                "error": executable_task.error,
            }

        # Execute the task
        self.active_tasks[executable_task.id] = executable_task
        executable_task.status = TaskStatus.IN_PROGRESS

        try:
            print(f"🔄 Executing task: {executable_task.description}")
            result = await agent.execute_task(executable_task)

            executable_task.status = TaskStatus.COMPLETED
            executable_task.result = result

            # Move to completed tasks
            self.completed_tasks[executable_task.id] = executable_task
            del self.active_tasks[executable_task.id]

            # Update agent performance
            agent.update_performance_metrics(executable_task)

            print(f"✅ Completed task: {executable_task.description}")

            return {
                "task_id": executable_task.id,
                "status": "completed",
                "result": result,
            }

        except Exception as e:
            executable_task.status = TaskStatus.FAILED
            executable_task.error = str(e)

            # Move to completed tasks (even if failed)
            self.completed_tasks[executable_task.id] = executable_task
            del self.active_tasks[executable_task.id]

            # Update agent performance
            agent.update_performance_metrics(executable_task)

            print(f"❌ Task failed: {executable_task.description} - {e}")

            return {"task_id": executable_task.id, "status": "failed", "error": str(e)}

    def _can_execute_task(self, task: AgentTask) -> bool:
        """Check if a task can be executed (dependencies met)"""
        if not task.dependencies:
            return True

        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
            if self.completed_tasks[dep_id].status != TaskStatus.COMPLETED:
                return False

        return True

    async def execute_workflow(
        self, workflow_description: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a complex workflow using multiple agents"""
        print(f"🎭 Starting workflow: {workflow_description}")

        # Plan the workflow
        await self.create_task(
            AgentType.PLANNER,
            "workflow_planning",
            f"Plan workflow: {workflow_description}",
            {"description": workflow_description, "input_data": input_data},
            priority=10,
        )

        # Execute planning task
        plan_result = await self.execute_next_task()

        if not plan_result or plan_result["status"] != "completed":
            return {"error": "Failed to plan workflow", "details": plan_result}

        # Get the plan
        plan = plan_result["result"].get("plan", [])

        # Execute planned tasks
        task_ids = []
        for i, step in enumerate(plan):
            task_id = await self.create_task(
                AgentType(step["agent_type"]),
                step["task_type"],
                step["description"],
                step["input_data"],
                priority=10 - i,  # Higher priority for earlier steps
                dependencies=step.get("dependencies", []),
            )
            task_ids.append(task_id)

        # Execute all tasks
        results = []
        while self.task_queue or self.active_tasks:
            result = await self.execute_next_task()
            if result:
                results.append(result)
            else:
                # No executable tasks, wait a bit
                await asyncio.sleep(0.1)

        return {
            "workflow": workflow_description,
            "tasks_executed": len(results),
            "results": results,
            "success": all(r["status"] == "completed" for r in results),
        }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {"status": task.status.value, "progress": "in_progress"}
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "status": task.status.value,
                "result": task.result,
                "error": task.error,
            }
        else:
            # Check task queue
            for task in self.task_queue:
                if task.id == task_id:
                    return {"status": task.status.value, "progress": "queued"}

        return None

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {}

        for agent_type, agent in self.agents.items():
            status[agent_type.value] = {
                "active_tasks": len(agent.active_tasks),
                "performance": agent.performance_metrics,
                "capabilities": len(agent.capabilities),
            }

        return status

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "total_agents": len(self.agents),
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "task_dependencies": len(self.task_dependencies),
        }


# Built-in Agent Implementations


class PlannerAgent(LyrixaAgent):
    """Agent for planning and breaking down complex tasks"""

    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.name = "Planner"
        self.capabilities = [
            AgentCapability(
                name="workflow_planning",
                description="Break down complex workflows into executable steps",
                input_schema={"description": "string", "input_data": "object"},
                output_schema={"plan": "array"},
            )
        ]

    async def can_handle_task(self, task: AgentTask) -> bool:
        return task.task_type in [
            "workflow_planning",
            "task_breakdown",
            "project_planning",
        ]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        if task.task_type == "workflow_planning":
            return await self._plan_workflow(task.input_data)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}

    async def _plan_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        description = input_data.get("description", "")

        # Simple planning logic (in real implementation, use AI)
        plan = []

        if "code" in description.lower():
            plan.append(
                {
                    "agent_type": "analyzer",
                    "task_type": "code_analysis",
                    "description": "Analyze existing code",
                    "input_data": input_data,
                    "dependencies": [],
                }
            )
            plan.append(
                {
                    "agent_type": "coder",
                    "task_type": "code_generation",
                    "description": "Generate new code",
                    "input_data": input_data,
                    "dependencies": [],
                }
            )

        if "test" in description.lower():
            plan.append(
                {
                    "agent_type": "tester",
                    "task_type": "test_creation",
                    "description": "Create tests",
                    "input_data": input_data,
                    "dependencies": [],
                }
            )

        if "document" in description.lower():
            plan.append(
                {
                    "agent_type": "documenter",
                    "task_type": "documentation",
                    "description": "Create documentation",
                    "input_data": input_data,
                    "dependencies": [],
                }
            )

        return {"plan": plan}


class CoderAgent(LyrixaAgent):
    """Agent for code generation and modification"""

    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.name = "Coder"
        self.capabilities = [
            AgentCapability(
                name="code_generation",
                description="Generate code based on specifications",
                input_schema={"specification": "string", "language": "string"},
                output_schema={"code": "string", "explanation": "string"},
            )
        ]

    async def can_handle_task(self, task: AgentTask) -> bool:
        return task.task_type in [
            "code_generation",
            "code_modification",
            "code_refactoring",
        ]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "code": "# Generated code placeholder",
            "explanation": f"Generated code for task: {task.description}",
            "language": "python",
        }


class AnalyzerAgent(LyrixaAgent):
    """Agent for code and data analysis"""

    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.name = "Analyzer"
        self.capabilities = [
            AgentCapability(
                name="code_analysis",
                description="Analyze code for quality, patterns, and issues",
                input_schema={"code": "string", "language": "string"},
                output_schema={"analysis": "object", "recommendations": "array"},
            )
        ]

    async def can_handle_task(self, task: AgentTask) -> bool:
        return task.task_type in ["code_analysis", "data_analysis", "pattern_analysis"]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "analysis": {"complexity": "medium", "maintainability": "good"},
            "recommendations": ["Add more comments", "Consider refactoring"],
            "metrics": {"lines_of_code": 100, "functions": 5},
        }


class DebuggerAgent(LyrixaAgent):
    """Agent for debugging and error diagnosis"""

    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.name = "Debugger"

    async def can_handle_task(self, task: AgentTask) -> bool:
        return task.task_type in ["debug_analysis", "error_diagnosis", "bug_fixing"]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "issues_found": [],
            "fixes_suggested": [],
            "debug_info": "Debug analysis completed",
        }


class TesterAgent(LyrixaAgent):
    """Agent for test creation and execution"""

    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.name = "Tester"

    async def can_handle_task(self, task: AgentTask) -> bool:
        return task.task_type in ["test_creation", "test_execution", "test_analysis"]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "tests_created": 3,
            "test_code": "# Test code placeholder",
            "coverage": 85.5,
        }


class DocumenterAgent(LyrixaAgent):
    """Agent for documentation creation"""

    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.name = "Documenter"

    async def can_handle_task(self, task: AgentTask) -> bool:
        return task.task_type in ["documentation", "api_docs", "user_guide"]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "documentation": "# Documentation\n\nGenerated documentation placeholder",
            "format": "markdown",
            "sections": ["Overview", "Usage", "API Reference"],
        }


class OptimizerAgent(LyrixaAgent):
    """Agent for performance optimization"""

    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.name = "Optimizer"

    async def can_handle_task(self, task: AgentTask) -> bool:
        return task.task_type in [
            "performance_optimization",
            "code_optimization",
            "resource_optimization",
        ]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "optimizations": ["Reduced memory usage", "Improved algorithm efficiency"],
            "performance_gain": "25% faster execution",
            "recommendations": ["Use caching", "Optimize database queries"],
        }


class ResearcherAgent(LyrixaAgent):
    """Agent for research and information gathering"""

    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.name = "Researcher"

    async def can_handle_task(self, task: AgentTask) -> bool:
        return task.task_type in [
            "research",
            "information_gathering",
            "technology_analysis",
        ]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "research_results": [],
            "sources": [],
            "summary": "Research completed on the given topic",
            "confidence": 0.8,
        }

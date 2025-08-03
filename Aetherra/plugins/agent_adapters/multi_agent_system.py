#!/usr/bin/env python3
"""
Lyrixa Multi-Agent System
Production-ready multi-agent orchestration system
"""

import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentRole(Enum):
    """Available agent roles"""

    PLANNER = "planner"
    CODER = "coder"
    ANALYZER = "analyzer"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class Agent:
    """Individual agent in the multi-agent system"""

    def __init__(
        self, name: str, role: AgentRole, capabilities: Optional[List[str]] = None
    ):
        self.name = name
        self.role = role
        self.capabilities = capabilities or []
        self.status = "idle"
        self.active_tasks = []
        self.completed_tasks = 0
        self.created_at = datetime.now()

    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type"""
        return task_type in self.capabilities

    def assign_task(self, task):
        """Assign a task to this agent"""
        self.active_tasks.append(task)
        self.status = "busy"

    def complete_task(self, task):
        """Mark a task as completed"""
        if task in self.active_tasks:
            self.active_tasks.remove(task)
            self.completed_tasks += 1

        if not self.active_tasks:
            self.status = "idle"

    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "name": self.name,
            "role": self.role.value,
            "status": self.status,
            "capabilities": self.capabilities,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": self.completed_tasks,
            "created_at": self.created_at.isoformat(),
        }


class Task:
    """Task in the multi-agent system"""

    def __init__(
        self, task_id: str, description: str, task_type: str, priority: int = 1
    ):
        self.id = task_id
        self.description = description
        self.task_type = task_type
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.assigned_agent = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None

    def start(self, agent: Agent):
        """Start task execution"""
        self.assigned_agent = agent
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self, result: Any = None):
        """Complete the task"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def fail(self, error: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()

    def get_status(self) -> Dict[str, Any]:
        """Get task status information"""
        return {
            "id": self.id,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority,
            "status": self.status.value,
            "assigned_agent": self.assigned_agent.name if self.assigned_agent else None,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "result": self.result,
            "error": self.error,
        }


class LyrixaMultiAgentSystem:
    """
    Lyrixa Multi-Agent System
    Orchestrates multiple AI agents for complex task execution
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.running = False
        self.system_status = "initialized"

        # Create default agents
        self._create_default_agents()

        print("🤖 Lyrixa Multi-Agent System initialized")
        print(f"   [TOOL] Created {len(self.agents)} default agents")

    def _create_default_agents(self):
        """Create default set of agents"""
        default_agents = [
            ("planner", AgentRole.PLANNER, ["planning", "strategy", "coordination"]),
            ("coder", AgentRole.CODER, ["coding", "implementation", "debugging"]),
            (
                "analyzer",
                AgentRole.ANALYZER,
                ["analysis", "research", "data_processing"],
            ),
            (
                "reviewer",
                AgentRole.REVIEWER,
                ["review", "quality_assurance", "validation"],
            ),
        ]

        for name, role, capabilities in default_agents:
            agent = Agent(name, role, capabilities)
            self.agents[name] = agent

    def add_agent(
        self, name: str, role: AgentRole, capabilities: Optional[List[str]] = None
    ) -> bool:
        """Add a new agent to the system"""
        if name in self.agents:
            return False

        agent = Agent(name, role, capabilities or [])
        self.agents[name] = agent
        return True

    def remove_agent(self, name: str) -> bool:
        """Remove an agent from the system"""
        if name not in self.agents:
            return False

        agent = self.agents[name]
        if agent.active_tasks:
            # Can't remove agent with active tasks
            return False

        del self.agents[name]
        return True

    def create_task(self, description: str, task_type: str, priority: int = 1) -> str:
        """Create a new task"""
        task_id = f"task_{len(self.tasks) + 1}_{int(time.time())}"
        task = Task(task_id, description, task_type, priority)

        self.tasks[task_id] = task
        self.task_queue.append(task)

        # Sort queue by priority
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)

        return task_id

    def assign_task(self, task_id: str, agent_name: Optional[str] = None) -> bool:
        """Assign a task to an agent"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        if agent_name:
            # Assign to specific agent
            if agent_name not in self.agents:
                return False
            agent = self.agents[agent_name]
        else:
            # Find best available agent
            agent = self._find_best_agent(task)
            if not agent:
                return False

        # Assign task
        task.start(agent)
        agent.assign_task(task)

        # Remove from queue
        if task in self.task_queue:
            self.task_queue.remove(task)

        return True

    def _find_best_agent(self, task: Task) -> Optional[Agent]:
        """Find the best available agent for a task"""
        available_agents = [
            agent
            for agent in self.agents.values()
            if agent.status == "idle" and agent.can_handle(task.task_type)
        ]

        if not available_agents:
            return None

        # Return agent with least completed tasks (load balancing)
        return min(available_agents, key=lambda a: a.completed_tasks)

    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark a task as completed"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.complete(result)

        if task.assigned_agent:
            task.assigned_agent.complete_task(task)

        return True

    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.fail(error)

        if task.assigned_agent:
            task.assigned_agent.complete_task(task)

        return True

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_stats = {}
        for name, agent in self.agents.items():
            agent_stats[name] = agent.get_status()

        task_stats = []
        for task in self.tasks.values():
            task_stats.append(task.get_status())

        return {
            "system_status": self.system_status,
            "running": self.running,
            "agents": agent_stats,
            "tasks": task_stats,
            "queue_length": len(self.task_queue),
            "completed_tasks": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
            ),
            "failed_tasks": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
            ),
            "recent_activity": self._get_recent_activity(),
        }

    def _get_recent_activity(self) -> List[str]:
        """Get recent system activity"""
        activities = []

        # Recent completed tasks
        recent_completed = [
            t
            for t in self.tasks.values()
            if t.status == TaskStatus.COMPLETED and t.completed_at
        ]
        recent_completed.sort(
            key=lambda t: t.completed_at or datetime.min, reverse=True
        )

        for task in recent_completed[:3]:
            activities.append(f"Completed: {task.description}")

        # Active tasks
        active_tasks = [
            t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS
        ]
        for task in active_tasks[:2]:
            activities.append(f"In Progress: {task.description}")

        if not activities:
            activities.append("No recent activity")

        return activities

    def start(self):
        """Start the multi-agent system"""
        self.running = True
        self.system_status = "running"
        print("🚀 Multi-agent system started")

    def stop(self):
        """Stop the multi-agent system"""
        self.running = False
        self.system_status = "stopped"
        print("⏹️ Multi-agent system stopped")

    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an agent"""
        if agent_name not in self.agents:
            return None

        return self.agents[agent_name].get_status()

    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a task"""
        if task_id not in self.tasks:
            return None

        return self.tasks[task_id].get_status()


# Global instance
multi_agent_system = None


def get_multi_agent_system():
    """Get the global multi-agent system instance"""
    global multi_agent_system
    if multi_agent_system is None:
        multi_agent_system = LyrixaMultiAgentSystem()
    return multi_agent_system


if __name__ == "__main__":
    # Demo the multi-agent system
    print("🤖 LYRIXA MULTI-AGENT SYSTEM DEMO")
    print("=" * 50)

    # Initialize system
    mas = LyrixaMultiAgentSystem()

    # Start the system
    mas.start()

    # Create some test tasks
    task1_id = mas.create_task("Analyze user requirements", "analysis", priority=3)
    task2_id = mas.create_task("Design system architecture", "planning", priority=2)
    task3_id = mas.create_task("Implement core features", "coding", priority=1)

    print(f"\n📝 Created {len(mas.tasks)} tasks")

    # Assign tasks
    mas.assign_task(task1_id)  # Auto-assign
    mas.assign_task(task2_id, "planner")  # Specific assignment
    mas.assign_task(task3_id)  # Auto-assign

    print("✅ Tasks assigned to agents")

    # Complete some tasks
    mas.complete_task(task1_id, {"analysis": "Requirements analyzed"})
    mas.complete_task(task2_id, {"architecture": "System designed"})

    # Get system status
    status = mas.get_system_status()
    print("\n📊 System Status:")
    print(f"   - Agents: {len(status['agents'])}")
    print(f"   - Total tasks: {len(status['tasks'])}")
    print(f"   - Completed: {status['completed_tasks']}")
    print(f"   - Failed: {status['failed_tasks']}")
    print(f"   - Queue length: {status['queue_length']}")

    print("\n🎯 Recent Activity:")
    for activity in status["recent_activity"]:
        print(f"   - {activity}")

    print("\n🎉 Multi-Agent System Demo Complete!")
    print("=" * 50)

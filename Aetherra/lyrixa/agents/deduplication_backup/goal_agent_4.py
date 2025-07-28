from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .agent_base import AgentBase, AgentResponse


@dataclass
class Goal:
    """Represents a goal or task"""

    id: str
    description: str
    priority: int
    status: str  # "pending", "active", "completed", "failed"
    created_at: datetime
    deadline: Optional[datetime] = None
    progress: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class GoalAgent(AgentBase):
    """Agent responsible for goal creation, tracking, and execution"""

    def __init__(self, memory, prompt_engine, llm_manager):
        super().__init__("GoalAgent", "Handles goal creation, retry, and escalation")
        self.memory = memory
        self.prompt_engine = prompt_engine
        self.llm_manager = llm_manager

        self.goals = {}  # goal_id -> Goal
        self.goal_counter = 0
        self.max_retries = 3
        self.retry_delay = 30  # seconds

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process goal-related input"""
        context = context or {}

        try:
            # Determine if this is a goal creation, status check, or update
            if "create" in input_text.lower() or "new goal" in input_text.lower():
                result = await self._create_goal(input_text, context)
            elif "status" in input_text.lower() or "progress" in input_text.lower():
                result = await self._check_goal_status(input_text, context)
            elif "update" in input_text.lower():
                result = await self._update_goal_progress(input_text, context)
            else:
                # Default to creating a goal
                result = await self._create_goal(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing goal input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error processing your goal: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _create_goal(
        self, description: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Create a new goal"""
        goal_id = f"goal_{self.goal_counter}"
        self.goal_counter += 1

        # Parse priority from description or context
        priority = context.get("priority", 1)
        if "urgent" in description.lower() or "priority" in description.lower():
            priority = 3
        elif "important" in description.lower():
            priority = 2

        # Create the goal
        goal = Goal(
            id=goal_id,
            description=description,
            priority=priority,
            status="pending",
            created_at=datetime.now(),
            metadata=context,
        )

        self.goals[goal_id] = goal
        self.log(f"Created new goal: {goal_id} - {description}")

        return AgentResponse(
            content=f"Goal created successfully: {description}\nGoal ID: {goal_id}\nPriority: {priority}",
            confidence=0.9,
            agent_name=self.name,
            metadata={"goal_id": goal_id, "goal": goal.__dict__},
        )

    async def _check_goal_status(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Check status of goals"""
        if not self.goals:
            return AgentResponse(
                content="No goals currently tracked.",
                confidence=1.0,
                agent_name=self.name,
                metadata={"goal_count": 0},
            )

        # Get active goals
        active_goals = [g for g in self.goals.values() if g.status == "active"]
        pending_goals = [g for g in self.goals.values() if g.status == "pending"]
        completed_goals = [g for g in self.goals.values() if g.status == "completed"]

        status_text = f"Goal Status Summary:\n"
        status_text += f"Active Goals: {len(active_goals)}\n"
        status_text += f"Pending Goals: {len(pending_goals)}\n"
        status_text += f"Completed Goals: {len(completed_goals)}\n\n"

        if active_goals:
            status_text += "Active Goals:\n"
            for goal in active_goals:
                status_text += (
                    f"- {goal.id}: {goal.description} (Progress: {goal.progress:.1%})\n"
                )

        return AgentResponse(
            content=status_text,
            confidence=1.0,
            agent_name=self.name,
            metadata={
                "active_count": len(active_goals),
                "pending_count": len(pending_goals),
                "completed_count": len(completed_goals),
            },
        )

    async def _update_goal_progress(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Update progress on a goal"""
        goal_id = context.get("goal_id")
        progress = context.get("progress", 0.0)

        if not goal_id or goal_id not in self.goals:
            return AgentResponse(
                content="Please specify a valid goal ID to update progress.",
                confidence=0.5,
                agent_name=self.name,
                metadata={"error": "invalid_goal_id"},
            )

        goal = self.goals[goal_id]
        goal.progress = min(1.0, max(0.0, progress))

        if goal.progress >= 1.0:
            goal.status = "completed"
            self.log(f"Goal completed: {goal_id}")

        return AgentResponse(
            content=f"Goal progress updated: {goal.description}\nProgress: {goal.progress:.1%}",
            confidence=0.9,
            agent_name=self.name,
            metadata={"goal_id": goal_id, "progress": goal.progress},
        )

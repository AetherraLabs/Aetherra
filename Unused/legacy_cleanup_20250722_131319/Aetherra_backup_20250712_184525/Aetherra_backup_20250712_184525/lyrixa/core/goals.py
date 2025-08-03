#!/usr/bin/env python3
"""
🎯 LYRIXA GOAL SYSTEM
====================

Lyrixa's goal tracking and project management capabilities.
Helps users set, track, and achieve development goals.
"""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class GoalStatus(Enum):
    """Goal status enumeration"""

    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class GoalPriority(Enum):
    """Goal priority enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Goal:
    """Represents a development goal"""

    id: str
    title: str
    description: str
    status: GoalStatus
    priority: GoalPriority
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    progress: float = 0.0  # 0.0 to 1.0
    tags: List[str] = None
    subtasks: List[str] = None
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.subtasks is None:
            self.subtasks = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Subtask:
    """Represents a subtask within a goal"""

    id: str
    goal_id: str
    title: str
    description: str
    completed: bool = False
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class LyrixaGoalSystem:
    """
    Lyrixa's goal tracking and project management system

    Helps users set development goals, track progress, and stay organized.
    Integrates with Lyrixa's memory and plugin systems for comprehensive support.
    """

    def __init__(self, goals_file: str = "lyrixa_goals.json"):
        self.goals_file = goals_file
        self.goals: Dict[str, Goal] = {}
        self.subtasks: Dict[str, Subtask] = {}
        self.auto_save = True

        # Load existing goals
        self._load_goals()

    def _load_goals(self):
        """Load goals from the JSON file"""
        if os.path.exists(self.goals_file):
            try:
                with open(self.goals_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Load goals
                if "goals" in data:
                    for goal_data in data["goals"]:
                        goal = Goal(
                            id=goal_data["id"],
                            title=goal_data["title"],
                            description=goal_data["description"],
                            status=GoalStatus(goal_data["status"]),
                            priority=GoalPriority(goal_data["priority"]),
                            created_at=datetime.fromisoformat(goal_data["created_at"]),
                            updated_at=datetime.fromisoformat(goal_data["updated_at"]),
                            due_date=datetime.fromisoformat(goal_data["due_date"])
                            if goal_data.get("due_date")
                            else None,
                            completion_date=datetime.fromisoformat(
                                goal_data["completion_date"]
                            )
                            if goal_data.get("completion_date")
                            else None,
                            progress=goal_data.get("progress", 0.0),
                            tags=goal_data.get("tags", []),
                            subtasks=goal_data.get("subtasks", []),
                            dependencies=goal_data.get("dependencies", []),
                            metadata=goal_data.get("metadata", {}),
                        )
                        self.goals[goal.id] = goal

                # Load subtasks
                if "subtasks" in data:
                    for subtask_data in data["subtasks"]:
                        subtask = Subtask(
                            id=subtask_data["id"],
                            goal_id=subtask_data["goal_id"],
                            title=subtask_data["title"],
                            description=subtask_data["description"],
                            completed=subtask_data.get("completed", False),
                            created_at=datetime.fromisoformat(
                                subtask_data["created_at"]
                            ),
                            completed_at=datetime.fromisoformat(
                                subtask_data["completed_at"]
                            )
                            if subtask_data.get("completed_at")
                            else None,
                        )
                        self.subtasks[subtask.id] = subtask

                print(
                    f"✅ Loaded {len(self.goals)} goals and {len(self.subtasks)} subtasks"
                )

            except Exception as e:
                print(f"[ERROR] Failed to load goals: {e}")
        else:
            print("📝 No existing goals file found, starting fresh")

    def _save_goals(self):
        """Save goals to the JSON file"""
        if not self.auto_save:
            return

        try:
            data = {
                "goals": [],
                "subtasks": [],
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_goals": len(self.goals),
                    "total_subtasks": len(self.subtasks),
                },
            }

            # Serialize goals
            for goal in self.goals.values():
                goal_data = asdict(goal)
                # Convert datetime objects to ISO strings
                goal_data["created_at"] = goal.created_at.isoformat()
                goal_data["updated_at"] = goal.updated_at.isoformat()
                if goal.due_date:
                    goal_data["due_date"] = goal.due_date.isoformat()
                if goal.completion_date:
                    goal_data["completion_date"] = goal.completion_date.isoformat()
                goal_data["status"] = goal.status.value
                goal_data["priority"] = goal.priority.value
                data["goals"].append(goal_data)

            # Serialize subtasks
            for subtask in self.subtasks.values():
                subtask_data = asdict(subtask)
                subtask_data["created_at"] = subtask.created_at.isoformat()
                if subtask.completed_at:
                    subtask_data["completed_at"] = subtask.completed_at.isoformat()
                data["subtasks"].append(subtask_data)

            with open(self.goals_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"[ERROR] Failed to save goals: {e}")

    async def create_goal(
        self,
        title: str,
        description: str,
        priority: GoalPriority = GoalPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new goal"""
        goal_id = f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.goals)}"

        goal = Goal(
            id=goal_id,
            title=title,
            description=description,
            status=GoalStatus.ACTIVE,
            priority=priority,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=due_date,
            tags=tags or [],
            metadata=metadata or {},
        )

        self.goals[goal_id] = goal
        self._save_goals()

        print(f"🎯 Created goal: {title}")
        return goal_id

    async def update_goal(self, goal_id: str, **updates) -> bool:
        """Update an existing goal"""
        if goal_id not in self.goals:
            return False

        goal = self.goals[goal_id]

        # Update allowed fields
        if "title" in updates:
            goal.title = updates["title"]
        if "description" in updates:
            goal.description = updates["description"]
        if "status" in updates:
            goal.status = GoalStatus(updates["status"])
            if goal.status == GoalStatus.COMPLETED:
                goal.completion_date = datetime.now()
                goal.progress = 1.0
        if "priority" in updates:
            goal.priority = GoalPriority(updates["priority"])
        if "due_date" in updates:
            goal.due_date = updates["due_date"]
        if "progress" in updates:
            goal.progress = min(1.0, max(0.0, updates["progress"]))
        if "tags" in updates:
            goal.tags = updates["tags"]
        if "metadata" in updates:
            goal.metadata.update(updates["metadata"])

        goal.updated_at = datetime.now()
        self._save_goals()

        print(f"🔄 Updated goal: {goal.title}")
        return True

    async def complete_goal(self, goal_id: str) -> bool:
        """Mark a goal as completed"""
        return await self.update_goal(goal_id, status="completed", progress=1.0)

    async def delete_goal(self, goal_id: str) -> bool:
        """Delete a goal and its subtasks"""
        if goal_id not in self.goals:
            return False

        goal = self.goals[goal_id]

        # Delete associated subtasks
        subtasks_to_delete = [
            st_id for st_id, st in self.subtasks.items() if st.goal_id == goal_id
        ]
        for subtask_id in subtasks_to_delete:
            del self.subtasks[subtask_id]

        del self.goals[goal_id]
        self._save_goals()

        print(f"🗑️ Deleted goal: {goal.title}")
        return True

    async def add_subtask(self, goal_id: str, title: str, description: str = "") -> str:
        """Add a subtask to a goal"""
        if goal_id not in self.goals:
            return ""

        subtask_id = (
            f"subtask_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.subtasks)}"
        )

        subtask = Subtask(
            id=subtask_id, goal_id=goal_id, title=title, description=description
        )

        self.subtasks[subtask_id] = subtask

        # Add to goal's subtask list
        goal = self.goals[goal_id]
        if subtask_id not in goal.subtasks:
            goal.subtasks.append(subtask_id)
            goal.updated_at = datetime.now()

        self._save_goals()

        print(f"📋 Added subtask to {goal.title}: {title}")
        return subtask_id

    async def complete_subtask(self, subtask_id: str) -> bool:
        """Mark a subtask as completed"""
        if subtask_id not in self.subtasks:
            return False

        subtask = self.subtasks[subtask_id]
        subtask.completed = True
        subtask.completed_at = datetime.now()

        # Update goal progress
        await self._update_goal_progress(subtask.goal_id)

        self._save_goals()

        print(f"✅ Completed subtask: {subtask.title}")
        return True

    async def _update_goal_progress(self, goal_id: str):
        """Update goal progress based on completed subtasks"""
        if goal_id not in self.goals:
            return

        goal = self.goals[goal_id]
        goal_subtasks = [
            self.subtasks[st_id] for st_id in goal.subtasks if st_id in self.subtasks
        ]

        if goal_subtasks:
            completed_count = sum(1 for st in goal_subtasks if st.completed)
            goal.progress = completed_count / len(goal_subtasks)

            # Auto-complete goal if all subtasks are done
            if goal.progress == 1.0 and goal.status == GoalStatus.ACTIVE:
                goal.status = GoalStatus.COMPLETED
                goal.completion_date = datetime.now()

        goal.updated_at = datetime.now()

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a specific goal"""
        return self.goals.get(goal_id)

    def list_goals(
        self,
        status: Optional[GoalStatus] = None,
        priority: Optional[GoalPriority] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Goal]:
        """List goals with optional filters"""
        goals = list(self.goals.values())

        if status:
            goals = [g for g in goals if g.status == status]

        if priority:
            goals = [g for g in goals if g.priority == priority]

        if tags:
            goals = [g for g in goals if any(tag in g.tags for tag in tags)]

        # Sort by priority and creation date
        priority_order = {
            GoalPriority.CRITICAL: 4,
            GoalPriority.HIGH: 3,
            GoalPriority.MEDIUM: 2,
            GoalPriority.LOW: 1,
        }
        goals.sort(
            key=lambda g: (priority_order[g.priority], g.created_at), reverse=True
        )

        return goals

    def get_active_goals(self) -> List[Goal]:
        """Get all active goals"""
        return self.list_goals(status=GoalStatus.ACTIVE)

    def get_overdue_goals(self) -> List[Goal]:
        """Get overdue goals"""
        now = datetime.now()
        return [
            g
            for g in self.goals.values()
            if g.due_date and g.due_date < now and g.status == GoalStatus.ACTIVE
        ]

    def get_goal_statistics(self) -> Dict[str, Any]:
        """Get goal statistics"""
        total_goals = len(self.goals)
        active_goals = len(
            [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
        )
        completed_goals = len(
            [g for g in self.goals.values() if g.status == GoalStatus.COMPLETED]
        )
        overdue_goals = len(self.get_overdue_goals())

        avg_progress = 0.0
        if active_goals > 0:
            avg_progress = (
                sum(
                    g.progress
                    for g in self.goals.values()
                    if g.status == GoalStatus.ACTIVE
                )
                / active_goals
            )

        return {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "overdue_goals": overdue_goals,
            "completion_rate": completed_goals / total_goals
            if total_goals > 0
            else 0.0,
            "average_progress": avg_progress,
            "total_subtasks": len(self.subtasks),
        }

    async def suggest_next_actions(self) -> List[Dict[str, Any]]:
        """Suggest next actions based on current goals"""
        suggestions = []

        # High priority goals with low progress
        high_priority_goals = [
            g
            for g in self.goals.values()
            if g.priority in [GoalPriority.HIGH, GoalPriority.CRITICAL]
            and g.status == GoalStatus.ACTIVE
            and g.progress < 0.5
        ]

        for goal in high_priority_goals[:3]:  # Top 3
            suggestions.append(
                {
                    "type": "focus_on_goal",
                    "goal_id": goal.id,
                    "title": f"Focus on high-priority goal: {goal.title}",
                    "description": f"This {goal.priority.value} priority goal needs attention",
                    "urgency": "high",
                }
            )

        # Overdue goals
        overdue_goals = self.get_overdue_goals()
        for goal in overdue_goals[:2]:  # Top 2
            suggestions.append(
                {
                    "type": "overdue_goal",
                    "goal_id": goal.id,
                    "title": f"Overdue goal: {goal.title}",
                    "description": f"Due date was {goal.due_date.strftime('%Y-%m-%d')}",
                    "urgency": "critical",
                }
            )

        # Goals with incomplete subtasks
        for goal in self.goals.values():
            if goal.status == GoalStatus.ACTIVE and goal.subtasks:
                incomplete_subtasks = [
                    self.subtasks[st_id]
                    for st_id in goal.subtasks
                    if st_id in self.subtasks and not self.subtasks[st_id].completed
                ]
                if incomplete_subtasks:
                    suggestions.append(
                        {
                            "type": "complete_subtasks",
                            "goal_id": goal.id,
                            "title": f"Complete subtasks for: {goal.title}",
                            "description": f"{len(incomplete_subtasks)} subtasks remaining",
                            "urgency": "medium",
                        }
                    )

        return suggestions

    async def search_goals(self, query: str) -> List[Goal]:
        """Search goals by title, description, or tags"""
        query_lower = query.lower()
        matches = []

        for goal in self.goals.values():
            if (
                query_lower in goal.title.lower()
                or query_lower in goal.description.lower()
                or any(query_lower in tag.lower() for tag in goal.tags)
            ):
                matches.append(goal)

        return matches

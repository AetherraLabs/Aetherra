"""
🎯 Goal Agent
=============

Agent responsible for goal management, tracking, and achievement
within the Aetherra AI OS system.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .agent_base import AgentBase


class GoalAgent(AgentBase):
    """
    Agent for managing goals, objectives, and achievement tracking.

    Handles:
    - Goal creation and management
    - Progress tracking
    - Achievement validation
    - Goal prioritization
    - Milestone management
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize the goal agent.

        Args:
            name: Optional agent name
        """
        super().__init__("goal", name)
        self.active_goals = {}
        self.completed_goals = {}
        self.goal_templates = {}
        self.achievement_metrics = {}
        self._initialize_default_templates()
        self.update_status("ready")

    def can_handle(self, request_type: str) -> bool:
        """Check if this agent can handle the request type."""
        return request_type in [
            "goal_creation",
            "goal_tracking",
            "goal_update",
            "achievement_check",
            "milestone_update",
            "goal_analysis",
        ]

    def get_capabilities(self) -> List[str]:
        """Get list of goal management capabilities."""
        capabilities = super().get_capabilities()
        capabilities.extend(
            [
                "goal_management",
                "progress_tracking",
                "achievement_validation",
                "milestone_management",
                "priority_analysis",
                "success_metrics",
            ]
        )
        return capabilities

    async def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle goal management requests.

        Args:
            request: Goal request data

        Returns:
            Goal management response
        """
        request_type = request.get("type", "goal_tracking")

        if request_type == "goal_creation":
            return await self._create_goal(request)
        elif request_type == "goal_tracking":
            return await self._track_goals(request)
        elif request_type == "goal_update":
            return await self._update_goal(request)
        elif request_type == "achievement_check":
            return await self._check_achievements(request)
        elif request_type == "milestone_update":
            return await self._update_milestone(request)
        elif request_type == "goal_analysis":
            return await self._analyze_goals(request)
        else:
            return await self._get_goal_overview(request)

    async def _create_goal(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new goal."""
        goal_data = request.get("goal", {})

        goal_id = str(uuid.uuid4())
        goal = {
            "id": goal_id,
            "title": goal_data.get("title", "Untitled Goal"),
            "description": goal_data.get("description", ""),
            "priority": goal_data.get("priority", "medium"),
            "category": goal_data.get("category", "general"),
            "target_date": goal_data.get("target_date"),
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "progress": 0,
            "milestones": goal_data.get("milestones", []),
            "success_criteria": goal_data.get("success_criteria", []),
            "metadata": goal_data.get("metadata", {}),
            "agent_id": self.agent_id,
        }

        # Add to active goals
        self.active_goals[goal_id] = goal

        return {
            "success": True,
            "goal_id": goal_id,
            "goal": goal,
            "estimated_completion": self._estimate_completion_time(goal),
            "recommended_actions": self._get_recommended_actions(goal),
            "agent_id": self.agent_id,
        }

    async def _track_goals(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Track progress of goals."""
        goal_id = request.get("goal_id")

        if goal_id and goal_id in self.active_goals:
            goal = self.active_goals[goal_id]
            return {
                "success": True,
                "goal": goal,
                "progress_analysis": self._analyze_progress(goal),
                "next_steps": self._get_next_steps(goal),
                "agent_id": self.agent_id,
            }
        else:
            # Return overview of all active goals
            return {
                "success": True,
                "active_goals": len(self.active_goals),
                "completed_goals": len(self.completed_goals),
                "goals_by_priority": self._count_by_priority(),
                "goals_by_status": self._count_by_status(),
                "recent_activity": self._get_recent_activity(),
                "agent_id": self.agent_id,
            }

    async def _update_goal(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update goal progress or details."""
        goal_id = request.get("goal_id")
        updates = request.get("updates", {})

        if goal_id not in self.active_goals:
            return {
                "success": False,
                "error": f"Goal {goal_id} not found",
                "agent_id": self.agent_id,
            }

        goal = self.active_goals[goal_id]

        # Update fields
        for field, value in updates.items():
            if field in ["title", "description", "priority", "progress", "status"]:
                goal[field] = value
            elif field == "milestones":
                goal["milestones"] = value
            elif field == "metadata":
                goal["metadata"].update(value)

        goal["last_updated"] = datetime.now().isoformat()

        # Check if goal is completed
        if goal.get("progress", 0) >= 100 or goal.get("status") == "completed":
            self._complete_goal(goal_id)

        return {
            "success": True,
            "goal_id": goal_id,
            "updated_goal": goal,
            "progress_change": self._calculate_progress_change(goal, updates),
            "agent_id": self.agent_id,
        }

    async def _check_achievements(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Check and validate achievements."""
        goal_id = request.get("goal_id")

        if goal_id and goal_id in self.active_goals:
            goal = self.active_goals[goal_id]
            achievements = self._evaluate_achievements(goal)

            return {
                "success": True,
                "goal_id": goal_id,
                "achievements": achievements,
                "achievement_score": self._calculate_achievement_score(achievements),
                "recommendations": self._get_achievement_recommendations(
                    goal, achievements
                ),
                "agent_id": self.agent_id,
            }
        else:
            # Check all goals for achievements
            all_achievements = {}
            for gid, goal in self.active_goals.items():
                all_achievements[gid] = self._evaluate_achievements(goal)

            return {
                "success": True,
                "total_achievements": sum(len(a) for a in all_achievements.values()),
                "achievements_by_goal": all_achievements,
                "top_performers": self._get_top_performing_goals(),
                "agent_id": self.agent_id,
            }

    async def _update_milestone(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update milestone status."""
        goal_id = request.get("goal_id")
        milestone_index = request.get("milestone_index")
        milestone_status = request.get("status", "completed")

        if goal_id not in self.active_goals:
            return {
                "success": False,
                "error": f"Goal {goal_id} not found",
                "agent_id": self.agent_id,
            }

        goal = self.active_goals[goal_id]
        milestones = goal.get("milestones", [])

        if milestone_index < 0 or milestone_index >= len(milestones):
            return {
                "success": False,
                "error": "Invalid milestone index",
                "agent_id": self.agent_id,
            }

        # Update milestone
        milestones[milestone_index]["status"] = milestone_status
        milestones[milestone_index]["updated_at"] = datetime.now().isoformat()

        # Recalculate progress based on completed milestones
        completed_milestones = sum(
            1 for m in milestones if m.get("status") == "completed"
        )
        goal["progress"] = (
            (completed_milestones / len(milestones)) * 100 if milestones else 0
        )

        return {
            "success": True,
            "goal_id": goal_id,
            "milestone_updated": milestone_index,
            "new_progress": goal["progress"],
            "milestones_status": self._get_milestone_summary(milestones),
            "agent_id": self.agent_id,
        }

    async def _analyze_goals(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform goal analysis and insights."""
        analysis_type = request.get("analysis_type", "overview")

        if analysis_type == "performance":
            return await self._analyze_performance()
        elif analysis_type == "trends":
            return await self._analyze_trends()
        elif analysis_type == "recommendations":
            return await self._generate_recommendations()
        else:
            return await self._generate_overview_analysis()

    async def _get_goal_overview(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get overall goal management overview."""
        return {
            "success": True,
            "summary": {
                "active_goals": len(self.active_goals),
                "completed_goals": len(self.completed_goals),
                "total_goals": len(self.active_goals) + len(self.completed_goals),
            },
            "progress_overview": self._get_progress_overview(),
            "priority_breakdown": self._count_by_priority(),
            "recent_achievements": self._get_recent_achievements(),
            "agent_id": self.agent_id,
        }

    def _initialize_default_templates(self):
        """Initialize default goal templates."""
        self.goal_templates = {
            "learning": {
                "category": "learning",
                "default_milestones": ["Research", "Practice", "Apply", "Master"],
                "success_criteria": [
                    "Knowledge acquired",
                    "Skills demonstrated",
                    "Application successful",
                ],
            },
            "project": {
                "category": "project",
                "default_milestones": [
                    "Planning",
                    "Development",
                    "Testing",
                    "Deployment",
                ],
                "success_criteria": [
                    "Requirements met",
                    "Quality standards achieved",
                    "Delivery on time",
                ],
            },
            "personal": {
                "category": "personal",
                "default_milestones": [
                    "Goal set",
                    "Progress tracked",
                    "Milestone achieved",
                    "Goal completed",
                ],
                "success_criteria": [
                    "Personal satisfaction",
                    "Objective measures met",
                    "Sustained improvement",
                ],
            },
        }

    def _estimate_completion_time(self, goal: Dict[str, Any]) -> str:
        """Estimate completion time for a goal."""
        milestones = len(goal.get("milestones", []))
        priority = goal.get("priority", "medium")

        base_days = milestones * 7  # 1 week per milestone

        if priority == "high":
            base_days *= 0.7
        elif priority == "low":
            base_days *= 1.5

        return f"approximately {int(base_days)} days"

    def _get_recommended_actions(self, goal: Dict[str, Any]) -> List[str]:
        """Get recommended actions for a goal."""
        actions = ["Define clear success criteria"]

        if not goal.get("milestones"):
            actions.append("Break down into smaller milestones")

        if not goal.get("target_date"):
            actions.append("Set target completion date")

        if goal.get("priority") == "high":
            actions.append("Prioritize in daily planning")

        return actions

    def _analyze_progress(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze progress of a specific goal."""
        progress = goal.get("progress", 0)
        created_at = datetime.fromisoformat(goal["created_at"])
        days_active = (datetime.now() - created_at).days

        return {
            "current_progress": progress,
            "days_active": days_active,
            "average_daily_progress": progress / max(days_active, 1),
            "estimated_completion": self._estimate_remaining_time(goal),
            "momentum": "high"
            if progress > days_active * 2
            else "medium"
            if progress > days_active
            else "low",
        }

    def _get_next_steps(self, goal: Dict[str, Any]) -> List[str]:
        """Get next steps for a goal."""
        milestones = goal.get("milestones", [])

        # Find next incomplete milestone
        for i, milestone in enumerate(milestones):
            if milestone.get("status") != "completed":
                return [
                    f"Complete milestone: {milestone.get('title', f'Milestone {i + 1}')}"
                ]

        # If all milestones complete, final steps
        if goal.get("progress", 0) < 100:
            return ["Finalize goal completion", "Document results", "Mark as completed"]

        return ["Goal appears complete - consider marking as finished"]

    def _complete_goal(self, goal_id: str):
        """Move goal from active to completed."""
        if goal_id in self.active_goals:
            goal = self.active_goals.pop(goal_id)
            goal["completed_at"] = datetime.now().isoformat()
            goal["status"] = "completed"
            self.completed_goals[goal_id] = goal

    def _count_by_priority(self) -> Dict[str, int]:
        """Count goals by priority level."""
        priorities = {"high": 0, "medium": 0, "low": 0}
        for goal in self.active_goals.values():
            priority = goal.get("priority", "medium")
            if priority in priorities:
                priorities[priority] += 1
        return priorities

    def _count_by_status(self) -> Dict[str, int]:
        """Count goals by status."""
        statuses = {}
        for goal in self.active_goals.values():
            status = goal.get("status", "active")
            statuses[status] = statuses.get(status, 0) + 1
        return statuses

    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent goal activity."""
        activities = []

        # Get recently updated goals
        for goal in self.active_goals.values():
            if "last_updated" in goal:
                activities.append(
                    {
                        "type": "update",
                        "goal_id": goal["id"],
                        "goal_title": goal["title"],
                        "timestamp": goal["last_updated"],
                    }
                )

        # Sort by timestamp and return most recent
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:5]

    def _estimate_remaining_time(self, goal: Dict[str, Any]) -> str:
        """Estimate remaining time to complete goal."""
        progress = goal.get("progress", 0)
        if progress >= 100:
            return "completed"

        remaining_progress = 100 - progress
        created_at = datetime.fromisoformat(goal["created_at"])
        days_active = max((datetime.now() - created_at).days, 1)

        daily_rate = progress / days_active
        if daily_rate > 0:
            remaining_days = remaining_progress / daily_rate
            return f"approximately {int(remaining_days)} days"
        else:
            return "unable to estimate - no progress recorded"

    def _evaluate_achievements(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate achievements for a goal."""
        achievements = []

        # Milestone achievements
        milestones = goal.get("milestones", [])
        completed_milestones = [m for m in milestones if m.get("status") == "completed"]

        if completed_milestones:
            achievements.append(
                {
                    "type": "milestones",
                    "description": f"Completed {len(completed_milestones)}/{len(milestones)} milestones",
                    "value": len(completed_milestones),
                }
            )

        # Progress achievements
        progress = goal.get("progress", 0)
        if progress >= 25:
            achievements.append(
                {
                    "type": "progress",
                    "description": f"Reached {progress}% completion",
                    "value": progress,
                }
            )

        return achievements

    def _calculate_achievement_score(self, achievements: List[Dict[str, Any]]) -> int:
        """Calculate overall achievement score."""
        score = 0
        for achievement in achievements:
            if achievement["type"] == "milestones":
                score += achievement["value"] * 20
            elif achievement["type"] == "progress":
                score += achievement["value"]
        return min(score, 100)

    def _get_achievement_recommendations(
        self, goal: Dict[str, Any], achievements: List[Dict[str, Any]]
    ) -> List[str]:
        """Get recommendations based on achievements."""
        recommendations = []

        if not achievements:
            recommendations.append(
                "Focus on completing first milestone to build momentum"
            )

        progress = goal.get("progress", 0)
        if progress < 25:
            recommendations.append(
                "Break down next steps into smaller, actionable tasks"
            )
        elif progress < 75:
            recommendations.append("Maintain current pace and focus on consistency")
        else:
            recommendations.append(
                "Final push - complete remaining tasks to achieve goal"
            )

        return recommendations

    def _get_milestone_summary(
        self, milestones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get summary of milestone status."""
        total = len(milestones)
        completed = sum(1 for m in milestones if m.get("status") == "completed")

        return {
            "total": total,
            "completed": completed,
            "remaining": total - completed,
            "completion_rate": (completed / total) * 100 if total > 0 else 0,
        }

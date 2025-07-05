#!/usr/bin/env python3
"""
🔍 CONTEXT ANALYZER - PHASE 2
=============================

Analyzes user context and activity patterns to understand
current state and predict future needs.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ContextInfo:
    """Information about current user context"""

    primary_activity: str
    focus_level: float  # 0.0 to 1.0
    productivity_score: float  # 0.0 to 1.0
    time_in_state: float  # seconds
    transition_probability: float  # 0.0 to 1.0
    suggested_actions: List[str]


class ContextAnalyzer:
    """Analyzes user context from activity patterns"""

    def __init__(self):
        self.context_cache: Dict[str, Any] = {}
        self.analysis_history: List[ContextInfo] = []

    def analyze_context(
        self,
        recent_activities: List[Dict[str, Any]],
        current_time: Optional[datetime] = None,
    ) -> ContextInfo:
        """Analyze current context from recent activities"""

        if not recent_activities:
            return self._get_default_context()

        current_time = current_time or datetime.now()

        # Extract primary activity
        primary_activity = self._determine_primary_activity(recent_activities)

        # Calculate focus level
        focus_level = self._calculate_focus_level(recent_activities)

        # Calculate productivity score
        productivity_score = self._calculate_productivity_score(recent_activities)

        # Calculate time in current state
        time_in_state = self._calculate_time_in_state(recent_activities, current_time)

        # Calculate transition probability
        transition_probability = self._calculate_transition_probability(
            recent_activities
        )

        # Generate suggested actions
        suggested_actions = self._generate_context_actions(
            primary_activity, focus_level, productivity_score
        )

        context_info = ContextInfo(
            primary_activity=primary_activity,
            focus_level=focus_level,
            productivity_score=productivity_score,
            time_in_state=time_in_state,
            transition_probability=transition_probability,
            suggested_actions=suggested_actions,
        )

        # Cache for future reference
        self.analysis_history.append(context_info)
        if len(self.analysis_history) > 100:
            self.analysis_history = self.analysis_history[-100:]

        return context_info

    def _determine_primary_activity(self, activities: List[Dict[str, Any]]) -> str:
        """Determine the primary activity from recent activities"""

        if not activities:
            return "idle"

        # Count activity types
        activity_counts: Dict[str, int] = {}
        for activity in activities:
            activity_type = activity.get("activity_type", "unknown")
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1

        # Return most frequent activity
        return max(activity_counts.items(), key=lambda x: x[1])[0]

    def _calculate_focus_level(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate focus level based on activity patterns"""

        if not activities:
            return 0.0

        # Factors that indicate focus
        focus_indicators = {
            "single_task_duration": 0.0,
            "activity_consistency": 0.0,
            "intensity_level": 0.0,
        }

        # Single task duration (longer = more focused)
        if len(activities) > 0:
            avg_duration = sum(a.get("duration", 0) for a in activities) / len(
                activities
            )
            focus_indicators["single_task_duration"] = min(
                1.0, avg_duration / 3600
            )  # Normalize to 1 hour

        # Activity consistency (fewer switches = more focused)
        unique_activities = len(set(a.get("activity_type", "") for a in activities))
        total_activities = len(activities)
        if total_activities > 0:
            focus_indicators["activity_consistency"] = 1.0 - (
                unique_activities / total_activities
            )

        # Intensity level
        avg_intensity = sum(a.get("intensity", 0.5) for a in activities) / len(
            activities
        )
        focus_indicators["intensity_level"] = avg_intensity

        # Weighted average
        weights = {
            "single_task_duration": 0.4,
            "activity_consistency": 0.3,
            "intensity_level": 0.3,
        }
        focus_level = sum(focus_indicators[key] * weights[key] for key in weights)

        return max(0.0, min(1.0, focus_level))

    def _calculate_productivity_score(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate productivity score based on activity quality"""

        if not activities:
            return 0.0

        # Productivity factors
        productive_activities = {
            "coding",
            "writing",
            "designing",
            "researching",
            "planning",
        }
        break_activities = {"break", "social", "entertainment"}

        productive_count = 0
        break_count = 0
        total_duration = 0
        productive_duration = 0

        for activity in activities:
            activity_type = activity.get("activity_type", "").lower()
            duration = activity.get("duration", 0)
            intensity = activity.get("intensity", 0.5)

            total_duration += duration

            if any(prod in activity_type for prod in productive_activities):
                productive_count += 1
                productive_duration += duration * intensity
            elif any(brk in activity_type for brk in break_activities):
                break_count += 1

        if len(activities) == 0:
            return 0.0

        # Calculate score components
        activity_ratio = productive_count / len(activities)
        duration_ratio = productive_duration / max(1, total_duration)

        # Penalty for too many breaks
        break_penalty = max(
            0, break_count / len(activities) - 0.3
        )  # Penalty if >30% breaks

        productivity_score = (
            activity_ratio * 0.6 + duration_ratio * 0.4
        ) - break_penalty

        return max(0.0, min(1.0, productivity_score))

    def _calculate_time_in_state(
        self, activities: List[Dict[str, Any]], current_time: datetime
    ) -> float:
        """Calculate how long user has been in current activity state"""

        if not activities:
            return 0.0

        # Find the start of the current activity sequence
        current_activity = activities[-1].get("activity_type", "")
        state_start = None

        for activity in reversed(activities):
            if activity.get("activity_type", "") == current_activity:
                timestamp_str = activity.get("timestamp", "")
                if timestamp_str:
                    try:
                        state_start = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError):
                        pass
            else:
                break

        if state_start:
            return (current_time - state_start).total_seconds()
        else:
            return activities[-1].get("duration", 0)

    def _calculate_transition_probability(
        self, activities: List[Dict[str, Any]]
    ) -> float:
        """Calculate probability of transitioning to a different activity"""

        if len(activities) < 3:
            return 0.5

        # Analyze transition patterns
        transitions = []
        for i in range(1, len(activities)):
            if activities[i].get("activity_type") != activities[i - 1].get(
                "activity_type"
            ):
                transitions.append(i)

        if not transitions:
            return 0.1  # Low probability if no recent transitions

        # Calculate average time between transitions
        time_diffs = []
        for i in range(1, len(transitions)):
            time_diffs.append(transitions[i] - transitions[i - 1])

        if time_diffs:
            avg_transition_interval = sum(time_diffs) / len(time_diffs)
            # More frequent transitions = higher probability
            transition_probability = min(1.0, 1.0 / max(1, avg_transition_interval))
        else:
            transition_probability = 0.3

        return transition_probability

    def _generate_context_actions(
        self, primary_activity: str, focus_level: float, productivity_score: float
    ) -> List[str]:
        """Generate suggested actions based on context"""

        actions = []

        # Focus-based suggestions
        if focus_level < 0.3:
            actions.extend(
                [
                    "Eliminate distractions",
                    "Use focus techniques (Pomodoro, etc.)",
                    "Find a quieter environment",
                ]
            )
        elif focus_level > 0.8:
            actions.extend(
                ["Maintain current focus", "Take short breaks to sustain attention"]
            )

        # Productivity-based suggestions
        if productivity_score < 0.4:
            actions.extend(
                [
                    "Review and prioritize tasks",
                    "Break large tasks into smaller ones",
                    "Consider taking a productive break",
                ]
            )
        elif productivity_score > 0.8:
            actions.extend(["Keep up the great work!", "Document your progress"])

        # Activity-specific suggestions
        activity_suggestions = {
            "coding": ["Consider code reviews", "Write tests", "Document your changes"],
            "research": [
                "Take notes on key findings",
                "Cross-reference sources",
                "Create summary document",
            ],
            "writing": [
                "Review for clarity",
                "Check grammar and style",
                "Get feedback from others",
            ],
            "planning": [
                "Set specific deadlines",
                "Assign priorities",
                "Share plans with team",
            ],
        }

        if primary_activity.lower() in activity_suggestions:
            actions.extend(activity_suggestions[primary_activity.lower()])

        # Remove duplicates and limit
        unique_actions = list(dict.fromkeys(actions))  # Preserves order
        return unique_actions[:5]

    def _get_default_context(self) -> ContextInfo:
        """Return default context when no activity data is available"""

        return ContextInfo(
            primary_activity="idle",
            focus_level=0.0,
            productivity_score=0.0,
            time_in_state=0.0,
            transition_probability=0.5,
            suggested_actions=[
                "Start a productive activity",
                "Set clear goals",
                "Choose your priority task",
            ],
        )

    def get_context_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get context trends over time"""

        if not self.analysis_history:
            return {"trend": "no_data"}

        recent_history = (
            self.analysis_history[-hours:]
            if len(self.analysis_history) > hours
            else self.analysis_history
        )

        # Calculate averages
        avg_focus = sum(c.focus_level for c in recent_history) / len(recent_history)
        avg_productivity = sum(c.productivity_score for c in recent_history) / len(
            recent_history
        )

        # Activity distribution
        activities = [c.primary_activity for c in recent_history]
        activity_counts = {}
        for activity in activities:
            activity_counts[activity] = activity_counts.get(activity, 0) + 1

        return {
            "average_focus": avg_focus,
            "average_productivity": avg_productivity,
            "most_common_activity": max(activity_counts.items(), key=lambda x: x[1])[0]
            if activity_counts
            else "none",
            "activity_distribution": activity_counts,
            "analysis_count": len(recent_history),
        }

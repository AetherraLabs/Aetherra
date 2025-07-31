#!/usr/bin/env python3
"""
Lightweight Goal Tracker
=========================
🎯 Console-based goal tracking with progress indicators and reasoning trails
📊 Simple but effective goal management system
🧠 "Why was this goal created? What's blocking it?" analysis
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class GoalStatus(Enum):
    """Goal status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class GoalPriority(Enum):
    """Goal priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GoalTrigger:
    """What triggered the creation of this goal"""
    trigger_type: str
    description: str
    timestamp: datetime
    confidence: float = 0.8


@dataclass
class GoalBlocker:
    """What's blocking this goal"""
    blocker_type: str
    description: str
    severity: float
    identified_at: datetime
    resolution_plan: str = ""


@dataclass
class GoalMilestone:
    """Goal milestone"""
    id: str
    title: str
    description: str
    target_date: Optional[datetime] = None
    completed: bool = False
    completed_date: Optional[datetime] = None
    progress: float = 0.0


@dataclass
class GoalProgress:
    """Goal progress tracking"""
    current_progress: float = 0.0
    milestones: List[GoalMilestone] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)
    progress_history: List[Tuple[datetime, float]] = field(default_factory=list)
    velocity: float = 0.0
    estimated_completion: Optional[datetime] = None


@dataclass
class GoalReasoning:
    """Goal reasoning trail"""
    creation_reason: str = ""
    triggers: List[GoalTrigger] = field(default_factory=list)
    blockers: List[GoalBlocker] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class Goal:
    """Goal with progress tracking and reasoning"""
    id: str
    title: str
    description: str
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    status: GoalStatus = GoalStatus.ACTIVE
    priority: GoalPriority = GoalPriority.MEDIUM
    target_date: Optional[datetime] = None
    progress: GoalProgress = field(default_factory=lambda: GoalProgress())
    reasoning: GoalReasoning = field(default_factory=lambda: GoalReasoning())
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    parent_goal: Optional[str] = None
    sub_goals: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class GoalTracker:
    """Console-based goal tracker"""

    def __init__(self):
        self.goals = {}
        self.initialize_sample_data()

    def initialize_sample_data(self):
        """Initialize with sample goals"""
        # Create sample goals
        goal1 = Goal(
            id="goal_1",
            title="Complete AI Memory System",
            description="Implement world-class memory management with clustering",
            priority=GoalPriority.HIGH,
            category="development",
            target_date=datetime.now() + timedelta(days=30)
        )

        goal1.reasoning.creation_reason = "Critical component for AI system functionality"
        goal1.reasoning.triggers.append(GoalTrigger(
            trigger_type="system_insight",
            description="Analysis revealed need for better memory management",
            timestamp=datetime.now() - timedelta(days=5)
        ))

        # Add milestones
        milestones = [
            {"title": "Design architecture", "completed": True, "progress": 1.0},
            {"title": "Implement storage", "completed": True, "progress": 1.0},
            {"title": "Add clustering", "completed": False, "progress": 0.7},
            {"title": "System integration", "completed": False, "progress": 0.3}
        ]

        for i, m in enumerate(milestones):
            milestone = GoalMilestone(
                id=f"milestone_{i+1}",
                title=m["title"],
                description=m["title"],
                completed=m["completed"],
                progress=m["progress"]
            )
            goal1.progress.milestones.append(milestone)

        # Goal 2
        goal2 = Goal(
            id="goal_2",
            title="Develop Goal Tracking System",
            description="Create intelligent goal tracking with reasoning trails",
            priority=GoalPriority.MEDIUM,
            category="development",
            target_date=datetime.now() + timedelta(days=20)
        )

        goal2.reasoning.creation_reason = "Need better visibility into goal progress"
        goal2.reasoning.triggers.append(GoalTrigger(
            trigger_type="user_request",
            description="User requested enhanced goal tracking",
            timestamp=datetime.now() - timedelta(days=3)
        ))

        # Add a blocker
        goal2.reasoning.blockers.append(GoalBlocker(
            blocker_type="resource",
            description="Waiting for UI design approval",
            severity=0.6,
            identified_at=datetime.now() - timedelta(days=1)
        ))

        # Add milestones
        milestones2 = [
            {"title": "Design data structure", "completed": True, "progress": 1.0},
            {"title": "Implement tracking", "completed": False, "progress": 0.8},
            {"title": "Add reasoning", "completed": False, "progress": 0.5},
            {"title": "Create interface", "completed": False, "progress": 0.6}
        ]

        for i, m in enumerate(milestones2):
            milestone = GoalMilestone(
                id=f"milestone_{i+1}",
                title=m["title"],
                description=m["title"],
                completed=m["completed"],
                progress=m["progress"]
            )
            goal2.progress.milestones.append(milestone)

        self.goals["goal_1"] = goal1
        self.goals["goal_2"] = goal2

        # Update progress
        self.update_all_progress()

    def update_all_progress(self):
        """Update progress for all goals"""
        for goal in self.goals.values():
            self.update_goal_progress(goal)

    def update_goal_progress(self, goal: Goal):
        """Update goal progress based on milestones"""
        if not goal.progress.milestones:
            return

        # Calculate progress
        milestone_progress = sum(m.progress for m in goal.progress.milestones)
        goal.progress.current_progress = milestone_progress / len(goal.progress.milestones)

        # Update history
        goal.progress.progress_history.append((datetime.now(), goal.progress.current_progress))
        goal.progress.last_update = datetime.now()

        # Calculate velocity
        if len(goal.progress.progress_history) > 1:
            recent = goal.progress.progress_history[-5:]  # Last 5 updates
            if len(recent) >= 2:
                time_span = (recent[-1][0] - recent[0][0]).total_seconds() / 86400  # Days
                progress_change = recent[-1][1] - recent[0][1]
                if time_span > 0:
                    goal.progress.velocity = progress_change / time_span

        # Estimate completion
        if goal.progress.velocity > 0:
            remaining = 1.0 - goal.progress.current_progress
            days_remaining = remaining / goal.progress.velocity
            goal.progress.estimated_completion = datetime.now() + timedelta(days=days_remaining)

    def show_progress_bar(self, progress: float, width: int = 30) -> str:
        """Create a text progress bar"""
        filled = int(progress * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {progress:.1%}"

    def display_goal_list(self):
        """Display all goals with progress indicators"""
        print("\n🎯 World-Class Goal Tracker")
        print("=" * 50)

        active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
        completed_goals = [g for g in self.goals.values() if g.status == GoalStatus.COMPLETED]

        print(f"📊 Status: {len(active_goals)} active • {len(completed_goals)} completed\n")

        for goal in active_goals:
            # Priority indicator
            priority_icons = {
                GoalPriority.CRITICAL: "🔴",
                GoalPriority.HIGH: "🟠",
                GoalPriority.MEDIUM: "🟡",
                GoalPriority.LOW: "🟢"
            }

            # Blocker indicator
            blocker_icon = "🚫" if goal.reasoning.blockers else "✅"

            print(f"{priority_icons[goal.priority]} {goal.title}")
            print(f"   Progress: {self.show_progress_bar(goal.progress.current_progress)}")
            print(f"   Status: {blocker_icon} {goal.status.value.title()}")
            print(f"   Velocity: {goal.progress.velocity:.3f}/day")

            if goal.progress.estimated_completion:
                days_left = (goal.progress.estimated_completion - datetime.now()).days
                print(f"   Est. completion: {goal.progress.estimated_completion.strftime('%Y-%m-%d')} ({days_left} days)")

            print()

    def show_goal_details(self, goal_id: str):
        """Show detailed goal information"""
        if goal_id not in self.goals:
            print(f"❌ Goal {goal_id} not found")
            return

        goal = self.goals[goal_id]

        print(f"\n🎯 Goal Details: {goal.title}")
        print("=" * 60)

        # Basic information
        print(f"📋 Description: {goal.description}")
        print(f"📅 Created: {goal.created.strftime('%Y-%m-%d %H:%M')}")
        print(f"🎯 Target: {goal.target_date.strftime('%Y-%m-%d') if goal.target_date else 'No target'}")
        print(f"⚡ Priority: {goal.priority.value.title()}")
        print(f"📂 Category: {goal.category}")
        print(f"📊 Progress: {self.show_progress_bar(goal.progress.current_progress)}")

        # Reasoning trail
        print(f"\n🧠 Reasoning Trail:")
        print(f"   Creation Reason: {goal.reasoning.creation_reason}")

        # Triggers
        print(f"\n⚡ Triggers ({len(goal.reasoning.triggers)}):")
        for trigger in goal.reasoning.triggers:
            print(f"   • {trigger.trigger_type.title()}: {trigger.description}")
            print(f"     Timestamp: {trigger.timestamp.strftime('%Y-%m-%d %H:%M')}")

        # Blockers
        print(f"\n🚫 Blockers ({len(goal.reasoning.blockers)}):")
        if goal.reasoning.blockers:
            for blocker in goal.reasoning.blockers:
                print(f"   • {blocker.blocker_type.title()}: {blocker.description}")
                print(f"     Severity: {blocker.severity:.1%}")
                print(f"     Identified: {blocker.identified_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("   ✅ No blockers identified!")

        # Milestones
        print(f"\n🎯 Milestones ({len(goal.progress.milestones)}):")
        for milestone in goal.progress.milestones:
            status = "✅" if milestone.completed else "⏳"
            print(f"   {status} {milestone.title}: {self.show_progress_bar(milestone.progress, 20)}")

        print()

    def analyze_blockers(self):
        """Analyze blockers across all goals"""
        print("\n🔍 Blocker Analysis Report")
        print("=" * 40)

        total_blockers = 0
        goals_with_blockers = []

        for goal in self.goals.values():
            if goal.status == GoalStatus.ACTIVE:
                # Auto-identify potential blockers
                new_blockers = self.identify_potential_blockers(goal)

                # Add to goal
                for blocker in new_blockers:
                    if not any(b.description == blocker.description for b in goal.reasoning.blockers):
                        goal.reasoning.blockers.append(blocker)

                if goal.reasoning.blockers:
                    goals_with_blockers.append(goal)
                    total_blockers += len(goal.reasoning.blockers)

        if total_blockers == 0:
            print("✅ No blockers found! All goals are clear to proceed.")
        else:
            print(f"📊 Total blockers: {total_blockers}")
            print(f"🎯 Goals affected: {len(goals_with_blockers)}")

            # Show detailed blockers
            for goal in goals_with_blockers:
                print(f"\n🎯 {goal.title}:")
                for blocker in goal.reasoning.blockers:
                    print(f"   🚫 {blocker.blocker_type.title()}: {blocker.description}")
                    print(f"      Severity: {blocker.severity:.1%}")

        print()

    def identify_potential_blockers(self, goal: Goal) -> List[GoalBlocker]:
        """Identify potential blockers for a goal"""
        blockers = []
        now = datetime.now()

        # Check for overdue milestones
        for milestone in goal.progress.milestones:
            if milestone.target_date and milestone.target_date < now and not milestone.completed:
                blockers.append(GoalBlocker(
                    blocker_type="deadline",
                    description=f"Milestone '{milestone.title}' is overdue",
                    severity=0.8,
                    identified_at=now
                ))

        # Check for slow progress
        if goal.progress.velocity < 0.01:
            blockers.append(GoalBlocker(
                blocker_type="progress",
                description="Progress velocity is very low",
                severity=0.6,
                identified_at=now
            ))

        # Check for stalled milestones
        incomplete_milestones = [m for m in goal.progress.milestones if not m.completed]
        if incomplete_milestones:
            stalled = [m for m in incomplete_milestones if m.progress < 0.1]
            if len(stalled) > 1:
                blockers.append(GoalBlocker(
                    blocker_type="execution",
                    description=f"{len(stalled)} milestones show no progress",
                    severity=0.5,
                    identified_at=now
                ))

        return blockers

    def show_progress_analytics(self):
        """Show progress analytics"""
        print("\n📊 Progress Analytics")
        print("=" * 30)

        active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]

        if not active_goals:
            print("No active goals to analyze.")
            return

        # Calculate statistics
        total_progress = sum(g.progress.current_progress for g in active_goals)
        avg_progress = total_progress / len(active_goals)

        high_progress = [g for g in active_goals if g.progress.current_progress >= 0.8]
        low_progress = [g for g in active_goals if g.progress.current_progress < 0.3]

        print(f"Active Goals: {len(active_goals)}")
        print(f"Average Progress: {avg_progress:.1%}")
        print(f"High Progress (≥80%): {len(high_progress)}")
        print(f"Low Progress (<30%): {len(low_progress)}")

        print(f"\nGoal Progress Details:")
        for goal in active_goals:
            print(f"  • {goal.title}: {goal.progress.current_progress:.1%}")
            print(f"    Velocity: {goal.progress.velocity:.3f}/day")
            if goal.progress.estimated_completion:
                days_left = (goal.progress.estimated_completion - datetime.now()).days
                print(f"    Est. completion: {days_left} days")

        print()

    def create_goal(self, title: str, description: str, priority: str = "medium", category: str = "general"):
        """Create a new goal interactively"""
        goal_id = f"goal_{len(self.goals) + 1}"

        goal = Goal(
            id=goal_id,
            title=title,
            description=description,
            priority=GoalPriority(priority),
            category=category,
            target_date=datetime.now() + timedelta(days=30)
        )

        # Get creation reason
        reason = input("💭 Why is this goal being created? ")
        goal.reasoning.creation_reason = reason

        # Get trigger information
        trigger_type = input("⚡ What triggered this goal? (user_request/system_insight/deadline/opportunity): ")
        trigger_desc = input("📝 Describe the trigger: ")

        goal.reasoning.triggers.append(GoalTrigger(
            trigger_type=trigger_type,
            description=trigger_desc,
            timestamp=datetime.now()
        ))

        # Add initial milestone
        initial_milestone = GoalMilestone(
            id="milestone_1",
            title="Goal created",
            description="Initial goal setup",
            completed=True,
            progress=1.0
        )
        goal.progress.milestones.append(initial_milestone)

        self.goals[goal_id] = goal
        self.update_goal_progress(goal)

        print(f"✅ Goal created: {title}")
        return goal_id

    def interactive_menu(self):
        """Interactive menu system"""
        while True:
            print("\n🎯 World-Class Goal Tracker")
            print("=" * 30)
            print("1. 📋 Show all goals")
            print("2. 🔍 Show goal details")
            print("3. 🎯 Create new goal")
            print("4. 📊 Progress analytics")
            print("5. 🚫 Analyze blockers")
            print("6. 📈 Update progress")
            print("7. ❌ Exit")

            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                self.display_goal_list()
            elif choice == "2":
                goal_id = input("Enter goal ID (goal_1, goal_2, etc.): ").strip()
                self.show_goal_details(goal_id)
            elif choice == "3":
                title = input("Goal title: ").strip()
                description = input("Description: ").strip()
                priority = input("Priority (low/medium/high/critical): ").strip() or "medium"
                category = input("Category: ").strip() or "general"
                self.create_goal(title, description, priority, category)
            elif choice == "4":
                self.show_progress_analytics()
            elif choice == "5":
                self.analyze_blockers()
            elif choice == "6":
                self.update_all_progress()
                print("✅ Progress updated for all goals")
            elif choice == "7":
                print("👋 Thanks for using World-Class Goal Tracker!")
                break
            else:
                print("❌ Invalid choice. Please try again.")


def main():
    """Main application entry point"""
    print("🎯 Welcome to World-Class Goal Tracker!")
    print("Features:")
    print("• 📊 Interactive progress indicators")
    print("• 🧠 Reasoning trails for each goal")
    print("• 🔍 Intelligent blocker analysis")
    print("• 📈 Progress analytics and velocity tracking")
    print("• 🎯 Milestone management")

    tracker = GoalTracker()

    # Quick demo
    print("\n🚀 Quick Demo:")
    tracker.display_goal_list()
    tracker.analyze_blockers()
    tracker.show_progress_analytics()

    # Interactive mode
    response = input("\nEnter interactive mode? (y/n): ").strip().lower()
    if response == 'y':
        tracker.interactive_menu()


if __name__ == "__main__":
    main()

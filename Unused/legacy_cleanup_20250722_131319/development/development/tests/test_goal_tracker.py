#!/usr/bin/env python3
"""
Goal Tracker Testing Suite
==========================
🎯 Test and demonstrate the World-Class Goal Tracker
📊 Validate progress indicators and reasoning trails
🧠 Test blocker analysis and goal intelligence
"""

import sys
import time
from datetime import datetime, timedelta

# Import the lightweight goal tracker
from lightweight_goal_tracker import GoalTracker, Goal, GoalStatus, GoalPriority, GoalMilestone, GoalBlocker, GoalTrigger


def test_goal_tracker():
    """Test the goal tracker functionality"""
    print("🎯 Testing World-Class Goal Tracker")
    print("=" * 50)

    # Create tracker
    tracker = GoalTracker()

    # Test 1: Display goals
    print("\n1. Testing goal display:")
    tracker.display_goal_list()

    # Test 2: Show goal details
    print("\n2. Testing goal details:")
    tracker.show_goal_details("goal_1")

    # Test 3: Progress analytics
    print("\n3. Testing progress analytics:")
    tracker.show_progress_analytics()

    # Test 4: Blocker analysis
    print("\n4. Testing blocker analysis:")
    tracker.analyze_blockers()

    # Test 5: Create new goal
    print("\n5. Testing goal creation:")
    new_goal = Goal(
        id="goal_test",
        title="Test Goal Creation",
        description="Test the goal creation functionality",
        priority=GoalPriority.HIGH,
        category="testing"
    )

    new_goal.reasoning.creation_reason = "Testing the goal creation system"
    new_goal.reasoning.triggers.append(GoalTrigger(
        trigger_type="system_test",
        description="Automated test trigger",
        timestamp=datetime.now()
    ))

    # Add test milestones
    milestones = [
        {"title": "Initialize test", "completed": True, "progress": 1.0},
        {"title": "Run test cases", "completed": False, "progress": 0.6},
        {"title": "Validate results", "completed": False, "progress": 0.2}
    ]

    for i, m in enumerate(milestones):
        milestone = GoalMilestone(
            id=f"test_milestone_{i+1}",
            title=m["title"],
            description=m["title"],
            completed=m["completed"],
            progress=m["progress"]
        )
        new_goal.progress.milestones.append(milestone)

    tracker.goals["goal_test"] = new_goal
    tracker.update_goal_progress(new_goal)

    print("✅ Test goal created successfully!")

    # Test 6: Show updated goal list
    print("\n6. Testing updated goal list:")
    tracker.display_goal_list()

    # Test 7: Test new goal details
    print("\n7. Testing new goal details:")
    tracker.show_goal_details("goal_test")

    print("\n✅ All tests completed successfully!")
    return True


def demonstration_mode():
    """Run interactive demonstration"""
    print("\n🚀 World-Class Goal Tracker Demonstration")
    print("=" * 50)

    tracker = GoalTracker()

    print("This demonstration showcases the key features:")
    print("• Progress indicators with visual bars")
    print("• Reasoning trails (why goals were created)")
    print("• Blocker analysis (what's preventing progress)")
    print("• Progress analytics and velocity tracking")

    # Demo 1: Goal overview
    print("\n📊 DEMO 1: Goal Overview")
    print("-" * 25)
    tracker.display_goal_list()

    input("\nPress Enter to continue...")

    # Demo 2: Detailed goal analysis
    print("\n🎯 DEMO 2: Detailed Goal Analysis")
    print("-" * 35)
    print("Let's examine a specific goal in detail:")
    tracker.show_goal_details("goal_1")

    input("\nPress Enter to continue...")

    # Demo 3: Reasoning trail demonstration
    print("\n🧠 DEMO 3: Reasoning Trail Intelligence")
    print("-" * 40)
    print("This shows WHY each goal was created and what triggered it:")

    for goal_id, goal in tracker.goals.items():
        print(f"\n🎯 {goal.title}:")
        print(f"   💭 Why created: {goal.reasoning.creation_reason}")

        for trigger in goal.reasoning.triggers:
            print(f"   ⚡ Trigger: {trigger.trigger_type} - {trigger.description}")

    input("\nPress Enter to continue...")

    # Demo 4: Blocker analysis
    print("\n🚫 DEMO 4: Intelligent Blocker Analysis")
    print("-" * 40)
    print("This identifies what's blocking goal progress:")
    tracker.analyze_blockers()

    input("\nPress Enter to continue...")

    # Demo 5: Progress analytics
    print("\n📈 DEMO 5: Progress Analytics")
    print("-" * 30)
    print("This provides insights into goal progress and velocity:")
    tracker.show_progress_analytics()

    input("\nPress Enter to continue...")

    # Demo 6: Create new goal demonstration
    print("\n🎯 DEMO 6: Goal Creation with Reasoning")
    print("-" * 40)

    # Create a demo goal
    demo_goal = Goal(
        id="demo_goal",
        title="Demonstrate Goal Tracker Features",
        description="Show how the goal tracker captures reasoning and tracks progress",
        priority=GoalPriority.HIGH,
        category="demonstration"
    )

    demo_goal.reasoning.creation_reason = "Demonstrate the reasoning trail feature to show why goals are created"
    demo_goal.reasoning.triggers.append(GoalTrigger(
        trigger_type="demonstration",
        description="User requested demonstration of goal tracker capabilities",
        timestamp=datetime.now()
    ))

    # Add demo milestones
    demo_milestones = [
        {"title": "Setup demonstration", "completed": True, "progress": 1.0},
        {"title": "Show key features", "completed": False, "progress": 0.8},
        {"title": "Collect feedback", "completed": False, "progress": 0.1}
    ]

    for i, m in enumerate(demo_milestones):
        milestone = GoalMilestone(
            id=f"demo_milestone_{i+1}",
            title=m["title"],
            description=m["title"],
            completed=m["completed"],
            progress=m["progress"]
        )
        demo_goal.progress.milestones.append(milestone)

    tracker.goals["demo_goal"] = demo_goal
    tracker.update_goal_progress(demo_goal)

    print("✅ Created demonstration goal!")
    print("\nHere's how it appears in the system:")
    tracker.show_goal_details("demo_goal")

    print("\n🎉 Demonstration complete!")
    print("The World-Class Goal Tracker provides:")
    print("✅ Visual progress indicators")
    print("✅ Reasoning trails for each goal")
    print("✅ Intelligent blocker analysis")
    print("✅ Progress analytics and velocity tracking")
    print("✅ Milestone management")


def quick_test():
    """Quick functionality test"""
    print("⚡ Quick Test Mode")
    print("=" * 20)

    tracker = GoalTracker()

    # Test core functionality
    print("✅ Goal tracker initialized")
    print(f"✅ {len(tracker.goals)} sample goals loaded")

    # Test progress calculation
    for goal in tracker.goals.values():
        print(f"✅ Goal '{goal.title}': {goal.progress.current_progress:.1%} complete")

    # Test blocker analysis
    print("\n🔍 Running blocker analysis...")
    tracker.analyze_blockers()

    # Test analytics
    print("\n📊 Running progress analytics...")
    tracker.show_progress_analytics()

    print("\n✅ All core functionality working!")


def main():
    """Main test application"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == "test":
            test_goal_tracker()
        elif mode == "demo":
            demonstration_mode()
        elif mode == "quick":
            quick_test()
        else:
            print("Usage: python test_goal_tracker.py [test|demo|quick]")
    else:
        print("🎯 World-Class Goal Tracker Test Suite")
        print("=" * 45)
        print("Choose a mode:")
        print("1. Full test suite")
        print("2. Interactive demonstration")
        print("3. Quick test")
        print("4. Interactive goal tracker")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            test_goal_tracker()
        elif choice == "2":
            demonstration_mode()
        elif choice == "3":
            quick_test()
        elif choice == "4":
            tracker = GoalTracker()
            tracker.interactive_menu()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script for the real goal manager
"""

try:
    from Aetherra.lyrixa.gui.real_goal_manager import RealGoalManager
    print('✅ Import worked')

    mgr = RealGoalManager()
    print('✅ Goal manager created')

    print(f'Status: {"✅ Connected to real goals" if mgr.is_connected else "[ERROR] Not connected to real goals - using fallback data"}')

    # Test current goals
    current_goals = mgr.get_current_goals()
    print(f'Found {len(current_goals)} current goals')

    if current_goals:
        print('\nCurrent Goals Summary:')
        for goal in current_goals:
            title = goal.get('title', 'Unknown')
            priority = goal.get('priority', 'medium')
            progress = goal.get('progress', 0.0)
            print(f"  - {title}: {priority} priority ({progress:.1%} complete)")

    # Test predicted goals
    predicted_goals = mgr.get_predicted_goals()
    print(f'\nFound {len(predicted_goals)} predicted goals')

    if predicted_goals:
        print('\nPredicted Goals Summary:')
        for goal in predicted_goals:
            title = goal.get('title', 'Unknown')
            confidence = goal.get('confidence', 0.0)
            priority = goal.get('priority', 'medium')
            print(f"  - {title}: {confidence:.1%} confidence, {priority} priority")

    # Test goal details
    if current_goals:
        first_goal_id = current_goals[0].get('id')
        print(f'\nDetailed info for goal "{first_goal_id}":')
        details = mgr.get_goal_details(first_goal_id)
        print(f"  Description: {details.get('description', 'N/A')}")
        print(f"  Status: {details.get('status', 'N/A')}")
        print(f"  Created: {details.get('created_at', 'N/A')}")

    # Test statistics
    stats = mgr.get_goal_statistics()
    print(f'\nGoal Statistics:')
    print(f"  Total: {stats.get('total_goals', 0)}")
    print(f"  Active: {stats.get('active_goals', 0)}")
    print(f"  Completed: {stats.get('completed_goals', 0)}")
    print(f"  Average Progress: {stats.get('average_progress', 0.0):.1%}")

except Exception as e:
    print(f'[ERROR] Error: {e}')
    import traceback
    traceback.print_exc()

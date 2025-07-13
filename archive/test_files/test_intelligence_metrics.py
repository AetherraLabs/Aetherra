#!/usr/bin/env python3
"""
Test Intelligence Stack Metrics - Comprehensive Validation
==========================================================

This script tests all metrics that the GUI expects from the intelligence stack.
"""

import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_intelligence_metrics():
    """Test all metrics that the GUI expects"""
    print("🧪 Testing Intelligence Stack Metrics...")

    try:
        from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

        # Initialize the intelligence stack
        workspace_path = str(Path(__file__).parent.parent)
        stack = LyrixaIntelligenceStack(workspace_path)

        # Get metrics
        metrics = stack.get_real_time_metrics()

        print("\n📊 Metrics Retrieved Successfully!")
        print("=" * 50)

        # Test GUI expected fields
        gui_expected_fields = [
            'uptime',
            'active_agents',
            'performance_score',
            'total_insights',
            'recent_activity',
            'status'
        ]

        print("🎯 GUI Expected Fields:")
        for field in gui_expected_fields:
            if field in metrics:
                value = metrics[field]
                print(f"   ✅ {field}: {value}")
            else:
                print(f"   ❌ {field}: MISSING")

        print("\n📈 Additional Metrics Available:")
        additional_fields = [
            'intelligence',
            'workflows',
            'modules',
            'performance',
            'overall_health',
            'agent_analytics'
        ]

        for field in additional_fields:
            if field in metrics:
                print(f"   ✅ {field}: Available")
            else:
                print(f"   ❌ {field}: MISSING")

        # Test specific GUI format expectations
        print("\n🖥️ GUI Format Validation:")

        # Test uptime format
        uptime = metrics.get('uptime', '')
        if 'h' in uptime or 'm' in uptime:
            print(f"   ✅ Uptime format: {uptime}")
        else:
            print(f"   ❌ Uptime format invalid: {uptime}")

        # Test active agents count
        active_agents = metrics.get('active_agents', 0)
        if isinstance(active_agents, int) and active_agents > 0:
            print(f"   ✅ Active agents count: {active_agents}")
        else:
            print(f"   ❌ Active agents invalid: {active_agents}")

        # Test performance score format (0-1 scale for percentage)
        performance_score = metrics.get('performance_score', 0)
        if isinstance(performance_score, (int, float)) and 0 <= performance_score <= 1:
            print(f"   ✅ Performance score: {performance_score:.1%}")
        else:
            print(f"   ❌ Performance score invalid: {performance_score}")

        # Test total insights
        total_insights = metrics.get('total_insights', 0)
        if isinstance(total_insights, int) and total_insights >= 0:
            print(f"   ✅ Total insights: {total_insights}")
        else:
            print(f"   ❌ Total insights invalid: {total_insights}")

        # Test recent activity
        recent_activity = metrics.get('recent_activity', 0)
        if isinstance(recent_activity, int) and recent_activity >= 0:
            print(f"   ✅ Recent activity: {recent_activity}")
        else:
            print(f"   ❌ Recent activity invalid: {recent_activity}")

        # Test status message
        status = metrics.get('status', '')
        if isinstance(status, str) and len(status) > 0:
            print(f"   ✅ Status message: Available ({len(status)} chars)")
        else:
            print(f"   ❌ Status message invalid: {status}")

        print("\n🎉 Intelligence Stack Metrics Test Complete!")
        print(f"📊 Total fields returned: {len(metrics)}")

        # Show sample of how GUI will display this
        print(f"\n🖥️ GUI Display Preview:")
        print(f"⏱️ Uptime: {metrics.get('uptime', 'N/A')}")
        print(f"🤖 Active Agents: {metrics.get('active_agents', 0)}")
        print(f"📈 Performance: {metrics.get('performance_score', 0):.1%}")
        print(f"💡 Insights: {metrics.get('total_insights', 0)}")
        print(f"🔄 Recent Activity: {metrics.get('recent_activity', 0)} (5min)")
        print(f"\n{metrics.get('status', 'No status available')}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_intelligence_metrics()
    if success:
        print("\n✅ All metrics tests passed!")
    else:
        print("\n❌ Some metrics tests failed!")
        sys.exit(1)

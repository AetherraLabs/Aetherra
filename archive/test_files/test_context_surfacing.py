#!/usr/bin/env python3
"""
Test the context-aware surfacing system
"""


def test_context_aware_surfacing():
    """Test the context-aware surfacing functionality"""
    print("🔍 Testing context-aware surfacing...")

    try:
        from lyrixa.plugins.context_aware_surfacing import (
            ContextAwareSurfacing,
            capture_context,
            get_recommendations,
        )

        print("✅ Imports successful")

        # Test instantiation
        surfacing = ContextAwareSurfacing()
        print("✅ ContextAwareSurfacing instantiated successfully")

        # Test context capture
        context = capture_context(
            active_files=["test.py", "data.csv"],
            current_task="data processing",
            user_input="analyze csv file",
        )
        print("✅ Context captured successfully")

        # Test recommendations
        recommendations = get_recommendations(context, limit=5)
        print(f"✅ Got {len(recommendations)} recommendations")

        # Print sample recommendations
        if recommendations:
            print("\n📋 Sample recommendations:")
            for i, rec in enumerate(recommendations[:3]):
                print(
                    f"   {i + 1}. {rec['plugin']} (score: {rec['score']:.1f}) - {rec['reason']}"
                )

        # Test plugin usage recording
        surfacing.record_plugin_usage(
            plugin_name="csv_processor",
            context=context,
            success=True,
            execution_time=1.5,
        )
        print("✅ Plugin usage recorded successfully")

        # Test insights
        insights = surfacing.get_contextual_insights()
        print(f"✅ Got insights: {insights['total_contexts']} contexts tracked")

        print("\n🎉 All context-aware surfacing tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_context_aware_surfacing()
    if success:
        print("\n✅ Context-aware surfacing is working correctly!")
    else:
        print("\n❌ Context-aware surfacing test failed!")

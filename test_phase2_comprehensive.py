#!/usr/bin/env python3
"""
🚀 PHASE 2 TEST SUITE
====================

Test all Phase 2 components: Anticipation Engine, Context Analyzer,
Suggestion Generator, and Proactive Assistant.
"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_phase2_components():
    """Test all Phase 2 components"""

    print("🚀 TESTING PHASE 2 COMPONENTS")
    print("=" * 50)

    # Test 1: Import all modules
    print("\n1. Testing imports...")
    try:
        from lyrixa.anticipation.context_analyzer import ContextAnalyzer
        from lyrixa.anticipation.proactive_assistant import ProactiveAssistant
        from lyrixa.anticipation.suggestion_generator import SuggestionGenerator
        from lyrixa.core.anticipation_engine import AnticipationEngine

        print("   ✅ All Phase 2 modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

    # Test 2: Initialize components
    print("\n2. Testing component initialization...")
    try:
        anticipation_engine = AnticipationEngine()
        context_analyzer = ContextAnalyzer()
        suggestion_generator = SuggestionGenerator()
        proactive_assistant = ProactiveAssistant()
        print("   ✅ All components initialized successfully")
    except Exception as e:
        print(f"   ❌ Initialization error: {e}")
        return False

    # Test 3: Context Analysis
    print("\n3. Testing context analysis...")
    try:
        mock_activities = [
            {
                "activity_type": "coding",
                "timestamp": "2024-12-31T10:00:00",
                "duration": 1800,
                "intensity": 0.8,
                "context": {"language": "python", "project": "ai_assistant"},
            },
            {
                "activity_type": "research",
                "timestamp": "2024-12-31T10:30:00",
                "duration": 900,
                "intensity": 0.6,
                "context": {"topic": "machine_learning"},
            },
        ]

        context_info = context_analyzer.analyze_context(mock_activities)
        print(f"   📊 Primary activity: {context_info.primary_activity}")
        print(f"   📊 Focus level: {context_info.focus_level:.2f}")
        print(f"   📊 Productivity score: {context_info.productivity_score:.2f}")
        print("   ✅ Context analysis working")
    except Exception as e:
        print(f"   ❌ Context analysis error: {e}")
        return False

    # Test 4: Suggestion Generation
    print("\n4. Testing suggestion generation...")
    try:
        context_dict = {
            "primary_activity": "coding",
            "focus_level": 0.7,
            "productivity_score": 0.8,
            "time_in_state": 1800,
            "activity_count": 2,
        }

        suggestions = suggestion_generator.generate_suggestions(
            context=context_dict, activity_history=mock_activities, max_suggestions=2
        )

        print(f"   💡 Generated {len(suggestions)} suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(
                f"      {i}. {suggestion['title']} (confidence: {suggestion.get('confidence', 0):.2f})"
            )
        print("   ✅ Suggestion generation working")
    except Exception as e:
        print(f"   ❌ Suggestion generation error: {e}")
        return False

    # Test 5: Anticipation Engine Activity Tracking
    print("\n5. Testing anticipation engine...")
    try:
        activity_id = await anticipation_engine.track_activity(
            activity_type="testing",
            context={"test": "phase2"},
            duration=300,
            intensity=0.5,
        )
        print(f"   📝 Tracked activity: {activity_id[:8]}...")

        suggestions = await anticipation_engine.get_active_suggestions()
        print(f"   💡 Active suggestions: {len(suggestions)}")
        print("   ✅ Anticipation engine working")
    except Exception as e:
        print(f"   ❌ Anticipation engine error: {e}")
        return False

    # Test 6: Proactive Assistant
    print("\n6. Testing proactive assistant...")
    try:
        assistant = ProactiveAssistant(anticipation_engine=anticipation_engine)
        context_summary = assistant.get_current_context_summary()
        print(f"   🤖 Context status: {context_summary.get('status', 'active')}")

        metrics = assistant.get_performance_metrics()
        print(f"   📊 Suggestions generated: {metrics['suggestions_generated']}")
        print("   ✅ Proactive assistant working")
    except Exception as e:
        print(f"   ❌ Proactive assistant error: {e}")
        return False

    # Test 7: Integration Test
    print("\n7. Testing component integration...")
    try:
        # Simulate a small workflow
        for i in range(3):
            await anticipation_engine.track_activity(
                activity_type=f"task_{i}",
                context={"step": i},
                duration=600,
                intensity=0.7,
            )

        # Get suggestions
        current_suggestions = await anticipation_engine.get_active_suggestions()
        print(
            f"   🔗 Integration test: {len(current_suggestions)} suggestions generated"
        )

        # Test analytics
        analytics = await anticipation_engine.get_analytics_summary()
        print(
            f"   📈 Total activities tracked: {analytics['activity_tracking']['total_activities']}"
        )
        print("   ✅ Integration test successful")
    except Exception as e:
        print(f"   ❌ Integration test error: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 ALL PHASE 2 TESTS PASSED!")
    print("✅ Anticipation Engine: Operational")
    print("✅ Context Analyzer: Functional")
    print("✅ Suggestion Generator: Working")
    print("✅ Proactive Assistant: Ready")
    print("✅ Component Integration: Successful")
    print("\n🚀 Phase 2 is ready for deployment!")

    return True


if __name__ == "__main__":
    success = asyncio.run(test_phase2_components())
    sys.exit(0 if success else 1)

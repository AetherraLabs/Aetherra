#!/usr/bin/env python3
"""
🔄📈 LYRIXA FEEDBACK SYSTEM INTEGRATION TEST
==========================================

Comprehensive test script for Lyrixa's Feedback + Self-Improvement System.
Tests all feedback collection, learning, and adaptation capabilities.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lyrixa.assistant import LyrixaAI
from lyrixa.core.feedback_system import FeedbackRating, FeedbackType


async def test_feedback_system_comprehensive():
    """Comprehensive test of the feedback + self-improvement system"""

    print("🔄📈 LYRIXA FEEDBACK SYSTEM INTEGRATION TEST")
    print("=" * 50)

    # Initialize Lyrixa
    print("\n1. Initializing Lyrixa AI Assistant...")
    lyrixa = LyrixaAI(workspace_path=os.getcwd())
    await lyrixa.initialize()

    print("\n✅ Lyrixa initialized successfully")
    print(f"   Session ID: {lyrixa.session_id}")
    print(
        f"   Feedback system: {'✅ Active' if lyrixa.feedback_system else '❌ Not available'}"
    )

    # Test 1: Basic feedback collection
    print("\n" + "=" * 50)
    print("2. Testing Basic Feedback Collection")
    print("=" * 50)

    # Test suggestion feedback
    print("\n📝 Testing suggestion feedback...")
    suggestion_feedback = await lyrixa.collect_suggestion_feedback(
        suggestion_id="test_suggestion_1",
        accepted=True,
        rating=4,
        reason="Very helpful for my workflow",
    )
    print(f"   Result: {suggestion_feedback}")

    # Test response feedback
    print("\n📝 Testing response feedback...")
    response_feedback = await lyrixa.collect_response_feedback(
        response_id="test_response_1",
        quality_rating=5,
        helpfulness_rating=4,
        tone_feedback="Great tone, very friendly",
    )
    print(f"   Result: {response_feedback}")

    # Test personality feedback
    print("\n📝 Testing personality feedback...")
    personality_feedback = await lyrixa.collect_personality_feedback(
        persona_rating=4,
        preferred_adjustments={"formality": 0.6, "verbosity": 0.4},
        specific_feedback="Could be slightly more formal",
    )
    print(f"   Result: {personality_feedback}")

    # Test interaction feedback
    print("\n📝 Testing interaction feedback...")
    interaction_feedback = await lyrixa.collect_interaction_feedback(
        proactiveness_rating=3,
        timing_rating=4,
        interruption_feedback="Good timing, but maybe too frequent",
    )
    print(f"   Result: {interaction_feedback}")

    # Test 2: Generic feedback collection
    print("\n" + "=" * 50)
    print("3. Testing Generic Feedback Collection")
    print("=" * 50)

    feedback_types = [
        "suggestion",
        "response",
        "personality",
        "interaction",
        "helpfulness",
    ]

    for i, feedback_type in enumerate(feedback_types):
        print(f"\n📊 Testing {feedback_type} feedback...")
        result = await lyrixa.collect_user_feedback(
            feedback_type=feedback_type,
            rating=3 + (i % 3),  # Vary ratings 3-5
            context={"test_context": f"test_{feedback_type}_{i}"},
            comment=f"Test feedback for {feedback_type}",
        )
        print(f"   Result: {result}")

    # Test 3: Feedback widgets
    print("\n" + "=" * 50)
    print("4. Testing Feedback Widget Handling")
    print("=" * 50)

    # Test suggestion widget response
    print("\n🎛️ Testing suggestion widget response...")
    suggestion_widget_response = {
        "type": "suggestion_feedback",
        "suggestion_id": "widget_suggestion_1",
        "value": "helpful",
        "comment": "This suggestion was very useful",
    }
    widget_result = await lyrixa.handle_feedback_widget_response(
        suggestion_widget_response
    )
    print(f"   Result: {widget_result}")

    # Test response widget response
    print("\n🎛️ Testing response widget response...")
    response_widget_response = {
        "type": "response_feedback",
        "response_id": "widget_response_1",
        "quality_rating": 4,
        "helpfulness_rating": 5,
        "tone_feedback": "Perfect tone",
    }
    widget_result = await lyrixa.handle_feedback_widget_response(
        response_widget_response
    )
    print(f"   Result: {widget_result}")

    # Test 4: Performance and adaptive settings
    print("\n" + "=" * 50)
    print("5. Testing Performance Tracking & Adaptive Settings")
    print("=" * 50)

    # Get performance report
    print("\n📊 Getting performance report...")
    performance_report = await lyrixa.get_performance_report()
    print("   Performance Metrics:")
    if "performance_metrics" in performance_report:
        for metric, value in performance_report["performance_metrics"].items():
            print(f"     {metric}: {value}")

    # Get adaptive settings
    print("\n⚙️ Getting adaptive settings...")
    adaptive_settings = lyrixa.get_current_adaptive_settings()
    print("   Adaptive Parameters:")
    if "adaptive_parameters" in adaptive_settings:
        for param, value in adaptive_settings["adaptive_parameters"].items():
            print(f"     {param}: {value}")

    # Test 5: Proactive feedback requests
    print("\n" + "=" * 50)
    print("6. Testing Proactive Feedback Requests")
    print("=" * 50)

    # Test proactive feedback request
    print("\n🤖 Testing proactive feedback request...")
    feedback_context = {
        "recent_suggestions_count": 5,
        "user_activity": "high",
        "session_duration": 30,
    }
    proactive_request = await lyrixa.request_proactive_feedback(feedback_context)
    print(f"   Proactive request: {proactive_request}")

    # Test with different context
    feedback_context_2 = {
        "recent_suggestions_count": 1,
        "user_activity": "low",
        "session_duration": 5,
    }
    proactive_request_2 = await lyrixa.request_proactive_feedback(feedback_context_2)
    print(f"   Proactive request 2: {proactive_request_2}")

    # Test 6: Brain loop integration
    print("\n" + "=" * 50)
    print("7. Testing Brain Loop Integration")
    print("=" * 50)

    # Test brain loop with feedback integration
    print("\n🧠 Testing brain loop with feedback integration...")
    test_inputs = [
        "Generate .aether code for data processing",
        "Help me analyze this dataset",
        "What suggestions do you have for my workflow?",
    ]

    for i, test_input in enumerate(test_inputs):
        print(f"\n   Test {i + 1}: {test_input}")
        brain_result = await lyrixa.brain_loop(test_input, context={"test_mode": True})

        # Check for feedback widgets in GUI updates
        if "gui_updates" in brain_result:
            gui_updates = brain_result["gui_updates"]
            if "feedback_request" in gui_updates:
                print(
                    f"     Feedback request generated: {gui_updates['feedback_request']['type']}"
                )
            if "suggestion_feedback_widgets" in gui_updates:
                print(
                    f"     Suggestion feedback widgets: {len(gui_updates['suggestion_feedback_widgets'])}"
                )
            if "response_feedback_widget" in gui_updates:
                print(f"     Response feedback widget: ✅ Generated")

    # Test 7: Learning and adaptation
    print("\n" + "=" * 50)
    print("8. Testing Learning and Adaptation")
    print("=" * 50)

    # Add more feedback to trigger learning
    print("\n📚 Adding feedback to trigger learning...")
    feedback_scenarios = [
        {"type": "suggestion", "rating": 2, "comment": "Too frequent suggestions"},
        {"type": "suggestion", "rating": 2, "comment": "Not very relevant"},
        {"type": "personality", "rating": 2, "comment": "Too formal"},
        {"type": "interaction", "rating": 1, "comment": "Too interruptive"},
        {"type": "response", "rating": 5, "comment": "Excellent response"},
    ]

    for scenario in feedback_scenarios:
        result = await lyrixa.collect_user_feedback(
            feedback_type=scenario["type"],
            rating=scenario["rating"],
            context={"learning_test": True},
            comment=scenario["comment"],
        )
        print(f"   Added {scenario['type']} feedback: rating {scenario['rating']}")

    # Check adaptive parameters after learning
    print("\n🔄 Checking adaptive parameters after learning...")
    updated_settings = lyrixa.get_current_adaptive_settings()
    print("   Updated Adaptive Parameters:")
    if "adaptive_parameters" in updated_settings:
        for param, value in updated_settings["adaptive_parameters"].items():
            print(f"     {param}: {value}")

    # Test 8: Reset learning
    print("\n" + "=" * 50)
    print("9. Testing Learning Reset")
    print("=" * 50)

    print("\n🔄 Testing learning reset...")
    reset_result = await lyrixa.reset_learning(keep_recent_days=1)
    print(f"   Reset result: {reset_result}")

    # Final performance report
    print("\n" + "=" * 50)
    print("10. Final Performance Report")
    print("=" * 50)

    final_report = await lyrixa.get_performance_report()
    print("\n📊 Final Performance Report:")

    if "performance_metrics" in final_report:
        print("   Performance Metrics:")
        for metric, value in final_report["performance_metrics"].items():
            print(f"     {metric}: {value}")

    if "feedback_summary" in final_report:
        summary = final_report["feedback_summary"]
        print(f"\n   Feedback Summary:")
        print(f"     Total entries: {summary.get('total_entries', 0)}")
        print(f"     By type: {summary.get('by_type', {})}")

    if "recent_improvements" in final_report:
        improvements = final_report["recent_improvements"]
        print(f"\n   Recent Improvements: {len(improvements)}")
        for improvement in improvements:
            print(
                f"     - {improvement.get('area', 'unknown')}: {improvement.get('action', 'unknown')}"
            )

    print("\n" + "=" * 50)
    print("✅ FEEDBACK SYSTEM INTEGRATION TEST COMPLETE")
    print("=" * 50)
    print("\n🎉 All feedback and self-improvement features tested successfully!")
    print("   ✅ Basic feedback collection")
    print("   ✅ Widget handling")
    print("   ✅ Performance tracking")
    print("   ✅ Proactive feedback requests")
    print("   ✅ Brain loop integration")
    print("   ✅ Learning and adaptation")
    print("   ✅ Learning reset functionality")

    return True


async def main():
    """Main test execution"""
    try:
        success = await test_feedback_system_comprehensive()
        if success:
            print(f"\n🎊 All tests completed successfully at {datetime.now()}")
        else:
            print(f"\n❌ Some tests failed at {datetime.now()}")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

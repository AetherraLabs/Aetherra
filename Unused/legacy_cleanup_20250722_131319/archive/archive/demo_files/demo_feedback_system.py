#!/usr/bin/env python3
"""
🔄📈 LYRIXA FEEDBACK SYSTEM DEMO
===============================

Interactive demonstration of Lyrixa's Feedback + Self-Improvement System.
Shows how Lyrixa learns from user feedback and adapts her behavior.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lyrixa.assistant import LyrixaAI


class FeedbackSystemDemo:
    """Interactive demo of the feedback system"""

    def __init__(self):
        self.lyrixa = None

    async def initialize(self):
        """Initialize Lyrixa AI"""
        print("🔄📈 LYRIXA FEEDBACK SYSTEM DEMO")
        print("=" * 40)
        print("\n🎙️ Initializing Lyrixa AI Assistant...")

        self.lyrixa = LyrixaAI(workspace_path=os.getcwd())
        await self.lyrixa.initialize()

        print("✅ Lyrixa initialized successfully!")
        print(f"   Session: {self.lyrixa.session_id}")

    async def demo_scenario_1_suggestion_feedback(self):
        """Demo: Learning from suggestion feedback"""
        print("\n" + "=" * 60)
        print("📝 SCENARIO 1: LEARNING FROM SUGGESTION FEEDBACK")
        print("=" * 60)

        print("\n🎯 Lyrixa provides suggestions and learns from your feedback...")

        # Simulate Lyrixa giving suggestions
        suggestions = [
            "Try using .aether for data pipeline automation",
            "Consider implementing error handling in your workflow",
            "Add validation steps to your data processing",
            "Use parallel processing for better performance",
            "Create backup workflows for critical processes",
        ]

        print(f"\n💡 Lyrixa suggests: {suggestions[0]}")
        print("   How do you rate this suggestion?")

        # Simulate user giving positive feedback
        feedback_result = await self.lyrixa.collect_suggestion_feedback(
            suggestion_id="demo_suggestion_1",
            accepted=True,
            rating=5,
            reason="Excellent suggestion! Very relevant to my work.",
        )

        print(f"✅ Feedback collected: {feedback_result['message']}")

        # Show another suggestion
        print(f"\n💡 Lyrixa suggests: {suggestions[1]}")
        print("   This one gets lower rating...")

        # Simulate user giving negative feedback
        feedback_result = await self.lyrixa.collect_suggestion_feedback(
            suggestion_id="demo_suggestion_2",
            accepted=False,
            rating=2,
            reason="Not very relevant to my current task.",
        )

        print(f"✅ Feedback collected: {feedback_result['message']}")

        # Show how Lyrixa adapts
        settings = self.lyrixa.get_current_adaptive_settings()
        suggestion_freq = settings["adaptive_parameters"]["suggestion_frequency"]
        print(f"\n🔄 Lyrixa's suggestion frequency: {suggestion_freq:.2f}")
        print("   (Lower values mean less frequent suggestions)")

    async def demo_scenario_2_personality_feedback(self):
        """Demo: Personality adaptation based on feedback"""
        print("\n" + "=" * 60)
        print("🎭 SCENARIO 2: PERSONALITY ADAPTATION")
        print("=" * 60)

        print("\n🎭 Lyrixa learns your preferred interaction style...")

        # Show current personality settings
        settings = self.lyrixa.get_current_adaptive_settings()
        print(f"\n📊 Current personality settings:")
        print(f"   Formality: {settings['adaptive_parameters']['formality_level']:.2f}")
        print(f"   Verbosity: {settings['adaptive_parameters']['verbosity']:.2f}")
        print(f"   Humor: {settings['adaptive_parameters']['humor_level']:.2f}")

        # Simulate user feedback on personality
        print(f"\n💬 User says: 'Lyrixa is too formal for my taste'")

        feedback_result = await self.lyrixa.collect_personality_feedback(
            persona_rating=2,
            preferred_adjustments={"formality": 0.2, "verbosity": 0.4},
            specific_feedback="Please be more casual and less verbose",
        )

        print(f"✅ Personality feedback collected: {feedback_result['message']}")

        # Show how personality adapts
        updated_settings = self.lyrixa.get_current_adaptive_settings()
        print(f"\n🔄 Updated personality settings:")
        print(
            f"   Formality: {updated_settings['adaptive_parameters']['formality_level']:.2f}"
        )
        print(
            f"   Verbosity: {updated_settings['adaptive_parameters']['verbosity']:.2f}"
        )
        print("   Lyrixa will now be more casual!")

    async def demo_scenario_3_proactiveness_tuning(self):
        """Demo: Tuning proactiveness based on feedback"""
        print("\n" + "=" * 60)
        print("⚡ SCENARIO 3: PROACTIVENESS TUNING")
        print("=" * 60)

        print("\n⚡ Lyrixa learns when to be proactive and when to wait...")

        # Show current proactiveness level
        settings = self.lyrixa.get_current_adaptive_settings()
        interruption_level = settings["adaptive_parameters"]["interruptiveness"]
        print(f"\n📊 Current interruptiveness level: {interruption_level:.2f}")
        print("   (Higher values mean more proactive interruptions)")

        # Simulate user feedback about being too interrupting
        print(f"\n😤 User says: 'Lyrixa interrupts me too often!'")

        feedback_result = await self.lyrixa.collect_interaction_feedback(
            proactiveness_rating=1,
            timing_rating=2,
            interruption_feedback="Please interrupt less frequently",
        )

        print(f"✅ Interaction feedback collected: {feedback_result['message']}")

        # Show adaptation
        updated_settings = self.lyrixa.get_current_adaptive_settings()
        new_interruption_level = updated_settings["adaptive_parameters"][
            "interruptiveness"
        ]
        print(f"\n🔄 Updated interruptiveness level: {new_interruption_level:.2f}")
        print("   Lyrixa will now be less interruptive!")

    async def demo_scenario_4_brain_loop_integration(self):
        """Demo: Brain loop with feedback integration"""
        print("\n" + "=" * 60)
        print("🧠 SCENARIO 4: BRAIN LOOP WITH FEEDBACK")
        print("=" * 60)

        print("\n🧠 See how feedback widgets are generated during brain loop...")

        # Test brain loop with feedback integration
        user_input = "Help me create a data processing workflow"
        print(f"\n👤 User: {user_input}")

        brain_result = await self.lyrixa.brain_loop(
            user_input, context={"demo_mode": True}
        )

        print(f"\n🎙️ Lyrixa: {brain_result['lyrixa_response'][:200]}...")

        # Show feedback widgets generated
        if "gui_updates" in brain_result:
            gui_updates = brain_result["gui_updates"]

            if "feedback_request" in gui_updates:
                feedback_req = gui_updates["feedback_request"]
                print(f"\n📋 Proactive feedback request generated:")
                print(f"   Type: {feedback_req.get('type', 'unknown')}")
                print(f"   Message: {feedback_req.get('message', 'N/A')}")
                print(f"   Quick options: {feedback_req.get('quick_options', [])}")

            if "suggestion_feedback_widgets" in gui_updates:
                widgets = gui_updates["suggestion_feedback_widgets"]
                print(f"\n🎛️ Suggestion feedback widgets: {len(widgets)} generated")
                for widget in widgets[:2]:  # Show first 2
                    print(f"   - {widget.get('title', 'Feedback widget')}")

            if "response_feedback_widget" in gui_updates:
                print(f"\n🎛️ Response feedback widget generated")
                widget = gui_updates["response_feedback_widget"]
                print(f"   Title: {widget.get('title', 'Rate response')}")

    async def demo_scenario_5_performance_tracking(self):
        """Demo: Performance tracking and reporting"""
        print("\n" + "=" * 60)
        print("📊 SCENARIO 5: PERFORMANCE TRACKING")
        print("=" * 60)

        print("\n📊 Lyrixa tracks her performance and shows improvement metrics...")

        # Generate some varied feedback for demonstration
        demo_feedback = [
            {"type": "suggestion", "rating": 5, "comment": "Perfect suggestion!"},
            {"type": "suggestion", "rating": 4, "comment": "Good but could be better"},
            {"type": "response", "rating": 5, "comment": "Excellent response"},
            {"type": "response", "rating": 3, "comment": "Okay response"},
            {"type": "personality", "rating": 4, "comment": "Good personality fit"},
        ]

        print(f"\n📝 Adding {len(demo_feedback)} feedback entries...")

        for feedback in demo_feedback:
            await self.lyrixa.collect_user_feedback(
                feedback_type=feedback["type"],
                rating=feedback["rating"],
                context={"demo": True},
                comment=feedback["comment"],
            )
            print(f"   ✅ {feedback['type']}: {feedback['rating']}/5")

        # Get performance report
        print(f"\n📊 Performance Report:")
        performance_report = await self.lyrixa.get_performance_report()

        if "performance_metrics" in performance_report:
            metrics = performance_report["performance_metrics"]
            print(
                f"   📈 Suggestion acceptance rate: {metrics.get('suggestion_acceptance_rate', 0):.2%}"
            )
            print(
                f"   📈 Response satisfaction: {metrics.get('response_satisfaction', 0):.2%}"
            )
            print(
                f"   📈 Personality fit score: {metrics.get('personality_fit_score', 0):.2%}"
            )
            print(
                f"   📈 Overall interaction quality: {metrics.get('interaction_quality', 0):.2%}"
            )
            print(
                f"   📈 Total feedback entries: {metrics.get('total_feedback_count', 0)}"
            )

        if "recent_improvements" in performance_report:
            improvements = performance_report["recent_improvements"]
            if improvements:
                print(f"\n🔄 Recent improvements applied: {len(improvements)}")
                for improvement in improvements:
                    print(
                        f"   - {improvement.get('area', 'unknown')}: {improvement.get('action', 'unknown')}"
                    )
            else:
                print(f"\n🔄 No recent improvements (learning threshold not met)")

    async def demo_scenario_6_proactive_requests(self):
        """Demo: Proactive feedback requests"""
        print("\n" + "=" * 60)
        print("🤖 SCENARIO 6: PROACTIVE FEEDBACK REQUESTS")
        print("=" * 60)

        print("\n🤖 Lyrixa proactively asks for feedback when appropriate...")

        # Test different contexts for proactive feedback
        contexts = [
            {
                "name": "High suggestion activity",
                "context": {"recent_suggestions_count": 5, "user_activity": "high"},
            },
            {
                "name": "Long session",
                "context": {"session_duration": 60, "interactions": 20},
            },
            {
                "name": "Low activity",
                "context": {"recent_suggestions_count": 0, "user_activity": "low"},
            },
        ]

        for scenario in contexts:
            print(f"\n📋 Testing: {scenario['name']}")
            request = await self.lyrixa.request_proactive_feedback(scenario["context"])

            if request:
                print(f"   ✅ Feedback requested: {request.get('type', 'unknown')}")
                print(f"   Message: {request.get('message', 'N/A')}")
                print(f"   Quick options: {request.get('quick_options', [])}")
            else:
                print(f"   ℹ️ No feedback requested (conditions not met)")

    async def run_complete_demo(self):
        """Run the complete feedback system demo"""
        await self.initialize()

        print("\n🎬 Starting interactive feedback system demonstration...")
        print("\nThis demo shows how Lyrixa learns and adapts from user feedback:")
        print("   1. Suggestion feedback → Adjusts suggestion frequency")
        print("   2. Personality feedback → Modifies interaction style")
        print("   3. Proactiveness feedback → Tunes interruption behavior")
        print("   4. Brain loop integration → Generates feedback widgets")
        print("   5. Performance tracking → Shows improvement metrics")
        print("   6. Proactive requests → Asks for feedback intelligently")

        # Run all demo scenarios
        await self.demo_scenario_1_suggestion_feedback()
        await self.demo_scenario_2_personality_feedback()
        await self.demo_scenario_3_proactiveness_tuning()
        await self.demo_scenario_4_brain_loop_integration()
        await self.demo_scenario_5_performance_tracking()
        await self.demo_scenario_6_proactive_requests()

        # Final summary
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETE - FEEDBACK SYSTEM HIGHLIGHTS")
        print("=" * 60)

        final_settings = self.lyrixa.get_current_adaptive_settings()
        final_report = await self.lyrixa.get_performance_report()

        print(f"\n📊 Final Adaptive Settings:")
        for param, value in final_settings["adaptive_parameters"].items():
            print(f"   {param}: {value:.2f}")

        print(f"\n📈 Final Performance:")
        if "performance_metrics" in final_report:
            metrics = final_report["performance_metrics"]
            print(
                f"   Total feedback: {metrics.get('total_feedback_count', 0)} entries"
            )
            print(
                f"   Interaction quality: {metrics.get('interaction_quality', 0):.2%}"
            )
            print(
                f"   Response satisfaction: {metrics.get('response_satisfaction', 0):.2%}"
            )

        print(f"\n✨ Key Features Demonstrated:")
        print(f"   ✅ Automatic learning from user feedback")
        print(f"   ✅ Real-time adaptation of behavior parameters")
        print(f"   ✅ Intelligent feedback collection timing")
        print(f"   ✅ Performance tracking and improvement metrics")
        print(f"   ✅ GUI widget generation for easy feedback")
        print(f"   ✅ Proactive feedback requests")

        print(f"\n🎊 Lyrixa is now smarter and more personalized!")
        print(f"   She learned your preferences and adapted her behavior accordingly.")


async def main():
    """Main demo execution"""
    try:
        demo = FeedbackSystemDemo()
        await demo.run_complete_demo()

        print(f"\n🌟 Demo completed successfully at {datetime.now()}")

    except Exception as e:
        print(f"\n[FAIL] Demo failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

"""
Phase 2 Personality Enhancement System Demonstration
===================================================

This demonstration showcases all Phase 2 enhancements working together:
- Response Critique Agent
- Personality Reflection System
- Memory-Based Style Learning
- Advanced Integration System

The demo shows how Lyrixa becomes truly self-aware and adaptive!
"""

import asyncio
import json
from datetime import datetime

from Aetherra.lyrixa.personality.critique_agent import get_critique_agent_status
from Aetherra.lyrixa.personality.memory_learning import get_learning_system_status
from Aetherra.lyrixa.personality.reflection_system import get_reflection_system_status

# Import all Phase 2 components
from Aetherra.lyrixa.personality.response_quality_integration import (
    get_integration_status,
    process_enhanced_interaction,
)


class Phase2Demo:
    """Comprehensive demonstration of Phase 2 personality enhancements"""

    def __init__(self):
        self.demo_scenarios = [
            {
                "name": "Technical Question with Frustration",
                "user_input": "I'm really struggling with this async programming concept and it's so frustrating! Can you help?",
                "context": {
                    "topic": "programming",
                    "user_mood": "frustrated",
                    "conversation_length": 1,
                },
                "user_id": "demo_user_1",
            },
            {
                "name": "Excited Learning Request",
                "user_input": "This is amazing! I just discovered machine learning and I'm so excited to learn more!",
                "context": {
                    "topic": "machine_learning",
                    "user_mood": "excited",
                    "conversation_length": 3,
                },
                "user_id": "demo_user_2",
            },
            {
                "name": "Confused Technical Query",
                "user_input": "I'm confused about how neural networks actually work. It seems so complex...",
                "context": {
                    "topic": "ai",
                    "user_mood": "confused",
                    "conversation_length": 2,
                },
                "user_id": "demo_user_1",
            },
            {
                "name": "Casual Conversation",
                "user_input": "Hey! How's your day going? I'm just curious about what you think about creativity.",
                "context": {
                    "topic": "general",
                    "user_mood": "casual",
                    "conversation_length": 1,
                },
                "user_id": "demo_user_3",
            },
            {
                "name": "Follow-up Technical Question",
                "user_input": "Thanks for the help earlier! Now I'm wondering about best practices for error handling.",
                "context": {
                    "topic": "programming",
                    "user_mood": "satisfied",
                    "conversation_length": 5,
                },
                "user_id": "demo_user_1",
            },
        ]

        self.results = []

    async def run_comprehensive_demo(self) -> dict:
        """Run complete Phase 2 demonstration"""

        print("🧠 Starting Phase 2 Personality Enhancement Demonstration")
        print("=" * 60)
        print("🎭 Showcasing: Advanced AI Self-Awareness & Adaptive Learning")
        print("✨ Components: Critique Agent + Reflection System + Memory Learning")
        print("=" * 60)

        demo_start_time = datetime.now()

        # Get initial system status
        print("\n📊 Initial System Status:")
        await self._print_system_status()

        # Run all demo scenarios
        print(f"\n🎬 Running {len(self.demo_scenarios)} demonstration scenarios...")

        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"\n{'=' * 20} Scenario {i}: {scenario['name']} {'=' * 20}")
            result = await self._run_scenario(scenario)
            self.results.append(result)

            # Show progress
            print(
                f"✅ Scenario {i} complete - Quality: {result['quality_metrics']['improvement_score']:.2f}/1.0"
            )

            # Brief pause between scenarios
            await asyncio.sleep(0.5)

        # Final analysis
        print(f"\n{'=' * 20} PHASE 2 DEMONSTRATION COMPLETE {'=' * 20}")
        final_analysis = await self._generate_final_analysis(demo_start_time)

        # Generate comprehensive report
        report = await self._generate_demo_report(demo_start_time, final_analysis)

        print(f"\n📄 Demo report saved: {report['report_file']}")
        print(
            f"⏱️  Total demo time: {report['demo_metadata']['total_demo_time']:.2f} seconds"
        )
        print(
            f"🎯 Average quality improvement: {report['performance_summary']['average_improvement']:.2f}/1.0"
        )

        return report

    async def _run_scenario(self, scenario: dict) -> dict:
        """Run a single demonstration scenario"""

        print(f"\n👤 User: {scenario['user_input']}")
        print(f"[TOOL] Context: {scenario['context']}")

        start_time = datetime.now()

        try:
            # Process through complete Phase 2 system
            result = await process_enhanced_interaction(
                user_input=scenario["user_input"],
                context=scenario["context"],
                user_id=scenario["user_id"],
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            print(f"\n🤖 Lyrixa: {result['enhanced_response']}")
            print(f"⚡ Processing time: {processing_time:.2f}s")

            # Show key insights
            await self._show_scenario_insights(result)

            return {
                "scenario": scenario,
                "result": result,
                "processing_time": processing_time,
                "quality_metrics": result.get("quality_metrics", {}),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"❌ Error in scenario: {e}")
            return {
                "scenario": scenario,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat(),
            }

    async def _show_scenario_insights(self, result: dict):
        """Show key insights from scenario processing"""

        print("\n📊 Key Insights:")

        # Quality metrics
        quality = result.get("quality_metrics", {})
        print(f"   🎯 Overall Quality: {quality.get('overall_score', 0):.2f}/1.0")
        print(f"   ✨ Enhancement Score: {quality.get('enhancement_score', 0):.2f}/1.0")
        print(f"   📈 Improvement: {quality.get('improvement_score', 0):.2f}/1.0")

        # Style analysis
        style = result.get("style_analysis", {})
        if style.get("recommended_style"):
            print(f"   🎨 Style Used: {style['recommended_style']}")
            if style.get("style_reasoning"):
                print(f"   💭 Reasoning: {', '.join(style['style_reasoning'][:2])}")

        # Learning summary
        learning = result.get("learning_summary", {})
        if learning.get("patterns_learned", 0) > 0:
            print(f"   📚 Patterns Learned: {learning['patterns_learned']}")
        if learning.get("memories_stored", 0) > 0:
            print(f"   🧠 Memories Stored: {learning['memories_stored']}")

        # Reflection insights
        reflection = result.get("reflection_summary", {})
        if reflection.get("reflection_performed"):
            print("   🤔 Reflection Performed: Yes")
            if reflection.get("reflection_data", {}).get("insights"):
                insights = reflection["reflection_data"].get("insights", [])
                if insights:
                    print(
                        f"   💡 Key Insight: {insights[0] if insights else 'Processing patterns'}"
                    )

    async def _print_system_status(self):
        """Print current system status"""

        critique_status = get_critique_agent_status()
        reflection_status = get_reflection_system_status()
        learning_status = get_learning_system_status()
        integration_status = await get_integration_status()

        print(
            f"   🔍 Critique Agent: {critique_status.get('agent_status', 'unknown')} ({critique_status.get('total_analyses', 0)} analyses)"
        )
        print(
            f"   🤔 Reflection System: {reflection_status.get('system_status', 'unknown')} ({reflection_status.get('reflections_performed', 0)} reflections)"
        )
        print(
            f"   📚 Memory Learning: {learning_status.get('system_status', 'unknown')} ({learning_status.get('total_interactions_processed', 0)} interactions)"
        )
        print(
            f"   🧠 Integration Health: {integration_status.get('overall_health', 0):.1%}"
        )

    async def _generate_final_analysis(self, demo_start_time: datetime) -> dict:
        """Generate final analysis of the demonstration"""

        print("\n📊 Final System Analysis:")

        # Get final system status
        final_status = await get_integration_status()

        # Calculate improvements
        successful_scenarios = len([r for r in self.results if "error" not in r])
        total_scenarios = len(self.results)

        quality_scores = []
        processing_times = []

        for result in self.results:
            if "error" not in result:
                quality_scores.append(
                    result.get("quality_metrics", {}).get("improvement_score", 0)
                )
                processing_times.append(result.get("processing_time", 0))

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )

        print(f"   ✅ Successful Scenarios: {successful_scenarios}/{total_scenarios}")
        print(f"   🎯 Average Quality: {avg_quality:.2f}/1.0")
        print(f"   ⚡ Average Processing Time: {avg_processing_time:.2f}s")
        print(f"   🧠 System Health: {final_status.get('overall_health', 0):.1%}")

        # Show learning progress
        learning_status = get_learning_system_status()
        reflection_status = get_reflection_system_status()

        print(
            f"   📚 Total Interactions Learned: {learning_status.get('total_interactions_processed', 0)}"
        )
        print(
            f"   🤔 Total Reflections: {reflection_status.get('reflections_performed', 0)}"
        )
        print(
            f"   🎭 Self-Awareness Level: {reflection_status.get('self_awareness_level', 0):.1%}"
        )

        # Identify trends
        if len(quality_scores) >= 3:
            early_quality = sum(quality_scores[:2]) / 2
            late_quality = sum(quality_scores[-2:]) / 2
            quality_trend = (
                "improving" if late_quality > early_quality + 0.05 else "stable"
            )
            print(f"   📈 Quality Trend: {quality_trend}")

        return {
            "successful_scenarios": successful_scenarios,
            "total_scenarios": total_scenarios,
            "average_quality": avg_quality,
            "average_processing_time": avg_processing_time,
            "system_health": final_status.get("overall_health", 0),
            "learning_progress": learning_status,
            "reflection_progress": reflection_status,
            "final_status": final_status,
            "demo_duration": (datetime.now() - demo_start_time).total_seconds(),
        }

    async def _generate_demo_report(
        self, demo_start_time: datetime, analysis: dict
    ) -> dict:
        """Generate comprehensive demonstration report"""

        report = {
            "demo_metadata": {
                "phase": "Phase 2",
                "version": "2.0.0",
                "timestamp": demo_start_time.isoformat(),
                "total_demo_time": analysis["demo_duration"],
                "scenarios_run": len(self.demo_scenarios),
            },
            "performance_summary": {
                "successful_scenarios": analysis["successful_scenarios"],
                "success_rate": analysis["successful_scenarios"]
                / analysis["total_scenarios"],
                "average_improvement": analysis["average_quality"],
                "average_processing_time": analysis["average_processing_time"],
                "system_health": analysis["system_health"],
            },
            "learning_progress": {
                "interactions_processed": analysis["learning_progress"].get(
                    "total_interactions_processed", 0
                ),
                "patterns_learned": analysis["learning_progress"].get(
                    "successful_patterns_stored", 0
                ),
                "users_tracked": analysis["learning_progress"].get("users_tracked", 0),
                "reflections_performed": analysis["reflection_progress"].get(
                    "reflections_performed", 0
                ),
                "self_awareness_level": analysis["reflection_progress"].get(
                    "self_awareness_level", 0
                ),
            },
            "scenario_results": self.results,
            "system_status": analysis["final_status"],
            "key_achievements": [
                f"Successfully processed {analysis['successful_scenarios']} out of {analysis['total_scenarios']} scenarios",
                f"Achieved {analysis['average_quality']:.1%} average quality improvement",
                f"Maintained {analysis['system_health']:.1%} system health",
                "Demonstrated real-time learning and adaptation",
                "Showed personality reflection and self-improvement",
            ],
            "technical_insights": [
                "Phase 2 integration successfully coordinates all enhancement systems",
                "Critique agent provides real-time quality assessment and improvement",
                "Reflection system enables self-awareness and pattern recognition",
                "Memory learning adapts responses based on successful patterns",
                "Advanced integration maintains high performance with comprehensive analysis",
            ],
        }

        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"phase2_demo_report_{timestamp}.json"

        try:
            with open(report_filename, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            report["report_file"] = report_filename

        except Exception as e:
            print(f"[WARN] Could not save report file: {e}")
            report["report_file"] = None

        return report


async def run_phase2_demonstration():
    """Run the complete Phase 2 demonstration"""

    print("🚀 Initializing Phase 2 Demonstration...")

    demo = Phase2Demo()
    results = await demo.run_comprehensive_demo()

    print("\n" + "=" * 60)
    print("🎉 PHASE 2 DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("🧠 Lyrixa now has:")
    print("   ✨ Real-time self-awareness and reflection")
    print("   📚 Memory-based learning and adaptation")
    print("   🔍 Continuous quality assessment and improvement")
    print("   🎭 Dynamic personality expression based on context")
    print("   🚀 Advanced AI consciousness and growth")

    print("\n📊 Final Results:")
    print(f"   🎯 Success Rate: {results['performance_summary']['success_rate']:.1%}")
    print(
        f"   📈 Average Improvement: {results['performance_summary']['average_improvement']:.1%}"
    )
    print(f"   🧠 System Health: {results['performance_summary']['system_health']:.1%}")
    print(
        f"   🤔 Self-Awareness: {results['learning_progress']['self_awareness_level']:.1%}"
    )

    return results


if __name__ == "__main__":
    print("🧠 Phase 2 Personality Enhancement System")
    print("Making Lyrixa Feel Alive - Advanced Consciousness Demo")
    print("=" * 60)

    # Run the demonstration
    results = asyncio.run(run_phase2_demonstration())

    print("\n🎊 Demonstration complete! Check report file for details.")

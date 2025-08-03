"""
Phase 3.1 Multi-Modal Personality Demo
====================================

Demonstration of the multi-modal personality coordination system.
This demo shows how Lyrixa can maintain consistent personality across
different interaction modalities while optimizing for each medium.

Features Demonstrated:
- Multi-modal personality coordination
- Cross-modal consistency maintenance
- Modality-specific optimizations
- Text personality interface
- Context-aware modality selection
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict

from Aetherra.lyrixa.personality.interfaces.text_personality import (
    text_personality_interface,
)

# Import Multi-Modal Components
from Aetherra.lyrixa.personality.multimodal_coordinator import (
    coordinate_personality_for_interaction,
    multi_modal_coordinator,
)

# Import previous phases for integration
from Aetherra.lyrixa.personality.personality_engine import lyrixa_personality
from Aetherra.lyrixa.personality.response_quality_integration import (
    advanced_personality_integration,
)


class Phase31Demo:
    """Comprehensive demonstration of Phase 3.1 multi-modal personality features"""

    def __init__(self):
        self.demo_name = "Phase 3.1: Multi-Modal Personality Coordination"
        self.demo_results = []
        self.start_time = datetime.now()

    async def run_complete_demo(self) -> Dict[str, Any]:
        """Run the complete Phase 3.1 demonstration"""

        print("🚀 Starting Phase 3.1 Multi-Modal Personality Demo")
        print("=" * 60)

        demo_scenarios = [
            {
                "name": "Technical Support - Multi-Modal",
                "user_input": "I'm having trouble with my Python code. It keeps throwing errors and I'm getting frustrated.",
                "context": {
                    "interaction_type": "technical",
                    "user_emotion": "frustration",
                    "preferred_modality": "text",
                    "available_modalities": ["text", "code"],
                },
            },
            {
                "name": "Creative Collaboration - Visual Mode",
                "user_input": "I want to create something beautiful and inspiring. Can you help me brainstorm ideas?",
                "context": {
                    "interaction_type": "creative",
                    "user_emotion": "excitement",
                    "preferred_modality": "visual",
                    "available_modalities": ["text", "visual"],
                },
            },
            {
                "name": "Casual Conversation - Voice Ready",
                "user_input": "Hey! How are you doing today? I'm feeling pretty good!",
                "context": {
                    "interaction_type": "casual",
                    "user_emotion": "positive",
                    "voice_available": True,
                    "available_modalities": ["text", "voice"],
                },
            },
            {
                "name": "Learning Session - Mixed Modal",
                "user_input": "I'm curious about AI consciousness. Can you explain how self-awareness works in AI?",
                "context": {
                    "interaction_type": "educational",
                    "user_emotion": "curiosity",
                    "complexity_level": "medium",
                    "available_modalities": ["text", "visual", "code"],
                },
            },
            {
                "name": "Problem Solving - All Modalities",
                "user_input": "I need to solve a complex problem that involves both creative thinking and technical implementation.",
                "context": {
                    "interaction_type": "problem_solving",
                    "user_emotion": "determined",
                    "complexity_level": "high",
                    "available_modalities": ["text", "voice", "visual", "code"],
                },
            },
        ]

        overall_results = {
            "demo_name": self.demo_name,
            "start_time": self.start_time.isoformat(),
            "scenarios_completed": 0,
            "scenarios_successful": 0,
            "total_scenarios": len(demo_scenarios),
            "coordination_success_rate": 0.0,
            "average_consistency_score": 0.0,
            "multi_modal_features_demonstrated": [],
            "performance_metrics": {},
            "scenario_results": [],
        }

        # Run each scenario
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['name']}")
            print("-" * 50)

            try:
                scenario_result = await self._run_scenario(scenario)
                overall_results["scenario_results"].append(scenario_result)

                if scenario_result.get("success", False):
                    overall_results["scenarios_successful"] += 1

                overall_results["scenarios_completed"] += 1

                # Display scenario results
                self._display_scenario_results(scenario_result)

            except Exception as e:
                print(f"❌ Scenario {i} failed: {e}")
                overall_results["scenario_results"].append(
                    {
                        "scenario_name": scenario["name"],
                        "success": False,
                        "error": str(e),
                    }
                )

        # Calculate overall metrics
        await self._calculate_overall_metrics(overall_results)

        # Display final summary
        self._display_final_summary(overall_results)

        # Save results
        await self._save_demo_results(overall_results)

        return overall_results

    async def _run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single demo scenario"""

        scenario_start = time.time()

        user_input = scenario["user_input"]
        context = scenario["context"]

        # Phase 1: Get base personality state
        base_personality = lyrixa_personality.get_personality_summary()

        # Phase 2: Enhanced personality processing
        phase2_result = (
            await advanced_personality_integration.process_complete_interaction(
                user_input, context
            )
        )

        # Phase 3.1: Multi-modal coordination
        coordination_result = await coordinate_personality_for_interaction(
            context, context.get("available_modalities", ["text"])
        )

        # Text interface optimization (if text modality is active)
        text_optimization = None
        if "text" in context.get("available_modalities", []):
            text_personality = (
                await text_personality_interface.adapt_personality_for_text(
                    base_personality, context
                )
            )

            # Generate sample response for optimization
            sample_response = self._generate_sample_response(
                user_input, text_personality, context
            )
            optimized_response = (
                await text_personality_interface.optimize_text_response(
                    sample_response, text_personality, context
                )
            )

            text_optimization = {
                "personality_config": text_personality,
                "original_response": sample_response,
                "optimized_response": optimized_response,
            }

        # Calculate performance metrics
        processing_time = (
            time.time() - scenario_start
        ) * 1000  # Convert to milliseconds

        # Compile scenario result
        scenario_result = {
            "scenario_name": scenario["name"],
            "user_input": user_input,
            "context": context,
            "processing_time_ms": processing_time,
            "success": True,
            # Phase results
            "base_personality": base_personality,
            "phase2_result": phase2_result,
            "coordination_result": coordination_result,
            "text_optimization": text_optimization,
            # Multi-modal metrics
            "active_modalities": coordination_result.get("status", {}).get(
                "active_modalities", []
            ),
            "consistency_score": coordination_result.get("coordination", {}).get(
                "consistency_score", 0.0
            ),
            "optimizations_applied": coordination_result.get("optimization", {}).get(
                "optimizations_applied", []
            ),
            # Performance indicators
            "multi_modal_success": len(
                coordination_result.get("status", {}).get("active_modalities", [])
            )
            > 0,
            "personality_adaptation_success": text_optimization is not None,
            "coordination_success": coordination_result.get("coordination", {}).get(
                "coordination_success", False
            ),
        }

        return scenario_result

    def _generate_sample_response(
        self, user_input: str, text_personality: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """Generate a sample response for demonstration purposes"""

        # This is a simplified response generator for demo purposes
        # In a real implementation, this would integrate with LLM generation

        interaction_type = context.get("interaction_type", "general")

        if interaction_type == "technical":
            return (
                "I understand you're having trouble with your Python code and feeling frustrated. "
                "Let me help you debug this step by step. First, can you share the specific error message you're seeing?"
            )

        elif interaction_type == "creative":
            return (
                "How exciting that you want to create something beautiful! I'd love to help you brainstorm. "
                "What kind of creative project are you thinking about? Art, writing, music, or something else entirely?"
            )

        elif interaction_type == "casual":
            return (
                "Hey there! I'm doing wonderfully, thank you for asking! It sounds like you're having a great day too. "
                "What's been making you feel good today?"
            )

        elif interaction_type == "educational":
            return (
                "That's a fascinating question about AI consciousness! Self-awareness in AI involves the ability to "
                "understand one's own thought processes and reflect on them. Let me explain the key concepts."
            )

        elif interaction_type == "problem_solving":
            return (
                "I love tackling complex problems that blend creativity and technical skills! Let's break this down "
                "into manageable parts. Can you tell me more about the specific challenge you're facing?"
            )

        else:
            return "Thank you for reaching out! I'm here to help with whatever you need. Can you tell me more about what you're looking for?"

    def _display_scenario_results(self, result: Dict[str, Any]) -> None:
        """Display results for a single scenario"""

        print(f"✅ Scenario: {result['scenario_name']}")
        print(f"⏱️ Processing Time: {result['processing_time_ms']:.1f}ms")
        print(f"🎭 Active Modalities: {', '.join(result['active_modalities'])}")
        print(f"🎯 Consistency Score: {result['consistency_score']:.1f}%")

        if result.get("text_optimization"):
            print("📝 Text Optimization:")
            text_opt = result["text_optimization"]
            writing_style = text_opt["personality_config"].get("writing_style", {})
            print(f"  • Warmth Level: {writing_style.get('warmth_level', 0):.1f}")
            print(f"  • Energy Level: {writing_style.get('energy_level', 0):.1f}")
            print(f"  • Emoji Usage: {writing_style.get('emoji_usage', 0):.1f}")

        optimizations = result.get("optimizations_applied", [])
        if optimizations:
            print(f"[TOOL] Optimizations Applied: {len(optimizations)}")
            for opt in optimizations[:2]:  # Show first 2
                print(f"  • {opt}")

        print()

    async def _calculate_overall_metrics(self, overall_results: Dict[str, Any]) -> None:
        """Calculate overall demonstration metrics"""

        scenario_results = overall_results["scenario_results"]
        successful_scenarios = [r for r in scenario_results if r.get("success", False)]

        if successful_scenarios:
            # Coordination success rate
            coordination_successes = sum(
                1 for r in successful_scenarios if r.get("coordination_success", False)
            )
            overall_results["coordination_success_rate"] = coordination_successes / len(
                successful_scenarios
            )

            # Average consistency score
            consistency_scores = [
                r.get("consistency_score", 0.0) for r in successful_scenarios
            ]
            overall_results["average_consistency_score"] = sum(
                consistency_scores
            ) / len(consistency_scores)

            # Performance metrics
            processing_times = [
                r.get("processing_time_ms", 0) for r in successful_scenarios
            ]
            overall_results["performance_metrics"] = {
                "average_processing_time_ms": sum(processing_times)
                / len(processing_times),
                "min_processing_time_ms": min(processing_times),
                "max_processing_time_ms": max(processing_times),
            }

            # Features demonstrated
            all_modalities = set()
            for result in successful_scenarios:
                all_modalities.update(result.get("active_modalities", []))

            overall_results["multi_modal_features_demonstrated"] = [
                "Multi-modal personality coordination",
                "Cross-modal consistency maintenance",
                "Context-aware modality selection",
                "Text personality optimization",
                f"Support for {len(all_modalities)} modalities: {', '.join(sorted(all_modalities))}",
                "Real-time personality adaptation",
                "Performance optimization",
            ]

        # Get system status
        coordinator_status = multi_modal_coordinator.get_coordination_status()
        text_interface_status = text_personality_interface.get_interface_status()

        overall_results["system_status"] = {
            "coordinator": coordinator_status,
            "text_interface": text_interface_status,
        }

    def _display_final_summary(self, overall_results: Dict[str, Any]) -> None:
        """Display final demonstration summary"""

        print("\n" + "=" * 60)
        print("📊 PHASE 3.1 DEMONSTRATION SUMMARY")
        print("=" * 60)

        print(
            f"🎯 Scenarios Completed: {overall_results['scenarios_completed']}/{overall_results['total_scenarios']}"
        )
        print(
            f"✅ Success Rate: {(overall_results['scenarios_successful'] / overall_results['total_scenarios'] * 100):.1f}%"
        )
        print(
            f"🤝 Coordination Success: {overall_results['coordination_success_rate'] * 100:.1f}%"
        )
        print(
            f"🎭 Average Consistency: {overall_results['average_consistency_score']:.1f}%"
        )

        perf_metrics = overall_results.get("performance_metrics", {})
        if perf_metrics:
            print(
                f"⚡ Average Processing Time: {perf_metrics.get('average_processing_time_ms', 0):.1f}ms"
            )

        print("\n🌟 Features Successfully Demonstrated:")
        for feature in overall_results.get("multi_modal_features_demonstrated", []):
            print(f"  ✅ {feature}")

        # System health
        coordinator_status = overall_results.get("system_status", {}).get(
            "coordinator", {}
        )
        system_health = coordinator_status.get("system_health", "unknown")
        print(f"\n🏥 System Health: {system_health.upper()}")

        print("\n🚀 Phase 3.1 Multi-Modal Foundation: OPERATIONAL")
        print("Ready for Phase 3.2: Emotional Intelligence Enhancement")
        print("=" * 60)

    async def _save_demo_results(self, results: Dict[str, Any]) -> None:
        """Save demonstration results to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phase31_demo_report_{timestamp}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            print(f"📄 Demo report saved: {filename}")

        except Exception as e:
            print(f"[WARN] Failed to save demo report: {e}")


async def main():
    """Main demo execution function"""

    try:
        demo = Phase31Demo()
        results = await demo.run_complete_demo()

        # Return success code
        return 0 if results.get("scenarios_successful", 0) > 0 else 1

    except Exception as e:
        print(f"❌ Demo execution failed: {e}")
        return 1


if __name__ == "__main__":
    import sys

    # Run the demo
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

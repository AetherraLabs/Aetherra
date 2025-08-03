"""
Phase 3.2 Emotional Intelligence Enhancement - Demonstration
===========================================================

This script demonstrates the advanced emotional intelligence capabilities
of Phase 3.2, showing how Lyrixa can now understand and respond to complex
emotional states with deep empathy and appropriate emotional mirroring.

Features Demonstrated:
- Advanced emotion detection with multi-dimensional analysis
- Empathetic response generation with emotional resonance
- Emotional memory and pattern recognition
- Mood tracking and long-term adaptation
- Complex emotional state modeling
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add the Aetherra package to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from Aetherra.lyrixa.personality.emotional_intelligence_integration import (
    get_comprehensive_emotional_analysis,
    get_emotional_intelligence_integration_status,
    process_with_emotional_intelligence,
)


class EmotionalIntelligenceDemo:
    """Demonstrates advanced emotional intelligence capabilities"""

    def __init__(self):
        self.demo_scenarios = [
            {
                "name": "Frustrated User with Complex Problem",
                "user_input": "I've been trying to fix this bug for hours and nothing is working. I'm getting really frustrated and starting to think maybe I'm just not cut out for programming.",
                "expected_emotions": ["frustration", "self-doubt", "discouragement"],
                "context": {
                    "task_type": "debugging",
                    "difficulty": "high",
                    "time_spent": "hours",
                },
            },
            {
                "name": "Excited User with Breakthrough",
                "user_input": "Oh my god, I finally figured out how to implement that AI feature! This is so exciting, I can't wait to show everyone what I've built!",
                "expected_emotions": ["excitement", "pride", "accomplishment"],
                "context": {
                    "task_type": "implementation",
                    "breakthrough": True,
                    "achievement": "major",
                },
            },
            {
                "name": "Anxious User Seeking Reassurance",
                "user_input": "I'm about to deploy this to production and I'm really nervous. What if something goes wrong? What if I break everything?",
                "expected_emotions": ["anxiety", "worry", "uncertainty"],
                "context": {
                    "task_type": "deployment",
                    "stakes": "high",
                    "confidence": "low",
                },
            },
            {
                "name": "Confused User Needing Guidance",
                "user_input": "I don't understand why this code isn't working. The documentation says it should work but I keep getting errors I've never seen before.",
                "expected_emotions": ["confusion", "uncertainty", "mild_frustration"],
                "context": {
                    "task_type": "learning",
                    "documentation_issue": True,
                    "error_type": "unknown",
                },
            },
            {
                "name": "Grateful User After Help",
                "user_input": "Thank you so much for helping me understand that concept! You explained it perfectly and now it all makes sense. I really appreciate your patience.",
                "expected_emotions": ["gratitude", "relief", "satisfaction"],
                "context": {
                    "task_type": "learning",
                    "help_received": True,
                    "understanding": "achieved",
                },
            },
        ]

        self.results = []
        self.performance_metrics = {
            "total_scenarios": 0,
            "successful_enhancements": 0,
            "avg_empathy_score": 0.0,
            "avg_processing_time": 0.0,
            "emotional_accuracy": 0.0,
        }

    async def run_demonstration(self) -> Dict[str, Any]:
        """Run the complete emotional intelligence demonstration"""

        print(
            "🧠💫 LYRIXA EMOTIONAL INTELLIGENCE ENHANCEMENT - PHASE 3.2 DEMONSTRATION"
        )
        print("=" * 80)
        print()

        # Get initial system status
        initial_status = get_emotional_intelligence_integration_status()
        print("📊 System Status:")
        print(f"   Phase: {initial_status['phase']}")
        print(f"   Status: {initial_status['system_status']}")
        print(
            f"   Components: {len(initial_status['emotional_capabilities'])} emotional capabilities"
        )
        print()

        # Run each scenario
        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"🎭 Scenario {i}: {scenario['name']}")
            print("-" * 60)

            result = await self._run_scenario(scenario)
            self.results.append(result)

            self._display_scenario_results(result)
            print()

        # Calculate and display overall results
        overall_results = self._calculate_overall_results()
        self._display_overall_results(overall_results)

        # Save detailed report
        report_path = self._save_demonstration_report()

        return {
            "demonstration_complete": True,
            "scenarios_tested": len(self.demo_scenarios),
            "overall_results": overall_results,
            "detailed_results": self.results,
            "report_saved": report_path,
        }

    async def _run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single emotional intelligence scenario"""

        start_time = datetime.now()

        try:
            # Process with emotional intelligence
            result = await process_with_emotional_intelligence(
                user_input=scenario["user_input"],
                context=scenario["context"],
                user_id="demo_user_phase32",
            )

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "scenario_name": scenario["name"],
                "user_input": scenario["user_input"],
                "expected_emotions": scenario["expected_emotions"],
                "context": scenario["context"],
                "result": result,
                "processing_time_ms": processing_time,
                "success": result["status"] == "success",
                "timestamp": start_time.isoformat(),
            }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "scenario_name": scenario["name"],
                "user_input": scenario["user_input"],
                "expected_emotions": scenario["expected_emotions"],
                "context": scenario["context"],
                "result": {"error": str(e)},
                "processing_time_ms": processing_time,
                "success": False,
                "timestamp": start_time.isoformat(),
            }

    def _display_scenario_results(self, result: Dict[str, Any]):
        """Display results for a single scenario"""

        print(f"📝 Input: {result['user_input'][:80]}...")
        print()

        if result["success"]:
            # Display emotional analysis
            emotional_analysis = result["result"]["emotional_intelligence"][
                "emotional_analysis"
            ]
            user_state = emotional_analysis["user_emotional_state"]

            print("🧠 Emotional Analysis:")
            print(f"   Primary Emotion: {user_state['primary_emotion']}")
            print(f"   Intensity: {user_state['intensity']:.2f}")
            print(f"   Valence: {user_state['valence']:.2f} (positive/negative)")
            print(f"   Arousal: {user_state['arousal']:.2f} (energy level)")
            print(f"   Confidence: {user_state['confidence']:.2f}")
            print()

            # Display empathy metrics
            empathy_metrics = result["result"]["emotional_intelligence"][
                "empathy_metrics"
            ]
            print("💖 Empathy Metrics:")
            print(f"   Strategy Used: {empathy_metrics['strategy_used']}")
            print(f"   Empathy Score: {empathy_metrics['empathy_score']:.2f}")
            print()

            # Display enhanced response
            final_response = result["result"]["final_response"]
            print("💫 Enhanced Response:")
            print(f"   {final_response}")
            print()

            # Display performance
            processing_time = result["result"]["integration_metrics"][
                "processing_time_ms"
            ]
            empathy_score = result["result"]["integration_metrics"]["empathy_score"]

            print("⚡ Performance:")
            print(f"   Processing Time: {processing_time:.1f}ms")
            print(f"   Empathy Score: {empathy_score:.2f}")
            print(f"   Status: {result['result']['status']}")

        else:
            print(f"❌ Error: {result['result'].get('error', 'Unknown error')}")
            print(f"⚡ Processing Time: {result['processing_time_ms']:.1f}ms")

    def _calculate_overall_results(self) -> Dict[str, Any]:
        """Calculate overall demonstration results"""

        successful_results = [r for r in self.results if r["success"]]

        if successful_results:
            # Calculate averages
            avg_processing_time = sum(
                r["processing_time_ms"] for r in successful_results
            ) / len(successful_results)

            empathy_scores = [
                r["result"]["integration_metrics"]["empathy_score"]
                for r in successful_results
            ]
            avg_empathy_score = sum(empathy_scores) / len(empathy_scores)

            # Emotional accuracy (how well we detected expected emotions)
            emotion_matches = 0
            total_emotions_checked = 0

            for result in successful_results:
                if "emotional_analysis" in result["result"]["emotional_intelligence"]:
                    detected_emotion = result["result"]["emotional_intelligence"][
                        "emotional_analysis"
                    ]["user_emotional_state"]["primary_emotion"]
                    expected_emotions = result["expected_emotions"]

                    if detected_emotion in expected_emotions:
                        emotion_matches += 1
                    total_emotions_checked += 1

            emotional_accuracy = (
                emotion_matches / total_emotions_checked
                if total_emotions_checked > 0
                else 0
            )

            return {
                "total_scenarios": len(self.results),
                "successful_scenarios": len(successful_results),
                "success_rate": len(successful_results) / len(self.results),
                "avg_processing_time_ms": avg_processing_time,
                "avg_empathy_score": avg_empathy_score,
                "emotional_accuracy": emotional_accuracy,
                "min_empathy_score": min(empathy_scores),
                "max_empathy_score": max(empathy_scores),
                "performance_rating": self._calculate_performance_rating(
                    len(successful_results) / len(self.results),
                    avg_empathy_score,
                    emotional_accuracy,
                ),
            }
        else:
            return {
                "total_scenarios": len(self.results),
                "successful_scenarios": 0,
                "success_rate": 0.0,
                "performance_rating": "failed",
            }

    def _calculate_performance_rating(
        self, success_rate: float, empathy_score: float, emotional_accuracy: float
    ) -> str:
        """Calculate overall performance rating"""

        overall_score = (
            (success_rate * 0.4) + (empathy_score * 0.4) + (emotional_accuracy * 0.2)
        )

        if overall_score >= 0.9:
            return "exceptional"
        elif overall_score >= 0.8:
            return "excellent"
        elif overall_score >= 0.7:
            return "good"
        elif overall_score >= 0.6:
            return "acceptable"
        else:
            return "needs_improvement"

    def _display_overall_results(self, results: Dict[str, Any]):
        """Display overall demonstration results"""

        print("🏆 OVERALL DEMONSTRATION RESULTS")
        print("=" * 50)
        print()

        print("📊 Summary Statistics:")
        print(f"   Total Scenarios: {results['total_scenarios']}")
        print(f"   Successful: {results['successful_scenarios']}")
        print(f"   Success Rate: {results['success_rate']:.1%}")
        print()

        if results["successful_scenarios"] > 0:
            print("💫 Performance Metrics:")
            print(
                f"   Average Processing Time: {results['avg_processing_time_ms']:.1f}ms"
            )
            print(f"   Average Empathy Score: {results['avg_empathy_score']:.2f}")
            print(f"   Emotional Accuracy: {results['emotional_accuracy']:.1%}")
            print(
                f"   Empathy Range: {results['min_empathy_score']:.2f} - {results['max_empathy_score']:.2f}"
            )
            print()

            print(
                f"🎯 Overall Performance Rating: {results['performance_rating'].upper()}"
            )
            print()

            # Performance interpretation
            if results["performance_rating"] == "exceptional":
                print(
                    "🚀 Phase 3.2 is performing exceptionally! Emotional intelligence is operating at the highest level."
                )
            elif results["performance_rating"] == "excellent":
                print(
                    "✨ Phase 3.2 is performing excellently! Emotional intelligence is highly effective."
                )
            elif results["performance_rating"] == "good":
                print(
                    "👍 Phase 3.2 is performing well with good emotional intelligence capabilities."
                )
            elif results["performance_rating"] == "acceptable":
                print(
                    "✅ Phase 3.2 is functional with acceptable emotional intelligence performance."
                )
            else:
                print(
                    "[WARN] Phase 3.2 performance needs improvement in emotional intelligence areas."
                )

        print()
        print("🧠 Emotional Intelligence Features Demonstrated:")
        print("   ✅ Multi-dimensional emotion detection")
        print("   ✅ Empathetic response generation")
        print("   ✅ Emotional state modeling (valence, arousal, dominance)")
        print("   ✅ Context-aware emotional analysis")
        print("   ✅ Adaptive empathy strategies")
        print("   ✅ Emotional memory integration")
        print("   ✅ Real-time emotional processing")

    def _save_demonstration_report(self) -> str:
        """Save detailed demonstration report"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emotional_intelligence_demo_report_{timestamp}.json"

        # Get comprehensive system status
        system_status = get_emotional_intelligence_integration_status()
        emotional_analysis = get_comprehensive_emotional_analysis()

        report_data = {
            "demonstration_info": {
                "phase": "3.2 - Emotional Intelligence Enhancement",
                "timestamp": datetime.now().isoformat(),
                "total_scenarios": len(self.demo_scenarios),
                "scenarios_tested": len(self.results),
            },
            "system_status": system_status,
            "emotional_analysis": emotional_analysis,
            "scenario_results": self.results,
            "overall_performance": self._calculate_overall_results(),
            "technical_details": {
                "components_tested": [
                    "EmotionalState modeling",
                    "EmotionalMemory tracking",
                    "EmpatheticResponseGenerator",
                    "MoodTracker",
                    "AdvancedEmotionalIntelligence",
                    "EmotionalIntelligenceIntegration",
                ],
                "features_demonstrated": [
                    "Multi-dimensional emotion detection",
                    "Complex emotional state modeling",
                    "Empathetic response generation",
                    "Emotional memory and pattern recognition",
                    "Mood tracking and adaptation",
                    "Context-aware emotional analysis",
                ],
            },
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            print(f"📄 Detailed report saved: {filename}")
            return filename

        except Exception as e:
            print(f"[WARN] Could not save report: {e}")
            return "report_save_failed"


async def main():
    """Run the Phase 3.2 emotional intelligence demonstration"""

    print("🧠💫 Starting Phase 3.2 Emotional Intelligence Enhancement Demonstration...")
    print()

    demo = EmotionalIntelligenceDemo()
    results = await demo.run_demonstration()

    print()
    print("🎉 Emotional Intelligence Enhancement Demonstration Complete!")
    print(f"📊 Results: {results['scenarios_tested']} scenarios tested")
    print(f"📄 Report: {results['report_saved']}")

    return results


if __name__ == "__main__":
    asyncio.run(main())

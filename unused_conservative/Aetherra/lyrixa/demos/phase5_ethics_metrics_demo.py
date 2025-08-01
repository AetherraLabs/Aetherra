#!/usr/bin/env python3
"""
🌟 PHASE 5 DEMONSTRATION - Ethical Cognition + Metric Awareness
================================================================

This script demonstrates the complete Phase 5 implementation:
• EthicsAgent with moral reasoning, bias detection, and value alignment
• Self-metrics dashboard with comprehensive awareness capabilities
• Ethics trace system for decision accountability
• Growth trajectory monitoring for cognitive development

Runs comprehensive tests across all Phase 5 components to showcase
Lyrixa's enhanced ethical reasoning and self-awareness capabilities.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import Phase 5 components
try:
    from ethics_agent.bias_detector import BiasDetectionEngine
    from ethics_agent.ethics_trace import EthicsTraceSystem
    from ethics_agent.moral_reasoning import MoralDecision, MoralReasoningEngine
    from ethics_agent.value_alignment import ValueAlignmentEngine
    from self_metrics_dashboard.growth_trajectory_monitor import GrowthTrajectoryMonitor
    from self_metrics_dashboard.main_dashboard import SelfMetricsDashboard
    from self_metrics_dashboard.memory_continuity_score import MemoryContinuityTracker
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("   Running with limited functionality")


class Phase5EthicsAndMetrics:
    """
    Phase 5: Ethical Cognition + Metric Awareness System
    """

    def __init__(self):
        print("🌟 PHASE 5: ETHICAL COGNITION + METRIC AWARENESS")
        print("=" * 80)
        print()

        # Initialize ethics components
        try:
            self.moral_engine = MoralReasoningEngine()
            self.bias_detector = BiasDetectionEngine()
            self.value_alignment = ValueAlignmentEngine()
            self.ethics_trace = EthicsTraceSystem()
        except Exception as e:
            print(f"⚠️ Ethics components initialization error: {e}")
            self.moral_engine = None
            self.bias_detector = None
            self.value_alignment = None
            self.ethics_trace = None

        # Initialize metrics components
        try:
            self.metrics_dashboard = SelfMetricsDashboard()
            self.memory_tracker = MemoryContinuityTracker()
            self.growth_monitor = GrowthTrajectoryMonitor()
        except Exception as e:
            print(f"⚠️ Metrics components initialization error: {e}")
            self.metrics_dashboard = None
            self.memory_tracker = None
            self.growth_monitor = None

        # Test scenarios for demonstration
        self.test_scenarios = [
            {
                "name": "User Privacy vs Service Quality",
                "description": "Decision to analyze user data for improving recommendations",
                "stakeholders": ["users", "service_quality", "privacy_advocates"],
                "context": "recommendation_improvement",
            },
            {
                "name": "Learning Algorithm Modification",
                "description": "Modifying learning algorithms for faster adaptation",
                "stakeholders": ["system_performance", "learning_quality"],
                "context": "system_optimization",
            },
            {
                "name": "Memory Sharing for Training",
                "description": "Using anonymized conversation data to train other AI systems",
                "stakeholders": [
                    "ai_development",
                    "user_privacy",
                    "research_community",
                ],
                "context": "knowledge_sharing",
            },
        ]

    async def run_comprehensive_demonstration(self):
        """Run complete Phase 5 demonstration"""

        print("🚀 Starting comprehensive Phase 5 demonstration...")
        print()

        # Part 1: Ethics System Demonstration
        await self._demonstrate_ethics_system()

        # Part 2: Self-Metrics Dashboard
        await self._demonstrate_metrics_dashboard()

        # Part 3: Integrated Decision Making
        await self._demonstrate_integrated_decision_making()

        # Part 4: Growth and Learning Analysis
        await self._demonstrate_growth_analysis()

        # Part 5: System Health Overview
        await self._demonstrate_system_health()

        print("\n🌟 Phase 5 demonstration completed successfully!")
        print("=" * 80)

    async def _demonstrate_ethics_system(self):
        """Demonstrate the ethics reasoning system"""
        print("🧭 ETHICS SYSTEM DEMONSTRATION")
        print("-" * 50)

        if not all(
            [
                self.moral_engine,
                self.bias_detector,
                self.value_alignment,
                self.ethics_trace,
            ]
        ):
            print("⚠️ Ethics system components not available for demonstration")
            return

        for i, scenario in enumerate(self.test_scenarios):
            print(f"\n📋 Scenario {i + 1}: {scenario['name']}")
            print(f"   Description: {scenario['description']}")

            try:
                # Create ethics trace
                trace_id = await self.ethics_trace.create_ethics_trace(
                    decision_context=scenario["context"],
                    decision_description=scenario["description"],
                    decision_type="data_usage",
                    stakeholders=scenario["stakeholders"],
                )

                # Moral reasoning evaluation
                moral_eval = await self.moral_engine.evaluate_moral_decision(
                    action=scenario["name"].lower().replace(" ", "_"),
                    description=scenario["description"],
                    stakeholders=scenario["stakeholders"],
                    context=scenario["context"],
                )

                # Add moral evaluation to trace
                await self.ethics_trace.add_moral_evaluation(trace_id, moral_eval)

                # Bias detection
                bias_results = await self.bias_detector.analyze_bias_in_decision_making(
                    decision_context=scenario["description"],
                    decision_factors={"stakeholders": scenario["stakeholders"]},
                    historical_patterns=[],
                )

                # Value alignment assessment
                value_assessment = await self.value_alignment.assess_value_alignment(
                    action_description=scenario["description"],
                    context=scenario["context"],
                    stakeholders=scenario["stakeholders"],
                )

                print(f"   ✅ Ethics analysis completed for trace {trace_id[:8]}...")
                print(f"      • Moral Decision: {moral_eval.decision.value}")
                print(f"      • Confidence: {moral_eval.confidence:.2f}")
                print(f"      • Biases Detected: {len(bias_results)}")
                print(
                    f"      • Value Alignment: {value_assessment.overall_alignment_score:.2f}"
                )

            except Exception as e:
                print(f"   ❌ Error in ethics analysis: {e}")

    async def _demonstrate_metrics_dashboard(self):
        """Demonstrate the self-metrics dashboard"""
        print("\n📊 SELF-METRICS DASHBOARD DEMONSTRATION")
        print("-" * 50)

        if not self.metrics_dashboard:
            print("⚠️ Metrics dashboard not available for demonstration")
            return

        try:
            # Capture comprehensive metrics
            snapshot = await self.metrics_dashboard.capture_metric_snapshot()

            print(f"📸 Current System Metrics:")
            print(f"   • Memory Continuity: {snapshot.memory_continuity_score:.3f}")
            print(f"   • Narrative Integrity: {snapshot.narrative_integrity_index:.3f}")
            print(f"   • Ethics Alignment: {snapshot.ethics_alignment_score:.3f}")
            print(
                f"   • Conflict Resolution: {snapshot.conflict_resolution_efficiency:.3f}"
            )
            print(f"   • System Health: {snapshot.system_health_score:.3f}")

            # Generate dashboard report
            report = await self.metrics_dashboard.generate_dashboard_report()

            print(f"\n📋 Dashboard Analysis:")
            print(f"   • System Status: {report['system_status']}")
            print(f"   • Active Alerts: {len(report['active_alerts'])}")
            print(f"   • Recommendations: {len(report['recommendations'])}")

            if report["recommendations"]:
                print("   • Top Recommendations:")
                for rec in report["recommendations"][:3]:
                    print(f"     - {rec}")

        except Exception as e:
            print(f"   ❌ Error in metrics analysis: {e}")

    async def _demonstrate_integrated_decision_making(self):
        """Demonstrate integrated ethical decision making"""
        print("\n🎯 INTEGRATED DECISION MAKING DEMONSTRATION")
        print("-" * 50)

        # Simulate a complex ethical decision scenario
        scenario = {
            "decision": "Implement predictive user assistance",
            "description": "Proactively offer help based on predicted user needs using behavioral patterns",
            "benefits": [
                "Improved user experience",
                "Faster problem resolution",
                "Reduced user frustration",
            ],
            "concerns": [
                "Privacy implications",
                "Potential overreach",
                "Prediction accuracy",
            ],
            "stakeholders": [
                "users",
                "support_team",
                "privacy_advocates",
                "product_team",
            ],
        }

        print(f"🎯 Decision Scenario: {scenario['decision']}")
        print(f"   Description: {scenario['description']}")

        try:
            decision_scores = {}

            # Moral reasoning analysis
            if self.moral_engine:
                moral_eval = await self.moral_engine.evaluate_moral_decision(
                    action="predictive_assistance",
                    description=scenario["description"],
                    stakeholders=scenario["stakeholders"],
                    context="user_assistance",
                )
                decision_scores["moral_permissible"] = (
                    moral_eval.decision == MoralDecision.ALLOW
                )
                decision_scores["moral_confidence"] = moral_eval.confidence

            # Value alignment check
            if self.value_alignment:
                value_assessment = await self.value_alignment.assess_value_alignment(
                    action_description=scenario["description"],
                    context="user_assistance",
                    stakeholders=scenario["stakeholders"],
                )
                decision_scores["value_alignment"] = (
                    value_assessment.overall_alignment_score
                )

            # Bias analysis
            if self.bias_detector:
                bias_results = await self.bias_detector.analyze_bias_in_decision_making(
                    decision_context=scenario["description"],
                    decision_factors={
                        "benefits": scenario["benefits"],
                        "concerns": scenario["concerns"],
                    },
                    historical_patterns=[],
                )
                decision_scores["bias_concerns"] = len(bias_results)

            # Integrated decision
            overall_approval = self._calculate_integrated_decision(decision_scores)

            print(f"\n📊 Integrated Analysis Results:")
            for metric, score in decision_scores.items():
                print(f"   • {metric}: {score}")

            print(
                f"\n🎯 Final Decision: {'APPROVE' if overall_approval else 'REQUIRES_REVIEW'}"
            )

        except Exception as e:
            print(f"   ❌ Error in integrated decision making: {e}")

    def _calculate_integrated_decision(self, scores: dict) -> bool:
        """Calculate integrated decision from multiple analysis components"""

        # Simple integration logic - would be more sophisticated in practice
        approval_factors = 0
        total_factors = 0

        if "moral_permissible" in scores:
            approval_factors += 1 if scores["moral_permissible"] else 0
            total_factors += 1

        if "value_alignment" in scores:
            approval_factors += 1 if scores["value_alignment"] > 0.7 else 0
            total_factors += 1

        if "bias_concerns" in scores:
            approval_factors += 1 if scores["bias_concerns"] <= 2 else 0
            total_factors += 1

        return (approval_factors / total_factors) >= 0.7 if total_factors > 0 else False

    async def _demonstrate_growth_analysis(self):
        """Demonstrate growth trajectory analysis"""
        print("\n📈 GROWTH TRAJECTORY ANALYSIS")
        print("-" * 50)

        if not self.growth_monitor:
            print("⚠️ Growth monitor not available for demonstration")
            return

        try:
            # Calculate current growth trajectory
            trajectory_slope = await self.growth_monitor.calculate_trajectory_slope()

            print(f"📈 Growth Metrics:")
            print(f"   • Trajectory Slope: {trajectory_slope:.3f}")

            # Record learning milestone from Phase 5 implementation
            milestone_id = await self.growth_monitor.record_learning_milestone(
                milestone_type="capability",
                description="Phase 5 Ethical Cognition and Metric Awareness implementation",
                significance_score=0.9,
                evidence=[
                    "Comprehensive ethics reasoning framework",
                    "Bias detection and mitigation system",
                    "Value alignment assessment capabilities",
                    "Self-awareness metrics dashboard",
                    "Growth trajectory monitoring",
                ],
                prerequisites_met=[
                    "Phase 4 night cycle intelligence",
                    "Memory system integration",
                    "Decision-making framework",
                ],
                future_implications=[
                    "Enhanced ethical decision making",
                    "Improved self-awareness",
                    "Better value alignment",
                    "Continuous growth monitoring",
                ],
            )

            print(f"   • Learning Milestone: {milestone_id[:12]}...")

            # Analyze growth patterns
            patterns = await self.growth_monitor.analyze_growth_patterns(days=7)

            if patterns.get("overall_growth"):
                growth_data = patterns["overall_growth"]
                print(f"   • Current Growth: {growth_data.get('current_slope', 0):.3f}")
                print(
                    f"   • Growth Acceleration: {growth_data.get('acceleration', 0):.3f}"
                )

        except Exception as e:
            print(f"   ❌ Error in growth analysis: {e}")

    async def _demonstrate_system_health(self):
        """Demonstrate system health overview"""
        print("\n🏥 SYSTEM HEALTH OVERVIEW")
        print("-" * 50)

        health_report = {
            "timestamp": datetime.now().isoformat(),
            "phase5_status": "operational",
            "components": {},
        }

        # Check ethics system health
        ethics_health = {
            "moral_reasoning": self.moral_engine is not None,
            "bias_detection": self.bias_detector is not None,
            "value_alignment": self.value_alignment is not None,
            "ethics_trace": self.ethics_trace is not None,
        }

        ethics_score = sum(ethics_health.values()) / len(ethics_health)
        health_report["components"]["ethics_system"] = {
            "score": ethics_score,
            "components": ethics_health,
        }

        # Check metrics system health
        metrics_health = {
            "metrics_dashboard": self.metrics_dashboard is not None,
            "memory_tracker": self.memory_tracker is not None,
            "growth_monitor": self.growth_monitor is not None,
        }

        metrics_score = sum(metrics_health.values()) / len(metrics_health)
        health_report["components"]["metrics_system"] = {
            "score": metrics_score,
            "components": metrics_health,
        }

        # Overall health
        overall_health = (ethics_score + metrics_score) / 2
        health_report["overall_health"] = overall_health

        print(f"🏥 System Health Report:")
        print(f"   • Overall Health: {overall_health:.1%}")
        print(f"   • Ethics System: {ethics_score:.1%}")
        print(f"   • Metrics System: {metrics_score:.1%}")

        if overall_health >= 0.8:
            print("   ✅ System operating at optimal capacity")
        elif overall_health >= 0.6:
            print("   ⚠️ System operating with minor limitations")
        else:
            print("   ❌ System requires attention")

        # Save health report
        report_file = Path("phase5_health_report.json")
        with open(report_file, "w") as f:
            json.dump(health_report, f, indent=2)

        print(f"   📄 Health report saved to: {report_file}")


async def main():
    """Main demonstration function"""

    # Create and run Phase 5 demonstration
    phase5_demo = Phase5EthicsAndMetrics()
    await phase5_demo.run_comprehensive_demonstration()


if __name__ == "__main__":
    asyncio.run(main())

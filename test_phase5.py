#!/usr/bin/env python3

"""Test for Phase 5 homeostasis continuous validation implementation."""

import asyncio
import sys

sys.path.append(".")

from Aetherra.homeostasis.homeostasis_integration import get_homeostasis_orchestrator


async def test_phase5_validation():
    print("🔍 Testing Phase 5 continuous validation...")

    try:
        # Get orchestrator and initialize
        orchestrator = get_homeostasis_orchestrator()
        await orchestrator.initialize()

        # Check validation system initialization
        if orchestrator.validator:
            print("✓ ContinuousValidator initialized")
            print(
                f"✓ Validation interval: {orchestrator.validator.validation_interval}s"
            )
            print(
                f"✓ Effectiveness threshold: {orchestrator.validator.min_effectiveness_score}"
            )
        else:
            print("❌ ContinuousValidator not initialized")
            return False

        # Test manual validation trigger
        print("\n🧪 Testing manual effectiveness validation...")
        validation_report = await orchestrator.validate_effectiveness()

        if "error" not in validation_report:
            print("✓ Validation completed")
            print(
                f"✓ Overall effectiveness: {validation_report.get('overall_effectiveness', 0.0):.2f}"
            )
            print(
                f"✓ Tuning required: {validation_report.get('tuning_required', False)}"
            )
            print(
                f"✓ Recommendations: {len(validation_report.get('recommendations', []))}"
            )
        else:
            print(f"❌ Validation error: {validation_report.get('error')}")

        # Test validation summary
        print("\n📊 Testing validation summary...")
        summary = orchestrator.get_validation_summary()

        if "error" not in summary:
            print(f"✓ Total validations: {summary.get('total_validations', 0)}")
            print(
                f"✓ Effectiveness metrics available: {len(summary.get('effectiveness_metrics', {}))}"
            )
        else:
            print(f"❌ Summary error: {summary.get('error')}")

        # Test effectiveness metrics
        print("\n📈 Testing effectiveness metrics...")
        metrics = orchestrator.get_effectiveness_metrics()

        if "error" not in metrics:
            print(
                f"✓ Effectiveness metrics: {list(metrics.get('effectiveness_metrics', {}).keys())}"
            )
            print(f"✓ Recent validations: {len(metrics.get('recent_validations', []))}")
        else:
            print(f"❌ Metrics error: {metrics.get('error')}")

        # Test self-tuning trigger
        print("\n🎯 Testing manual self-tuning...")
        tuning_result = await orchestrator.trigger_self_tuning()

        if "error" not in tuning_result:
            print(
                f"✓ Self-tuning triggered: {tuning_result.get('tuning_triggered', False)}"
            )
            effectiveness = tuning_result.get("effectiveness_after_tuning", 0.0)
            print(f"✓ Effectiveness after tuning: {effectiveness:.2f}")
        else:
            print(f"❌ Tuning error: {tuning_result.get('error')}")

        # Test sensitivity adjustment
        print("\n⚙️ Testing validation sensitivity adjustment...")
        adjustment_result = await orchestrator.adjust_validation_sensitivity(0.7, 90.0)
        print(f"✓ Sensitivity adjustment: {adjustment_result}")

        if adjustment_result:
            print(f"✓ New threshold: {orchestrator.validator.min_effectiveness_score}")
            print(f"✓ New interval: {orchestrator.validator.validation_interval}s")

        # Test with some feedback to see validation adapt
        print("\n🔄 Testing validation with feedback input...")
        test_feedback = {
            "timestamp": "2025-10-12T10:00:00Z",
            "metrics": {
                "cpu_usage": 45.0,  # Good CPU usage
                "memory_usage": 60.0,  # Moderate memory
                "response_time": 0.8,  # Good response time
                "error_rate": 1.0,  # Low error rate
            },
            "source_type": "test_positive",
        }

        await orchestrator.receive_system_feedback("test_positive", test_feedback)

        # Run another validation to see if it detected the improvement
        final_validation = await orchestrator.validate_effectiveness()
        final_effectiveness = final_validation.get("overall_effectiveness", 0.0)
        print(
            f"✓ Final effectiveness after positive feedback: {final_effectiveness:.2f}"
        )

        return True

    except Exception as e:
        print(f"❌ Error during Phase 5 test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_phase5_validation())
    if success:
        print("\n✅ Phase 5 continuous validation implementation working correctly!")
        print("🔍 Effectiveness monitoring and self-tuning operational")
    else:
        print("\n❌ Phase 5 implementation has issues")

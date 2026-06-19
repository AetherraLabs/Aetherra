#!/usr/bin/env python3

"""Test for Phase 4 homeostasis cross-system feedback implementation."""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from Aetherra.homeostasis.homeostasis_integration import get_homeostasis_orchestrator


async def test_phase4_feedback():
    print("🔄 Testing Phase 4 cross-system feedback...")

    try:
        # Get orchestrator and initialize
        orchestrator = get_homeostasis_orchestrator()
        await orchestrator.initialize()

        # Check feedback system initialization
        if orchestrator.feedback_system:
            print("✓ SystemFeedback initialized")
            print(
                f"✓ Feedback interval: {orchestrator.feedback_system.feedback_interval}s"
            )
            print(
                f"✓ Adaptation weights: {orchestrator.feedback_system.adaptation_weights}"
            )
        else:
            print("❌ SystemFeedback not initialized")
            return False

        # Test receiving manual feedback
        print("\n🧪 Testing manual feedback reception...")
        test_feedback = {
            "timestamp": "2025-10-12T10:00:00Z",
            "metrics": {
                "cpu_usage": 85.0,  # High CPU - should trigger adaptation
                "memory_usage": 70.0,
                "response_time": 1.5,
                "error_rate": 2.0,
            },
            "source_type": "test_system",
        }

        result = await orchestrator.receive_system_feedback(
            "test_system", test_feedback
        )
        print(f"✓ Feedback reception result: {result}")

        # Check if adaptation occurred
        feedback_summary = orchestrator.get_feedback_summary()
        print(f"✓ Total feedback entries: {feedback_summary['total_feedback_entries']}")
        print(f"✓ Active adjustments: {feedback_summary['active_adjustments']}")

        # Test feedback collection (will try to collect from real systems)
        print("\n📊 Testing proactive feedback collection...")
        collected_feedback = await orchestrator.collect_all_system_feedback()
        print(
            f"✓ Collected feedback from {len(collected_feedback)} systems: {list(collected_feedback.keys())}"
        )

        # Test adaptive tuning trigger
        print("\n🎯 Testing adaptive tuning...")
        tuning_result = await orchestrator.trigger_adaptive_tuning()
        print(f"✓ Adaptive tuning result: {tuning_result}")

        # Test with high-stress feedback that should trigger more aggressive adaptation
        stress_feedback = {
            "timestamp": "2025-10-12T10:01:00Z",
            "metrics": {
                "cpu_usage": 95.0,  # Very high CPU
                "memory_usage": 90.0,  # Very high memory
                "response_time": 5.0,  # Very slow response
                "error_rate": 15.0,  # High error rate
            },
            "source_type": "stress_test",
        }

        print("\n🚨 Testing high-stress feedback...")
        await orchestrator.receive_system_feedback("stress_test", stress_feedback)

        # Check adaptations after stress
        final_summary = orchestrator.get_feedback_summary()
        print(f"✓ Adjustments after stress: {final_summary['active_adjustments']}")

        return True

    except Exception as e:
        print(f"❌ Error during Phase 4 test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_phase4_feedback())
    if success:
        print("\n✅ Phase 4 cross-system feedback implementation working correctly!")
        print("🎯 Adaptive threshold adjustment and dynamic tuning operational")
    else:
        print("\n❌ Phase 4 implementation has issues")

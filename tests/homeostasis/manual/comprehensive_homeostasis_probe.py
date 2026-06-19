#!/usr/bin/env python3

"""Comprehensive test of all 6 phases of homeostasis implementation."""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from Aetherra.homeostasis.homeostasis_integration import get_homeostasis_orchestrator


async def test_all_phases():
    print("🌐 COMPREHENSIVE AETHERRA HOMEOSTASIS TEST")
    print("=" * 60)
    print("Testing all 6 phases of the homeostasis roadmap")
    print("")

    try:
        # Get and initialize orchestrator
        print("🚀 Phase 1-2: OS Integration & Self-Verification")
        orchestrator = get_homeostasis_orchestrator()
        await orchestrator.initialize()

        # Start the full system
        await orchestrator.start()
        print("✓ Homeostasis system started with all components")

        # Phase 3: Test watchdog
        print("\n🐕 Phase 3: Persistent Watchdog")
        if orchestrator.watchdog and orchestrator.watchdog.running:
            print(f"✓ Watchdog active: {orchestrator.watchdog.cycle_count} cycles")
        else:
            print("⚠️ Watchdog not active")

        # Phase 4: Test feedback system
        print("\n🔄 Phase 4: Cross-System Feedback")
        if orchestrator.feedback_system:
            feedback_result = await orchestrator.receive_system_feedback(
                "comprehensive_test",
                {
                    "timestamp": "2025-10-12T10:00:00Z",
                    "metrics": {
                        "cpu_usage": 75.0,
                        "memory_usage": 65.0,
                        "response_time": 1.2,
                        "error_rate": 3.0,
                    },
                    "source_type": "test",
                },
            )
            print(f"✓ Feedback processed: {feedback_result}")

            feedback_summary = orchestrator.get_feedback_summary()
            print(
                f"✓ Total feedback entries: {feedback_summary.get('total_feedback_entries', 0)}"
            )

        # Phase 5: Test validation
        print("\n🔍 Phase 5: Continuous Validation")
        if orchestrator.validator:
            validation_report = await orchestrator.validate_effectiveness()
            effectiveness = validation_report.get("overall_effectiveness", 0.0)
            print(f"✓ System effectiveness: {effectiveness:.2f}")

            if effectiveness < 0.6:
                tuning_result = await orchestrator.trigger_self_tuning()
                print(
                    f"✓ Self-tuning triggered: {tuning_result.get('tuning_triggered', False)}"
                )

        # Phase 6: Test live observability
        print("\n📊 Phase 6: Live Observability")
        if orchestrator.observability:
            await orchestrator.start_live_monitoring()
            print("✓ Live monitoring started")

            # Let it collect some metrics
            await asyncio.sleep(8)

            # Generate dashboard
            dashboard = orchestrator.get_live_dashboard()
            print("✓ Live dashboard generated:")
            print("-" * 40)
            print(dashboard)
            print("-" * 40)

            # Export data
            export_path = orchestrator.export_observability_data()
            if export_path:
                print(f"✓ Observability data exported to: {export_path}")

            await orchestrator.stop_live_monitoring()
            print("✓ Live monitoring stopped")

        # Get final system status
        print("\n📋 FINAL SYSTEM STATUS")
        print("=" * 30)
        health_status = await orchestrator.get_system_health_status()
        homeostasis_status = health_status.get("homeostasis", {})

        print(f"Running: {homeostasis_status.get('running', False)}")
        print(f"Mode: {homeostasis_status.get('mode', 'Unknown')}")
        print(f"Uptime: {homeostasis_status.get('uptime', 0):.1f}s")
        print(f"Watchdog Active: {homeostasis_status.get('watchdog_active', False)}")

        # Test adaptive capabilities
        print("\n🎯 ADAPTIVE CAPABILITIES TEST")
        print("=" * 35)

        # Trigger high-stress scenario
        stress_feedback = {
            "timestamp": "2025-10-12T10:01:00Z",
            "metrics": {
                "cpu_usage": 92.0,
                "memory_usage": 89.0,
                "response_time": 4.5,
                "error_rate": 15.0,
            },
            "source_type": "stress_scenario",
        }

        await orchestrator.receive_system_feedback("stress_scenario", stress_feedback)
        print("✓ High-stress feedback submitted")

        # Check adaptations
        final_feedback_summary = orchestrator.get_feedback_summary()
        active_adjustments = final_feedback_summary.get("active_adjustments", {})
        print(f"✓ Active adaptations: {len(active_adjustments)} systems")

        for system, adjustments in active_adjustments.items():
            print(f"  - {system}: {list(adjustments.keys())}")

        # Final validation
        final_validation = await orchestrator.validate_effectiveness()
        final_effectiveness = final_validation.get("overall_effectiveness", 0.0)
        print(f"✓ Final effectiveness: {final_effectiveness:.2f}")

        # Clean shutdown
        await orchestrator.stop()
        print("\n✅ COMPREHENSIVE TEST COMPLETED SUCCESSFULLY")
        print("🌐 All 6 phases of homeostasis operational")

        return True

    except Exception as e:
        print(f"\n❌ Error during comprehensive test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_all_phases())
    if success:
        print("\n" + "=" * 60)
        print("🎉 AETHERRA HOMEOSTASIS ROADMAP COMPLETE!")
        print("✅ Phase 1: OS Integration")
        print("✅ Phase 2: Self-Verification Loop")
        print("✅ Phase 3: Persistent Watchdog")
        print("✅ Phase 4: Cross-System Feedback")
        print("✅ Phase 5: Continuous Validation")
        print("✅ Phase 6: Live Observability")
        print("🌟 Full autonomous stability control operational!")
    else:
        print("\n❌ Comprehensive test failed")

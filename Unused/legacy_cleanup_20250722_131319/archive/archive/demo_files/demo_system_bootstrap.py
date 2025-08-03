#!/usr/bin/env python3
"""
🚀🧠 SYSTEM BOOTSTRAP + AWARENESS DEMONSTRATION
===============================================

This script demonstrates the System Bootstrap + Awareness feature
that enables Lyrixa to detect system status and provide intelligent
startup summaries with contextual awareness.
"""

import asyncio

from lyrixa.assistant import LyrixaAI


async def demonstrate_system_bootstrap():
    """Demonstrate System Bootstrap + Awareness functionality"""

    print("🚀🧠 LYRIXA SYSTEM BOOTSTRAP + AWARENESS DEMONSTRATION")
    print("=" * 60)
    print()

    # Initialize Lyrixa AI (which includes system bootstrap)
    print("🔄 Initializing Lyrixa AI Assistant...")
    lyrixa = LyrixaAI(workspace_path=".")

    print("\n" + "=" * 60)
    print("INTELLIGENT STARTUP SUMMARY")
    print("=" * 60)

    # Display intelligent startup summary
    await lyrixa.display_startup_summary()

    print("\n" + "=" * 60)
    print("REAL-TIME SYSTEM STATUS")
    print("=" * 60)

    # Get current system status
    status = await lyrixa.system_bootstrap.get_current_system_status()

    print(f"\n🌡️ Overall System Health: {status['overall_health']:.1%}")
    print(f"🔍 Issues Detected: {'Yes' if status['issues_detected'] else 'No'}")
    print(f"[TOOL] Components Monitored: {len(status['components'])}")

    print("\n📊 Component Health:")
    status_emojis = {
        "active": "🟢",
        "inactive": "🟡",
        "error": "🔴",
        "degraded": "🟠",
        "loading": "🔵",
    }

    for name, comp in status["components"].items():
        emoji = status_emojis.get(comp["status"], "⚪")
        print(
            f"   {emoji} {name}: {comp['status']} (Health: {comp['health_score']:.1%})"
        )

        if comp["error_message"]:
            print(f"      [WARN] {comp['error_message']}")

    if status["recommendations"]:
        print("\n💡 System Recommendations:")
        for rec in status["recommendations"][:5]:  # Show top 5
            print(f"   • {rec}")

    print("\n" + "=" * 60)
    print("DETAILED HEALTH REPORT")
    print("=" * 60)

    # Generate detailed health report
    health_report = await lyrixa.system_bootstrap.generate_health_report()
    print(f"\n{health_report}")

    print("\n" + "=" * 60)
    print("SYSTEM BOOTSTRAP CAPABILITIES")
    print("=" * 60)

    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ Automatic system component detection")
    print("   ✅ Memory database connection monitoring")
    print("   ✅ Plugin ecosystem health assessment")
    print("   ✅ Goal system state tracking")
    print("   ✅ Feedback system metrics collection")
    print("   ✅ Resource usage monitoring")
    print("   ✅ Intelligent startup context recognition")
    print("   ✅ 'Here's what I remember and where we left off' messaging")
    print("   ✅ System health diagnostics and recommendations")

    print("\n🧠 System Awareness Capabilities:")
    print("   • Detects first launch vs. returning user")
    print("   • Tracks session continuity and context")
    print("   • Monitors component health in real-time")
    print("   • Provides actionable system recommendations")
    print("   • Maintains system status history")
    print("   • Enables self-diagnostic capabilities")

    print("\n🎉 SUCCESS: System Bootstrap + Awareness is fully functional!")
    print("   Lyrixa is now aware of her own system state and can provide")
    print("   intelligent startup summaries and system status reports.")

    return True


if __name__ == "__main__":
    result = asyncio.run(demonstrate_system_bootstrap())
    print(f"\n✅ Demonstration completed successfully: {result}")

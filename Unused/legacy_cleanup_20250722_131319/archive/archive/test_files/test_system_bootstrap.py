#!/usr/bin/env python3
"""Test the System Bootstrap + Awareness functionality"""

import asyncio

from lyrixa.assistant import LyrixaAI


async def test_system_bootstrap():
    """Test system bootstrap and awareness"""
    print("🧪 Testing Lyrixa System Bootstrap + Awareness...")

    # Initialize Lyrixa
    lyrixa = LyrixaAI(workspace_path=".")

    print("\n" + "=" * 60)
    print("TESTING STARTUP SUMMARY")
    print("=" * 60)

    # Test startup summary
    startup_summary = await lyrixa.display_startup_summary()

    print("\n" + "=" * 60)
    print("TESTING SYSTEM STATUS")
    print("=" * 60)

    # Test current system status
    status = await lyrixa.system_bootstrap.get_current_system_status()
    print(f"\n🌡️ Overall Health: {status['overall_health']:.1%}")
    print(f"🔍 Issues Detected: {status['issues_detected']}")

    print("\n📊 Component Status:")
    for name, comp in status["components"].items():
        status_emoji = {
            "active": "🟢",
            "inactive": "🟡",
            "error": "🔴",
            "degraded": "🟠",
        }
        emoji = status_emoji.get(comp["status"], "⚪")
        print(
            f"   {emoji} {name}: {comp['status']} (Health: {comp['health_score']:.1%})"
        )

    if status["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in status["recommendations"]:
            print(f"   • {rec}")

    print("\n" + "=" * 60)
    print("TESTING HEALTH REPORT")
    print("=" * 60)

    # Test health report
    health_report = await lyrixa.system_bootstrap.generate_health_report()
    print(f"\n{health_report}")

    print("\n✅ System Bootstrap + Awareness test completed!")


if __name__ == "__main__":
    asyncio.run(test_system_bootstrap())

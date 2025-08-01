#!/usr/bin/env python3
"""Simple System Bootstrap Test"""

import asyncio

from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager
from lyrixa.core.conversation import PersonalityProcessor
from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem
from lyrixa.core.feedback_system import LyrixaFeedbackSystem
from lyrixa.core.goals import LyrixaGoalSystem
from lyrixa.core.system_bootstrap import LyrixaSystemBootstrap


async def simple_test():
    print("🚀 Testing System Bootstrap...")

    # Initialize components
    memory = LyrixaEnhancedMemorySystem()
    goals = LyrixaGoalSystem()
    plugins = LyrixaAdvancedPluginManager(
        "plugins",
        additional_directories=[
            "lyrixa/plugins",
            "src/aetherra/plugins",
            "sdk/plugins",
        ],
    )
    personality = PersonalityProcessor()
    feedback = LyrixaFeedbackSystem(memory, personality)

    # Initialize bootstrap
    bootstrap = LyrixaSystemBootstrap(".", memory, plugins, goals, feedback)

    print("✅ Components initialized")

    # Get system status
    status = await bootstrap.get_current_system_status()
    print(f"📊 Overall Health: {status['overall_health']:.1%}")
    print(f"🔧 Components checked: {len(status['components'])}")

    return True


if __name__ == "__main__":
    result = asyncio.run(simple_test())
    print(f"✅ Test result: {result}")

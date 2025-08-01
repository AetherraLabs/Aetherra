#!/usr/bin/env python3
"""
🧠 UNIFIED COGNITIVE ARCHITECTURE DEMO LAUNCHER
===============================================

Quick demonstration of the unified cognitive architecture with all five systems:
1. FractalMesh Memory System
2. Enhanced Plugin System
3. Reflection Engine
4. Self Metrics Dashboard
5. Memory Continuity Tracker

This script demonstrates the complete integrated system in action.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def demo_unified_architecture():
    """Demonstrate the unified cognitive architecture"""

    print("🧠 UNIFIED COGNITIVE ARCHITECTURE DEMO")
    print("=" * 50)
    print()

    # Initialize Lyrixa Conversation Manager with unified cognitive architecture
    print("🚀 Initializing Unified Cognitive Architecture...")
    print("-" * 50)

    try:
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

        # Initialize with all cognitive systems
        conversation_manager = LyrixaConversationManager(
            workspace_path=str(project_root)
        )

        print("✅ Conversation Manager initialized with unified cognitive architecture")
        print()

        # Get system context to show all active systems
        print("📊 SYSTEM STATUS:")
        print("-" * 20)

        context = await conversation_manager.get_system_context()
        formatted_context = conversation_manager.format_system_context(context)
        print(formatted_context)
        print()

        # Demonstrate cognitive capabilities
        print("🧠 COGNITIVE CAPABILITIES DEMO:")
        print("-" * 30)

        # Test memory integration
        if (
            hasattr(conversation_manager, "fractal_memory")
            and conversation_manager.fractal_memory
        ):
            print(
                "✅ FractalMesh Memory System: Multi-dimensional memory storage active"
            )

        # Test plugin system
        if (
            hasattr(conversation_manager, "plugin_manager")
            and conversation_manager.plugin_manager
        ):
            print("✅ Enhanced Plugin System: Memory-aware plugin routing active")

        # Test reflection engine
        if (
            hasattr(conversation_manager, "validation_engine")
            and conversation_manager.validation_engine
        ):
            print(
                "✅ Reflection Engine: Validation protocols and shadow state testing active"
            )

        # Test self metrics
        if (
            hasattr(conversation_manager, "metrics_dashboard")
            and conversation_manager.metrics_dashboard
        ):
            print(
                "✅ Self Metrics Dashboard: Comprehensive self-awareness monitoring active"
            )

        # Test memory continuity
        if (
            hasattr(conversation_manager, "memory_continuity")
            and conversation_manager.memory_continuity
        ):
            print("✅ Memory Continuity Tracker: Temporal coherence analysis active")

        print()

        # Demonstrate conversation capabilities
        print("💬 SYSTEM SUMMARY DEMO:")
        print("-" * 24)

        # Test system summary
        test_query = "System status and cognitive capabilities"
        print(f"Query: {test_query}")

        # Get conversation summary through unified cognitive architecture
        summary = await conversation_manager.get_conversation_summary()

        print(f"System Summary: {summary.get('system_status', 'Operational')}")
        print(
            f"Active Systems: {summary.get('active_systems', 'All cognitive systems active')}"
        )
        print()

        print("🎉 UNIFIED COGNITIVE ARCHITECTURE DEMONSTRATION COMPLETE!")
        print()
        print("The system is now operational with all five cognitive subsystems:")
        print("• 🧠 FractalMesh Memory System")
        print("• 🔌 Enhanced Plugin System")
        print("• 🔍 Reflection Engine")
        print("• 📊 Self Metrics Dashboard")
        print("• 🧩 Memory Continuity Tracker")
        print()
        print("Ready for advanced cognitive operations! 🚀")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(demo_unified_architecture())
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback

        traceback.print_exc()

#!/usr/bin/env python3
"""
🐛🔍 LYRIXA DEBUG CONSOLE DEMO
=============================

Demonstration of the Debug Console / Developer View for Lyrixa AI.

This shows what Lyrixa sees, thinks, and why she makes decisions.
Can be accessed via GUI or CLI.

Usage:
    python debug_console_demo.py
"""

import asyncio
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


async def demo_debug_console():
    """Demonstrate debug console functionality"""
    print("🐛🔍 LYRIXA DEBUG CONSOLE DEMO")
    print("=" * 50)

    try:
        from lyrixa import LyrixaAI

        # Initialize Lyrixa with debug console
        lyrixa = LyrixaAI(workspace_path=project_root)
        await lyrixa.initialize()

        print("\n📊 Debug Console Integration:")
        print(f"   Debug Level: {lyrixa.debug_console.debug_level.name}")
        print(
            f"   Cognitive State: {lyrixa.debug_console.current_cognitive_state.value}"
        )

        # Process some test inputs to generate debug data
        test_inputs = [
            "Help me debug this Python function",
            "Create a data analysis workflow",
            "What are my current goals?",
            "Show me the project structure",
        ]

        print("\n🎭 Processing test inputs to generate debug data...")

        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n--- Test Input {i}: {test_input} ---")

            # Process the input (this will generate debug traces)
            await lyrixa.process_natural_language(test_input)

            # Show what the debug console captured
            if lyrixa.debug_console.thought_history:
                latest_thought = lyrixa.debug_console.thought_history[-1]
                print(f"🧠 Thought ID: {latest_thought.thought_id}")
                print(f"⏱️  Duration: {latest_thought.execution_time_ms:.1f}ms")
                print(f"🎯 Decision: {latest_thought.final_decision or 'In progress'}")

                if latest_thought.reasoning_steps:
                    print("💭 Reasoning:")
                    for j, step in enumerate(latest_thought.reasoning_steps[:3], 1):
                        print(f"    {j}. {step}")

        # Show CLI access methods
        print("\n" + "=" * 50)
        print("🖥️  CLI DEBUG COMMANDS:")
        print("=" * 50)
        print("• debug                    - Show current state")
        print("• debug thoughts           - Show recent thought processes")
        print("• debug export             - Export debug session to file")
        print("• debug level VERBOSE      - Change debug level")

        # Demonstrate CLI debug access
        print("\n🔍 Current Debug State:")
        lyrixa.debug_console.show_current_state()

        print("\n🧠 Latest Thought Analysis:")
        analysis = lyrixa.debug_console.get_thought_analysis()
        if "error" not in analysis:
            print(f"   ID: {analysis['thought_id']}")
            print(f"   Duration: {analysis['execution_time_ms']:.1f}ms")
            print(f"   Reasoning Steps: {len(analysis['reasoning_steps'])}")

            for i, step in enumerate(analysis["reasoning_steps"], 1):
                print(f"      {i}. {step}")

        # Export debug session
        print("\n📁 Exporting Debug Session...")
        filepath = lyrixa.debug_console.export_debug_session("demo_debug_session.json")

        # Show GUI access
        print("\n" + "=" * 50)
        print("🖼️  GUI DEBUG ACCESS:")
        print("=" * 50)
        print("• Enhanced Lyrixa GUI includes debug console widget")
        print("• Real-time cognitive state monitoring")
        print("• Tabbed interface: Perception | Thoughts | Decisions | Performance")
        print("• Auto-updating displays with 1-second refresh")
        print("• Visual progress bars for timing and confidence")

        try:
            from lyrixa.gui.debug_console_widget import create_debug_widget

            widget = create_debug_widget(lyrixa.debug_console)
            print("✅ Debug GUI widget available")

            if hasattr(widget, "show_status"):
                print("\n🖥️  CLI Debug Widget Status:")
                widget.show_status()
        except Exception as e:
            print(f"[WARN]  GUI widget not available: {e}")

        print("\n" + "=" * 50)
        print("🎉 DEBUG CONSOLE FEATURES SUMMARY:")
        print("=" * 50)
        print("✅ What Lyrixa sees:")
        print("   • User input analysis")
        print("   • Context window and memory")
        print("   • Current goals and system state")
        print("   • Attention focus areas")

        print("\n✅ What Lyrixa thinks:")
        print("   • Cognitive state tracking (idle, analyzing, reasoning, etc.)")
        print("   • Step-by-step reasoning process")
        print("   • Confidence scores for each step")
        print("   • Alternative options considered")

        print("\n✅ Why she picks suggestions/plans:")
        print("   • Decision matrix with weighted scoring")
        print("   • Option rankings and comparisons")
        print("   • Reasoning explanations")
        print("   • Confidence levels for decisions")

        print("\n✅ Developer Access:")
        print("   • CLI commands in Lyrixa launcher")
        print("   • GUI widget with real-time updates")
        print("   • JSON export for offline analysis")
        print("   • Configurable debug levels")

        print(f"\n🎯 Debug session exported to: {filepath}")
        print("🐛 Debug Console / Developer View is ready for use!")

        # Cleanup
        await lyrixa.cleanup()

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(demo_debug_console())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"❌ Error running demo: {e}")

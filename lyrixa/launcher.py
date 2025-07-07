#!/usr/bin/env python3
"""
🎙️ LYRIXA AI ASSISTANT LAUNCHER
===============================

Launch the new Python-based Lyrixa AI Assistant for Aetherra.
Enhanced with Aether Runtime integration for AI OS capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent  # Go up one level to project root
sys.path.insert(0, str(project_root))

try:
    from Aetherra.runtime.aether_runtime import AetherRuntime
    from lyrixa import LyrixaAI
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


async def main():
    """Main entry point for Lyrixa AI Assistant with Aether Runtime integration"""
    print("🎙️ Starting Lyrixa AI Assistant for Aetherra...")
    print("🚀 Initializing AI OS Kernel...")

    # Initialize Lyrixa
    workspace_path = str(project_root)
    lyrixa = LyrixaAI(workspace_path=workspace_path)

    try:
        # Initialize all systems
        await lyrixa.initialize()

        # Initialize Aether Runtime and connect to Lyrixa's ecosystem
        print("\n🔮 Initializing Aether Runtime...")
        aether_runtime = AetherRuntime()

        # Connect Lyrixa's systems to the Aether Runtime
        aether_runtime.register_context(
            memory=getattr(lyrixa, "memory_system", None),
            plugins=getattr(lyrixa, "plugin_manager", None),
            agents=getattr(lyrixa, "agent_system", None),
        )

        # Store runtime reference in lyrixa for chat integration
        lyrixa.aether_runtime = aether_runtime

        print("\n" + "=" * 60)
        print("🎙️ LYRIXA AI ASSISTANT READY")
        print("🔮 AETHER RUNTIME INTEGRATED")
        print("=" * 60)
        print(
            "Type 'help' for assistance, 'status' for system info, or 'quit' to exit."
        )
        print("You can also ask me anything in natural language!")
        print("💡 NEW: Use .aether commands for AI OS operations!")
        print("   Example: 'run this .aether script: goal \"test goal\"'")
        print()

        # Interactive loop
        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("👋 Goodbye! Thanks for using Lyrixa!")
                    break

                elif user_input.lower() == "status":
                    status = await lyrixa.get_system_status()
                    print(f"""
🎙️ **LYRIXA SYSTEM STATUS**
Session: {status["session_id"][:8]}...
Workspace: {status["workspace_path"]}
Conversation Length: {status["conversation_length"]} exchanges

💾 Memory: {status["memory_system"]["total_memories"]} memories
🎯 Goals: {status["goal_system"]["active_goals"]} active, {status["goal_system"]["completed_goals"]} completed
🧩 Plugins: {status["plugin_system"]["loaded_plugins"]} loaded
🤖 Agents: {status["agent_system"].__len__()} specialized agents
⚡ Workflows: {status["aether_interpreter"]["execution_history"]} executed
""")
                    continue

                elif user_input.lower() == "help":
                    print("""
🎙️ **LYRIXA AI ASSISTANT HELP**

I'm your AI assistant for Aetherra development. Here's what I can do:

**Natural Language Commands:**
• "Create a data analysis workflow"
• "Remember that I prefer Python for scripting"
• "Show me my active goals"
• "List the files in my project"
• "Execute a web search for machine learning"
• "Plan a testing workflow for my code"

**System Commands:**
• `status` - Show system status
• `aether status` - Show Aether Runtime status
• `bootstrap` - Run bootstrap.aether script
• `debug` - Show debug console state
• `debug thoughts` - Show recent thought processes
• `debug export` - Export debug session to file
• `debug level <LEVEL>` - Change debug level (MINIMAL, STANDARD, DETAILED, VERBOSE, TRACE)
• `help` - Show this help
• `quit` - Exit Lyrixa

**.aether Commands:**
• "run this .aether script: goal \"my goal\""
• "load .aether file: path/to/script.aether"
• "goal \"summarize today's work\""
• "use plugin \"DailyLogSummarizer\""
• "recall \"recent goals\" → $goals"
• "run agent \"Summarizer\" with $goals"
• "store $result in memory"

**Core Capabilities:**
🎯 Goal & Task Management - Set and track development goals
🧠 Memory System - Remember preferences and context
🧩 Plugin Ecosystem - Execute various tools and integrations
⚡ .aether Workflows - Generate and execute .aether code
🤖 Agent Orchestration - Coordinate specialized AI agents
📁 Project Intelligence - Understand and navigate your codebase

🐛 **Debug Console Features:**
• See what Lyrixa perceives in real-time
• View her reasoning process and decision making
• Understand why she picks specific suggestions
• Export debug sessions for analysis
""")
                    continue

                # Handle debug console commands
                elif user_input.lower().startswith("debug"):
                    parts = user_input.lower().split()

                    if len(parts) == 1:  # Just "debug"
                        debug_state = lyrixa.debug_console.show_current_state()
                        print(f"""
🐛 **DEBUG CONSOLE STATE**
Current cognitive state: {debug_state["cognitive_state"]}
Debug level: {debug_state["debug_level"]}
Recent decisions: {debug_state["recent_decision_count"]}
Average decision time: {debug_state["avg_decision_time"]:.1f}ms
Average confidence: {debug_state["avg_confidence"]:.2f}
""")

                    elif len(parts) >= 2 and parts[1] == "thoughts":
                        analysis = lyrixa.debug_console.get_thought_analysis()
                        if "error" in analysis:
                            print(f"🐛 {analysis['error']}")
                        else:
                            print(f"""
🐛 **LATEST THOUGHT PROCESS**
ID: {analysis["thought_id"]}
Duration: {analysis["execution_time_ms"]:.1f}ms
Reasoning steps: {len(analysis["reasoning_steps"])}

🧠 **Reasoning Process:**""")
                            for i, step in enumerate(analysis["reasoning_steps"], 1):
                                print(f"   {i}. {step}")

                            if analysis["final_decision"]:
                                print(
                                    f"\n✅ Final Decision: {analysis['final_decision']}"
                                )

                    elif len(parts) >= 2 and parts[1] == "export":
                        filepath = lyrixa.debug_console.export_debug_session()
                        print(f"🐛 Debug session exported to: {filepath}")

                    elif len(parts) >= 3 and parts[1] == "level":
                        level_name = parts[2].upper()
                        try:
                            from lyrixa.core.debug_console import DebugLevel

                            level = DebugLevel[level_name]
                            lyrixa.debug_console.toggle_debug_level(level)
                            print(f"🐛 Debug level changed to: {level.name}")
                        except KeyError:
                            print(f"🐛 Invalid debug level: {level_name}")
                            print(
                                "Valid levels: MINIMAL, STANDARD, DETAILED, VERBOSE, TRACE"
                            )

                    else:
                        print("🐛 Debug commands:")
                        print("   debug - Show current state")
                        print("   debug thoughts - Show recent thought processes")
                        print("   debug export - Export session to file")
                        print("   debug level <LEVEL> - Change debug level")

                    continue

                # Check for .aether commands
                if ".aether" in user_input.lower():
                    print("🔮 Detected .aether command...")

                    # Extract .aether script from user input
                    if "run this .aether script:" in user_input.lower():
                        # Extract the script part
                        script_start = user_input.lower().find(
                            "run this .aether script:"
                        ) + len("run this .aether script:")
                        aether_script = user_input[script_start:].strip()

                        print(f"🔮 Executing .aether script: {aether_script}")
                        try:
                            aether_runtime.execute_goal(aether_script)
                        except Exception as e:
                            print(f"❌ .aether execution failed: {e}")
                        continue

                    # Check for individual .aether commands
                    elif any(
                        cmd in user_input
                        for cmd in [
                            "goal ",
                            "use plugin ",
                            "recall ",
                            "run agent ",
                            "store ",
                        ]
                    ):
                        print(f"🔮 Executing .aether instruction: {user_input}")
                        try:
                            success = aether_runtime.interpret_aether_line(user_input)
                            if not success:
                                print(
                                    "💡 Try: 'goal \"my goal\"', 'use plugin \"name\"', 'recall \"query\" → $var'"
                                )
                        except Exception as e:
                            print(f"❌ .aether command failed: {e}")
                        continue

                    # Load .aether file
                    elif "load .aether file:" in user_input.lower():
                        file_start = user_input.lower().find(
                            "load .aether file:"
                        ) + len("load .aether file:")
                        file_path = user_input[file_start:].strip()

                        print(f"📁 Loading .aether file: {file_path}")
                        try:
                            aether_runtime.load_aether_goal(file_path)
                        except Exception as e:
                            print(f"❌ Failed to load .aether file: {e}")
                        continue

                # Special commands for Aether Runtime
                elif user_input.lower() in ["aether status", ".aether status"]:
                    stats = aether_runtime.get_execution_stats()
                    print("🔮 Aether Runtime Status:")
                    print(f"   🎯 Goals completed: {stats['goals_completed']}")
                    print(f"   ❌ Goals failed: {stats['goals_failed']}")
                    print(f"   📝 Variables set: {stats['variables_set']}")
                    print(f"   🎯 Goals defined: {stats['goals_defined']}")
                    print(f"   📋 Queue size: {stats['queue_size']}")
                    continue

                elif user_input.lower() in ["bootstrap", "run bootstrap"]:
                    print("🚀 Running bootstrap.aether...")
                    try:
                        bootstrap_path = project_root / "bootstrap.aether"
                        if bootstrap_path.exists():
                            aether_runtime.load_aether_goal(str(bootstrap_path))
                        else:
                            print("❌ bootstrap.aether file not found")
                    except Exception as e:
                        print(f"❌ Bootstrap failed: {e}")
                    continue

                # Process natural language input
                print("🎙️ Lyrixa: Processing...")
                response = await lyrixa.process_natural_language(user_input)

                print(f"🎙️ Lyrixa: {response['lyrixa_response']}")

                # Show suggestions if available
                if response.get("suggestions"):
                    print(f"\n💡 Suggestions: {', '.join(response['suggestions'][:3])}")

                print()  # Empty line for readability

            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using Lyrixa!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("I'm still here! Try asking me something else.")
                continue

    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for using Lyrixa!")
    except Exception as e:
        print(f"❌ Failed to start Lyrixa: {e}")
    finally:
        # Cleanup
        try:
            await lyrixa.cleanup()
        except Exception:
            pass


def run_lyrixa():
    """Synchronous wrapper for running Lyrixa"""
    try:
        if sys.platform == "win32":
            # Windows-specific event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Failed to run Lyrixa: {e}")


if __name__ == "__main__":
    run_lyrixa()

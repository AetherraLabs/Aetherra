#!/usr/bin/env python3
"""
🎙️ LYRIXA AI ASSISTANT LAUNCHER
===============================

Launch the new Python-based Lyrixa AI Assistant for Aetherra.
This replaces the legacy web-based implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from lyrixa import LyrixaAI
except ImportError as e:
    print(f"❌ Failed to import Lyrixa: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


async def main():
    """Main entry point for Lyrixa AI Assistant"""
    print("🎙️ Starting Lyrixa AI Assistant for Aetherra...")

    # Initialize Lyrixa
    workspace_path = str(project_root)
    lyrixa = LyrixaAI(workspace_path=workspace_path)

    try:
        # Initialize all systems
        await lyrixa.initialize()

        print("\n" + "=" * 50)
        print("🎙️ LYRIXA AI ASSISTANT READY")
        print("=" * 50)
        print(
            "Type 'help' for assistance, 'status' for system info, or 'quit' to exit."
        )
        print("You can also ask me anything in natural language!")
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
• `help` - Show this help
• `quit` - Exit Lyrixa

**Core Capabilities:**
🎯 Goal & Task Management - Set and track development goals
🧠 Memory System - Remember preferences and context
🧩 Plugin Ecosystem - Execute various tools and integrations
⚡ .aether Workflows - Generate and execute .aether code
🤖 Agent Orchestration - Coordinate specialized AI agents
📁 Project Intelligence - Understand and navigate your codebase

Just talk to me naturally - I'll figure out what you want to accomplish!
""")
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

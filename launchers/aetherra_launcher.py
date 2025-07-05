#!/usr/bin/env python3
"""
🌌 AETHERRA WITH LYRIXA AI ASSISTANT
===================================

The complete Aetherra development environment with Lyrixa AI Assistant integration.
Launch intelligent coding, natural language workflows, and .aether development.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def main():
    """Launch Aetherra with Lyrixa integration"""
    print("🌌 AETHERRA WITH LYRIXA AI ASSISTANT")
    print("=" * 50)
    print("Welcome to the intelligent development environment!")
    print()

    print("Available options:")
    print("1. Launch Lyrixa AI Assistant (Interactive)")
    print("2. Test Lyrixa AI Assistant")
    print("3. Launch Aetherra UI")
    print("4. Show System Status")
    print("5. Exit")
    print()

    while True:
        try:
            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                print("\n🎙️ Launching Lyrixa AI Assistant...")
                launch_lyrixa()
                break
            elif choice == "2":
                print("\n🧪 Testing Lyrixa AI Assistant...")
                test_lyrixa()
                break
            elif choice == "3":
                print("\n🌌 Launching Aetherra UI...")
                launch_aetherra()
                break
            elif choice == "4":
                print("\n📊 System Status...")
                show_status()
                break
            elif choice == "5":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Please enter a number between 1-5")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def launch_lyrixa():
    """Launch the Lyrixa AI Assistant"""

    async def run_lyrixa():
        try:
            from lyrixa.assistant import LyrixaAI

            print("\n🎙️ Starting Lyrixa AI Assistant...")
            lyrixa = LyrixaAI()
            await lyrixa.initialize()

            print("\n💬 Type 'exit' to quit, 'help' for commands")
            print("=" * 50)

            while True:
                try:
                    user_input = input("\n🎙️ You: ").strip()

                    if user_input.lower() in ["exit", "quit", "bye"]:
                        print("👋 Goodbye!")
                        break
                    elif user_input.lower() == "help":
                        print_help()
                        continue
                    elif not user_input:
                        continue

                    # Process input with Lyrixa
                    response = await lyrixa.process_natural_language(user_input)
                    print(
                        f"\n🎙️ Lyrixa: {response.get('response', 'I processed your request!')}"
                    )

                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break

        except ImportError as e:
            print(f"❌ Could not import Lyrixa: {e}")
            print("Make sure the lyrixa module is properly installed")

    # Run the async function
    asyncio.run(run_lyrixa())


def launch_aetherra():
    """Launch the Aetherra UI"""
    aetherra_ui_path = current_dir / "src" / "aetherra" / "ui"
    if aetherra_ui_path.exists():
        print("🌌 Starting Aetherra UI...")
        os.system(f"python -m http.server 8080 --directory {aetherra_ui_path}")
    else:
        print("❌ Aetherra UI not found")
        print("You can try running the Aetherra verification task instead")


def test_lyrixa():
    """Test the Lyrixa AI Assistant"""
    test_path = current_dir / "test_lyrixa.py"
    if test_path.exists():
        print("🧪 Running Lyrixa tests...")
        os.system(f"python {test_path}")
    else:
        print("❌ Test file not found")
        print("Creating and running basic tests...")
        create_basic_test()


def create_basic_test():
    """Create and run a basic test"""

    async def run_test():
        try:
            from lyrixa.assistant import LyrixaAI

            print("\n🧪 Testing Lyrixa core functionality...")
            lyrixa = LyrixaAI()
            await lyrixa.initialize()

            # Test basic functionality
            response = await lyrixa.process_natural_language("Hello Lyrixa")
            print(f"✅ Basic response: {response.get('response', 'Success')[:100]}...")

            # Test memory
            await lyrixa.memory.store_memory(
                content={"key": "test_key", "value": "test_value"},
                context={"test": True},
                tags=["test"],
                importance=0.5,
            )
            memories = await lyrixa.memory.recall_memories("test_key")
            print(f"✅ Memory test: Found {len(memories)} memories")

            print("✅ Basic tests completed successfully!")

        except Exception as e:
            print(f"❌ Test failed: {e}")

    # Run the async test
    asyncio.run(run_test())


def show_status():
    """Show system status"""
    print("\n📊 AETHERRA + LYRIXA SYSTEM STATUS")
    print("=" * 40)

    # Check Lyrixa availability
    try:
        import importlib.util

        spec = importlib.util.find_spec("lyrixa.assistant")
        if spec is not None:
            print("✅ Lyrixa AI Assistant: Available")
        else:
            print("❌ Lyrixa AI Assistant: Not available")
    except ImportError:
        print("❌ Lyrixa AI Assistant: Not available")

    # Check core modules
    core_modules = [
        ("lyrixa.core.memory", "Memory System"),
        ("lyrixa.core.plugins", "Plugin Manager"),
        ("lyrixa.core.goals", "Goal Tracker"),
        ("lyrixa.core.agents", "Agent System"),
        ("lyrixa.core.aether_interpreter", ".aether Interpreter"),
    ]

    for module_name, display_name in core_modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name}: Available")
        except ImportError:
            print(f"❌ {display_name}: Not available")

    # Check data directories
    data_dirs = [
        ("data", "Data Directory"),
        ("lyrixa", "Lyrixa Directory"),
        ("src", "Source Directory"),
    ]

    for dir_name, display_name in data_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            print(f"✅ {display_name}: Found")
        else:
            print(f"❌ {display_name}: Missing")


def print_help():
    """Print help information"""
    print("\n🎙️ LYRIXA AI ASSISTANT HELP")
    print("=" * 30)
    print("Commands:")
    print("  help     - Show this help")
    print("  exit     - Exit the assistant")
    print("  status   - Show system status")
    print()
    print("Natural Language Examples:")
    print("  'Create a Python function to sort a list'")
    print("  'Remember that I prefer React for frontend'")
    print("  'What goals do I have?'")
    print("  'Run the summarize plugin on readme.md'")
    print("  'Show me my recent memory'")


if __name__ == "__main__":
    main()

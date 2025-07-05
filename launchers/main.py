#!/usr/bin/env python3
"""
Lyrixa - AI-Native Programming Language
Main entry point for the Lyrixa interpreter
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, project_root)

# Use Enhanced Interpreter for best AI-native experience
try:
    from lyrixa.core.aether_interpreter import AetherInterpreter

    use_enhanced = True
except ImportError:
    print(
        "❌ Error: Could not import AetherInterpreter from lyrixa.core.aether_interpreter."
    )
    print(
        "Please ensure all dependencies are installed and PYTHONPATH is set correctly."
    )
    sys.exit(1)


def main():
    """Main entry point for Lyrixa"""
    print("🧠 Lyrixa - AI-Native Programming Language")
    if use_enhanced:
        print("🚀 Enhanced mode: Natural language programming enabled!")
    else:
        print("⚠️  Basic mode: Enhanced features not available")

    interpreter = AetherInterpreter()

    print("=" * 50)
    print("Type commands or 'help' for assistance")
    if use_enhanced:
        print("🚀 Enhanced mode: Natural language programming enabled!")

    interpreter = AetherInterpreter()

    while True:
        try:
            code = input("🔮 >> ")
        except EOFError:
            print("\n🚀 Input stream closed. Thanks for using Lyrixa!")
            break

        if code.lower() in ["exit", "quit", "q"]:
            print("🚀 Thanks for using Lyrixa!")
            break
        elif code.lower() in ["help", "?"]:
            print("""
📋 Lyrixa Commands:
  remember('text') as 'tag'    - Store memory with tag
  recall tag: 'tag'            - Recall memories by tag
  memory summary               - Show memory statistics
  define func() ... end        - Define function
  run func()                   - Execute function
  agent goal: 'description'    - Set AI agent goal
  simulate ... end             - Simulation mode
  help                         - Show this help
  exit                         - Quit interpreter
            """)
            continue
        elif code.strip() == "":
            continue

        # Execute the code
        try:
            import asyncio

            # Parse the input code into a workflow using the interpreter
            workflow = asyncio.run(interpreter.parse_aether_code(code))

            # Execute the workflow
            result = asyncio.run(interpreter.execute_workflow(workflow))
            print(f"✅ Execution completed: {result.get('status', 'unknown')}")

            # Show any outputs or errors
            if result.get("outputs"):
                print(f"📤 Outputs: {result['outputs']}")
            if result.get("errors"):
                print(f"❌ Errors: {result['errors']}")

        except Exception as exec_error:
            print(f"❌ Execution error: {exec_error}")

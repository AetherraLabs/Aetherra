#!/usr/bin/env python3
"""
🧬 NeuroCode Quick Start Launcher
===============================

One-click launcher to get started with NeuroCode:
- Run status check
- Launch playground
- Run example programs
- View documentation
"""

import subprocess
import sys
from pathlib import Path


def print_header():
    """Print welcome header"""
    print("🧬 NeuroCode v1.0 - AI-Native Programming Language")
    print("=" * 55)
    print("The world's first multi-LLM programming language!")
    print()


def run_status_check():
    """Run system status check"""
    print("🔍 Running system status check...")
    try:
        # Run from tools directory
        status_path = Path(__file__).parent / "status_check.py"
        subprocess.run([sys.executable, str(status_path)], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Status check failed. Please check your installation.")
        return False
    except FileNotFoundError:
        print("❌ status_check.py not found.")
        return False


def show_menu():
    """Show main menu"""
    print("\n🎯 What would you like to do?")
    print("1. 🎮 Launch Interactive Playground")
    print("2. 🧪 Run Multi-LLM Demo")
    print("3. 📖 View Tutorial")
    print("4. 🔧 Run Status Check")
    print("5. 📋 View Examples")
    print("6. 🚪 Exit")
    print()


def launch_playground():
    """Launch the NeuroCode playground"""
    print("🎮 Launching NeuroCode Playground...")
    try:
        # Launch from tools directory
        playground_path = Path(__file__).parent / "launch_playground.py"
        subprocess.run([sys.executable, str(playground_path)], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to launch playground.")
    except FileNotFoundError:
        print("❌ launch_playground.py not found.")


def run_demo():
    """Run multi-LLM demo"""
    print("🧪 Running Multi-LLM Demo...")
    try:
        # Run from parent directory (tests folder)
        parent_dir = Path(__file__).parent.parent
        demo_path = parent_dir / "tests" / "test_multi_llm_integration.py"
        subprocess.run([sys.executable, str(demo_path)], check=True)
    except subprocess.CalledProcessError:
        print("❌ Demo failed to run.")
    except FileNotFoundError:
        print("❌ Demo file not found.")


def view_tutorial():
    """View tutorial information"""
    print("📖 NeuroCode Tutorial")
    print("-" * 20)
    print("Tutorial file: docs/TUTORIAL.md")
    print("Language spec: docs/LANGUAGE_SPEC.md")
    print("Examples: examples/ directory")
    print("\nKey concepts:")
    print("• model: 'gpt-4' - Switch AI models")
    print("• assistant: 'help me code' - Get AI assistance")
    print("• remember('insight') as 'memory' - Store knowledge")
    print("• goal: 'optimize performance' - Set intentions")


def view_examples():
    """Show available examples"""
    print("📋 Available Examples:")
    print("-" * 20)

    parent_dir = Path(__file__).parent.parent
    examples_dir = parent_dir / "examples"
    if examples_dir.exists():
        for example in examples_dir.glob("*.aether"):
            print(f"• {example.name}")
    else:
        print("❌ Examples directory not found.")

    print("\nTo run an example:")
    print(
        "python -c \"from src.aethercode_engine import aetherra_engine; engine = neurocode_engine(); engine.execute_file('examples/example.aether')\""
    )


def main():
    """Main launcher function"""
    print_header()

    # Run initial status check
    if not run_status_check():
        print("\n⚠️ Please fix issues before continuing.")
        return

    while True:
        show_menu()

        try:
            choice = input("Enter your choice (1-6): ").strip()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

        if choice == "1":
            launch_playground()
        elif choice == "2":
            run_demo()
        elif choice == "3":
            view_tutorial()
        elif choice == "4":
            run_status_check()
        elif choice == "5":
            view_examples()
        elif choice == "6":
            print("👋 Thanks for using NeuroCode!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

        print("\nPress Enter to continue...")
        input()


if __name__ == "__main__":
    main()

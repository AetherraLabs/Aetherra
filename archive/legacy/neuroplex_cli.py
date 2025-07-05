#!/usr/bin/env python3
"""
🚀 Neuroplex Command-Line Interface
==================================

Enhanced aetherplex command with support for running .neuro files:
- aetherplex run monitor.neuro
- aetherplex run examples/basic_memory.neuro
- aetherplex ui (launch GUI)
- aetherplex help

This completes the vision of AetherraCode as a standalone programming language.
"""

import subprocess
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_neuro_file(file_path: str, verbose: bool = False) -> int:
    """Run a .neuro file using the standalone runner"""

    runner_path = project_root / "scripts" / "neuro_runner_standalone.py"

    if not runner_path.exists():
        print(
            "❌ AetherraCode runner not found. Please ensure scripts/neuro_runner_standalone.py exists."
        )
        return 1

    # Build command
    cmd = [sys.executable, str(runner_path), file_path]
    if verbose:
        cmd.append("--verbose")

    try:
        # Run the file
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Failed to execute AetherraCode file: {e}")
        return 1


def launch_ui() -> int:
    """Launch the AetherraCode UI"""

    ui_paths = [
        project_root / "ui" / "neuro_ui.py",
        project_root / "ui" / "aetherplex_gui.py",
        project_root / "launch_neuro_ui.py",
    ]

    # Find available UI
    for ui_path in ui_paths:
        if ui_path.exists():
            try:
                print(f"🚀 Launching AetherraCode UI: {ui_path.name}")
                result = subprocess.run([sys.executable, str(ui_path)])
                return result.returncode
            except Exception as e:
                print(f"⚠️ Failed to launch {ui_path.name}: {e}")
                continue

    print("❌ No AetherraCode UI found. Please ensure UI files exist.")
    return 1


def show_help():
    """Show comprehensive help"""
    help_text = """
🧬 Neuroplex - AetherraCode Command-Line Interface
==============================================

USAGE:
    aetherplex <command> [options]

COMMANDS:
    run <file>          Execute a .neuro file
    ui                  Launch the AetherraCode user interface
    translate <text>    Translate natural language to AetherraCode
    chat                Interactive natural language translation
    help                Show this help message

EXAMPLES:
    🧬 Run AetherraCode files:
        aetherplex run monitor.neuro
        aetherplex run examples/basic_memory.neuro
        aetherplex run advanced_syntax_demo.neuro --verbose

    🗣️ Natural Language Translation:
        aetherplex translate "Remember this conversation"
        aetherplex translate "Fix any recurring errors" --execute
        aetherplex chat

    🎨 Launch UI:
        aetherplex ui

    📚 Get help:
        aetherplex help

FILE RUNNER OPTIONS:
    --verbose, -v       Show detailed execution trace

TRANSLATION OPTIONS:
    --execute, -e       Execute the translated AetherraCode

AVAILABLE .NEURO FILES:
"""

    print(help_text)

    # List available .neuro files
    neuro_files = list(project_root.glob("**/*.neuro"))
    if neuro_files:
        for file in sorted(neuro_files):
            rel_path = file.relative_to(project_root)
            print(f"    📄 {rel_path}")
    else:
        print("    (No .neuro files found)")

    print("""
NEUROCODE LANGUAGE FEATURES:
    💾 Memory: remember("text") as "tag"
    🧠 Recall: recall tag: "tag_name"
    🔍 Reflection: reflect on tags="tag"
    🎯 Goals: goal: description priority: level
    🤖 Agents: agent: on/off
    ⚙️ Functions: define name() ... end
    🔀 Control: if/when/for/while statements

GETTING STARTED:
    1. Create a .neuro file with AetherraCode syntax
    2. Run it: aetherplex run your_file.neuro
    3. Explore the UI: aetherplex ui

For more information, visit the AetherraCode documentation.
""")


def translate_natural(natural_input: str, execute: bool = False) -> int:
    """Translate natural language to AetherraCode"""
    try:
        from natural_translator import NaturalToNeuroTranslator

        translator = NaturalToNeuroTranslator()
        neurocode = translator.translate(natural_input)

        print(f"🗣️  Natural: {natural_input}")
        print(f"🧬 AetherraCode: {neurocode}")

        if execute:
            print("⚡ Executing translated AetherraCode...")
            translator._execute_neurocode(neurocode)

        return 0

    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return 1


def interactive_translate() -> int:
    """Start interactive natural language translation"""
    try:
        from natural_translator import NaturalToNeuroTranslator

        translator = NaturalToNeuroTranslator()
        translator.interactive_translate()
        return 0

    except Exception as e:
        print(f"❌ Interactive translation failed: {e}")
        return 1


def main():
    """Main CLI interface"""

    # Handle no arguments
    if len(sys.argv) == 1:
        show_help()
        return 0

    # Parse command
    command = sys.argv[1].lower()

    if command == "run":
        if len(sys.argv) < 3:
            print("❌ Usage: aetherplex run <file>")
            return 1

        file_path = sys.argv[2]
        verbose = "--verbose" in sys.argv or "-v" in sys.argv

        return run_neuro_file(file_path, verbose)

    elif command == "ui":
        return launch_ui()

    elif command in ["translate", "trans", "t"]:
        if len(sys.argv) < 3:
            return interactive_translate()

        natural_input = " ".join(sys.argv[2:])
        execute = "--execute" in sys.argv or "-e" in sys.argv

        return translate_natural(natural_input, execute)

    elif command in ["chat", "interactive", "i"]:
        return interactive_translate()

    elif command in ["help", "--help", "-h"]:
        show_help()
        return 0

    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'aetherplex help' for available commands.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

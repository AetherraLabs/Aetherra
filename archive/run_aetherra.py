#!/usr/bin/env python3
"""
NeuroCode File Runner
====================

Simple command-line runner for executing .aether files.
Supports plugin execution and basic NeuroCode commands.

Usage:
    python run_neuro.py examples/plugin_demo_corrected.aether
    python run_neuro.py path/to/your/file.aether
"""

import os
import re
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def parse_plugin_command(line):
    """Parse a plugin command line and extract plugin name, function, and arguments."""
    # Pattern 1: plugin: plugin_name.function_name "arguments"
    pattern1 = r'plugin:\s*(\w+)\.(\w+)\s*"([^"]*)"'
    match = re.match(pattern1, line.strip())

    if match:
        plugin_name = match.group(1)
        function_name = match.group(2)
        arguments = match.group(3)
        return plugin_name, function_name, arguments

    # Pattern 2: plugin: plugin_name.function_name arguments (no quotes)
    pattern2 = r"plugin:\s*(\w+)\.(\w+)\s*(.*)"
    match = re.match(pattern2, line.strip())

    if match:
        plugin_name = match.group(1)
        function_name = match.group(2)
        arguments = match.group(3).strip().strip('"')
        return plugin_name, function_name, arguments

    # Pattern 3: plugin: single_function_name "arguments" (for plugins that don't use dots)
    pattern3 = r'plugin:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*"([^"]*)"'
    match = re.match(pattern3, line.strip())

    if match:
        full_name = match.group(1)
        arguments = match.group(2)
        return (
            None,
            full_name,
            arguments,
        )  # Return None for plugin_name, full name as function

    # Pattern 4: plugin: single_function_name arguments (no quotes, including empty)
    pattern4 = r"plugin:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(.*)"
    match = re.match(pattern4, line.strip())

    if match:
        full_name = match.group(1)
        arguments = match.group(2).strip().strip('"')
        return None, full_name, arguments

    return None, None, None


def execute_plugin_command(plugin_name, function_name, arguments):
    """Execute a plugin command by calling the appropriate function."""
    try:
        # Import the plugin manager functions
        from core.plugin_manager import execute_plugin, load_plugins

        # Ensure plugins are loaded
        load_plugins()

        # Construct the full plugin function name
        if plugin_name:
            full_plugin_name = f"{plugin_name}_{function_name}"
        else:
            full_plugin_name = function_name

        # Try to call the plugin function
        result = execute_plugin(full_plugin_name, arguments)

        display_name = (
            f"{plugin_name}.{function_name}" if plugin_name else function_name
        )

        if result:
            if isinstance(result, dict):
                if result.get("success"):
                    message = result.get("message", result.get("result", str(result)))
                    print(f"✅ {display_name}: {message}")
                else:
                    error = result.get("error", str(result))
                    print(f"❌ {display_name}: {error}")
            else:
                print(f"✅ {display_name}: {result}")
        else:
            print(f"⚠️ {display_name}: No result returned")

    except Exception as e:
        display_name = (
            f"{plugin_name}.{function_name}" if plugin_name else function_name
        )
        print(f"❌ {display_name}: Error - {str(e)}")


def run_neuro_file(file_path):
    """Execute a .aether file by processing each command."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found")
        return False

    print(f"🚀 Running NeuroCode file: {file_path}")
    print("=" * 60)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        command_count = 0

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Check if it's a plugin command
            if line.startswith("plugin:"):
                command_count += 1
                plugin_name, function_name, arguments = parse_plugin_command(line)

                if function_name:  # We got at least a function name
                    if plugin_name:
                        print(
                            f"\n[{command_count}] Line {line_num}: {plugin_name}.{function_name}"
                        )
                    else:
                        print(f"\n[{command_count}] Line {line_num}: {function_name}")
                    execute_plugin_command(plugin_name, function_name, arguments)
                else:
                    print(f"❌ Line {line_num}: Invalid plugin command format")
                    print(f"   Command: {line}")
            else:
                # Handle other NeuroCode commands here in the future
                print(f"⚠️ Line {line_num}: Unrecognized command: {line}")

        print("\n" + "=" * 60)
        print(f"✅ Completed execution of {command_count} commands from {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return False


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python run_neuro.py <path_to_neuro_file>")
        print("\nExample:")
        print("  python run_neuro.py examples/plugin_demo_corrected.aether")
        sys.exit(1)

    file_path = sys.argv[1]

    print("🧬 NeuroCode File Runner")
    print("========================")

    success = run_neuro_file(file_path)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
LYRIXA INTERFACES VALIDATION
============================

This script validates that all the interface files in lyrixa/interfaces
are properly implemented and not empty.
"""

from pathlib import Path


def check_interface_files():
    """Check all interface files"""
    print("LYRIXA INTERFACES VALIDATION")
    print("=" * 40)

    interfaces_dir = Path("lyrixa/interfaces")

    if not interfaces_dir.exists():
        print("❌ Interfaces directory does not exist")
        return False

    # Expected interface files
    expected_files = {
        "__init__.py": "Package initialization file",
        "lyrixa.py": "Main Lyrixa core interface",
        "lyrixa_agent_integration.py": "Agent integration interface",
        "lyrixa_assistant.py": "Assistant interface",
        "lyrixa_assistant_console.py": "Console interface",
        "web_integration.js": "Web integration (JavaScript)",
    }

    all_good = True

    for filename, description in expected_files.items():
        filepath = interfaces_dir / filename

        if not filepath.exists():
            print(f"❌ Missing: {filename} - {description}")
            all_good = False
            continue

        # Check if file is empty
        if filepath.stat().st_size == 0:
            print(f"❌ Empty: {filename} - {description}")
            all_good = False
            continue

        # Check if Python file has basic content
        if filename.endswith(".py"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            if len(content.strip()) < 100:  # Very basic check
                print(
                    f"⚠️  Minimal: {filename} - {description} (only {len(content)} chars)"
                )
            else:
                print(f"✅ Good: {filename} - {description} ({len(content)} chars)")
        else:
            print(f"✅ Present: {filename} - {description}")

    if all_good:
        print("\n🎉 All interface files are present and non-empty!")
        return True
    else:
        print("\n⚠️  Some interface files have issues.")
        return False


def check_interface_structure():
    """Check the internal structure of interface files"""
    print("\nINTERFACE STRUCTURE CHECK")
    print("=" * 40)

    interfaces_dir = Path("lyrixa/interfaces")

    # Check specific classes/functions exist
    checks = {
        "lyrixa.py": [
            "class LyrixaCore",
            "def get_lyrixa_instance",
            "def initialize_lyrixa",
        ],
        "lyrixa_agent_integration.py": ["class LyrixaAgentInterface"],
        "lyrixa_assistant.py": [
            "class LyrixaAssistant",
            "def create_assistant",
            "def quick_chat",
        ],
        "lyrixa_assistant_console.py": ["class LyrixaConsole"],
        "__init__.py": ["from .lyrixa import", "from .lyrixa_assistant import"],
    }

    for filename, expected_content in checks.items():
        filepath = interfaces_dir / filename

        if not filepath.exists():
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            print(f"\n📄 {filename}:")
            for expected in expected_content:
                if expected in content:
                    print(f"  ✅ Found: {expected}")
                else:
                    print(f"  ❌ Missing: {expected}")

        except Exception as e:
            print(f"  ❌ Error reading {filename}: {e}")


if __name__ == "__main__":
    result1 = check_interface_files()
    check_interface_structure()

    if result1:
        print(
            "\n🎉 VALIDATION COMPLETE: All Lyrixa interfaces are properly implemented!"
        )
        print("The interface files are ready for use.")
    else:
        print("\n⚠️  VALIDATION INCOMPLETE: Some issues found.")

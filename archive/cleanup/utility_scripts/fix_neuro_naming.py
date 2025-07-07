#!/usr/bin/env python3
"""Fix Neuro* to Aetherra* naming throughout the codebase"""

import glob
import os
import re

# Define replacement patterns
replacements = [
    (r"\bNeuroAgent\b", "AetherraAgent"),
    (r"\bAetherra\b", "AetherraCode"),
    (r"\bNeuroDebug\b", "AetherraDebug"),
    (r"\bNeuroUI\b", "AetherraUI"),
    (r"\bNeuroChat\b", "AetherraChat"),
    (r"\bNeuroParser\b", "AetherraParser"),
    (r"\bNeuroInterpreter\b", "AetherraInterpreter"),
    (r"\bNeuroMemory\b", "AetherraMemory"),
    (r"\bNeuroPlugin\b", "AetherraPlugin"),
    (r"\bNeuroRuntime\b", "AetherraRuntime"),
    (r"\bNeuro([A-Z][a-zA-Z]*)\b", r"Aetherra\1"),  # General pattern for AetherraXxx
    # Fix import paths
    (r"from aetherra_", "from aetherra_"),
    (r"import aetherra_", "import aetherra_"),
    # Fix file references
    (r"aethercode_", "aethercode_"),
    (r"aetherdebug_", "aetherdebug_"),
    # Fix UI component names
    (r"aetherchat", "aetherchat"),
    (r"aetherplex", "aetherplex"),
]


def fix_file(filepath):
    """Fix Neuro* naming in a single file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply all replacements
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        # Only write if changes were made
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Updated {filepath}")
            return True
        else:
            print(f"⚪ No changes needed in {filepath}")
            return False

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False


def main():
    """Fix all Python files"""
    print("🔧 Fixing Neuro* to Aetherra* naming...")

    # Find all Python files
    python_files = []
    for pattern in ["**/*.py", "*.py"]:
        python_files.extend(glob.glob(pattern, recursive=True))

    # Remove duplicates and filter out some directories
    python_files = list(set(python_files))
    python_files = [
        f
        for f in python_files
        if not any(x in f for x in ["__pycache__", ".git", "node_modules"])
    ]

    print(f"Found {len(python_files)} Python files")

    updated_count = 0
    for py_file in python_files:
        if fix_file(py_file):
            updated_count += 1

    print(f"\n🎉 Updated {updated_count} out of {len(python_files)} Python files")


if __name__ == "__main__":
    main()

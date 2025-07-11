#!/usr/bin/env python3
"""
Plugin Schema Fixer
===================

Automatically adds missing required fields to existing plugin files.
"""

import os
import re
from pathlib import Path
from typing import Dict, List


class PluginSchemaFixer:
    """Fixes plugin files by adding missing required fields."""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.required_fields = [
            "name",
            "description",
            "input_schema",
            "output_schema",
            "created_by",
        ]
        self.fixes_applied = []

    def fix_plugin_file(self, file_path: Path) -> bool:
        """Fix a single plugin file by adding missing required fields."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if it's already properly formatted
            if all(field in content for field in self.required_fields):
                return False  # Already has all fields

            # Extract class name
            class_match = re.search(r"class\s+(\w+)", content)
            if not class_match:
                return False

            class_name = class_match.group(1)
            plugin_name = file_path.stem

            # Create the schema additions
            schema_additions = f'''
    # Required plugin metadata
    name = "{plugin_name}"
    description = "{class_name} - Auto-generated description"
    input_schema = {{
        "type": "object",
        "properties": {{
            "input": {{"type": "string", "description": "Input data"}}
        }},
        "required": ["input"]
    }}
    output_schema = {{
        "type": "object",
        "properties": {{
            "result": {{"type": "string", "description": "Processing result"}},
            "status": {{"type": "string", "description": "Operation status"}}
        }}
    }}
    created_by = "Plugin System Auto-Fixer"
'''

            # Find insertion point (after class declaration)
            class_line_match = re.search(r"(class\s+\w+[^:]*:)\s*\n", content)
            if class_line_match:
                insertion_point = class_line_match.end()

                # Check if there's already a docstring
                remaining_content = content[insertion_point:]
                docstring_match = re.match(r'\s*"""[^"]*"""', remaining_content)
                if docstring_match:
                    insertion_point += docstring_match.end()

                # Insert the schema
                new_content = (
                    content[:insertion_point]
                    + schema_additions
                    + content[insertion_point:]
                )

                # Write back to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                self.fixes_applied.append(str(file_path))
                return True

            return False

        except Exception as e:
            print(f"   ❌ Error fixing {file_path}: {e}")
            return False

    def fix_all_plugins(self):
        """Fix all plugin files in the project."""
        print("🔧 PLUGIN SCHEMA FIXER")
        print("=" * 40)

        plugin_dirs = [
            self.project_root / "lyrixa" / "plugins",
            self.project_root / "src" / "aetherra" / "plugins",
            self.project_root / "sdk" / "plugins",
        ]

        total_fixed = 0

        for plugin_dir in plugin_dirs:
            if not plugin_dir.exists():
                continue

            print(f"\n📁 Processing: {plugin_dir}")

            for file_path in plugin_dir.rglob("*.py"):
                if file_path.name.startswith("__"):
                    continue

                if self.fix_plugin_file(file_path):
                    print(f"   ✅ Fixed: {file_path.name}")
                    total_fixed += 1
                else:
                    print(f"   ⏭️  Skipped: {file_path.name}")

        print(f"\n📊 Summary: Fixed {total_fixed} plugin files")
        return total_fixed


def main():
    """Main function."""
    fixer = PluginSchemaFixer()
    fixed_count = fixer.fix_all_plugins()

    if fixed_count > 0:
        print(f"\n✅ Successfully fixed {fixed_count} plugin files!")
        print("🚀 Run the plugin discovery again to test the fixes.")
    else:
        print("\n📝 No plugin files needed fixing.")

    return fixed_count


if __name__ == "__main__":
    main()

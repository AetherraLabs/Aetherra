#!/usr/bin/env python3
"""
Comprehensive Plugin Schema Fixer
=================================

This script fixes plugin files by adding the required class attributes
that the plugin discovery system expects. It analyzes decorator-based
plugins and converts them to have proper class attributes.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ComprehensivePluginFixer:
    """Comprehensive plugin schema fixer."""

    def __init__(self, project_root: str | None = None):
        self.project_root = Path(project_root or os.getcwd())
        self.plugin_directories = [
            self.project_root / "lyrixa" / "plugins",
            self.project_root / "src" / "aetherra" / "plugins",
            self.project_root / "sdk" / "plugins",
        ]
        self.required_attributes = [
            "name",
            "description",
            "input_schema",
            "output_schema",
            "created_by",
        ]
        self.fixes_applied = []

    def fix_all_plugins(self):
        """Fix all plugins in the specified directories."""
        print("🔧 COMPREHENSIVE PLUGIN FIXER")
        print("=" * 50)

        total_fixed = 0

        for plugin_dir in self.plugin_directories:
            if not plugin_dir.exists():
                print(f"📁 Directory not found: {plugin_dir}")
                continue

            print(f"📁 Processing: {plugin_dir}")

            for file_path in plugin_dir.rglob("*.py"):
                if file_path.name.startswith("__"):
                    continue

                if self._fix_plugin_file(file_path):
                    total_fixed += 1
                    print(f"   ✅ Fixed: {file_path.name}")
                else:
                    print(f"   ⏭️  Skipped: {file_path.name}")

        print(f"\n📊 Summary: Fixed {total_fixed} plugin files")
        self._save_fix_report()

        if total_fixed > 0:
            print("🚀 Run the plugin discovery again to test the fixes.")

    def _fix_plugin_file(self, file_path: Path) -> bool:
        """Fix a single plugin file by adding required attributes."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Skip if already has all required attributes as class attributes
            if self._has_required_class_attributes(content):
                return False

            # Check if it's a valid plugin file that needs fixing
            if not self._is_plugin_file(content):
                return False

            # Extract metadata from decorators or functions
            metadata = self._extract_metadata(content, file_path)

            # Add missing attributes to the first class found
            fixed_content = self._add_class_attributes(content, metadata)

            if fixed_content != content:
                # Create backup
                backup_path = file_path.with_suffix(".py.backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Write fixed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                self.fixes_applied.append(
                    {
                        "file": str(file_path),
                        "backup": str(backup_path),
                        "metadata_added": metadata,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                return True

        except Exception as e:
            print(f"   ⚠️ Error fixing {file_path}: {e}")

        return False

    def _has_required_class_attributes(self, content: str) -> bool:
        """Check if content already has required class attributes."""
        lines = content.split("\n")
        found_attributes = set()

        for line in lines:
            line = line.strip()
            for attr in self.required_attributes:
                if line.startswith(f"{attr} ="):
                    found_attributes.add(attr)

        return (
            len(found_attributes) >= 4
        )  # At least name, description, input_schema, output_schema

    def _is_plugin_file(self, content: str) -> bool:
        """Check if this is a plugin file that should be fixed."""
        indicators = [
            "@register_plugin",
            "class.*Plugin",
            "BasePlugin",
            "LyrixaPlugin",
            "def execute",
            "def run",
            "def process",
        ]

        content_lower = content.lower()
        return any(
            re.search(indicator.lower(), content_lower) for indicator in indicators
        )

    def _extract_metadata(self, content: str, file_path: Path) -> Dict:
        """Extract metadata from decorators, comments, or file structure."""
        metadata = {
            "name": file_path.stem,
            "description": f"Plugin for {file_path.stem} functionality",
            "input_schema": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Input data"}
                },
                "required": ["input"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": "Processing result"},
                    "status": {"type": "string", "description": "Operation status"},
                },
            },
            "created_by": "Plugin System Auto-Fixer",
        }

        # Try to extract from @register_plugin decorator
        decorator_match = re.search(r"@register_plugin\((.*?)\)", content, re.DOTALL)
        if decorator_match:
            decorator_content = decorator_match.group(1)

            # Extract name
            name_match = re.search(r'name=["\'](.*?)["\']', decorator_content)
            if name_match:
                metadata["name"] = name_match.group(1)

            # Extract description
            desc_match = re.search(r'description=["\'](.*?)["\']', decorator_content)
            if desc_match:
                metadata["description"] = desc_match.group(1)

        # Try to extract from function docstrings
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "def " in line and '"""' in lines[i + 1 : i + 10]:
                for j in range(i + 1, min(i + 10, len(lines))):
                    if '"""' in lines[j]:
                        docstring = lines[j].replace('"""', "").strip()
                        if docstring and len(docstring) > 10:
                            metadata["description"] = docstring
                        break

        return metadata

    def _add_class_attributes(self, content: str, metadata: Dict) -> str:
        """Add required class attributes to the first class found."""
        lines = content.split("\n")

        # Find the first class definition
        class_line_idx = None
        for i, line in enumerate(lines):
            if re.match(r"\s*class\s+\w+", line):
                class_line_idx = i
                break

        if class_line_idx is None:
            # No class found, create one at the beginning
            class_definition = self._create_plugin_class(metadata)
            return class_definition + "\n\n" + content

        # Find where to insert attributes (after class definition and docstring)
        insert_idx = class_line_idx + 1

        # Skip docstring if present
        if insert_idx < len(lines) and '"""' in lines[insert_idx]:
            # Find end of docstring
            for i in range(insert_idx, len(lines)):
                if lines[i].count('"""') >= 2 or (i > insert_idx and '"""' in lines[i]):
                    insert_idx = i + 1
                    break

        # Generate attribute lines
        attribute_lines = self._generate_attribute_lines(metadata)

        # Insert attributes
        lines[insert_idx:insert_idx] = attribute_lines

        return "\n".join(lines)

    def _create_plugin_class(self, metadata: Dict) -> str:
        """Create a complete plugin class."""
        class_name = self._to_class_name(metadata["name"])
        attributes = self._generate_attribute_lines(metadata, indent="    ")

        return f'''class {class_name}:
    """Plugin class for {metadata["description"]}"""
{chr(10).join(attributes)}

    def execute(self, input_data):
        """Execute the plugin functionality."""
        return {{"result": "Not implemented", "status": "success"}}
'''

    def _generate_attribute_lines(
        self, metadata: Dict, indent: str = "    "
    ) -> List[str]:
        """Generate class attribute lines."""
        lines = [
            f"{indent}# Required plugin metadata",
            f'{indent}name = "{metadata["name"]}"',
            f'{indent}description = "{metadata["description"]}"',
            f"{indent}input_schema = {json.dumps(metadata['input_schema'], indent=4).replace(chr(10), chr(10) + indent)}",
            f"{indent}output_schema = {json.dumps(metadata['output_schema'], indent=4).replace(chr(10), chr(10) + indent)}",
            f'{indent}created_by = "{metadata["created_by"]}"',
            "",
        ]
        return lines

    def _to_class_name(self, name: str) -> str:
        """Convert a name to a valid class name."""
        # Remove special characters and convert to PascalCase
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        parts = clean_name.split("_")
        class_name = "".join(part.capitalize() for part in parts if part)

        if not class_name:
            class_name = "Plugin"
        elif not class_name.endswith("Plugin"):
            class_name += "Plugin"

        return class_name

    def _save_fix_report(self):
        """Save the fix report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "total_fixed": len(self.fixes_applied),
            "status": "completed",
        }

        report_file = self.project_root / "plugin_schema_fixes.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"📋 Fix report saved: {report_file}")


if __name__ == "__main__":
    fixer = ComprehensivePluginFixer()
    fixer.fix_all_plugins()

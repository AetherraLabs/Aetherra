#!/usr/bin/env python3
"""
Final Plugin System Verification
================================
Complete test of the plugin system after all repairs.
"""

import json
import os
import re
from pathlib import Path


class PluginSystemValidator:
    """Final validation of the plugin system."""

    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.plugin_directories = [
            self.project_root / "lyrixa" / "plugins",
            self.project_root / "src" / "aetherra" / "plugins",
            self.project_root / "sdk" / "plugins",
        ]
        self.results = {
            "valid_plugins": [],
            "invalid_plugins": [],
            "fixed_plugins": [],
            "total_scanned": 0,
            "success_rate": 0.0,
        }

    def validate_all_plugins(self):
        """Validate all plugins and fix remaining issues."""
        print("[TOOL] FINAL PLUGIN SYSTEM VERIFICATION")
        print("=" * 50)

        for plugin_dir in self.plugin_directories:
            if not plugin_dir.exists():
                continue

            print(f"📁 Validating: {plugin_dir}")

            for file_path in plugin_dir.rglob("*.py"):
                if file_path.name.startswith("__"):
                    continue

                self.results["total_scanned"] += 1

                if self._validate_plugin(file_path):
                    self.results["valid_plugins"].append(str(file_path))
                    print(f"   ✅ Valid: {file_path.name}")
                else:
                    self.results["invalid_plugins"].append(str(file_path))
                    print(f"   [ERROR] Invalid: {file_path.name}")

                    # Try to fix it
                    if self._fix_invalid_plugin(file_path):
                        self.results["fixed_plugins"].append(str(file_path))
                        self.results["valid_plugins"].append(str(file_path))
                        self.results["invalid_plugins"].remove(str(file_path))
                        print(f"   [TOOL] Fixed: {file_path.name}")

        self._calculate_success_rate()
        self._generate_report()

    def _validate_plugin(self, file_path: Path) -> bool:
        """Validate a single plugin file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Must have plugin indicators
            plugin_indicators = [
                r"class.*plugin",
                r"@register_plugin",
                r"baseplugin",
                r"def execute",
                r"def run",
            ]

            has_plugin_indicator = any(
                re.search(indicator, content, re.IGNORECASE)
                for indicator in plugin_indicators
            )

            if not has_plugin_indicator:
                return False

            # Must have required class attributes
            required_attrs = ["name", "description", "input_schema", "output_schema"]
            lines = content.split("\n")
            found_attrs = set()

            for line in lines:
                line = line.strip()
                for attr in required_attrs:
                    if line.startswith(f"{attr} ="):
                        found_attrs.add(attr)

            return len(found_attrs) >= 4

        except Exception as e:
            print(f"   [WARN] Error validating {file_path}: {e}")
            return False

    def _fix_invalid_plugin(self, file_path: Path) -> bool:
        """Try to fix an invalid plugin."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if it's a plugin file that just needs attributes
            plugin_indicators = [
                r"class.*plugin",
                r"@register_plugin",
                r"def execute",
                r"def run",
            ]

            has_plugin_indicator = any(
                re.search(indicator, content, re.IGNORECASE)
                for indicator in plugin_indicators
            )

            if not has_plugin_indicator:
                return False

            # Check if it already has some attributes
            lines = content.split("\n")
            has_some_attrs = any(
                line.strip().startswith(
                    ("name =", "description =", "input_schema =", "output_schema =")
                )
                for line in lines
            )

            if has_some_attrs:
                return False  # Already has attributes, must be some other issue

            # Add basic attributes to first class
            class_line_idx = None
            for i, line in enumerate(lines):
                if re.match(r"\\s*class\\s+\\w+", line):
                    class_line_idx = i
                    break

            if class_line_idx is None:
                return False

            # Insert basic attributes after class definition
            insert_idx = class_line_idx + 1

            # Skip docstring if present
            if insert_idx < len(lines) and '"""' in lines[insert_idx]:
                for i in range(insert_idx, len(lines)):
                    if lines[i].count('"""') >= 2 or (
                        i > insert_idx and '"""' in lines[i]
                    ):
                        insert_idx = i + 1
                        break

            # Generate attributes
            plugin_name = file_path.stem
            attributes = [
                "    # Required plugin metadata",
                f'    name = "{plugin_name}"',
                f'    description = "Plugin for {plugin_name} functionality"',
                '    input_schema = {"type": "object", "properties": {"input": {"type": "string"}}}',
                '    output_schema = {"type": "object", "properties": {"result": {"type": "string"}}}',
                '    created_by = "Plugin System Auto-Fixer"',
                "",
            ]

            # Insert attributes
            lines[insert_idx:insert_idx] = attributes

            # Create backup and write fixed content
            backup_path = file_path.with_suffix(".py.backup")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\\n".join(lines))

            return True

        except Exception as e:
            print(f"   [WARN] Error fixing {file_path}: {e}")
            return False

    def _calculate_success_rate(self):
        """Calculate the success rate."""
        if self.results["total_scanned"] > 0:
            valid_count = len(self.results["valid_plugins"])
            self.results["success_rate"] = (
                valid_count / self.results["total_scanned"]
            ) * 100

    def _generate_report(self):
        """Generate final validation report."""
        print("\n📊 FINAL VALIDATION RESULTS")
        print("=" * 40)
        print(f"Total plugins scanned: {self.results['total_scanned']}")
        print(f"Valid plugins: {len(self.results['valid_plugins'])}")
        print(f"Invalid plugins: {len(self.results['invalid_plugins'])}")
        print(f"Plugins fixed: {len(self.results['fixed_plugins'])}")
        print(f"Success rate: {self.results['success_rate']:.1f}%")

        if self.results["invalid_plugins"]:
            print("\\n[ERROR] Remaining invalid plugins:")
            for plugin in self.results["invalid_plugins"]:
                print(f"   - {Path(plugin).name}")

        # Save report
        report_file = self.project_root / "final_plugin_validation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        print(f"\\n📋 Report saved: {report_file}")

        if self.results["success_rate"] >= 90:
            print("\\n🎉 Plugin system validation SUCCESSFUL!")
        else:
            print("\\n[WARN] Plugin system needs additional work.")


if __name__ == "__main__":
    validator = PluginSystemValidator()
    validator.validate_all_plugins()

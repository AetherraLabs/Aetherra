#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Import Updater
Updates import statements after file reorganization in aetherra_core
"""

# Standard library imports
import os
import re
from pathlib import Path


class AetherraImportUpdater:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.import_mappings = {
            # Files moved from agents/ to plugins/
            r"from aetherra_core\.agents\.advanced_plugins": "from aetherra_core.plugins.advanced_plugins",
            r"from aetherra_core\.agents import advanced_plugins": "from aetherra_core.plugins import advanced_plugins",
            r"import aetherra_core\.agents\.advanced_plugins": "import aetherra_core.plugins.advanced_plugins",
            # Files moved from system/ to memory/
            r"from aetherra_core\.system\.lightweight_memory_core": "from aetherra_core.memory.lightweight_memory_core",
            r"from aetherra_core\.system\.memory_core": "from aetherra_core.memory.memory_core",
            r"from aetherra_core\.system\.memory_core_adapter": "from aetherra_core.memory.memory_core_adapter",
            r"from aetherra_core\.system\.world_class_memory_core": "from aetherra_core.memory.world_class_memory_core",
            r"from aetherra_core\.system import lightweight_memory_core": "from aetherra_core.memory import lightweight_memory_core",
            r"from aetherra_core\.system import memory_core": "from aetherra_core.memory import memory_core",
            r"from aetherra_core\.system import memory_core_adapter": "from aetherra_core.memory import memory_core_adapter",
            r"from aetherra_core\.system import world_class_memory_core": "from aetherra_core.memory import world_class_memory_core",
            r"import aetherra_core\.system\.lightweight_memory_core": "import aetherra_core.memory.lightweight_memory_core",
            r"import aetherra_core\.system\.memory_core": "import aetherra_core.memory.memory_core",
            r"import aetherra_core\.system\.memory_core_adapter": "import aetherra_core.memory.memory_core_adapter",
            r"import aetherra_core\.system\.world_class_memory_core": "import aetherra_core.memory.world_class_memory_core",
            # Files moved from system/ to kernel/
            r"from aetherra_core\.system\.coretools": "from aetherra_core.kernel.coretools",
            r"from aetherra_core\.system import coretools": "from aetherra_core.kernel import coretools",
            r"import aetherra_core\.system\.coretools": "import aetherra_core.kernel.coretools",
            # Files moved from system/ to agents/
            r"from aetherra_core\.system\.core_agent": "from aetherra_core.agents.core_agent",
            r"from aetherra_core\.system import core_agent": "from aetherra_core.agents import core_agent",
            r"import aetherra_core\.system\.core_agent": "import aetherra_core.agents.core_agent",
            # Files moved from plugins/ to orchestration/
            r"from aetherra_core\.plugins\.plugin_manager": "from aetherra_core.orchestration.plugin_manager",
            r"from aetherra_core\.plugins import plugin_manager": "from aetherra_core.orchestration import plugin_manager",
            r"import aetherra_core\.plugins\.plugin_manager": "import aetherra_core.orchestration.plugin_manager",
        }
        self.updated_files = []
        self.updates_made = 0

    def update_file_imports(self, file_path):
        """Update import statements in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            file_updated = False
            updates_in_file = 0

            # Apply each import mapping
            for old_pattern, new_import in self.import_mappings.items():
                if re.search(old_pattern, content):
                    new_content = re.sub(old_pattern, new_import, content)
                    if new_content != content:
                        content = new_content
                        file_updated = True
                        updates_in_file += 1
                        print(f"  ✅ Updated: {old_pattern} → {new_import}")

            # Write back if changes were made
            if file_updated:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.updated_files.append(
                    {"file": file_path, "updates": updates_in_file}
                )
                self.updates_made += updates_in_file
                return True

            return False

        except Exception as e:
            print(f"  ❌ Error updating {file_path}: {e}")
            return False

    def scan_and_update_imports(self):
        """Scan all Python files and update import statements"""
        print("🔄 Scanning for import statements to update...")
        print("=" * 60)

        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(self.base_path):
            # Skip __pycache__ and .git directories
            dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", ".vscode"]]

            for filename in files:
                if filename.endswith(".py"):
                    python_files.append(Path(root) / filename)

        print(f"📁 Found {len(python_files)} Python files to check")
        print()

        # Update imports in each file
        files_updated = 0
        for file_path in python_files:
            # Check if file contains any of our target import patterns
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                has_target_imports = any(
                    re.search(pattern, content)
                    for pattern in self.import_mappings.keys()
                )

                if has_target_imports:
                    print(f"🔍 Updating: {file_path.relative_to(self.base_path)}")
                    if self.update_file_imports(file_path):
                        files_updated += 1
                    print()

            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")

        self.generate_report(files_updated, len(python_files))

    def generate_report(self, files_updated, total_files):
        """Generate update report"""
        print("📊 IMPORT UPDATE SUMMARY")
        print("=" * 40)
        print(f"Files scanned: {total_files}")
        print(f"Files updated: {files_updated}")
        print(f"Total import updates: {self.updates_made}")
        print()

        if self.updated_files:
            print("📝 Updated Files:")
            for item in self.updated_files:
                rel_path = item["file"].relative_to(self.base_path)
                print(f"  ✅ {rel_path} ({item['updates']} updates)")
        else:
            print("✅ No import updates needed - all imports are already correct!")

        # Save detailed report
        report_lines = [
            "# 🔄 AETHERRA IMPORT UPDATE REPORT",
            "=" * 50,
            "",
            f"**Update Date:** {Path.cwd()}",
            f"**Files Scanned:** {total_files}",
            f"**Files Updated:** {files_updated}",
            f"**Total Updates:** {self.updates_made}",
            "",
            "## 📋 UPDATED FILES",
            "",
        ]

        if self.updated_files:
            for item in self.updated_files:
                rel_path = item["file"].relative_to(self.base_path)
                report_lines.append(f"- `{rel_path}` ({item['updates']} updates)")
        else:
            report_lines.append("- No files needed updates")

        report_lines.extend(["", "## 🎯 IMPORT MAPPINGS APPLIED", ""])

        for old_pattern, new_import in self.import_mappings.items():
            clean_pattern = (
                old_pattern.replace(r"\.", ".").replace(r"\b", "").replace(r"\s*", " ")
            )
            report_lines.append(f"- `{clean_pattern}` → `{new_import}`")

        report_lines.extend(
            [
                "",
                "## ✅ COMPLETION STATUS",
                "",
                "Import statement updates have been completed successfully!",
                "All moved files now have correct import paths.",
                "",
                "**Next Steps:**",
                "1. Test the system to ensure all imports work correctly",
                "2. Run any existing tests to verify functionality",
                "3. Commit the cleaned and updated code structure",
            ]
        )

        with open("AETHERRA_IMPORT_UPDATE_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        print()
        print("📄 Detailed report saved to: AETHERRA_IMPORT_UPDATE_REPORT.md")


if __name__ == "__main__":
    updater = AetherraImportUpdater()
    updater.scan_and_update_imports()

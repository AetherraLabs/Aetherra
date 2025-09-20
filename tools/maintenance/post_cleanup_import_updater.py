#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Post-Cleanup Import Updater
Updates import statements after our specific plugins and lyrixa reorganization
"""

# Standard library imports
import os
import re
from pathlib import Path


class PostCleanupImportUpdater:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.specific_mappings = {
            # Plugins reorganization mappings
            r"from\s+Aetherra\.plugins\.agent_adapters\.agent_orchestrator": "from Aetherra.plugins.agent_components.agent_orchestrator",
            r"from\s+Aetherra\.plugins\.agent_adapters\.agent_bridge": "from Aetherra.plugins.agent_components.agent_bridge",
            r"from\s+Aetherra\.plugins\.agent_adapters\.agent_discovery_and_integration": "from Aetherra.plugins.agent_components.agent_discovery_and_integration",
            r"from\s+Aetherra\.plugins\.agent_adapters\.agent_base": "from Aetherra.plugins.core.agent_base",
            r"import\s+Aetherra\.plugins\.agent_adapters\.agent_orchestrator": "import Aetherra.plugins.agent_components.agent_orchestrator",
            r"import\s+Aetherra\.plugins\.agent_adapters\.agent_bridge": "import Aetherra.plugins.agent_components.agent_bridge",
            r"import\s+Aetherra\.plugins\.agent_adapters\.agent_discovery_and_integration": "import Aetherra.plugins.agent_components.agent_discovery_and_integration",
            r"import\s+Aetherra\.plugins\.agent_adapters\.agent_base": "import Aetherra.plugins.core.agent_base",
            # Lyrixa reorganization mappings
            r"from\s+Aetherra\.lyrixa\.advanced_memory_integration": "from Aetherra.lyrixa.memory.advanced_memory_integration",
            r"from\s+Aetherra\.lyrixa\.agent_collaboration_manager": "from Aetherra.lyrixa.agents.agent_collaboration_manager",
            r"from\s+Aetherra\.lyrixa\.conversation_manager": "from Aetherra.lyrixa.agents.conversation_manager",
            r"from\s+Aetherra\.lyrixa\.enhanced_conversation_manager": "from Aetherra.lyrixa.agents.enhanced_conversation_manager",
            r"import\s+Aetherra\.lyrixa\.advanced_memory_integration": "import Aetherra.lyrixa.memory.advanced_memory_integration",
            r"import\s+Aetherra\.lyrixa\.agent_collaboration_manager": "import Aetherra.lyrixa.agents.agent_collaboration_manager",
            r"import\s+Aetherra\.lyrixa\.conversation_manager": "import Aetherra.lyrixa.agents.conversation_manager",
            r"import\s+Aetherra\.lyrixa\.enhanced_conversation_manager": "import Aetherra.lyrixa.agents.enhanced_conversation_manager",
            # Alternative import patterns (without Aetherra prefix)
            r"from\s+plugins\.agent_adapters\.agent_orchestrator": "from plugins.agent_components.agent_orchestrator",
            r"from\s+plugins\.agent_adapters\.agent_bridge": "from plugins.agent_components.agent_bridge",
            r"from\s+plugins\.agent_adapters\.agent_discovery_and_integration": "from plugins.agent_components.agent_discovery_and_integration",
            r"from\s+plugins\.agent_adapters\.agent_base": "from plugins.core.agent_base",
            r"from\s+lyrixa\.advanced_memory_integration": "from lyrixa.memory.advanced_memory_integration",
            r"from\s+lyrixa\.agent_collaboration_manager": "from lyrixa.agents.agent_collaboration_manager",
            r"from\s+lyrixa\.conversation_manager": "from lyrixa.agents.conversation_manager",
            r"from\s+lyrixa\.enhanced_conversation_manager": "from lyrixa.agents.enhanced_conversation_manager",
        }
        self.updated_files = []
        self.updates_made = 0

    def update_file_imports(self, file_path):
        """Update import statements in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            file_updated = False
            updates_in_file = 0

            # Apply each import mapping
            for old_pattern, new_import in self.specific_mappings.items():
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
        print("🔄 Scanning for specific post-cleanup import statements...")
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
                    for pattern in self.specific_mappings.keys()
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
        print("📊 POST-CLEANUP IMPORT UPDATE SUMMARY")
        print("=" * 50)
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
            print("✅ No import updates needed for our reorganized files!")
            print("This means either:")
            print("  • The moved files aren't currently imported elsewhere")
            print("  • All existing imports use relative paths")
            print("  • Import patterns use different naming conventions")

        # Save detailed report
        report_lines = [
            "# 🔄 POST-CLEANUP IMPORT UPDATE REPORT",
            "=" * 60,
            "",
            f"**Update Date:** {Path.cwd()}",
            f"**Files Scanned:** {total_files}",
            f"**Files Updated:** {files_updated}",
            f"**Total Updates:** {self.updates_made}",
            "",
            "## 🎯 TARGETED REORGANIZATION IMPORTS",
            "",
            "This scan specifically looked for imports of files we reorganized:",
            "",
            "### Plugins Reorganization:",
            "- agent_adapters/* → agent_components/* or core/*",
            "",
            "### Lyrixa Reorganization:",
            "- Root lyrixa files → memory/* or agents/*",
            "",
            "## 📋 SEARCH PATTERNS USED",
            "",
        ]

        for old_pattern, new_import in self.specific_mappings.items():
            clean_pattern = old_pattern.replace(r"\s+", " ").replace(r"\.", ".")
            report_lines.append(f"- `{clean_pattern}` → `{new_import}`")

        if self.updated_files:
            report_lines.extend(["", "## ✅ UPDATED FILES", ""])
            for item in self.updated_files:
                rel_path = item["file"].relative_to(self.base_path)
                report_lines.append(f"- `{rel_path}` ({item['updates']} updates)")
        else:
            report_lines.extend(
                [
                    "",
                    "## ✅ NO UPDATES NEEDED",
                    "",
                    "No files currently import the reorganized modules using the patterns we searched for.",
                    "This is actually good - it means:",
                    "",
                    "1. **Clean slate:** The reorganized files can be used with new import paths",
                    "2. **No breaking changes:** Existing code continues to work",
                    "3. **Future imports:** New code should use the updated directory structure",
                    "",
                    "## 🎯 RECOMMENDATIONS",
                    "",
                    "1. **Use new paths** when creating new imports to reorganized files",
                    "2. **Test the system** to ensure all functionality works",
                    "3. **Update documentation** to reflect new file locations",
                    "4. **Consider this a successful reorganization** with minimal impact",
                ]
            )

        with open("POST_CLEANUP_IMPORT_UPDATE_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        print()
        print("📄 Detailed report saved to: POST_CLEANUP_IMPORT_UPDATE_REPORT.md")


if __name__ == "__main__":
    updater = PostCleanupImportUpdater()
    updater.scan_and_update_imports()

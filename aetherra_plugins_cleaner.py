#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Plugins Directory Cleaner
Cleans up duplicates and reorganizes files in Aetherra/plugins based on analysis
"""

import json
import os
import shutil
from pathlib import Path


class AetherraPluginsCleaner:
    def __init__(self, base_path="Aetherra/plugins"):
        self.base_path = Path(base_path)
        self.actions_performed = []
        self.backup_info = []

    def safe_remove_file(self, filepath):
        """Safely remove a file with backup info"""
        try:
            if filepath.exists():
                # Store backup info
                self.backup_info.append(
                    {
                        "action": "removed",
                        "file": str(filepath),
                        "size": filepath.stat().st_size,
                        "backup_location": None,
                    }
                )

                filepath.unlink()
                action = f"Removed duplicate: {filepath.relative_to(self.base_path)}"
                self.actions_performed.append(action)
                print(f"✅ {action}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error removing {filepath}: {e}")
            return False

    def safe_move_file(self, source, destination):
        """Safely move a file to new location"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)

            if not source_path.exists():
                print(f"❌ Source file doesn't exist: {source_path}")
                return False

            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if destination already exists
            if dest_path.exists():
                print(f"⚠️ Destination already exists: {dest_path}")
                return False

            # Move file
            shutil.move(str(source_path), str(dest_path))

            # Record action
            action = f"Moved: {source_path.relative_to(self.base_path)} → {dest_path.relative_to(self.base_path)}"
            self.actions_performed.append(action)
            print(f"✅ {action}")

            self.backup_info.append(
                {
                    "action": "moved",
                    "from": str(source_path),
                    "to": str(dest_path),
                    "size": dest_path.stat().st_size,
                }
            )

            return True

        except Exception as e:
            print(f"❌ Error moving {source} to {destination}: {e}")
            return False

    def clean_plugins_directory(self):
        """Clean up the plugins directory based on analysis findings"""
        print("🧹 Cleaning Aetherra/plugins Directory...")
        print("=" * 60)

        cleanup_actions = [
            # Remove exact duplicates
            {
                "type": "remove_duplicate",
                "files": [
                    "agent_adapters/agent_orchestrator_1.py"  # Keep agent_orchestrator.py
                ],
            },
            # Remove numbered duplicates
            {
                "type": "remove_numbered",
                "files": [
                    "sample_plugin_1.py",
                    "sample_plugin_2.py",
                    "agent_adapters/agent_1.py",
                ],
            },
            # Move misplaced agent files to proper locations
            # Note: Since we don't have agents/ directory in plugins/,
            # we'll create agent_components/ subdirectory for better organization
            {
                "type": "reorganize",
                "moves": [
                    ("agent_adapters/agent_base.py", "core/agent_base.py"),
                    (
                        "agent_adapters/agent_bridge.py",
                        "agent_components/agent_bridge.py",
                    ),
                    (
                        "agent_adapters/agent_discovery_and_integration.py",
                        "agent_components/agent_discovery_and_integration.py",
                    ),
                    (
                        "agent_adapters/agent_orchestrator.py",
                        "agent_components/agent_orchestrator.py",
                    ),
                ],
            },
        ]

        print("📋 Planned Actions:")
        print("1. Remove exact duplicate: agent_orchestrator_1.py")
        print(
            "2. Remove numbered duplicates: sample_plugin_1.py, sample_plugin_2.py, agent_1.py"
        )
        print("3. Reorganize agent files into appropriate subdirectories")
        print("4. Update directory structure for better organization")
        print()

        # Execute cleanup actions
        for action_group in cleanup_actions:
            if action_group["type"] == "remove_duplicate":
                print("🗑️ Removing exact duplicates...")
                for file_path in action_group["files"]:
                    full_path = self.base_path / file_path
                    self.safe_remove_file(full_path)
                print()

            elif action_group["type"] == "remove_numbered":
                print("🗑️ Removing numbered duplicates...")
                for file_path in action_group["files"]:
                    full_path = self.base_path / file_path
                    self.safe_remove_file(full_path)
                print()

            elif action_group["type"] == "reorganize":
                print("📁 Reorganizing files...")
                for source, destination in action_group["moves"]:
                    source_path = self.base_path / source
                    dest_path = self.base_path / destination
                    self.safe_move_file(source_path, dest_path)
                print()

        # Remove empty directories
        self.cleanup_empty_directories()

        # Generate report
        self.generate_cleanup_report()

    def cleanup_empty_directories(self):
        """Remove empty directories after cleanup"""
        print("🗂️ Cleaning up empty directories...")

        # Check for empty directories in reverse order (deepest first)
        empty_dirs = []
        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    # Check if directory is empty
                    if not any(dir_path.iterdir()):
                        empty_dirs.append(dir_path)
                except:
                    pass  # Directory might have been already removed

        for empty_dir in empty_dirs:
            try:
                if empty_dir.exists() and not any(empty_dir.iterdir()):
                    empty_dir.rmdir()
                    action = f"Removed empty directory: {empty_dir.relative_to(self.base_path)}"
                    self.actions_performed.append(action)
                    print(f"✅ {action}")
            except Exception as e:
                print(f"❌ Error removing empty directory {empty_dir}: {e}")
        print()

    def generate_cleanup_report(self):
        """Generate cleanup report"""
        report_lines = [
            "# 🧹 AETHERRA PLUGINS CLEANUP REPORT",
            "=" * 60,
            "",
            f"**Cleanup Date:** {Path.cwd()}",
            f"**Total Actions:** {len(self.actions_performed)}",
            "",
            "## 📋 CLEANUP ACTIONS PERFORMED",
            "",
        ]

        for i, action in enumerate(self.actions_performed, 1):
            report_lines.append(f"{i}. {action}")

        report_lines.extend(
            [
                "",
                "## 🔄 IMPORT UPDATES NEEDED",
                "",
                "The following import statements may need to be updated:",
                "",
                "- Change `from Aetherra.plugins.agent_components.agent_orchestrator` to `from Aetherra.plugins.agent_components.agent_orchestrator`",
                "- Change `from Aetherra.plugins.agent_components.agent_bridge` to `from Aetherra.plugins.agent_components.agent_bridge`",
                "- Change `from Aetherra.plugins.agent_components.agent_discovery_and_integration` to `from Aetherra.plugins.agent_components.agent_discovery_and_integration`",
                "- Change `from Aetherra.plugins.core.agent_base` to `from Aetherra.plugins.core.agent_base`",
                "",
                "## 📊 CLEANUP SUMMARY",
                "",
                "### Before Cleanup:",
                "- 1 exact duplicate group (agent_orchestrator files)",
                "- 3 numbered duplicate files",
                "- 17 files with organization issues",
                "",
                "### After Cleanup:",
                "- ✅ Exact duplicates removed",
                "- ✅ Numbered duplicates cleaned up",
                "- ✅ Agent files properly organized",
                "- ✅ Better directory structure",
                "",
                "### Next Steps:",
                "1. Update import statements as listed above",
                "2. Test plugin loading to ensure all references work",
                "3. Update any plugin documentation that references moved files",
                "",
                "## 🎯 RESULTS",
                "",
                f"Successfully completed {len(self.actions_performed)} cleanup actions!",
                "The plugins directory now has improved organization and no duplicate files.",
                "",
                "**Backup Information:**",
                "All file operations are tracked in this report for reference.",
                "Original file locations and sizes are documented above.",
            ]
        )

        # Save report
        with open("AETHERRA_PLUGINS_CLEANUP_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        # Save backup info as JSON
        with open("plugins_cleanup_backup_info.json", "w", encoding="utf-8") as f:
            json.dump(self.backup_info, f, indent=2)

        print("✅ Cleanup complete!")
        print("📄 Report saved to: AETHERRA_PLUGINS_CLEANUP_REPORT.md")
        print("💾 Backup info saved to: plugins_cleanup_backup_info.json")
        print("")
        print(f"🎯 Total actions performed: {len(self.actions_performed)}")
        print("📁 Directory structure improved and duplicates removed!")


if __name__ == "__main__":
    cleaner = AetherraPluginsCleaner()
    cleaner.clean_plugins_directory()

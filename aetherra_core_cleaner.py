#!/usr/bin/env python3
"""
Aetherra Core Cleanup Script
Removes exact duplicates and reorganizes misplaced files
"""

import os
import shutil
from pathlib import Path
import json

class AetherraCoreCleaner:
    def __init__(self, base_path="Aetherra/aetherra_core"):
        self.base_path = Path(base_path)
        self.cleanup_actions = []
        self.backup_info = {}

    def remove_exact_duplicates(self):
        """Remove exact duplicate files, keeping the one in the most appropriate directory"""

        duplicates_to_remove = [
            # Keep aetherra_grammar.py, remove aetherra_grammar_1.py
            ("agents/aetherra_grammar_1.py", "agents/aetherra_grammar.py"),

            # Keep aetherra_interpreter.py, remove aetherra_interpreter_1.py
            ("agents/aetherra_interpreter_1.py", "agents/aetherra_interpreter.py"),

            # Keep agents.py in orchestration/, remove from agents/
            ("agents/agents.py", "orchestration/agents.py"),

            # Keep base.py, remove base_1.py
            ("agents/base_1.py", "agents/base.py"),

            # Keep critique_agent.py in personality/, remove from agents/
            ("agents/critique_agent.py", "personality/critique_agent.py"),

            # Keep goal_forecaster.py in orchestration/, remove from agents/
            ("agents/goal_forecaster.py", "orchestration/goal_forecaster.py"),

            # Keep grammar.py, remove grammar_1.py
            ("agents/grammar_1.py", "agents/grammar.py"),

            # Keep intelligence.py in engine/, remove from agents/
            ("agents/intelligence.py", "engine/intelligence.py"),

            # Keep personality_engine.py in personality/, remove from agents/
            ("agents/personality_engine.py", "personality/personality_engine.py"),

            # Keep prompt_engine.py in engine/, remove from agents/
            ("agents/prompt_engine.py", "engine/prompt_engine.py"),

            # Keep episodic_timeline.py in fractal_mesh/timelines/, remove from memory/
            ("memory/episodic_timeline.py", "memory/fractal_mesh/timelines/episodic_timeline.py"),
        ]

        print("🗑️ Removing exact duplicate files...")

        for file_to_remove, file_to_keep in duplicates_to_remove:
            remove_path = self.base_path / file_to_remove
            keep_path = self.base_path / file_to_keep

            if remove_path.exists() and keep_path.exists():
                print(f"   ❌ Removing: {file_to_remove}")
                print(f"   ✅ Keeping:  {file_to_keep}")

                # Backup file info
                self.backup_info[str(remove_path)] = {
                    'kept_version': str(keep_path),
                    'action': 'removed_duplicate'
                }

                # Remove the duplicate
                remove_path.unlink()
                self.cleanup_actions.append(f"Removed duplicate: {file_to_remove}")
            else:
                print(f"   ⚠️ Warning: Could not find {file_to_remove} or {file_to_keep}")

    def reorganize_misplaced_files(self):
        """Move files to more appropriate directories"""

        # Selected moves based on analysis (focusing on clear cases)
        moves = [
            # Move plugin-related files to plugins/
            ("agents/advanced_plugins.py", "plugins/advanced_plugins.py"),

            # Move memory-related files from system/ to memory/
            ("system/lightweight_memory_core.py", "memory/lightweight_memory_core.py"),
            ("system/memory_core.py", "memory/memory_core.py"),
            ("system/memory_core_adapter.py", "memory/memory_core_adapter.py"),
            ("system/world_class_memory_core.py", "memory/world_class_memory_core.py"),

            # Move core tools to appropriate locations
            ("system/coretools.py", "kernel/coretools.py"),
            ("system/core_agent.py", "agents/core_agent.py"),

            # Move plugin manager to orchestration
            ("plugins/plugin_manager.py", "orchestration/plugin_manager.py"),
        ]

        print("📁 Reorganizing misplaced files...")

        for old_path, new_path in moves:
            old_file = self.base_path / old_path
            new_file = self.base_path / new_path

            if old_file.exists():
                # Create target directory if it doesn't exist
                new_file.parent.mkdir(parents=True, exist_ok=True)

                print(f"   📦 Moving: {old_path} → {new_path}")

                # Move the file
                shutil.move(str(old_file), str(new_file))

                self.backup_info[str(old_file)] = {
                    'moved_to': str(new_file),
                    'action': 'moved'
                }

                self.cleanup_actions.append(f"Moved: {old_path} → {new_path}")
            else:
                print(f"   ⚠️ Warning: Could not find {old_path}")

    def remove_numbered_duplicates(self):
        """Remove remaining numbered duplicate files"""

        numbered_files = [
            "agents/aetherra_parser_1.py",
            "agents/parser_1.py",
            "agents/__init___17.py",
            "agents/__init___9.py",
        ]

        print("🔢 Removing numbered duplicate files...")

        for file_path in numbered_files:
            file_to_remove = self.base_path / file_path

            if file_to_remove.exists():
                print(f"   ❌ Removing: {file_path}")

                self.backup_info[str(file_to_remove)] = {
                    'action': 'removed_numbered_duplicate'
                }

                file_to_remove.unlink()
                self.cleanup_actions.append(f"Removed numbered duplicate: {file_path}")

    def cleanup_empty_directories(self):
        """Remove any empty directories created by the cleanup"""

        print("🧹 Cleaning up empty directories...")

        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):  # Directory is empty
                        print(f"   📁 Removing empty directory: {dir_path.relative_to(self.base_path)}")
                        dir_path.rmdir()
                        self.cleanup_actions.append(f"Removed empty directory: {dir_path.relative_to(self.base_path)}")
                except OSError:
                    pass  # Directory not empty or other issue

    def generate_cleanup_report(self):
        """Generate a report of all cleanup actions"""

        report = []
        report.append("# 🧹 AETHERRA CORE CLEANUP REPORT")
        report.append("=" * 60)
        report.append("")
        report.append(f"**Cleanup Date:** {Path().cwd()}")
        report.append(f"**Total Actions:** {len(self.cleanup_actions)}")
        report.append("")

        report.append("## 📋 CLEANUP ACTIONS PERFORMED")
        report.append("")

        for i, action in enumerate(self.cleanup_actions, 1):
            report.append(f"{i}. {action}")

        report.append("")
        report.append("## 🔄 IMPORT UPDATES NEEDED")
        report.append("")
        report.append("The following import statements may need to be updated:")
        report.append("")

        # Generate import update suggestions
        for old_path, info in self.backup_info.items():
            if info['action'] == 'moved':
                old_module = old_path.replace('/', '.').replace('.py', '').replace(str(self.base_path), 'aetherra_core')
                new_module = info['moved_to'].replace('/', '.').replace('.py', '').replace(str(self.base_path), 'aetherra_core')
                report.append(f"- Change `from {old_module}` to `from {new_module}`")

        report.append("")
        report.append("## ✅ CLEANUP COMPLETE")
        report.append("")
        report.append("The aetherra_core directory has been cleaned and organized:")
        report.append("- ✅ Exact duplicates removed")
        report.append("- ✅ Files moved to appropriate directories")
        report.append("- ✅ Numbered duplicates eliminated")
        report.append("- ✅ Empty directories cleaned")
        report.append("")
        report.append("**Next Steps:**")
        report.append("1. Update import statements as listed above")
        report.append("2. Test the system to ensure all references work")
        report.append("3. Commit the cleaned structure to git")

        # Save report
        report_content = "\n".join(report)

        with open("AETHERRA_CORE_CLEANUP_REPORT.md", "w", encoding='utf-8') as f:
            f.write(report_content)

        # Save backup info as JSON
        with open("aetherra_core_cleanup_backup.json", "w", encoding='utf-8') as f:
            json.dump(self.backup_info, f, indent=2)

        print("📄 Cleanup report saved to: AETHERRA_CORE_CLEANUP_REPORT.md")
        print("💾 Backup info saved to: aetherra_core_cleanup_backup.json")

    def run_cleanup(self):
        """Run the complete cleanup process"""

        print("🧹 Starting Aetherra Core Cleanup...")
        print("=" * 60)
        print("")

        # Step 1: Remove exact duplicates
        self.remove_exact_duplicates()
        print("")

        # Step 2: Reorganize misplaced files
        self.reorganize_misplaced_files()
        print("")

        # Step 3: Remove numbered duplicates
        self.remove_numbered_duplicates()
        print("")

        # Step 4: Clean up empty directories
        self.cleanup_empty_directories()
        print("")

        # Step 5: Generate report
        self.generate_cleanup_report()
        print("")

        print("🎉 Aetherra Core cleanup completed successfully!")
        print(f"📊 Total cleanup actions: {len(self.cleanup_actions)}")

if __name__ == "__main__":
    cleaner = AetherraCoreCleaner()
    cleaner.run_cleanup()

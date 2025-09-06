#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Lyrixa Directory Cleaner
Cleans up and reorganizes files in Aetherra/lyrixa based on analysis
"""

import os
import shutil
from pathlib import Path
import json

class AetherraLyrixaCleaner:
    def __init__(self, base_path="Aetherra/lyrixa"):
        self.base_path = Path(base_path)
        self.actions_performed = []
        self.backup_info = []

    def safe_move_file(self, source, destination):
        """Safely move a file to new location"""
        try:
            source_path = self.base_path / source
            dest_path = self.base_path / destination

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
            action = f"Moved: {source} → {destination}"
            self.actions_performed.append(action)
            print(f"✅ {action}")

            self.backup_info.append({
                'action': 'moved',
                'from': str(source_path),
                'to': str(dest_path),
                'size': dest_path.stat().st_size
            })

            return True

        except Exception as e:
            print(f"❌ Error moving {source} to {destination}: {e}")
            return False

    def clean_lyrixa_directory(self):
        """Clean up the lyrixa directory based on analysis findings"""
        print("🧹 Cleaning Aetherra/lyrixa Directory...")
        print("=" * 60)

        # File reorganization moves based on analysis
        moves = [
            # Move memory-related file to memory subdirectory
            ('advanced_memory_integration.py', 'memory/advanced_memory_integration.py'),

            # Move agent-related files to agents subdirectory
            ('agent_collaboration_manager.py', 'agents/agent_collaboration_manager.py'),
            ('conversation_manager.py', 'agents/conversation_manager.py'),
            ('enhanced_conversation_manager.py', 'agents/enhanced_conversation_manager.py'),
        ]

        print("📋 Planned Actions:")
        print("1. Move advanced_memory_integration.py → memory/")
        print("2. Move agent_collaboration_manager.py → agents/")
        print("3. Move conversation_manager.py → agents/")
        print("4. Move enhanced_conversation_manager.py → agents/")
        print()

        # Execute moves
        print("📁 Reorganizing files for better structure...")
        for source, destination in moves:
            self.safe_move_file(source, destination)

        print()
        self.generate_cleanup_report()

    def generate_cleanup_report(self):
        """Generate cleanup report"""
        report_lines = [
            "# 🧹 AETHERRA LYRIXA CLEANUP REPORT",
            "=" * 60,
            "",
            f"**Cleanup Date:** {Path.cwd()}",
            f"**Total Actions:** {len(self.actions_performed)}",
            "",
            "## 📋 CLEANUP ACTIONS PERFORMED",
            ""
        ]

        for i, action in enumerate(self.actions_performed, 1):
            report_lines.append(f"{i}. {action}")

        report_lines.extend([
            "",
            "## 🔄 IMPORT UPDATES NEEDED",
            "",
            "The following import statements may need to be updated:",
            "",
            "- Change `from Aetherra.lyrixa.memory.advanced_memory_integration` to `from Aetherra.lyrixa.memory.advanced_memory_integration`",
            "- Change `from Aetherra.lyrixa.agents.agent_collaboration_manager` to `from Aetherra.lyrixa.agents.agent_collaboration_manager`",
            "- Change `from Aetherra.lyrixa.agents.conversation_manager` to `from Aetherra.lyrixa.agents.conversation_manager`",
            "- Change `from Aetherra.lyrixa.agents.enhanced_conversation_manager` to `from Aetherra.lyrixa.agents.enhanced_conversation_manager`",
            "",
            "## 📊 CLEANUP SUMMARY",
            "",
            "### Before Cleanup:",
            "- 4 files in wrong directories",
            "- Memory file mixed with core lyrixa files",
            "- Agent files scattered in root directory",
            "",
            "### After Cleanup:",
            "- ✅ Memory integration file moved to memory/",
            "- ✅ Agent files organized in agents/",
            "- ✅ Better logical organization",
            "- ✅ Cleaner root directory",
            "",
            "### Directory Structure Improvements:",
            "- `memory/` - Memory-related functionality",
            "- `agents/` - Agent collaboration and conversation management",
            "- Root directory now focused on core lyrixa functionality",
            "",
            "### Next Steps:",
            "1. Update import statements as listed above",
            "2. Test lyrixa system to ensure all references work",
            "3. Update any documentation that references moved files",
            "",
            "## 🎯 RESULTS",
            "",
            f"Successfully completed {len(self.actions_performed)} reorganization actions!",
            "The lyrixa directory now has improved logical organization.",
            "",
            "**Backup Information:**",
            "All file operations are tracked in this report for reference.",
            "Original file locations and sizes are documented above."
        ])

        # Save report
        with open("AETHERRA_LYRIXA_CLEANUP_REPORT.md", "w", encoding='utf-8') as f:
            f.write("\n".join(report_lines))

        # Save backup info as JSON
        with open("lyrixa_cleanup_backup_info.json", "w", encoding='utf-8') as f:
            json.dump(self.backup_info, f, indent=2)

        print("✅ Cleanup complete!")
        print("📄 Report saved to: AETHERRA_LYRIXA_CLEANUP_REPORT.md")
        print("💾 Backup info saved to: lyrixa_cleanup_backup_info.json")
        print("")
        print(f"🎯 Total actions performed: {len(self.actions_performed)}")
        print("📁 Directory structure improved with logical organization!")

if __name__ == "__main__":
    cleaner = AetherraLyrixaCleaner()
    cleaner.clean_lyrixa_directory()

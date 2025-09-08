#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎯 Final Aetherra Core File Organization
======================================
Moves the remaining misplaced files to their correct directories.
"""

import logging
import os
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FinalFileOrganizer:
    def __init__(self, base_path="Aetherra/aetherra_core", dry_run=False):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.backup_dir = Path("final_organization_backup")
        self.moves_performed = []

        # Create backup directory
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)

    def get_final_moves(self):
        """Get the strategic file moves that make the most sense"""

        moves = {
            # Agent files that should move to other directories
            "agents/multi_agent_manager.py": "orchestration/multi_agent_manager.py",
            "agents/security_system.py": "system/security_system.py",
            "agents/system_bootstrap.py": "system/system_bootstrap.py",
            "agents/web_bridge.py": "kernel/web_bridge.py",
            # Engine files that are misplaced
            "engine/agent_executor.py": "agents/agent_executor.py",  # Move back to agents
            "engine/introspection_controller.py": "reflection/introspection_controller.py",
            "engine/personality_engine.py": "personality/personality_engine.py",
            "engine/plugin_chain_executor.py": "plugins/plugin_chain_executor.py",
            "engine/quantum_memory_engine.py": "memory/quantum_memory_engine.py",
            "engine/reasoning_engine.py": "cognitive/reasoning_engine.py",
            # Intelligence engine files
            "engine/intelligence/meta_reasoning.py": "cognitive/meta_reasoning.py",
            # Kernel files that belong elsewhere
            "kernel/memory_kernel.py": "memory/memory_kernel.py",
            "kernel/plugin_registry.py": "plugins/plugin_registry.py",
            "kernel/coretools.py": "system/coretools.py",
            # Memory files
            "memory/compression_analyzer.py": "file_system/compression_analyzer.py",
            "memory/enhanced_memory_manager.py": "memory/enhanced_memory_manager.py",  # Keep in memory
            "memory/fractal_mesh/components.py": "memory/fractal_mesh/components.py",  # Keep as is
            # Orchestration files
            "orchestration/knowledge_graph.py": "intelligence/knowledge_graph.py",
            "orchestration/memory_orchestrator.py": "memory/memory_orchestrator.py",
            "orchestration/personality_manager.py": "personality/personality_manager.py",
            # Personality files
            "personality/adaptive_personality.py": "personality/adaptive_personality.py",  # Keep
            "personality/introspective_personality.py": "reflection/introspective_personality.py",
            # Plugin files
            "plugins/memory_plugin_manager.py": "memory/memory_plugin_manager.py",
            # Reflection files
            "reflection/reflection_agent.py": "reflection/reflection_agent.py",  # Keep
            # System files
            "system/base_system.py": "system/base_system.py",  # Keep
            "system/reflection_system.py": "system/reflection_system.py",  # Keep
        }

        # Filter to only include files that actually exist
        existing_moves = {}
        for src, dst in moves.items():
            src_path = self.base_path / src
            if src_path.exists():
                existing_moves[src] = dst
            else:
                logger.warning(f"⚠️ Source file not found: {src}")

        return existing_moves

    def backup_file(self, file_path):
        """Create a backup of the file before moving"""
        if self.dry_run:
            return

        try:
            rel_path = file_path.relative_to(self.base_path)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            logger.info(f"💾 Backed up: {rel_path}")
        except Exception as e:
            logger.error(f"❌ Backup failed for {file_path}: {e}")

    def move_file(self, src_path, dst_path):
        """Move a file from source to destination"""
        src_full = self.base_path / src_path
        dst_full = self.base_path / dst_path

        if self.dry_run:
            logger.info(f"   [DRY RUN] Would move: {src_path} → {dst_path}")
            return True

        try:
            # Create destination directory if needed
            dst_full.parent.mkdir(parents=True, exist_ok=True)

            # Backup source file
            self.backup_file(src_full)

            # Move the file
            shutil.move(str(src_full), str(dst_full))
            logger.info(f"✅ Moved: {src_path} → {dst_path}")
            self.moves_performed.append((src_path, dst_path))
            return True

        except Exception as e:
            logger.error(f"❌ Failed to move {src_path} → {dst_path}: {e}")
            return False

    def run_final_organization(self):
        """Execute the final organization"""
        logger.info("🚀 Starting Final File Organization...")
        logger.info(f"📁 Target directory: {self.base_path}")
        logger.info(f"🔄 Dry run mode: {self.dry_run}")
        logger.info("=" * 60)

        moves = self.get_final_moves()

        if not moves:
            logger.info("✅ No files need to be moved!")
            return

        logger.info(f"📦 Planning to move {len(moves)} files...")

        for src_path, dst_path in moves.items():
            logger.info(f"📦 Moving: {src_path} → {dst_path}")
            self.move_file(src_path, dst_path)

        # Clean up empty directories
        self.cleanup_empty_directories()

        # Generate final report
        self.generate_final_report()

        logger.info("✅ Final organization completed!")
        logger.info(f"📦 Files moved: {len(self.moves_performed)}")

    def cleanup_empty_directories(self):
        """Remove empty directories"""
        if self.dry_run:
            logger.info("🧹 [DRY RUN] Would clean up empty directories...")
            return

        logger.info("🧹 Cleaning up empty directories...")

        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):  # Directory is empty
                        dir_path.rmdir()
                        rel_path = dir_path.relative_to(self.base_path)
                        logger.info(f"🗑️ Removed empty directory: {rel_path}")
                except OSError:
                    pass  # Directory not empty or can't be removed

    def generate_final_report(self):
        """Generate a final organization report"""
        report = []
        report.append("# 🎯 FINAL AETHERRA CORE ORGANIZATION REPORT")
        report.append("=" * 60)
        report.append("")

        if self.moves_performed:
            report.append("## 📦 Files Moved")
            report.append("")
            for src, dst in self.moves_performed:
                report.append(f"- `{src}` → `{dst}`")
            report.append("")

        report.append("## 📊 Summary")
        report.append("")
        report.append(f"- **Files moved:** {len(self.moves_performed)}")
        report.append(f"- **Dry run mode:** {self.dry_run}")
        report.append("")

        report.append("## ✅ Next Steps")
        report.append("")
        report.append("1. Run the Aetherra OS to test functionality")
        report.append("2. Check for any import errors")
        report.append("3. Run the analyzer to verify organization")
        report.append("4. Update documentation if needed")
        report.append("")

        report_content = "\n".join(report)

        with open("FINAL_ORGANIZATION_REPORT.md", "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info("📄 Final report saved to: FINAL_ORGANIZATION_REPORT.md")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Final Aetherra Core file organization"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the moves (default is dry run)",
    )
    parser.add_argument(
        "--base-path",
        default="Aetherra/aetherra_core",
        help="Base path to aetherra_core directory",
    )

    args = parser.parse_args()

    # Run final organization
    organizer = FinalFileOrganizer(base_path=args.base_path, dry_run=not args.execute)

    organizer.run_final_organization()


if __name__ == "__main__":
    main()

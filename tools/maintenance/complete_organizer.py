#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎯 Complete Aetherra Core Organization & Import Fixer
===================================================
Addresses ALL remaining organizational issues and fixes imports systematically.
"""

import ast
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ComprehensiveAetherraOrganizer:
    def __init__(self, base_path="Aetherra/aetherra_core", dry_run=False):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.backup_dir = Path("comprehensive_cleanup_backup")
        self.moves_performed = []
        self.import_fixes = []

        # Create backup directory
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)

    def get_comprehensive_reorganization_plan(self) -> Dict[str, str]:
        """Generate a comprehensive reorganization plan based on file analysis"""

        reorganization_plan = {}

        # Agent-related files → agents/
        agent_files = {
            "agents/agent_executor.py": "engine/agent_executor.py",  # Actually belongs in engine
            "agents/collaboration.py": "agents/collaboration.py",  # Keep in agents
            "agents/contradiction_detection_agent.py": "agents/contradiction_detection_agent.py",  # Keep
            "agents/conversation.py": "agents/conversation.py",  # Keep in agents
            "agents/conversation_manager.py": "agents/conversation_manager.py",  # Keep in agents
            "agents/core_agent.py": "agents/core_agent.py",  # Keep in agents (it's an agent)
            "agents/curiosity_agent.py": "agents/curiosity_agent.py",  # Keep
            "agents/data_manager.py": "orchestration/data_manager.py",  # Move to orchestration
            "agents/enhanced_conversation_manager.py": "agents/enhanced_conversation_manager.py",  # Keep
            "agents/enhanced_self_evaluation_agent.py": "agents/enhanced_self_evaluation_agent.py",  # Keep
            "agents/escalation_agent.py": "agents/escalation_agent.py",  # Keep
            "agents/intelligence_integration.py": "intelligence/intelligence_integration.py",  # Move to intelligence
            "agents/multi_agent_system.py": "agents/multi_agent_system.py",  # Keep
            "agents/optimized_integration.py": "agents/optimized_integration.py",  # Keep
            "agents/reflection_agent.py": "reflection/reflection_agent.py",  # Move to reflection
            "agents/security_system.py": "agents/security_system.py",  # Keep
        }

        # AI/Intelligence files → ai/ or intelligence/
        ai_files = {
            "ai/llm_integration.py": "ai/llm_integration.py",  # Keep
            "engine/intelligence.py": "intelligence/core_intelligence.py",  # Move to intelligence
        }

        # Engine files → engine/
        engine_files = {
            "memory/QuantumEnhancedMemoryEngine/engine.py": "engine/quantum_memory_engine.py",
            "memory/QuantumEnhancedMemoryEngine/bootstrap.py": "system/quantum_bootstrap.py",
        }

        # Memory organization
        memory_files = {
            "personality/memory_learning.py": "memory/memory_learning.py",
            "memory/QuantumEnhancedMemoryEngine/fractal_encoder.py": "memory/fractal_encoder.py",
            "memory/QuantumEnhancedMemoryEngine/quantum_bridge.py": "kernel/quantum_bridge.py",
        }

        # System files → system/
        system_files = {
            "personality/reflection_system.py": "system/reflection_system.py",
        }

        # Reflection files → reflection/
        reflection_files = {
            "agents/reflection_agent.py": "reflection/reflection_agent.py",
        }

        # Orchestration files
        orchestration_files = {
            "orchestration/agents.py": "agents/orchestration_bridge.py",  # Rename to avoid confusion
            "orchestration/goal_forecaster.py": "agents/goal_forecaster.py",
        }

        # Plugin files → plugins/
        plugin_files = {
            "kernel/memory_plugin_bridge.py": "plugins/memory_plugin_bridge.py",
        }

        # Personality files organization
        personality_files = {
            "personality/integration.py": "personality/integration.py",  # Keep
            "personality/multimodal_coordinator.py": "personality/multimodal_coordinator.py",  # Keep
            "personality/response_quality_integration.py": "personality/response_quality_integration.py",  # Keep
            "personality/social_learning_integration.py": "personality/social_learning_integration.py",  # Keep
            "personality/interfaces/text_personality.py": "personality/text_personality.py",  # Move up
        }

        # Metrics/Dashboard files → self_metrics_dashboard/
        metrics_files = {
            "memory/QuantumEnhancedMemoryEngine/fidelity_metrics.py": "self_metrics_dashboard/fidelity_metrics.py",
        }

        # Combine all plans
        all_moves = {}
        all_moves.update(agent_files)
        all_moves.update(ai_files)
        all_moves.update(engine_files)
        all_moves.update(memory_files)
        all_moves.update(system_files)
        all_moves.update(reflection_files)
        all_moves.update(orchestration_files)
        all_moves.update(plugin_files)
        all_moves.update(personality_files)
        all_moves.update(metrics_files)

        # Filter to only include actual moves (source != destination)
        reorganization_plan = {src: dst for src, dst in all_moves.items() if src != dst}

        return reorganization_plan

    def backup_file(self, filepath: Path) -> Path:
        """Create backup of file before modification"""
        if self.dry_run:
            return filepath

        relative_path = filepath.relative_to(self.base_path)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, backup_path)
        logger.info(f"💾 Backed up: {relative_path}")
        return backup_path

    def execute_reorganization(self):
        """Execute the comprehensive reorganization plan"""
        logger.info("📁 Executing comprehensive reorganization...")

        reorganization_plan = self.get_comprehensive_reorganization_plan()

        for old_path, new_path in reorganization_plan.items():
            source = self.base_path / old_path
            destination = self.base_path / new_path

            if source.exists():
                logger.info(f"📦 Moving: {old_path} → {new_path}")

                if not self.dry_run:
                    # Create destination directory if needed
                    destination.parent.mkdir(parents=True, exist_ok=True)

                    # Backup original
                    self.backup_file(source)

                    # Move file
                    shutil.move(str(source), str(destination))
                    self.moves_performed.append((old_path, new_path))
                else:
                    logger.info(f"   [DRY RUN] Would move: {old_path} → {new_path}")
            else:
                logger.warning(f"⚠️ Source file not found: {old_path}")

    def find_all_python_files(self) -> List[Path]:
        """Find all Python files in the aetherra_core directory"""
        python_files = []
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)
        return python_files

    def extract_imports(self, filepath: Path) -> List[tuple[str, str, int]]:
        """Extract import statements from a Python file"""
        imports = []
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(("import", alias.name, node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(
                            (
                                "from",
                                f"{module}.{alias.name}" if module else alias.name,
                                node.lineno,
                            )
                        )

        except Exception as e:
            logger.warning(f"⚠️ Could not parse imports from {filepath}: {e}")

        return imports

    def fix_imports_in_file(self, filepath: Path):
        """Fix imports in a single file based on the reorganization"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Build mapping of old module paths to new paths
            move_mapping = {}
            for old_path, new_path in self.moves_performed:
                old_module = old_path.replace("/", ".").replace(".py", "")
                new_module = new_path.replace("/", ".").replace(".py", "")
                move_mapping[old_module] = new_module

            # Fix relative imports
            for old_module, new_module in move_mapping.items():
                # Fix direct imports
                content = re.sub(
                    f"from aetherra_core\\.{re.escape(old_module)}",
                    f"from aetherra_core.{new_module}",
                    content,
                )
                content = re.sub(
                    f"import aetherra_core\\.{re.escape(old_module)}",
                    f"import aetherra_core.{new_module}",
                    content,
                )

                # Fix relative imports within the same package
                old_parts = old_module.split(".")
                new_parts = new_module.split(".")

                if len(old_parts) > 1 and len(new_parts) > 1:
                    # (old_package/new_package computed previously were unused; removed for clarity)
                    old_filename = old_parts[-1]
                    new_filename = new_parts[-1]

                    # Fix relative imports from the same package
                    content = re.sub(
                        f"from \\.{re.escape(old_filename)}",
                        f"from .{new_filename}",
                        content,
                    )

            # Fix broken relative imports by converting to absolute
            content = re.sub(r"from \.\. import", "from aetherra_core import", content)

            # Fix relative imports that might be broken
            content = re.sub(
                r"from \. import (\w+)",
                lambda m: f"from aetherra_core.{filepath.parent.name} import {m.group(1)}",
                content,
            )

            if content != original_content:
                if not self.dry_run:
                    self.backup_file(filepath)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)

                rel_path = filepath.relative_to(self.base_path)
                logger.info(f"🔧 Fixed imports in: {rel_path}")
                self.import_fixes.append(str(rel_path))

        except Exception as e:
            logger.warning(f"⚠️ Could not fix imports in {filepath}: {e}")

    def fix_all_imports(self):
        """Fix imports in all Python files"""
        logger.info("🔧 Fixing imports in all Python files...")

        python_files = self.find_all_python_files()

        for filepath in python_files:
            self.fix_imports_in_file(filepath)

    def clean_empty_directories(self):
        """Remove empty directories after reorganization"""
        logger.info("🧹 Cleaning up empty directories...")

        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        logger.info(
                            f"🗑️ Removing empty directory: {dir_path.relative_to(self.base_path)}"
                        )
                        if not self.dry_run:
                            dir_path.rmdir()
                except OSError:
                    pass

    def generate_final_report(self):
        """Generate comprehensive final report"""
        report = []
        report.append("# 🎯 COMPREHENSIVE AETHERRA CORE ORGANIZATION REPORT")
        report.append("=" * 60)
        report.append("")

        if self.dry_run:
            report.append("## 🔍 DRY RUN - No actual changes made")
            report.append("")

        report.append("## 📦 Files Reorganized")
        report.append("")
        if self.moves_performed:
            for old_path, new_path in self.moves_performed:
                report.append(f"- `{old_path}` → `{new_path}`")
        else:
            report.append("- No files moved")
        report.append("")

        report.append("## 🔧 Import Fixes Applied")
        report.append("")
        if self.import_fixes:
            for fixed_file in self.import_fixes:
                report.append(f"- `{fixed_file}`")
        else:
            report.append("- No import fixes needed")
        report.append("")

        report.append("## 📊 Summary Statistics")
        report.append("")
        report.append(f"- **Files moved:** {len(self.moves_performed)}")
        report.append(f"- **Import fixes applied:** {len(self.import_fixes)}")
        report.append("")

        report.append("## ✅ Recommended Next Steps")
        report.append("")
        report.append("1. Run the Aetherra OS to test functionality")
        report.append("2. Check for any remaining import errors")
        report.append("3. Run unit tests if available")
        report.append("4. Update documentation to reflect new structure")
        report.append("5. Commit the organized codebase")

        # Save report
        report_content = "\n".join(report)
        report_file = "COMPREHENSIVE_ORGANIZATION_REPORT.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"📄 Final report saved to: {report_file}")
        return report_content

    def run_complete_organization(self):
        """Execute the complete organization process"""
        logger.info("🚀 Starting Complete Aetherra Core Organization...")
        logger.info(f"📁 Target directory: {self.base_path}")
        logger.info(f"🔄 Dry run mode: {self.dry_run}")
        logger.info("=" * 60)

        try:
            # Step 1: Execute reorganization
            self.execute_reorganization()

            # Step 2: Fix all imports
            if not self.dry_run:
                self.fix_all_imports()

            # Step 3: Clean empty directories
            if not self.dry_run:
                self.clean_empty_directories()

            # Step 4: Generate final report
            self.generate_final_report()

            logger.info("✅ Complete organization finished successfully!")
            logger.info(f"📦 Files moved: {len(self.moves_performed)}")
            logger.info(f"🔧 Import fixes applied: {len(self.import_fixes)}")

        except Exception as e:
            logger.error(f"❌ Organization failed: {e}")
            raise


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Complete Aetherra Core organization and import fixing"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the organization (default is dry run)",
    )
    parser.add_argument(
        "--base-path",
        default="Aetherra/aetherra_core",
        help="Base path to aetherra_core directory",
    )

    args = parser.parse_args()

    # Run complete organization
    organizer = ComprehensiveAetherraOrganizer(
        base_path=args.base_path, dry_run=not args.execute
    )

    organizer.run_complete_organization()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Aetherra Project Cleanup Script
==============================

This script performs comprehensive cleanup of the Aetherra project based on
the file usage audit results and implements best practices for code organization.
"""

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("cleanup.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class AetherraCleanup:
    """Main cleanup orchestrator for Aetherra project"""

    def __init__(self, project_root: Path, dry_run: bool = True):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.stats = {
            "files_moved": 0,
            "files_deleted": 0,
            "directories_created": 0,
            "errors": 0,
            "warnings": 0,
        }

        # Directories to create/organize
        self.target_structure = {
            "src/core": "Core system components",
            "src/agents": "Agent implementations",
            "src/memory": "Memory system components",
            "src/analytics": "Analytics and reporting",
            "src/neural": "Neural interface components",
            "src/quantum": "Quantum computing integration",
            "src/ui": "User interface components",
            "src/api": "API endpoints and handlers",
            "src/utils": "Utility functions and helpers",
            "tests/unit": "Unit tests",
            "tests/integration": "Integration tests",
            "tests/e2e": "End-to-end tests",
            "tests/fixtures": "Test fixtures and data",
            "docs": "Documentation",
            "scripts": "Utility scripts",
            "config": "Configuration files",
            "unused": "Unused files (for potential cleanup)",
            "backup": "Backup of original files",
            "logs": "Log files",
        }

        # Patterns for file categorization
        self.file_patterns = {
            "core": [
                "*core*",
                "*main*",
                "*launcher*",
                "*engine*",
                "*orchestrator*",
                "*coordinator*",
            ],
            "agents": ["*agent*", "*task*", "*worker*", "*executor*"],
            "memory": [
                "*memory*",
                "*episodic*",
                "*semantic*",
                "*recall*",
                "*introspection*",
                "*timeline*",
            ],
            "analytics": [
                "*analytics*",
                "*dashboard*",
                "*report*",
                "*metric*",
                "*benchmark*",
                "*performance*",
            ],
            "neural": ["*neural*", "*brain*", "*interface*", "*signal*"],
            "quantum": ["*quantum*", "*qubit*", "*circuit*"],
            "ui": [
                "*ui*",
                "*gui*",
                "*widget*",
                "*dialog*",
                "*window*",
                "*panel*",
                "*view*",
                "*component*",
            ],
            "api": [
                "*api*",
                "*server*",
                "*endpoint*",
                "*handler*",
                "*router*",
                "*controller*",
            ],
            "utils": ["*util*", "*helper*", "*tool*", "*common*"],
            "tests": ["test_*", "*_test*", "*conftest*"],
            "config": [
                "*.ini",
                "*.yaml",
                "*.yml",
                "*.toml",
                "*.json",
                "*config*",
                "*setting*",
            ],
        }

        # Files to exclude from cleanup
        self.exclude_patterns = {
            "*.git*",
            "*.vscode*",
            "*.pytest_cache*",
            "__pycache__*",
            "*.pyc",
            "*.pyo",
            "*.egg-info*",
            "node_modules*",
            "venv*",
            ".venv*",
            "env*",
            ".env*",
            "*.log",
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.backup*",
        }

    def create_directory_structure(self) -> None:
        """Create the target directory structure"""
        logger.info("Creating target directory structure...")

        for dir_path, description in self.target_structure.items():
            full_path = self.project_root / dir_path

            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_path} - {description}")
            else:
                logger.info(f"[DRY RUN] Would create: {dir_path} - {description}")

            self.stats["directories_created"] += 1

    def backup_current_state(self) -> None:
        """Create backup of current project state"""
        logger.info("Creating backup of current project state...")

        backup_dir = (
            self.project_root
            / "backup"
            / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        if not self.dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Copy important files to backup
            important_files = [
                "*.py",
                "*.md",
                "*.txt",
                "*.yml",
                "*.yaml",
                "*.json",
                "*.toml",
                "*.ini",
            ]

            for pattern in important_files:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file() and not self._should_exclude(file_path):
                        backup_target = backup_dir / file_path.name
                        try:
                            shutil.copy2(file_path, backup_target)
                            logger.debug(f"Backed up: {file_path.name}")
                        except Exception as e:
                            logger.error(f"Failed to backup {file_path}: {e}")
                            self.stats["errors"] += 1
        else:
            logger.info(f"[DRY RUN] Would create backup at: {backup_dir}")

    def categorize_files(self) -> Dict[str, List[Path]]:
        """Categorize files based on patterns and content"""
        logger.info("Categorizing files...")

        categorized = {category: [] for category in self.file_patterns.keys()}
        categorized["unknown"] = []

        # Find all Python files
        python_files = list(self.project_root.glob("**/*.py"))

        for file_path in python_files:
            if self._should_exclude(file_path):
                continue

            category = self._determine_category(file_path)
            categorized[category].append(file_path)

            logger.debug(f"Categorized {file_path.name} as {category}")

        # Log categorization summary
        for category, files in categorized.items():
            if files:
                logger.info(f"Category '{category}': {len(files)} files")

        return categorized

    def _determine_category(self, file_path: Path) -> str:
        """Determine the category for a file based on patterns and content"""
        file_name = file_path.name.lower()
        file_content = ""

        try:
            # Read file content for more intelligent categorization
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                file_content = f.read()[:2000].lower()  # First 2KB for analysis
        except Exception:
            pass

        # Check patterns
        for category, patterns in self.file_patterns.items():
            for pattern in patterns:
                if self._matches_pattern(file_name, pattern.lower()):
                    return category

        # Content-based categorization
        if any(
            keyword in file_content
            for keyword in ["class.*agent", "def.*agent", "agent.*class"]
        ):
            return "agents"
        elif any(
            keyword in file_content for keyword in ["memory", "episodic", "semantic"]
        ):
            return "memory"
        elif any(
            keyword in file_content for keyword in ["analytics", "dashboard", "metrics"]
        ):
            return "analytics"
        elif any(
            keyword in file_content for keyword in ["neural", "brain", "interface"]
        ):
            return "neural"
        elif any(
            keyword in file_content for keyword in ["quantum", "qubit", "circuit"]
        ):
            return "quantum"
        elif any(
            keyword in file_content for keyword in ["qtwidgets", "qapplication", "gui"]
        ):
            return "ui"
        elif any(
            keyword in file_content
            for keyword in ["flask", "fastapi", "endpoint", "router"]
        ):
            return "api"
        elif any(keyword in file_content for keyword in ["test", "pytest", "unittest"]):
            return "tests"

        return "unknown"

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a pattern (simple wildcard matching)"""
        if "*" not in pattern:
            return pattern in text

        # Simple wildcard matching
        if pattern.startswith("*") and pattern.endswith("*"):
            return pattern[1:-1] in text
        elif pattern.startswith("*"):
            return text.endswith(pattern[1:])
        elif pattern.endswith("*"):
            return text.startswith(pattern[:-1])

        return pattern in text

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from processing"""
        path_str = str(file_path).lower()

        for pattern in self.exclude_patterns:
            if self._matches_pattern(path_str, pattern):
                return True

        return False

    def organize_files(self, categorized_files: Dict[str, List[Path]]) -> None:
        """Organize files into the new structure"""
        logger.info("Organizing files into new structure...")

        for category, files in categorized_files.items():
            if not files:
                continue

            if category == "unknown":
                target_dir = self.project_root / "src" / "misc"
            elif category == "tests":
                target_dir = self.project_root / "tests" / "unit"
            else:
                target_dir = self.project_root / "src" / category

            for file_path in files:
                self._move_file(file_path, target_dir)

    def _move_file(self, source: Path, target_dir: Path) -> None:
        """Move a file to target directory"""
        target_path = target_dir / source.name

        # Handle naming conflicts
        counter = 1
        while target_path.exists():
            name_parts = source.stem, counter, source.suffix
            target_path = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1

        if not self.dry_run:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(target_path))
                logger.info(f"Moved: {source} -> {target_path}")
                self.stats["files_moved"] += 1
            except Exception as e:
                logger.error(f"Failed to move {source} to {target_path}: {e}")
                self.stats["errors"] += 1
        else:
            logger.info(f"[DRY RUN] Would move: {source} -> {target_path}")

    def clean_empty_directories(self) -> None:
        """Remove empty directories"""
        logger.info("Cleaning empty directories...")

        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name

                if self._should_exclude(dir_path):
                    continue

                try:
                    if not any(dir_path.iterdir()):  # Directory is empty
                        if not self.dry_run:
                            dir_path.rmdir()
                            logger.info(f"Removed empty directory: {dir_path}")
                        else:
                            logger.info(
                                f"[DRY RUN] Would remove empty directory: {dir_path}"
                            )
                except OSError:
                    pass  # Directory not empty or other issue

    def identify_duplicates(self) -> List[Tuple[Path, Path]]:
        """Identify potential duplicate files"""
        logger.info("Identifying potential duplicate files...")

        duplicates = []
        file_hashes = {}

        for file_path in self.project_root.glob("**/*.py"):
            if self._should_exclude(file_path):
                continue

            try:
                import hashlib

                with open(file_path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()

                if file_hash in file_hashes:
                    duplicates.append((file_hashes[file_hash], file_path))
                    logger.warning(
                        f"Potential duplicate: {file_path} <-> {file_hashes[file_hash]}"
                    )
                    self.stats["warnings"] += 1
                else:
                    file_hashes[file_hash] = file_path

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                self.stats["errors"] += 1

        return duplicates

    def generate_report(
        self,
        categorized_files: Dict[str, List[Path]],
        duplicates: List[Tuple[Path, Path]],
    ) -> None:
        """Generate cleanup report"""
        logger.info("Generating cleanup report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "dry_run": self.dry_run,
            "statistics": self.stats,
            "categorization": {
                category: [str(f) for f in files]
                for category, files in categorized_files.items()
            },
            "duplicates": [[str(f1), str(f2)] for f1, f2 in duplicates],
            "recommendations": self._generate_recommendations(
                categorized_files, duplicates
            ),
        }

        report_path = self.project_root / "cleanup_report.json"

        if not self.dry_run:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

        logger.info(
            f"Cleanup report {'saved to' if not self.dry_run else 'would be saved to'}: {report_path}"
        )

        # Print summary
        self._print_summary(categorized_files, duplicates)

    def _generate_recommendations(
        self,
        categorized_files: Dict[str, List[Path]],
        duplicates: List[Tuple[Path, Path]],
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if categorized_files.get("unknown"):
            recommendations.append(
                f"Review {len(categorized_files['unknown'])} uncategorized files for proper organization"
            )

        if duplicates:
            recommendations.append(
                f"Review {len(duplicates)} potential duplicate files for consolidation"
            )

        if self.stats["errors"] > 0:
            recommendations.append(
                f"Address {self.stats['errors']} errors encountered during cleanup"
            )

        # Check for large files
        large_files = []
        for category, files in categorized_files.items():
            for file_path in files:
                try:
                    if file_path.stat().st_size > 1024 * 1024:  # > 1MB
                        large_files.append(file_path)
                except:
                    pass

        if large_files:
            recommendations.append(
                f"Review {len(large_files)} large files (>1MB) for optimization"
            )

        return recommendations

    def _print_summary(
        self,
        categorized_files: Dict[str, List[Path]],
        duplicates: List[Tuple[Path, Path]],
    ) -> None:
        """Print cleanup summary"""
        print("\n" + "=" * 60)
        print("AETHERRA PROJECT CLEANUP SUMMARY")
        print("=" * 60)

        print(f"\nProject Root: {self.project_root}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'ACTUAL CLEANUP'}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"\nStatistics:")
        print(f"  Files moved: {self.stats['files_moved']}")
        print(f"  Files deleted: {self.stats['files_deleted']}")
        print(f"  Directories created: {self.stats['directories_created']}")
        print(f"  Errors: {self.stats['errors']}")
        print(f"  Warnings: {self.stats['warnings']}")

        print(f"\nFile Categorization:")
        for category, files in categorized_files.items():
            if files:
                print(f"  {category}: {len(files)} files")

        if duplicates:
            print(f"\nPotential Duplicates: {len(duplicates)} pairs")

        print("\n" + "=" * 60)

    def run_cleanup(self) -> None:
        """Run the complete cleanup process"""
        logger.info(
            f"Starting Aetherra project cleanup {'(DRY RUN)' if self.dry_run else '(ACTUAL CLEANUP)'}"
        )

        try:
            # Step 1: Create backup
            self.backup_current_state()

            # Step 2: Create directory structure
            self.create_directory_structure()

            # Step 3: Categorize files
            categorized_files = self.categorize_files()

            # Step 4: Identify duplicates
            duplicates = self.identify_duplicates()

            # Step 5: Organize files
            self.organize_files(categorized_files)

            # Step 6: Clean empty directories
            self.clean_empty_directories()

            # Step 7: Generate report
            self.generate_report(categorized_files, duplicates)

            logger.info("Cleanup process completed successfully")

        except Exception as e:
            logger.error(f"Cleanup process failed: {e}")
            self.stats["errors"] += 1
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Aetherra Project Cleanup Script")
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Path to Aetherra project root (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Perform dry run without making changes (default: True)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the cleanup (overrides --dry-run)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Override dry_run if --execute is specified
    dry_run = not args.execute

    project_root = Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"Error: Project root does not exist: {project_root}")
        sys.exit(1)

    print(f"Aetherra Project Cleanup")
    print(f"Project Root: {project_root}")
    print(f"Mode: {'DRY RUN' if dry_run else 'ACTUAL CLEANUP'}")

    if not dry_run:
        response = input(
            "\nThis will make actual changes to your project. Continue? (y/N): "
        )
        if response.lower() != "y":
            print("Cleanup cancelled.")
            sys.exit(0)

    try:
        cleanup = AetherraCleanup(project_root, dry_run=dry_run)
        cleanup.run_cleanup()

        print(f"\nCleanup completed {'(dry run)' if dry_run else 'successfully'}!")
        if dry_run:
            print("Run with --execute to perform actual cleanup.")

    except Exception as e:
        print(f"Error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

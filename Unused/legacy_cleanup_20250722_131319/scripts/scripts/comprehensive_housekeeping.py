#!/usr/bin/env python3
"""
Comprehensive Project Housekeeping Script

This script performs thorough cleanup and organization of the Aetherra & Lyrixa project:
- Organizes and consolidates files
- Removes temporary and duplicate files
- Creates proper directory structure
- Generates cleanup report
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import re


class ProjectHousekeeper:
    """Comprehensive project cleanup and organization system"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "actions": [],
            "moved_files": [],
            "deleted_files": [],
            "created_directories": [],
            "consolidated_files": [],
            "warnings": []
        }

        # Define file categories for organization
        self.file_categories = {
            "status_reports": [
                "*COMPLETE*.md", "*SUCCESS*.md", "*ACCOMPLISHED*.md",
                "*REPORT*.md", "*STATUS*.md", "*SUMMARY*.md"
            ],
            "temporary_files": [
                "debug_*.py", "test_*.py", "quick_*.py", "simple_*.py",
                "temp_*.py", "tmp_*.py", "check_*.py", "verify_*.py",
                "fix_*.py", "clean_*.py", "monitor_*.py"
            ],
            "launcher_files": [
                "*launcher*.py", "*launch*.py", "run_*.py", "unified_*.py"
            ],
            "database_files": [
                "*.db", "*.sqlite", "*.sqlite3"
            ],
            "log_files": [
                "*.log"
            ],
            "json_data": [
                "*.json"
            ],
            "backup_files": [
                "*backup*", "*bak*", "*.backup"
            ]
        }

        # Directories to organize into
        self.target_directories = {
            "archive/status_reports": "Project status and completion reports",
            "archive/temporary_scripts": "Temporary and debug scripts",
            "launchers": "Application launchers and entry points",
            "data/databases": "Database files",
            "data/logs": "Log files",
            "data/json": "JSON configuration and data files",
            "archive/backups": "Backup files and directories"
        }

    def run_housekeeping(self, dry_run: bool = False) -> Dict:
        """Run comprehensive housekeeping"""
        print("🧹 Starting Comprehensive Project Housekeeping")
        print("=" * 60)

        if dry_run:
            print("🔍 DRY RUN MODE - No files will be moved or deleted")
            print()

        # Create target directories
        self._create_target_directories(dry_run)

        # Organize files by category
        self._organize_files_by_category(dry_run)

        # Consolidate duplicate files
        self._consolidate_duplicates(dry_run)

        # Clean up empty directories
        self._cleanup_empty_directories(dry_run)

        # Update .gitignore
        self._update_gitignore(dry_run)

        # Generate final report
        self._generate_cleanup_report()

        return self.cleanup_report

    def _create_target_directories(self, dry_run: bool):
        """Create organized directory structure"""
        print("📁 Creating organized directory structure...")

        for target_dir, description in self.target_directories.items():
            dir_path = self.project_root / target_dir

            if not dir_path.exists():
                if not dry_run:
                    dir_path.mkdir(parents=True, exist_ok=True)

                self.cleanup_report["created_directories"].append({
                    "path": str(dir_path),
                    "description": description
                })
                print(f"  📁 Created: {target_dir}")

    def _organize_files_by_category(self, dry_run: bool):
        """Organize files into appropriate directories"""
        print("\n📂 Organizing files by category...")

        # Get all files in project root
        root_files = [f for f in self.project_root.iterdir() if f.is_file()]

        for category, patterns in self.file_categories.items():
            print(f"\n  📋 Processing {category}...")

            matching_files = []
            for pattern in patterns:
                matching_files.extend(self.project_root.glob(pattern))

            # Remove duplicates and ensure they're files
            matching_files = list(set([f for f in matching_files if f.is_file()]))

            if matching_files:
                target_dir = self._get_target_directory(category)

                for file_path in matching_files:
                    self._move_file(file_path, target_dir, dry_run)
            else:
                print(f"    No files found for {category}")

    def _get_target_directory(self, category: str) -> Path:
        """Get target directory for file category"""
        category_mapping = {
            "status_reports": "archive/status_reports",
            "temporary_files": "archive/temporary_scripts",
            "launcher_files": "launchers",
            "database_files": "data/databases",
            "log_files": "data/logs",
            "json_data": "data/json",
            "backup_files": "archive/backups"
        }

        target = category_mapping.get(category, "archive/misc")
        return self.project_root / target

    def _move_file(self, source: Path, target_dir: Path, dry_run: bool):
        """Move a file to target directory"""
        if not target_dir.exists() and not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / source.name

        # Handle conflicts
        if target_path.exists():
            counter = 1
            while target_path.exists():
                name_parts = source.stem, counter, source.suffix
                target_path = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1

        if not dry_run:
            try:
                shutil.move(str(source), str(target_path))
                print(f"    📄 Moved: {source.name} → {target_dir.name}/")

                self.cleanup_report["moved_files"].append({
                    "source": str(source),
                    "target": str(target_path)
                })
            except Exception as e:
                self.cleanup_report["warnings"].append(f"Failed to move {source}: {e}")
                print(f"    [WARN] Failed to move {source.name}: {e}")
        else:
            print(f"    📄 Would move: {source.name} → {target_dir.name}/")

    def _consolidate_duplicates(self, dry_run: bool):
        """Find and consolidate duplicate files"""
        print("\n🔄 Consolidating duplicate files...")

        # Look for obvious duplicates by name patterns
        duplicate_patterns = [
            r".*_backup\d*\.(py|md|json|txt)$",
            r".*_old\.(py|md|json|txt)$",
            r".*_copy\.(py|md|json|txt)$",
            r".*_\d+\.(py|md|json|txt)$"
        ]

        for pattern in duplicate_patterns:
            matches = []
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file() and re.match(pattern, file_path.name):
                    matches.append(file_path)

            if matches:
                print(f"  🔍 Found {len(matches)} potential duplicates matching pattern: {pattern}")

                # Group by base name
                groups = {}
                for match in matches:
                    base_name = re.sub(r'(_backup\d*|_old|_copy|_\d+)', '', match.stem)
                    if base_name not in groups:
                        groups[base_name] = []
                    groups[base_name].append(match)

                # Move duplicates to archive
                for base_name, files in groups.items():
                    if len(files) > 1:
                        archive_dir = self.project_root / "archive" / "duplicates" / base_name

                        for dup_file in files:
                            if not dry_run and not archive_dir.exists():
                                archive_dir.mkdir(parents=True, exist_ok=True)

                            self._move_file(dup_file, archive_dir, dry_run)

    def _cleanup_empty_directories(self, dry_run: bool):
        """Remove empty directories"""
        print("\n🗑️ Cleaning up empty directories...")

        def is_empty_dir(path: Path) -> bool:
            if not path.is_dir():
                return False

            try:
                # Check if directory has any content
                return len(list(path.iterdir())) == 0
            except PermissionError:
                return False

        # Find empty directories (excluding important ones)
        important_dirs = {".git", ".vscode", ".github", "__pycache__"}

        for dir_path in self.project_root.rglob("*"):
            if (dir_path.is_dir() and
                is_empty_dir(dir_path) and
                dir_path.name not in important_dirs and
                not any(part.startswith('.') for part in dir_path.parts[len(self.project_root.parts):])):

                if not dry_run:
                    try:
                        dir_path.rmdir()
                        print(f"    🗑️ Removed empty directory: {dir_path.relative_to(self.project_root)}")

                        self.cleanup_report["deleted_files"].append({
                            "path": str(dir_path),
                            "type": "empty_directory"
                        })
                    except Exception as e:
                        self.cleanup_report["warnings"].append(f"Failed to remove {dir_path}: {e}")
                else:
                    print(f"    🗑️ Would remove empty directory: {dir_path.relative_to(self.project_root)}")

    def _update_gitignore(self, dry_run: bool):
        """Update .gitignore with organized structure"""
        print("\n📝 Updating .gitignore...")

        gitignore_path = self.project_root / ".gitignore"

        additional_ignores = [
            "\n# Housekeeping - Generated files",
            "data/logs/*.log",
            "data/databases/*.db",
            "data/json/temp_*.json",
            "archive/temporary_scripts/",
            "*.tmp",
            "*.temp",
            "__pycache__/",
            "*.pyc"
        ]

        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                current_content = f.read()

            # Add missing ignores
            new_ignores = []
            for ignore in additional_ignores:
                if ignore.strip() and ignore.strip() not in current_content:
                    new_ignores.append(ignore)

            if new_ignores and not dry_run:
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(new_ignores))

                print(f"    📝 Added {len(new_ignores)} entries to .gitignore")
                self.cleanup_report["actions"].append(f"Updated .gitignore with {len(new_ignores)} new entries")

    def _generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        report_path = self.project_root / "HOUSEKEEPING_REPORT.md"

        # Calculate statistics
        stats = {
            "files_moved": len(self.cleanup_report["moved_files"]),
            "files_deleted": len(self.cleanup_report["deleted_files"]),
            "directories_created": len(self.cleanup_report["created_directories"]),
            "warnings": len(self.cleanup_report["warnings"])
        }

        report_content = f"""# Project Housekeeping Report

**Generated:** {self.cleanup_report['timestamp']}

## 📊 Summary Statistics

- **Files Moved:** {stats['files_moved']}
- **Files Deleted:** {stats['files_deleted']}
- **Directories Created:** {stats['directories_created']}
- **Warnings:** {stats['warnings']}

## 📁 New Directory Structure

"""

        for target_dir, description in self.target_directories.items():
            report_content += f"- `{target_dir}/` - {description}\n"

        if self.cleanup_report["warnings"]:
            report_content += "\n## [WARN] Warnings\n\n"
            for warning in self.cleanup_report["warnings"]:
                report_content += f"- {warning}\n"

        report_content += f"""
## 🎯 Recommendations

1. **Review moved files** in archive directories
2. **Update documentation** to reflect new structure
3. **Test launchers** in the new launchers/ directory
4. **Verify data integrity** after file moves
5. **Consider removing** very old archived files

## 📋 Next Steps

- [ ] Review organized files
- [ ] Test application functionality
- [ ] Update README with new structure
- [ ] Run integration tests
- [ ] Clean up any remaining issues

---
*Generated by Project Housekeeping System*
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n📋 Cleanup report generated: {report_path.name}")

        # Also save JSON report
        json_report_path = self.project_root / "data" / "json" / "housekeeping_report.json"
        json_report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(self.cleanup_report, f, indent=2, ensure_ascii=False)

    def get_cleanup_preview(self) -> Dict:
        """Get preview of what would be cleaned up"""
        print("🔍 Analyzing project for cleanup opportunities...")

        preview = {
            "status_reports": [],
            "temporary_files": [],
            "launcher_files": [],
            "database_files": [],
            "log_files": [],
            "potential_duplicates": [],
            "empty_directories": []
        }

        # Analyze each category
        for category, patterns in self.file_categories.items():
            matching_files = []
            for pattern in patterns:
                matching_files.extend(self.project_root.glob(pattern))

            matching_files = [f for f in matching_files if f.is_file()]
            preview[category] = [str(f.relative_to(self.project_root)) for f in matching_files]

        # Find potential duplicates
        duplicate_patterns = [
            r".*_backup\d*\.(py|md|json|txt)$",
            r".*_old\.(py|md|json|txt)$",
            r".*_copy\.(py|md|json|txt)$"
        ]

        for pattern in duplicate_patterns:
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file() and re.match(pattern, file_path.name):
                    preview["potential_duplicates"].append(str(file_path.relative_to(self.project_root)))

        return preview


def main():
    """Main housekeeping interface"""
    import sys

    housekeeper = ProjectHousekeeper()

    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        print("🔍 PREVIEW MODE - Analyzing cleanup opportunities")
        print("=" * 60)

        preview = housekeeper.get_cleanup_preview()

        for category, files in preview.items():
            if files:
                print(f"\n📋 {category.replace('_', ' ').title()}: {len(files)} files")
                for file in files[:5]:  # Show first 5
                    print(f"  📄 {file}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")

        print(f"\n💡 Run without --preview to perform cleanup")
        print(f"💡 Add --dry-run to see what would be moved without actually moving")

    elif len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("🔍 DRY RUN MODE - Showing what would be done")
        housekeeper.run_housekeeping(dry_run=True)

    else:
        print("[WARN] This will reorganize your entire project structure!")
        response = input("Continue? (yes/no): ").lower().strip()

        if response == 'yes':
            result = housekeeper.run_housekeeping(dry_run=False)
            print("\n✅ Housekeeping complete!")
            print(f"📄 Files moved: {len(result['moved_files'])}")
            print(f"📁 Directories created: {len(result['created_directories'])}")
            print(f"[WARN] Warnings: {len(result['warnings'])}")
            print("\n📋 Check HOUSEKEEPING_REPORT.md for details")
        else:
            print("[ERROR] Housekeeping cancelled")


if __name__ == "__main__":
    main()

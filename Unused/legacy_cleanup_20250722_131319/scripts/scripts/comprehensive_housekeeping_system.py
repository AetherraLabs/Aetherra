#!/usr/bin/env python3
"""
🧹 AETHERRA PROJECT HOUSEKEEPING SYSTEM
=====================================

Comprehensive project cleanup and organization system.
Removes unnecessary test files, organizes project structure, and creates clean workspace.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class AetherraHousekeeping:
    """
    🧹 Comprehensive project housekeeping and cleanup system
    """

    def __init__(self, project_root: str):
        """Initialize housekeeping system."""
        self.project_root = Path(project_root)
        self.cleanup_report = {
            "operation_start": datetime.now().isoformat(),
            "files_removed": [],
            "files_moved": [],
            "directories_cleaned": [],
            "space_saved_mb": 0,
            "operations_performed": []
        }

        # Define cleanup patterns
        self.test_patterns = [
            "test_*.py",
            "*_test.py",
            "quick_test*.py",
            "simple_test*.py",
            "validate_*.py",
            "verify_*.py"
        ]

        self.demo_patterns = [
            "demo_*.py",
            "*_demo.py",
            "simple_*.py",
            "minimal_*.py"
        ]

        self.temp_patterns = [
            "debug_*.py",
            "quick_*.py",
            "fix_*.py",
            "*.tmp",
            "*.temp"
        ]

        self.report_patterns = [
            "*_report.json",
            "*_report.md",
            "*COMPLETE.md",
            "*FIXED.md",
            "*RESOLVED.md",
            "*ACCOMPLISHED.md"
        ]

        # Files to definitely keep
        self.keep_files = {
            "README.md",
            "LICENSE",
            "requirements.txt",
            ".gitignore",
            "manifest.json",
            "index.html",
            "script.js",
            "styles.css",
            "sw.js"
        }

        # Important directories to preserve
        self.important_dirs = {
            "Aetherra",
            ".git",
            ".vscode",
            "assets",
            "docs",
            "documentation"
        }

        print("🧹 Aetherra Housekeeping System initialized")
        print(f"📁 Project root: {self.project_root}")

    def analyze_project_clutter(self) -> Dict:
        """Analyze project to identify clutter and cleanup opportunities."""
        analysis = {
            "total_files": 0,
            "test_files": [],
            "demo_files": [],
            "temp_files": [],
            "report_files": [],
            "large_files": [],
            "duplicate_patterns": [],
            "cleanup_candidates": []
        }

        print("🔍 Analyzing project clutter...")

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                analysis["total_files"] += 1
                file_name = file_path.name
                relative_path = file_path.relative_to(self.project_root)

                # Check against patterns
                if self._matches_patterns(file_name, self.test_patterns):
                    analysis["test_files"].append(str(relative_path))

                if self._matches_patterns(file_name, self.demo_patterns):
                    analysis["demo_files"].append(str(relative_path))

                if self._matches_patterns(file_name, self.temp_patterns):
                    analysis["temp_files"].append(str(relative_path))

                if self._matches_patterns(file_name, self.report_patterns):
                    analysis["report_files"].append(str(relative_path))

                # Check file size
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > 10:  # Files larger than 10MB
                        analysis["large_files"].append({
                            "file": str(relative_path),
                            "size_mb": round(size_mb, 2)
                        })
                except Exception:
                    pass

        # Identify cleanup candidates
        analysis["cleanup_candidates"] = (
            analysis["test_files"] +
            analysis["demo_files"] +
            analysis["temp_files"] +
            analysis["report_files"]
        )

        print("📊 Analysis complete:")
        print(f"  • Total files: {analysis['total_files']}")
        print(f"  • Test files: {len(analysis['test_files'])}")
        print(f"  • Demo files: {len(analysis['demo_files'])}")
        print(f"  • Temp files: {len(analysis['temp_files'])}")
        print(f"  • Report files: {len(analysis['report_files'])}")
        print(f"  • Large files: {len(analysis['large_files'])}")
        print(f"  • Cleanup candidates: {len(analysis['cleanup_candidates'])}")

        return analysis

    def _matches_patterns(self, filename: str, patterns: List[str]) -> bool:
        """Check if filename matches any of the given patterns."""
        from fnmatch import fnmatch
        return any(fnmatch(filename.lower(), pattern.lower()) for pattern in patterns)

    def create_archive_structure(self):
        """Create organized archive structure for files being moved."""
        archive_root = self.project_root / "archive"

        archive_dirs = [
            "archive/test_files",
            "archive/demo_files",
            "archive/temp_files",
            "archive/reports",
            "archive/old_backups",
            "archive/deprecated"
        ]

        for dir_path in archive_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)

        print("📁 Archive structure created")
        return archive_root

    def move_test_files(self, test_files: List[str]) -> int:
        """Move test files to archive."""
        moved_count = 0
        test_archive = self.project_root / "archive" / "test_files"

        for test_file in test_files:
            source = self.project_root / test_file
            if source.exists() and source.name not in self.keep_files:
                try:
                    destination = test_archive / source.name
                    shutil.move(str(source), str(destination))
                    self.cleanup_report["files_moved"].append({
                        "from": str(test_file),
                        "to": str(destination.relative_to(self.project_root)),
                        "type": "test"
                    })
                    moved_count += 1
                except Exception as e:
                    print(f"[WARN] Could not move {test_file}: {e}")

        print(f"[DISC] Moved {moved_count} test files to archive")
        return moved_count

    def move_demo_files(self, demo_files: List[str]) -> int:
        """Move demo files to archive."""
        moved_count = 0
        demo_archive = self.project_root / "archive" / "demo_files"

        for demo_file in demo_files:
            source = self.project_root / demo_file
            if source.exists() and source.name not in self.keep_files:
                try:
                    destination = demo_archive / source.name
                    shutil.move(str(source), str(destination))
                    self.cleanup_report["files_moved"].append({
                        "from": str(demo_file),
                        "to": str(destination.relative_to(self.project_root)),
                        "type": "demo"
                    })
                    moved_count += 1
                except Exception as e:
                    print(f"[WARN] Could not move {demo_file}: {e}")

        print(f"[DISC] Moved {moved_count} demo files to archive")
        return moved_count

    def remove_temp_files(self, temp_files: List[str]) -> int:
        """Remove temporary files."""
        removed_count = 0

        for temp_file in temp_files:
            source = self.project_root / temp_file
            if source.exists() and source.name not in self.keep_files:
                try:
                    file_size = source.stat().st_size
                    source.unlink()
                    self.cleanup_report["files_removed"].append({
                        "file": str(temp_file),
                        "size_bytes": file_size,
                        "type": "temporary"
                    })
                    self.cleanup_report["space_saved_mb"] += file_size / (1024 * 1024)
                    removed_count += 1
                except Exception as e:
                    print(f"[WARN] Could not remove {temp_file}: {e}")

        print(f"🗑️ Removed {removed_count} temporary files")
        return removed_count

    def archive_report_files(self, report_files: List[str]) -> int:
        """Archive report and status files."""
        moved_count = 0
        reports_archive = self.project_root / "archive" / "reports"

        for report_file in report_files:
            source = self.project_root / report_file
            if source.exists() and source.name not in self.keep_files:
                try:
                    destination = reports_archive / source.name
                    shutil.move(str(source), str(destination))
                    self.cleanup_report["files_moved"].append({
                        "from": str(report_file),
                        "to": str(destination.relative_to(self.project_root)),
                        "type": "report"
                    })
                    moved_count += 1
                except Exception as e:
                    print(f"[WARN] Could not move {report_file}: {e}")

        print(f"📊 Archived {moved_count} report files")
        return moved_count

    def clean_empty_directories(self) -> int:
        """Remove empty directories."""
        removed_count = 0

        # Get all directories, sorted by depth (deepest first)
        all_dirs = [p for p in self.project_root.rglob("*") if p.is_dir()]
        all_dirs.sort(key=lambda x: len(x.parts), reverse=True)

        for dir_path in all_dirs:
            if dir_path.name not in self.important_dirs:
                try:
                    if not any(dir_path.iterdir()):  # Directory is empty
                        dir_path.rmdir()
                        self.cleanup_report["directories_cleaned"].append(str(dir_path.relative_to(self.project_root)))
                        removed_count += 1
                except Exception:
                    pass  # Directory not empty or permission issues

        print(f"📁 Removed {removed_count} empty directories")
        return removed_count

    def clean_pycache(self) -> int:
        """Remove Python cache directories."""
        removed_count = 0

        for pycache_dir in self.project_root.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache_dir)
                self.cleanup_report["directories_cleaned"].append(str(pycache_dir.relative_to(self.project_root)))
                removed_count += 1
            except Exception as e:
                print(f"[WARN] Could not remove {pycache_dir}: {e}")

        print(f"🐍 Removed {removed_count} __pycache__ directories")
        return removed_count

    def organize_remaining_files(self):
        """Organize remaining files into proper structure."""
        print("📋 Organizing remaining files...")

        # Create organized structure
        organized_dirs = {
            "scripts": ["*.py"],
            "docs": ["*.md"],
            "config": ["*.json", "*.yaml", "*.yml"],
            "web": ["*.html", "*.css", "*.js"]
        }

        for dir_name, patterns in organized_dirs.items():
            target_dir = self.project_root / dir_name
            target_dir.mkdir(exist_ok=True)

            for pattern in patterns:
                for file_path in self.project_root.glob(pattern):
                    if (file_path.is_file() and
                        file_path.parent == self.project_root and
                        file_path.name not in self.keep_files):

                        try:
                            destination = target_dir / file_path.name
                            if not destination.exists():
                                shutil.move(str(file_path), str(destination))
                                self.cleanup_report["files_moved"].append({
                                    "from": file_path.name,
                                    "to": str(destination.relative_to(self.project_root)),
                                    "type": "organization"
                                })
                        except Exception as e:
                            print(f"[WARN] Could not organize {file_path.name}: {e}")

    def perform_comprehensive_cleanup(self) -> Dict:
        """Perform complete project cleanup."""
        print("🧹 Starting comprehensive cleanup...")
        self.cleanup_report["operations_performed"].append("comprehensive_cleanup_started")

        # 1. Analyze project
        analysis = self.analyze_project_clutter()

        # 2. Create archive structure
        self.create_archive_structure()

        # 3. Move test files
        test_moved = self.move_test_files(analysis["test_files"])

        # 4. Move demo files
        demo_moved = self.move_demo_files(analysis["demo_files"])

        # 5. Remove temp files
        temp_removed = self.remove_temp_files(analysis["temp_files"])

        # 6. Archive reports
        reports_moved = self.archive_report_files(analysis["report_files"])

        # 7. Clean Python cache
        cache_removed = self.clean_pycache()

        # 8. Remove empty directories
        dirs_removed = self.clean_empty_directories()

        # 9. Organize remaining files
        self.organize_remaining_files()

        # Update report
        self.cleanup_report.update({
            "operation_end": datetime.now().isoformat(),
            "test_files_moved": test_moved,
            "demo_files_moved": demo_moved,
            "temp_files_removed": temp_removed,
            "report_files_moved": reports_moved,
            "cache_dirs_removed": cache_removed,
            "empty_dirs_removed": dirs_removed,
            "total_files_processed": test_moved + demo_moved + temp_removed + reports_moved
        })

        self.cleanup_report["operations_performed"].append("comprehensive_cleanup_completed")

        print("✅ Comprehensive cleanup completed!")
        return self.cleanup_report

    def generate_cleanup_report(self) -> str:
        """Generate detailed cleanup report."""
        report_path = self.project_root / f"housekeeping_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Add summary statistics
        self.cleanup_report["summary"] = {
            "total_files_moved": len(self.cleanup_report["files_moved"]),
            "total_files_removed": len(self.cleanup_report["files_removed"]),
            "total_dirs_cleaned": len(self.cleanup_report["directories_cleaned"]),
            "space_saved_mb": round(self.cleanup_report["space_saved_mb"], 2),
            "cleanup_success": True
        }

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.cleanup_report, f, indent=2, ensure_ascii=False)

            print(f"📊 Cleanup report saved: {report_path}")
            return str(report_path)
        except Exception as e:
            print(f"[ERROR] Failed to save cleanup report: {e}")
            return ""

    def create_maintenance_script(self):
        """Create ongoing maintenance script for future use."""
        maintenance_script = self.project_root / "scripts" / "maintenance.py"
        maintenance_script.parent.mkdir(exist_ok=True)

        script_content = '''#!/usr/bin/env python3
"""
[TOOL] Aetherra Project Maintenance Script
====================================

Regular maintenance tasks for keeping the project clean and organized.
Run this script periodically to maintain project health.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def quick_cleanup():
    """Perform quick cleanup of common clutter."""
    project_root = Path(__file__).parent.parent
    removed_count = 0

    # Remove Python cache
    for pycache in project_root.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache)
            removed_count += 1
        except Exception:
            pass

    # Remove temporary files
    temp_patterns = ["*.tmp", "*.temp", "*.log"]
    for pattern in temp_patterns:
        for temp_file in project_root.rglob(pattern):
            try:
                temp_file.unlink()
                removed_count += 1
            except Exception:
                pass

    print(f"🧹 Quick cleanup complete: {removed_count} items removed")

if __name__ == "__main__":
    quick_cleanup()
'''

        try:
            with open(maintenance_script, 'w', encoding='utf-8') as f:
                f.write(script_content)
            print(f"[TOOL] Maintenance script created: {maintenance_script}")
        except Exception as e:
            print(f"[ERROR] Failed to create maintenance script: {e}")


def main():
    """Main housekeeping function."""
    project_root = Path(__file__).parent

    print("🧹 AETHERRA PROJECT HOUSEKEEPING")
    print("=" * 50)

    # Initialize housekeeping system
    housekeeper = AetherraHousekeeping(str(project_root))

    # Perform cleanup
    cleanup_report = housekeeper.perform_comprehensive_cleanup()

    # Generate reports
    report_path = housekeeper.generate_cleanup_report()

    # Create maintenance tools
    housekeeper.create_maintenance_script()

    # Display summary
    print("\n📊 CLEANUP SUMMARY:")
    print("=" * 30)
    print(f"Files moved to archive: {cleanup_report['summary']['total_files_moved']}")
    print(f"Files removed: {cleanup_report['summary']['total_files_removed']}")
    print(f"Directories cleaned: {cleanup_report['summary']['total_dirs_cleaned']}")
    print(f"Space saved: {cleanup_report['summary']['space_saved_mb']} MB")
    print(f"Report saved: {report_path}")
    print("\n✅ Housekeeping complete! Project is now organized and clean.")


if __name__ == "__main__":
    main()

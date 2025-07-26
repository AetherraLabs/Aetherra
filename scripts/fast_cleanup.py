#!/usr/bin/env python3
"""
🚀 Fast Aetherra File Cleanup
=============================

Simplified and fast file cleanup for large projects.
Focuses on identifying truly unused files quickly.
"""

import shutil
from datetime import datetime
from pathlib import Path


class FastFileCleanup:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.stats = {
            "total_files": 0,
            "moved_files": 0,
            "errors": 0,
            "start_time": datetime.now(),
        }

        # Patterns for files that are likely unused
        self.unused_patterns = [
            "*test*.py",
            "*demo*.py",
            "*example*.py",
            "*backup*.py",
            "*old*.py",
            "*legacy*.py",
            "*temp*.py",
            "*tmp*.py",
        ]

        # Directories that are definitely unused
        self.unused_dirs = [
            "Unused",
            "unused",
            "backup",
            "backups",
            "archive",
            "legacy",
            "old",
            "temp",
            "tmp",
            "examples",
            "demos",
            "test_*",
            "*_test",
            "legacy_cleanup_*",
            "Aetherra_backup_*",
        ]

        # Critical files to never move
        self.critical_files = {
            "aetherra_launcher.py",
            "aetherra_launcher_new.py",
            "launcher.py",
            "main.py",
            "app.py",
            "run.py",
            "server.py",
            "__init__.py",
            "setup.py",
            "requirements.txt",
        }

    def quick_cleanup(self, dry_run=True):
        """Perform quick cleanup of obviously unused files"""
        print("🚀 Starting Fast Aetherra File Cleanup...")
        print(f"Project: {self.project_root}")
        print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")

        unused_target = self.project_root / "unused_fast_cleanup"
        if not dry_run:
            unused_target.mkdir(exist_ok=True)

        moved_files = []

        # 1. Move entire unused directories
        print("\n📁 Moving unused directories...")
        for item in self.project_root.iterdir():
            if item.is_dir() and any(
                pattern in item.name.lower() for pattern in self.unused_dirs
            ):
                if self._is_unused_directory(item):
                    self._move_directory(item, unused_target, dry_run, moved_files)

        # 2. Move files matching unused patterns
        print("\n📄 Moving unused files...")
        for pattern in self.unused_patterns:
            for file_path in self.project_root.rglob(pattern):
                if self._should_move_file(file_path):
                    self._move_file(file_path, unused_target, dry_run, moved_files)

        # 3. Move obviously duplicate files
        print("\n🔄 Moving duplicate files...")
        self._move_duplicates(unused_target, dry_run, moved_files)

        self._print_summary(moved_files, dry_run)
        return moved_files

    def _is_unused_directory(self, dir_path: Path) -> bool:
        """Check if directory appears to be unused"""
        dir_name = dir_path.name.lower()

        # Skip if it's a critical directory
        critical_dirs = {".git", ".github", "src", "tests", "scripts", "requirements"}
        if dir_name in critical_dirs:
            return False

        # Check for unused directory patterns
        unused_indicators = [
            "backup",
            "archive",
            "legacy",
            "old",
            "temp",
            "tmp",
            "unused",
            "test_",
            "_test",
            "demo",
            "example",
        ]

        return any(indicator in dir_name for indicator in unused_indicators)

    def _should_move_file(self, file_path: Path) -> bool:
        """Determine if a file should be moved to unused"""
        # Never move critical files
        if file_path.name in self.critical_files:
            return False

        # Skip if already in unused directory
        if "unused" in str(file_path).lower():
            return False

        # Skip if in critical directories
        critical_parts = {".git", ".github", "requirements", "scripts"}
        if any(part in file_path.parts for part in critical_parts):
            return False

        return True

    def _move_directory(
        self, src_dir: Path, target_dir: Path, dry_run: bool, moved_files: list
    ):
        """Move an entire directory"""
        dest = target_dir / src_dir.name

        if dry_run:
            print(f"  [DRY RUN] Would move directory: {src_dir} -> {dest}")
            # Count files that would be moved
            file_count = sum(1 for _ in src_dir.rglob("*") if _.is_file())
            moved_files.append(f"DIR: {src_dir} ({file_count} files)")
        else:
            try:
                shutil.move(str(src_dir), str(dest))
                file_count = sum(1 for _ in dest.rglob("*") if _.is_file())
                print(f"  ✅ Moved directory: {src_dir} ({file_count} files)")
                moved_files.append(f"DIR: {src_dir} ({file_count} files)")
                self.stats["moved_files"] += file_count
            except Exception as e:
                print(f"  ❌ Failed to move {src_dir}: {e}")
                self.stats["errors"] += 1

    def _move_file(
        self, src_file: Path, target_dir: Path, dry_run: bool, moved_files: list
    ):
        """Move a single file"""
        # Create relative path structure in target
        rel_path = src_file.relative_to(self.project_root)
        dest = target_dir / rel_path

        if dry_run:
            moved_files.append(str(rel_path))
        else:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_file), str(dest))
                moved_files.append(str(rel_path))
                self.stats["moved_files"] += 1
            except Exception as e:
                print(f"  ❌ Failed to move {src_file}: {e}")
                self.stats["errors"] += 1

    def _move_duplicates(self, target_dir: Path, dry_run: bool, moved_files: list):
        """Move obviously duplicate files"""
        # Find files with similar names
        file_groups = {}

        for py_file in self.project_root.rglob("*.py"):
            if not self._should_move_file(py_file):
                continue

            # Group by base name (without numbers/suffixes)
            base_name = py_file.stem
            # Remove common suffixes that indicate duplicates
            for suffix in ["_copy", "_backup", "_old", "_new", "_2", "_test", "_demo"]:
                if base_name.endswith(suffix):
                    base_name = base_name[: -len(suffix)]
                    break

            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(py_file)

        # Move duplicates (keep the shortest name)
        for base_name, files in file_groups.items():
            if len(files) > 1:
                # Sort by path length and name
                files.sort(key=lambda x: (len(str(x)), str(x)))
                # Keep the first (shortest/simplest), move the rest
                for duplicate_file in files[1:]:
                    if self._is_likely_duplicate(duplicate_file):
                        self._move_file(
                            duplicate_file, target_dir, dry_run, moved_files
                        )

    def _is_likely_duplicate(self, file_path: Path) -> bool:
        """Check if file is likely a duplicate"""
        name = file_path.stem.lower()
        duplicate_indicators = [
            "_copy",
            "_backup",
            "_old",
            "_new",
            "_2",
            "_3",
            "_test",
            "_demo",
            "_example",
            "_temp",
            "_tmp",
            "copy_of_",
        ]
        return any(indicator in name for indicator in duplicate_indicators)

    def _print_summary(self, moved_files: list, dry_run: bool):
        """Print cleanup summary"""
        duration = datetime.now() - self.stats["start_time"]

        print("\n" + "=" * 60)
        print("🧹 FAST CLEANUP SUMMARY")
        print("=" * 60)
        print(f"Duration: {duration.total_seconds():.1f} seconds")
        print(f"Files processed: {len(moved_files)}")

        if dry_run:
            print("Mode: DRY RUN - No files were actually moved")
            print(f"Would move {len(moved_files)} items:")
            for item in moved_files[:20]:  # Show first 20
                print(f"  - {item}")
            if len(moved_files) > 20:
                print(f"  ... and {len(moved_files) - 20} more")
        else:
            print(f"Successfully moved: {self.stats['moved_files']} files")
            print(f"Errors: {self.stats['errors']}")

        print("=" * 60)

    def create_organized_structure(self, dry_run=True):
        """Create organized directory structure and move files"""
        print("\n🏗️ Creating organized project structure...")

        structure = {
            "src/core": ["*core*", "*system*", "*base*"],
            "src/agents": ["*agent*", "*worker*", "*task*"],
            "src/memory": ["*memory*", "*episodic*", "*semantic*"],
            "src/analytics": ["*analytics*", "*report*", "*dashboard*"],
            "src/neural": ["*neural*", "*brain*", "*interface*"],
            "src/quantum": ["*quantum*", "*qubit*", "*circuit*"],
            "src/ui": ["*ui*", "*gui*", "*widget*", "*dialog*"],
            "src/api": ["*api*", "*endpoint*", "*route*", "*server*"],
            "src/utils": ["*util*", "*helper*", "*tool*", "*common*"],
        }

        # Create directories
        for target_dir in structure.keys():
            target_path = self.project_root / target_dir
            if not dry_run:
                target_path.mkdir(parents=True, exist_ok=True)
            print(
                f"  {'[DRY RUN] Would create' if dry_run else 'Created'}: {target_dir}"
            )

        print("📁 Organized structure ready for manual file organization")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Fast Aetherra File Cleanup")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually move files (default is dry run)",
    )
    parser.add_argument(
        "--organize", action="store_true", help="Create organized directory structure"
    )

    args = parser.parse_args()

    cleanup = FastFileCleanup()

    # Run fast cleanup
    cleanup.quick_cleanup(dry_run=not args.execute)

    # Create organized structure if requested
    if args.organize:
        cleanup.create_organized_structure(dry_run=not args.execute)

    if not args.execute:
        print("\n🎯 To execute the cleanup, run:")
        print("   python scripts/fast_cleanup.py --execute")
        print("   python scripts/fast_cleanup.py --execute --organize")


if __name__ == "__main__":
    main()

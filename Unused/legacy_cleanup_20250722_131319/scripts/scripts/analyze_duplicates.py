#!/usr/bin/env python3
"""
AetherraCode Duplicate File Analyzer

This script scans the entire project to identify:
1. Exact duplicate files (same content)
2. Similar files with different locations
3. Legacy/outdated files that can be archived
4. Redundant status/documentation files
5. Test files in multiple locations

Usage:
    python scripts/analyze_duplicates.py [--delete-confirmed] [--move-to-archive]
"""

import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class DuplicateAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.file_hashes = defaultdict(list)
        self.similar_files = defaultdict(list)
        self.status_files = []
        self.test_duplicates = []
        self.website_duplicates = []
        self.legacy_candidates = []

        # Skip these directories
        self.skip_dirs = {".git", "__pycache__", "node_modules", ".vscode", "logs"}
        # Skip these file types
        self.skip_extensions = {".pyc", ".pyo", ".pyd", ".dll", ".so", ".dylib"}

    def get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file content."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except (OSError, PermissionError):
            return ""

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        if file_path.suffix.lower() in self.skip_extensions:
            return True
        if file_path.name.startswith("."):
            return True
        for skip_dir in self.skip_dirs:
            if skip_dir in file_path.parts:
                return True
        return False

    def categorize_file(self, file_path: Path) -> str:
        """Categorize file type for analysis."""
        name = file_path.name.lower()
        parent = file_path.parent.name.lower()

        if any(
            pattern in name for pattern in ["status", "complete", "success", "summary"]
        ):
            return "status_doc"
        elif name.startswith("test_") or parent == "tests":
            return "test"
        elif parent == "website" or name in ["index.html", "styles.css", "script.js"]:
            return "website"
        elif any(pattern in name for pattern in ["readme", "changelog", "license"]):
            return "documentation"
        elif file_path.suffix == ".py":
            return "python"
        elif file_path.suffix == ".aether":
            return "Aetherra"
        elif file_path.suffix == ".md":
            return "markdown"
        else:
            return "other"

    def analyze_exact_duplicates(self) -> Dict[str, List[Path]]:
        """Find files with identical content."""
        print("🔍 Scanning for exact duplicates...")

        for root, dirs, files in os.walk(self.project_root):
            # Remove skip directories from dirs list
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]

            for file in files:
                file_path = Path(root) / file

                if self.should_skip_file(file_path):
                    continue

                file_hash = self.get_file_hash(file_path)
                if file_hash:
                    self.file_hashes[file_hash].append(file_path)

        # Find duplicates (hashes with multiple files)
        duplicates = {
            h: files for h, files in self.file_hashes.items() if len(files) > 1
        }

        print(f"📊 Found {len(duplicates)} groups of exact duplicates")
        return duplicates

    def analyze_similar_filenames(self) -> Dict[str, List[Path]]:
        """Find files with similar names that might be duplicates."""
        print("🔍 Scanning for similar filenames...")

        name_groups = defaultdict(list)

        for hash_val, files in self.file_hashes.items():
            for file_path in files:
                # Group by base name (without extension)
                base_name = file_path.stem.lower()
                # Remove common suffixes like _v1, _old, _backup, etc.
                clean_name = re.sub(
                    r"(_v\d+|_old|_backup|_new|_copy|_fixed|_final|_test)$",
                    "",
                    base_name,
                )
                name_groups[clean_name].append(file_path)

        # Find groups with multiple files
        similar = {
            name: files
            for name, files in name_groups.items()
            if len(files) > 1 and len(set(f.name for f in files)) > 1
        }

        print(f"📊 Found {len(similar)} groups of similar filenames")
        return similar

    def analyze_test_duplicates(self) -> List[Tuple[Path, Path]]:
        """Find test files that exist in both tests/ and tests/unit/."""
        print("🔍 Scanning for test duplicates...")

        tests_dir = self.project_root / "tests"
        unit_dir = tests_dir / "unit"

        if not tests_dir.exists() or not unit_dir.exists():
            return []

        duplicates = []
        for test_file in tests_dir.glob("test_*.py"):
            unit_equivalent = unit_dir / test_file.name
            if unit_equivalent.exists():
                duplicates.append((test_file, unit_equivalent))

        print(f"📊 Found {len(duplicates)} test file duplicates")
        return duplicates

    def analyze_website_duplicates(self) -> List[Tuple[Path, Path]]:
        """Find website files that exist in both root and website/ directory."""
        print("🔍 Scanning for website duplicates...")

        website_dir = self.project_root / "website"
        if not website_dir.exists():
            return []

        duplicates = []
        web_files = ["index.html", "styles.css", "script.js", "CNAME", "favicon.svg"]

        for filename in web_files:
            root_file = self.project_root / filename
            website_file = website_dir / filename

            if root_file.exists() and website_file.exists():
                duplicates.append((root_file, website_file))

        print(f"📊 Found {len(duplicates)} website file duplicates")
        return duplicates

    def analyze_status_documents(self) -> List[Path]:
        """Find status/completion documents that might be outdated."""
        print("🔍 Scanning for status documents...")

        status_patterns = [
            "WORKSPACE_REORGANIZATION_*.md",
            "WORKSPACE_OPTIMIZATION_*.md",
            "WORKSPACE_ERRORS_*.md",
            "WEBSITE_*_COMPLETE.md",
            "WEBSITE_*_SUCCESS.md",
            "*_COMPLETE.md",
            "*_SUCCESS.md",
            "REVOLUTIONARY_*.md",
            "REPOSITORY_*.md",
            "aetherhub_*.md",
            "PERSONA_*.md",
        ]

        status_files = []
        for pattern in status_patterns:
            status_files.extend(self.project_root.glob(pattern))

        print(f"📊 Found {len(status_files)} status documents")
        return status_files

    def identify_legacy_candidates(self) -> List[Path]:
        """Identify files that appear to be legacy/outdated."""
        print("🔍 Scanning for legacy files...")

        legacy_patterns = [
            "*_old.*",
            "*_backup.*",
            "*_copy.*",
            "*_temp.*",
            "*_v1.*",
            "*_v2.*",
            "*_original.*",
            "*_legacy.*",
            "old_*",
            "backup_*",
            "temp_*",
            "legacy_*",
        ]

        legacy_files = []
        for pattern in legacy_patterns:
            legacy_files.extend(self.project_root.rglob(pattern))

        # Filter out files in archive directory
        legacy_files = [f for f in legacy_files if "archive" not in f.parts]

        print(f"📊 Found {len(legacy_files)} potential legacy files")
        return legacy_files

    def generate_recommendations(
        self,
        exact_dupes: Dict,
        similar_files: Dict,
        test_dupes: List,
        website_dupes: List,
        status_docs: List,
        legacy_files: List,
    ) -> Dict:
        """Generate recommendations for each type of duplicate."""
        recommendations = {
            "delete_immediately": [],
            "move_to_archive": [],
            "keep_newer": [],
            "manual_review": [],
        }

        # Exact duplicates - usually safe to delete
        for hash_val, files in exact_dupes.items():
            if len(files) > 1:
                # Keep the one in the most "canonical" location
                files_sorted = sorted(files, key=self._get_file_priority)
                keep_file = files_sorted[0]
                delete_files = files_sorted[1:]

                for delete_file in delete_files:
                    recommendations["delete_immediately"].append(
                        {
                            "file": delete_file,
                            "reason": f"Exact duplicate of {keep_file.relative_to(self.project_root)}",
                            "keep_instead": keep_file,
                        }
                    )

        # Test duplicates - keep unit/ versions
        for root_test, unit_test in test_dupes:
            recommendations["delete_immediately"].append(
                {
                    "file": root_test,
                    "reason": "Duplicate test, keeping organized version in unit/",
                    "keep_instead": unit_test,
                }
            )

        # Website duplicates - keep root versions (for GitHub Pages)
        for root_file, website_file in website_dupes:
            recommendations["move_to_archive"].append(
                {
                    "file": website_file,
                    "reason": "Website files moved to root for GitHub Pages deployment",
                    "keep_instead": root_file,
                }
            )

        # Status documents - most can be archived
        for status_file in status_docs:
            if any(
                word in status_file.name.lower()
                for word in ["complete", "success", "summary"]
            ):
                recommendations["move_to_archive"].append(
                    {
                        "file": status_file,
                        "reason": "Historical status document, completed milestone",
                        "keep_instead": None,
                    }
                )

        # Legacy files - archive or delete
        for legacy_file in legacy_files:
            recommendations["move_to_archive"].append(
                {
                    "file": legacy_file,
                    "reason": "Legacy file based on naming pattern",
                    "keep_instead": None,
                }
            )

        return recommendations

    def _get_file_priority(self, file_path: Path) -> int:
        """Get priority score for file location (lower = higher priority)."""
        path_str = str(file_path.relative_to(self.project_root)).lower()

        # Priority order (lower number = higher priority)
        if path_str.startswith("src/"):
            return 1
        elif path_str.startswith("core/"):
            return 2
        elif path_str.startswith("scripts/"):
            return 3
        elif path_str.startswith("launchers/"):
            return 4
        elif "unit" in path_str:
            return 5
        elif path_str.startswith("tests/"):
            return 6
        elif path_str.startswith("docs/"):
            return 7
        elif path_str.startswith("examples/"):
            return 8
        elif "archive" in path_str:
            return 99
        else:
            return 10

    def print_analysis_report(self, recommendations: Dict):
        """Print a comprehensive analysis report."""
        print("\n" + "=" * 80)
        print("📋 DUPLICATE FILE ANALYSIS REPORT")
        print("=" * 80)

        total_files_to_process = sum(
            len(category) for category in recommendations.values()
        )
        print(f"\n📊 SUMMARY: {total_files_to_process} files identified for action\n")

        # Safe to delete immediately
        if recommendations["delete_immediately"]:
            print("🗑️  SAFE TO DELETE IMMEDIATELY:")
            print("   These are exact duplicates or redundant test files")
            for item in recommendations["delete_immediately"]:
                rel_path = item["file"].relative_to(self.project_root)
                print(f"   [ERROR] {rel_path}")
                print(f"      Reason: {item['reason']}")
                if item.get("keep_instead"):
                    keep_path = item["keep_instead"].relative_to(self.project_root)
                    print(f"      Keep: {keep_path}")
                print()

        # Move to archive
        if recommendations["move_to_archive"]:
            print("[DISC] MOVE TO ARCHIVE:")
            print("   These files have historical value but aren't needed actively")
            for item in recommendations["move_to_archive"]:
                rel_path = item["file"].relative_to(self.project_root)
                print(f"   [DISC] {rel_path}")
                print(f"      Reason: {item['reason']}")
                print()

        # Manual review needed
        if recommendations["manual_review"]:
            print("👁️  MANUAL REVIEW NEEDED:")
            print("   These files need human judgment")
            for item in recommendations["manual_review"]:
                rel_path = item["file"].relative_to(self.project_root)
                print(f"   ❓ {rel_path}")
                print(f"      Reason: {item['reason']}")
                print()

        print("\n💡 NEXT STEPS:")
        print("   1. Review the recommendations above")
        print("   2. Run with --move-to-archive to move historical files")
        print("   3. Run with --delete-confirmed to remove exact duplicates")
        print("   4. Check archive/duplicates/ folder before final cleanup")

    def execute_recommendations(
        self,
        recommendations: Dict,
        move_to_archive: bool = False,
        delete_confirmed: bool = False,
    ):
        """Execute the cleanup recommendations."""
        archive_dir = self.project_root / "archive" / "duplicates"

        if move_to_archive:
            print("\n[DISC] Moving files to archive...")
            archive_dir.mkdir(parents=True, exist_ok=True)

            for item in recommendations["move_to_archive"]:
                file_path = item["file"]
                if file_path.exists():
                    # Create subdirectory structure in archive
                    rel_path = file_path.relative_to(self.project_root)
                    archive_path = archive_dir / rel_path
                    archive_path.parent.mkdir(parents=True, exist_ok=True)

                    file_path.rename(archive_path)
                    print(f"   [DISC] Moved {rel_path} to archive/duplicates/")

        if delete_confirmed:
            print("\n🗑️  Deleting confirmed duplicates...")

            for item in recommendations["delete_immediately"]:
                file_path = item["file"]
                if file_path.exists():
                    rel_path = file_path.relative_to(self.project_root)
                    file_path.unlink()
                    print(f"   [ERROR] Deleted {rel_path}")

    def run_analysis(self) -> Dict:
        """Run the complete duplicate analysis."""
        print("🧬 AetherraCode Duplicate File Analysis")
        print("=" * 50)

        # Run all analyses
        exact_dupes = self.analyze_exact_duplicates()
        similar_files = self.analyze_similar_filenames()
        test_dupes = self.analyze_test_duplicates()
        website_dupes = self.analyze_website_duplicates()
        status_docs = self.analyze_status_documents()
        legacy_files = self.identify_legacy_candidates()

        # Generate recommendations
        recommendations = self.generate_recommendations(
            exact_dupes,
            similar_files,
            test_dupes,
            website_dupes,
            status_docs,
            legacy_files,
        )

        return recommendations


def main():
    import sys

    move_to_archive = "--move-to-archive" in sys.argv
    delete_confirmed = "--delete-confirmed" in sys.argv

    analyzer = DuplicateAnalyzer()
    recommendations = analyzer.run_analysis()

    analyzer.print_analysis_report(recommendations)

    if move_to_archive or delete_confirmed:
        print("\n[WARN]  EXECUTING CLEANUP...")
        analyzer.execute_recommendations(
            recommendations, move_to_archive, delete_confirmed
        )
        print("\n✅ Cleanup complete!")
    else:
        print(
            "\n💡 Run with --move-to-archive and/or --delete-confirmed to execute cleanup"
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
aetherra Targeted Duplicate Cleanup

Quick analysis and cleanup of the most obvious duplicates:
1. Test files in both tests/ and tests/unit/
2. Website files in both root and website/
3. Status documentation files
4. Legacy/backup files

Usage:
    python scripts/quick_duplicate_cleanup.py [--execute]
"""

import shutil
from pathlib import Path
from typing import List, Tuple


class QuickDuplicateCleanup:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.archive_dir = self.project_root / "archive" / "duplicates_cleanup"

    def find_test_duplicates(self) -> List[Tuple[Path, Path, str]]:
        """Find test files that exist in both tests/ and tests/unit/"""
        duplicates = []
        tests_dir = self.project_root / "tests"
        unit_dir = tests_dir / "unit"

        if not unit_dir.exists():
            return duplicates

        for test_file in tests_dir.glob("test_*.py"):
            unit_equivalent = unit_dir / test_file.name
            if unit_equivalent.exists():
                # Check if they're actually different or just duplicates
                try:
                    with open(test_file, encoding="utf-8") as f1:
                        content1 = f1.read()
                    with open(unit_equivalent, encoding="utf-8") as f2:
                        content2 = f2.read()

                    if content1.strip() == content2.strip():
                        duplicates.append(
                            (test_file, unit_equivalent, "Exact duplicate")
                        )
                    else:
                        duplicates.append(
                            (test_file, unit_equivalent, "Similar but different")
                        )
                except:
                    duplicates.append((test_file, unit_equivalent, "Could not compare"))

        return duplicates

    def find_website_duplicates(self) -> List[Tuple[Path, Path, str]]:
        """Find website files that exist in both root and website/"""
        duplicates = []
        website_dir = self.project_root / "website"

        if not website_dir.exists():
            return duplicates

        website_files = [
            "index.html",
            "styles.css",
            "script.js",
            "CNAME",
            "favicon.svg",
        ]

        for filename in website_files:
            root_file = self.project_root / filename
            website_file = website_dir / filename

            if root_file.exists() and website_file.exists():
                try:
                    with open(root_file, encoding="utf-8") as f1:
                        content1 = f1.read()
                    with open(website_file, encoding="utf-8") as f2:
                        content2 = f2.read()

                    if content1.strip() == content2.strip():
                        duplicates.append(
                            (website_file, root_file, "Exact duplicate - keep root")
                        )
                    else:
                        duplicates.append(
                            (
                                website_file,
                                root_file,
                                "Different content - needs review",
                            )
                        )
                except:
                    duplicates.append((website_file, root_file, "Could not compare"))

        return duplicates

    def find_status_documents(self) -> List[Path]:
        """Find status/completion documents that can be archived"""
        status_files = []

        patterns = [
            "WORKSPACE_REORGANIZATION_*.md",
            "WORKSPACE_OPTIMIZATION_*.md",
            "WORKSPACE_ERRORS_*.md",
            "WEBSITE_DEPLOYMENT_*.md",
            "WEBSITE_LIVE_*.md",
            "*_COMPLETE.md",
            "*_SUCCESS.md",
            "REVOLUTIONARY_*.md",
            "REPOSITORY_*.md",
            "aetherhub_*_COMPLETE.md",
            "aetherhub_*_SUCCESS.md",
            "PERSONA_*_COMPLETE.md",
            "REDIRECT_*_SOLVED.md",
            "SRC_FOLDER_*_COMPLETE.md",
        ]

        for pattern in patterns:
            status_files.extend(self.project_root.glob(pattern))

        return status_files

    def find_legacy_files(self) -> List[Path]:
        """Find obviously legacy files"""
        legacy_files = []

        patterns = [
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
            "*_clean.*",  # Like update_overview_clean.py
        ]

        for pattern in patterns:
            legacy_files.extend(self.project_root.rglob(pattern))

        # Filter out files already in archive
        legacy_files = [f for f in legacy_files if "archive" not in f.parts]

        return legacy_files

    def find_verification_scripts(self) -> List[Path]:
        """Find temporary verification/test scripts"""
        verification_files = []

        patterns = [
            "verify-*.ps1",
            "verify-*.bat",
            "test-*.ps1",
            "diagnose-*.bat",
            "force-*.bat",
        ]

        for pattern in patterns:
            verification_files.extend(self.project_root.glob(pattern))

        return verification_files

    def print_analysis(self):
        """Print analysis of all duplicates found"""
        print("🧬 aetherra Quick Duplicate Analysis")
        print("=" * 50)

        # Test duplicates
        test_dupes = self.find_test_duplicates()
        print(f"\n🧪 TEST FILE DUPLICATES: {len(test_dupes)} found")
        for root_file, unit_file, status in test_dupes:
            root_rel = root_file.relative_to(self.project_root)
            unit_rel = unit_file.relative_to(self.project_root)
            print(f"   📁 {root_rel}")
            print(f"   📁 {unit_rel}")
            print(f"      Status: {status}")
            print(f"      Recommendation: Keep {unit_rel} (organized location)")
            print()

        # Website duplicates
        website_dupes = self.find_website_duplicates()
        print(f"\n🌐 WEBSITE FILE DUPLICATES: {len(website_dupes)} found")
        for website_file, root_file, status in website_dupes:
            website_rel = website_file.relative_to(self.project_root)
            root_rel = root_file.relative_to(self.project_root)
            print(f"   📁 {website_rel}")
            print(f"   📁 {root_rel}")
            print(f"      Status: {status}")
            print(f"      Recommendation: Keep {root_rel} (GitHub Pages needs root)")
            print()

        # Status documents
        status_docs = self.find_status_documents()
        print(f"\n📋 STATUS DOCUMENTS: {len(status_docs)} found")
        for doc in status_docs:
            doc_rel = doc.relative_to(self.project_root)
            print(f"   📄 {doc_rel}")
            print("      Recommendation: Archive (historical document)")

        # Legacy files
        legacy_files = self.find_legacy_files()
        print(f"\n🗂️ LEGACY FILES: {len(legacy_files)} found")
        for file in legacy_files:
            file_rel = file.relative_to(self.project_root)
            print(f"   📄 {file_rel}")
            print("      Recommendation: Archive or delete")

        # Verification scripts
        verification_files = self.find_verification_scripts()
        print(f"\n🔧 VERIFICATION SCRIPTS: {len(verification_files)} found")
        for file in verification_files:
            file_rel = file.relative_to(self.project_root)
            print(f"   📄 {file_rel}")
            print("      Recommendation: Archive (temporary tools)")

        total_files = (
            len(test_dupes)
            + len(website_dupes)
            + len(status_docs)
            + len(legacy_files)
            + len(verification_files)
        )
        print(f"\n📊 TOTAL FILES TO PROCESS: {total_files}")
        print("\n💡 Run with --execute to perform cleanup")

    def execute_cleanup(self):
        """Execute the cleanup operations"""
        print("🧹 Executing cleanup operations...")

        # Create archive directory
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        cleanup_count = 0

        # 1. Handle test duplicates - delete root versions, keep unit versions
        test_dupes = self.find_test_duplicates()
        for root_file, unit_file, status in test_dupes:
            if status == "Exact duplicate":
                print(
                    f"   🗑️ Deleting {root_file.relative_to(self.project_root)} (keeping unit/ version)"
                )
                root_file.unlink()
                cleanup_count += 1
            else:
                # Move to archive for manual review
                archive_path = self.archive_dir / "tests_need_review" / root_file.name
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(root_file), str(archive_path))
                print(
                    f"   📦 Moved {root_file.relative_to(self.project_root)} to archive (needs review)"
                )
                cleanup_count += 1

        # 2. Handle website duplicates - move website/ versions to archive
        website_dupes = self.find_website_duplicates()
        for website_file, root_file, status in website_dupes:
            archive_path = self.archive_dir / "website_old" / website_file.name
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(website_file), str(archive_path))
            print(
                f"   📦 Moved {website_file.relative_to(self.project_root)} to archive"
            )
            cleanup_count += 1

        # 3. Archive status documents
        status_docs = self.find_status_documents()
        for doc in status_docs:
            archive_path = self.archive_dir / "status_docs" / doc.name
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(doc), str(archive_path))
            print(f"   📦 Archived {doc.relative_to(self.project_root)}")
            cleanup_count += 1

        # 4. Archive legacy files
        legacy_files = self.find_legacy_files()
        for file in legacy_files:
            archive_path = (
                self.archive_dir / "legacy" / file.relative_to(self.project_root)
            )
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(archive_path))
            print(f"   📦 Archived {file.relative_to(self.project_root)}")
            cleanup_count += 1

        # 5. Archive verification scripts
        verification_files = self.find_verification_scripts()
        for file in verification_files:
            archive_path = self.archive_dir / "verification_scripts" / file.name
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(archive_path))
            print(f"   📦 Archived {file.relative_to(self.project_root)}")
            cleanup_count += 1

        print(f"\n✅ Cleanup complete! Processed {cleanup_count} files")
        print(
            f"📁 Archived files are in: {self.archive_dir.relative_to(self.project_root)}"
        )


def main():
    import sys

    execute = "--execute" in sys.argv

    cleanup = QuickDuplicateCleanup()

    if execute:
        cleanup.execute_cleanup()
    else:
        cleanup.print_analysis()


if __name__ == "__main__":
    main()

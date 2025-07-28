#!/usr/bin/env python3
"""
Conservative File Usage Analysis
Only identifies files that are truly safe to move, protecting all database and core system files.
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path


class ConservativeFileAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.aetherra_dir = self.project_root / "Aetherra"
        self.lyrixa_dir = self.aetherra_dir / "lyrixa"

        # Files that should NEVER be moved (comprehensive list)
        self.protected_extensions = {
            ".db",
            ".sqlite",
            ".sqlite3",  # All database files
            ".py",  # All Python files (too risky)
            ".json",
            ".yaml",
            ".yml",  # Configuration files
            ".md",  # Documentation (might be referenced)
        }

        # Protected patterns
        self.protected_patterns = [
            r".*memory.*",  # Anything memory-related
            r".*config.*",  # Configuration files
            r".*launcher.*",  # Launchers
            r".*api.*",  # API files
            r".*core.*",  # Core system files
            r".*agent.*",  # Agent files
            r".*intelligence.*",  # Intelligence components
            r".*gui.*",  # GUI components
            r".*interface.*",  # Interface files
            r".*bridge.*",  # Bridge components
            r".*manager.*",  # Managers
            r".*engine.*",  # Engines
            r".*system.*",  # System files
        ]

        # Only these file types are safe candidates for moving
        self.safe_candidate_extensions = {
            ".log",
            ".txt",
            ".bak",
            ".backup",
            ".old",
            ".tmp",
            ".out",
            ".err",
            ".temp",
        }

        # Safe patterns (files that are likely just logs/outputs)
        self.safe_patterns = [
            r".*\.log$",
            r".*debug.*\.txt$",
            r".*output.*\.txt$",
            r".*report.*\.txt$",
            r".*status.*\.txt$",
            r".*backup.*",
            r".*\.old$",
            r".*\.bak$",
            r".*\.tmp$",
        ]

    def is_protected_file(self, file_path):
        """Check if file should be protected from moving"""
        file_path = Path(file_path)
        file_name = file_path.name.lower()
        file_str = str(file_path).lower()

        # Check extensions
        if file_path.suffix.lower() in self.protected_extensions:
            return True, f"Protected extension: {file_path.suffix}"

        # Check protected patterns
        for pattern in self.protected_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True, f"Protected pattern: {pattern}"

        # Check if it's in a critical directory
        path_parts = file_path.parts
        critical_dirs = {
            "core",
            "api",
            "gui",
            "memory",
            "agents",
            "intelligence",
            "system",
        }
        if any(part.lower() in critical_dirs for part in path_parts):
            return True, f"In critical directory"

        return False, "Not protected"

    def is_safe_candidate(self, file_path):
        """Check if file is a safe candidate for moving"""
        file_path = Path(file_path)
        file_name = file_path.name.lower()
        file_str = str(file_path).lower()

        # Check if it has a safe extension
        if file_path.suffix.lower() in self.safe_candidate_extensions:
            return True, f"Safe extension: {file_path.suffix}"

        # Check safe patterns
        for pattern in self.safe_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True, f"Safe pattern: {pattern}"

        return False, "Not a safe candidate"

    def analyze_directory(self, directory):
        """Analyze a directory for safe-to-move files"""
        safe_files = []
        protected_files = []

        directory = Path(directory)
        print(f"\n🔍 Conservative analysis of {directory}...")

        for root, dirs, files in os.walk(directory):
            # Skip system directories
            if any(
                skip in root
                for skip in ["__pycache__", ".git", ".venv", "node_modules"]
            ):
                continue

            for file in files:
                file_path = Path(root) / file

                # First check if it's protected
                is_protected, protect_reason = self.is_protected_file(file_path)
                if is_protected:
                    protected_files.append((file_path, protect_reason))
                    continue

                # Then check if it's a safe candidate
                is_safe, safe_reason = self.is_safe_candidate(file_path)
                if is_safe:
                    safe_files.append((file_path, safe_reason))

        return safe_files, protected_files

    def generate_conservative_report(self):
        """Generate a conservative analysis report"""
        print("🛡️  CONSERVATIVE FILE ANALYSIS")
        print("=" * 60)
        print("Only identifying files that are clearly safe to move:")
        print("- Log files, debug output, temporary files")
        print("- Backup files, old files")
        print("- Non-functional output files")
        print("\nPROTECTED (will not be moved):")
        print("- All .db/.sqlite files (memory databases)")
        print("- All .py files (Python code)")
        print("- All .json/.yaml files (configuration)")
        print("- Files in core directories (core/, api/, gui/, memory/, etc.)")
        print("- Any files with memory/config/launcher/agent patterns")

        # Analyze Lyrixa directory
        lyrixa_safe, lyrixa_protected = self.analyze_directory(self.lyrixa_dir)

        # Analyze Aetherra directory (excluding lyrixa)
        aetherra_safe = []
        aetherra_protected = []

        for root, dirs, files in os.walk(self.aetherra_dir):
            # Skip lyrixa directory as we analyzed it separately
            if "lyrixa" in root:
                continue
            if any(skip in root for skip in ["__pycache__", ".git", ".venv"]):
                continue

            for file in files:
                file_path = Path(root) / file

                is_protected, protect_reason = self.is_protected_file(file_path)
                if is_protected:
                    aetherra_protected.append((file_path, protect_reason))
                    continue

                is_safe, safe_reason = self.is_safe_candidate(file_path)
                if is_safe:
                    aetherra_safe.append((file_path, safe_reason))

        # Generate report
        report = {
            "analysis_type": "conservative",
            "analysis_timestamp": str(Path.cwd()),
            "lyrixa_analysis": {
                "safe_to_move": [
                    {"path": str(f[0].relative_to(self.project_root)), "reason": f[1]}
                    for f in lyrixa_safe
                ],
                "protected_count": len(lyrixa_protected),
                "safe_count": len(lyrixa_safe),
            },
            "aetherra_analysis": {
                "safe_to_move": [
                    {"path": str(f[0].relative_to(self.project_root)), "reason": f[1]}
                    for f in aetherra_safe
                ],
                "protected_count": len(aetherra_protected),
                "safe_count": len(aetherra_safe),
            },
        }

        # Print summary
        print(f"\n📁 LYRIXA DIRECTORY:")
        print(f"   🛡️  Protected files: {len(lyrixa_protected)}")
        print(f"   ✅ Safe to move: {len(lyrixa_safe)}")

        if lyrixa_safe:
            print("   Safe files identified:")
            for file_info, reason in lyrixa_safe:
                rel_path = file_info.relative_to(self.project_root)
                print(f"     • {rel_path} ({reason})")
        else:
            print("     (No files identified as safe to move)")

        print(f"\n📁 AETHERRA DIRECTORY:")
        print(f"   🛡️  Protected files: {len(aetherra_protected)}")
        print(f"   ✅ Safe to move: {len(aetherra_safe)}")

        if aetherra_safe:
            print("   Safe files identified:")
            for file_info, reason in aetherra_safe:
                rel_path = file_info.relative_to(self.project_root)
                print(f"     • {rel_path} ({reason})")
        else:
            print("     (No files identified as safe to move)")

        total_safe = len(lyrixa_safe) + len(aetherra_safe)
        total_protected = len(lyrixa_protected) + len(aetherra_protected)

        print(f"\n📊 SUMMARY:")
        print(f"   Total files analyzed: {total_safe + total_protected}")
        print(f"   Protected (kept): {total_protected}")
        print(f"   Safe to move: {total_safe}")
        print(
            f"   Protection ratio: {(total_protected / (total_safe + total_protected) * 100):.1f}%"
        )

        return report


def main():
    project_root = Path.cwd()
    analyzer = ConservativeFileAnalyzer(project_root)

    # Run conservative analysis
    report = analyzer.generate_conservative_report()

    # Save report
    with open("conservative_file_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Conservative analysis saved to: conservative_file_analysis.json")

    if (
        report["lyrixa_analysis"]["safe_count"] == 0
        and report["aetherra_analysis"]["safe_count"] == 0
    ):
        print("\n🎉 EXCELLENT! No files were identified as safe to move.")
        print("   This means all files are being treated as potentially important.")
        print("   Your Aetherra/Lyrixa system integrity is preserved!")

    return report


if __name__ == "__main__":
    main()

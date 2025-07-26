#!/usr/bin/env python3
"""
🔍 Aetherra File Usage Audit
===========================

This script analyzes the Aetherra project to identify:
1. Which Python files are actively imported/used
2. Which files are unused and can be moved to unused/
3. Import dependency mapping
4. Recommended file structure cleanup
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import List


class AetherraFileAuditor:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_files = set()
        self.imports = defaultdict(set)
        self.file_references = defaultdict(set)
        self.used_files = set()
        self.unused_files = set()
        self.entry_points = {
            "aetherra_launcher.py",
            "aetherra_launcher_new.py",
            "web_interface_server.py",
            "launcher.py",
            "main.py",
            "app.py",
            "run.py",
            "server.py",
            "__main__.py",
        }
        # Directories to exclude from scanning
        self.exclude_dirs = {
            "Unused",
            "unused",
            "backup",
            "backups",
            "archive",
            "legacy",
            ".venv",
            "__pycache__",
            "Aetherra_backup_",
            "legacy_cleanup_",
            ".git",
            "node_modules",
            "venv",
            "env",
            ".pytest_cache",
            ".mypy_cache",
        }

    def scan_project(self):
        """Scan entire project for Python files and their relationships"""
        print("🔍 Scanning Aetherra project structure...")

        # Find all Python files, excluding backup directories
        file_count = 0
        for py_file in self.project_root.rglob("*.py"):
            # Skip if in excluded directory
            if any(exclude_dir in str(py_file) for exclude_dir in self.exclude_dirs):
                continue
            self.python_files.add(py_file)
            file_count += 1
            if file_count % 1000 == 0:
                print(f"   Scanning... found {file_count} files so far")

        print(
            f"📁 Found {len(self.python_files)} active Python files (excluding backups)"
        )

        # Analyze imports and references with progress
        print("🔍 Analyzing file imports and dependencies...")
        analyzed_count = 0
        total_files = len(self.python_files)

        for py_file in self.python_files:
            self._analyze_file(py_file)
            analyzed_count += 1
            if analyzed_count % 500 == 0:
                progress = (analyzed_count / total_files) * 100
                print(f"   Progress: {analyzed_count}/{total_files} ({progress:.1f}%)")

        print("🔗 Categorizing files as used/unused...")
        # Determine used vs unused
        self._categorize_files()

    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file for imports and references"""
        try:
            # Quick file size check to skip very large files
            file_size = file_path.stat().st_size
            if file_size > 1024 * 1024:  # Skip files larger than 1MB
                print(
                    f"⚠️  Skipping large file: {file_path} ({file_size / 1024 / 1024:.1f} MB)"
                )
                return

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse AST for imports (with timeout protection)
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.imports[file_path].add(alias.name)

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.imports[file_path].add(node.module)
                            for alias in node.names:
                                full_name = f"{node.module}.{alias.name}"
                                self.imports[file_path].add(full_name)

            except (SyntaxError, RecursionError, MemoryError) as e:
                print(f"⚠️  Parse error in {file_path}: {type(e).__name__}")

            # Look for string references to other files (simplified)
            py_references = re.findall(
                r'["\']([^"\']*\.py)["\']', content[:10000]
            )  # Only check first 10KB
            for ref in py_references:
                self.file_references[file_path].add(ref)

        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
            return

    def _categorize_files(self):
        """Categorize files as used or unused"""
        # Start with entry points (known important files)
        entry_files = set()
        for py_file in self.python_files:
            if py_file.name in self.entry_points:
                entry_files.add(py_file)

        print(f"🚀 Found {len(entry_files)} entry point files")

        # Recursively find all imported files
        to_process = entry_files.copy()
        processed = set()

        while to_process:
            current_file = to_process.pop()
            if current_file in processed:
                continue

            processed.add(current_file)
            self.used_files.add(current_file)

            # Find files imported by current file
            for import_name in self.imports[current_file]:
                # Try to find corresponding Python file
                potential_files = self._resolve_import_to_file(import_name)
                for potential_file in potential_files:
                    if potential_file not in processed:
                        to_process.add(potential_file)

        # Mark remaining files as unused
        self.unused_files = self.python_files - self.used_files

    def _resolve_import_to_file(self, import_name: str) -> List[Path]:
        """Try to resolve an import name to actual file paths"""
        potential_files = []

        # Handle different import patterns
        parts = import_name.split(".")

        for py_file in self.python_files:
            # Check if file path matches import
            file_parts = (
                str(py_file.relative_to(self.project_root))
                .replace("\\", "/")
                .replace(".py", "")
                .split("/")
            )

            # Various matching strategies
            if parts[-1] == py_file.stem:  # Module name matches file name
                potential_files.append(py_file)
            elif (
                len(parts) > 1 and parts[-2:] == file_parts[-2:]
            ):  # Package.module match
                potential_files.append(py_file)
            elif import_name.replace(".", "/") in str(py_file):  # Direct path match
                potential_files.append(py_file)

        return potential_files

    def generate_report(self):
        """Generate comprehensive audit report"""
        report = {
            "summary": {
                "total_files": len(self.python_files),
                "used_files": len(self.used_files),
                "unused_files": len(self.unused_files),
                "usage_percentage": round(
                    (len(self.used_files) / len(self.python_files)) * 100, 2
                ),
            },
            "used_files": [
                str(f.relative_to(self.project_root)) for f in sorted(self.used_files)
            ],
            "unused_files": [
                str(f.relative_to(self.project_root)) for f in sorted(self.unused_files)
            ],
            "large_unused_files": [],
            "recommendations": [],
        }

        # Identify large unused files
        for unused_file in self.unused_files:
            try:
                size = unused_file.stat().st_size
                if size > 5000:  # Files larger than 5KB
                    report["large_unused_files"].append(
                        {
                            "file": str(unused_file.relative_to(self.project_root)),
                            "size_kb": round(size / 1024, 2),
                        }
                    )
            except Exception:
                pass

        # Generate recommendations
        report["recommendations"] = [
            f"Move {len(self.unused_files)} unused files to unused/ directory",
            f"Review {len(report['large_unused_files'])} large unused files for potential deletion",
            "Implement import optimization to reduce dependency complexity",
            "Consider modularizing large files for better maintainability",
        ]

        return report

    def print_report(self):
        """Print human-readable audit report"""
        print("\n" + "=" * 60)
        print("🔍 AETHERRA FILE USAGE AUDIT REPORT")
        print("=" * 60)

        report = self.generate_report()

        print("\n📊 SUMMARY:")
        print(f"   Total Python files: {report['summary']['total_files']}")
        print(f"   Used files: {report['summary']['used_files']}")
        print(f"   Unused files: {report['summary']['unused_files']}")
        print(f"   Usage rate: {report['summary']['usage_percentage']}%")

        print(f"\n❌ UNUSED FILES ({len(report['unused_files'])}):")
        for unused_file in report["unused_files"][:20]:  # Show first 20
            print(f"   - {unused_file}")
        if len(report["unused_files"]) > 20:
            print(f"   ... and {len(report['unused_files']) - 20} more")

        print("\n📦 LARGE UNUSED FILES:")
        for large_file in sorted(
            report["large_unused_files"], key=lambda x: x["size_kb"], reverse=True
        )[:10]:
            print(f"   - {large_file['file']} ({large_file['size_kb']} KB)")

        print("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   • {rec}")

        return report

    def create_cleanup_script(self):
        """Create a script to move unused files to unused/ directory"""
        cleanup_script = '''#!/usr/bin/env python3
"""
🧹 Aetherra File Cleanup Script
Generated by audit_file_usage.py
"""

import shutil
from pathlib import Path

def move_unused_files():
    """Move unused files to unused/ directory"""
    unused_dir = Path("unused")
    unused_dir.mkdir(exist_ok=True)

    unused_files = [
'''

        for unused_file in sorted(self.unused_files):
            rel_path = unused_file.relative_to(self.project_root)
            cleanup_script += f'        "{rel_path}",\n'

        cleanup_script += """    ]

    moved_count = 0
    for file_path in unused_files:
        src = Path(file_path)
        if src.exists():
            # Create destination directory structure
            dest = unused_dir / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(str(src), str(dest))
                print(f"✅ Moved: {file_path}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Failed to move {file_path}: {e}")

    print(f"\\n🎉 Cleanup complete! Moved {moved_count} files to unused/")

if __name__ == "__main__":
    move_unused_files()
"""

        with open(self.project_root / "scripts" / "cleanup_unused_files.py", "w") as f:
            f.write(cleanup_script)

        print("✅ Created cleanup script: scripts/cleanup_unused_files.py")


def main():
    """Main execution function"""
    print("🚀 Starting Aetherra File Usage Audit...")

    auditor = AetherraFileAuditor()
    auditor.scan_project()
    report = auditor.print_report()

    # Save detailed report
    report_file = Path("scripts") / "file_audit_report.json"
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Detailed report saved to: {report_file}")

    # Create cleanup script
    auditor.create_cleanup_script()

    print("\n🎯 Next steps:")
    print("1. Review the unused files list")
    print("2. Run: python scripts/cleanup_unused_files.py")
    print("3. Commit changes and proceed to CI/CD setup")


if __name__ == "__main__":
    main()

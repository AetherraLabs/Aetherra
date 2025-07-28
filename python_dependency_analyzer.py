#!/usr/bin/env python3
"""
Comprehensive Python Dependency Analysis
Maps all imports, finds orphaned files, redundant modules, and wiring issues.
"""

import ast
import importlib.util
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx


class PythonDependencyAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.aetherra_dir = self.project_root / "Aetherra"
        self.lyrixa_dir = self.aetherra_dir / "lyrixa"

        # Tracking structures
        self.all_py_files = set()
        self.import_graph = nx.DiGraph()  # Directed graph of imports
        self.file_imports = defaultdict(set)  # file -> what it imports
        self.file_imported_by = defaultdict(set)  # file -> what imports it
        self.broken_imports = defaultdict(set)  # file -> broken imports
        self.unused_imports = defaultdict(set)  # file -> unused imports
        self.entry_points = set()  # Files that could be entry points
        self.orphaned_files = set()  # Files never imported
        self.redundant_groups = []  # Groups of files doing similar things

        # Entry point patterns
        self.entry_point_patterns = [
            r".*launcher.*\.py$",
            r".*main.*\.py$",
            r".*server.*\.py$",
            r".*app.*\.py$",
            r".*run.*\.py$",
            r".*start.*\.py$",
            r".*demo.*\.py$",
            r".*test.*\.py$",
            r".*cli.*\.py$",
        ]

    def scan_all_python_files(self):
        """Find all Python files in the project"""
        print("🔍 Scanning all Python files...")

        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            if any(
                skip in root
                for skip in [
                    ".git",
                    "__pycache__",
                    ".venv",
                    "node_modules",
                    ".pytest_cache",
                ]
            ):
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    self.all_py_files.add(file_path)

                    # Check if it's a potential entry point
                    if any(
                        re.match(pattern, str(file_path), re.IGNORECASE)
                        for pattern in self.entry_point_patterns
                    ):
                        self.entry_points.add(file_path)

        print(f"   Found {len(self.all_py_files)} Python files")
        print(f"   Identified {len(self.entry_points)} potential entry points")

    def parse_file_imports(self, file_path):
        """Parse imports from a Python file using AST"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                        # Also add specific imports
                        for alias in node.names:
                            full_name = f"{node.module}.{alias.name}"
                            imports.add(full_name)

            return imports

        except Exception as e:
            print(f"   Error parsing {file_path}: {e}")
            return set()

    def resolve_import_to_file(self, import_name, current_file):
        """Try to resolve an import to an actual file"""
        # Handle relative imports
        if import_name.startswith("."):
            base_dir = current_file.parent
            # Remove leading dots and convert to path
            import_parts = import_name.lstrip(".").split(".")
            if import_parts == [""]:
                # Just dots, refers to package __init__.py
                return base_dir / "__init__.py"
            else:
                target_path = base_dir
                for part in import_parts:
                    target_path = target_path / part

                # Try .py file first, then __init__.py
                if (target_path.with_suffix(".py")).exists():
                    return target_path.with_suffix(".py")
                elif (target_path / "__init__.py").exists():
                    return target_path / "__init__.py"

        # Handle absolute imports
        import_parts = import_name.split(".")

        # Try from project root
        for i in range(len(import_parts), 0, -1):
            partial_import = ".".join(import_parts[:i])

            # Try various base directories
            base_dirs = [self.project_root, self.aetherra_dir, self.lyrixa_dir]

            for base_dir in base_dirs:
                target_path = base_dir
                for part in import_parts[:i]:
                    target_path = target_path / part

                # Check if file exists
                py_file = target_path.with_suffix(".py")
                init_file = target_path / "__init__.py"

                if py_file.exists() and py_file in self.all_py_files:
                    return py_file
                elif init_file.exists() and init_file in self.all_py_files:
                    return init_file

        return None

    def analyze_imports(self):
        """Analyze all imports and build dependency graph"""
        print("🔗 Analyzing import dependencies...")

        for file_path in self.all_py_files:
            imports = self.parse_file_imports(file_path)

            for import_name in imports:
                resolved_file = self.resolve_import_to_file(import_name, file_path)

                if resolved_file:
                    # Valid import
                    self.file_imports[file_path].add(resolved_file)
                    self.file_imported_by[resolved_file].add(file_path)
                    self.import_graph.add_edge(str(file_path), str(resolved_file))
                else:
                    # Broken import (might be external library)
                    if not self.is_external_library(import_name):
                        self.broken_imports[file_path].add(import_name)

    def is_external_library(self, import_name):
        """Check if import is likely an external library"""
        external_libs = {
            "os",
            "sys",
            "json",
            "pathlib",
            "re",
            "ast",
            "collections",
            "datetime",
            "time",
            "typing",
            "logging",
            "sqlite3",
            "asyncio",
            "numpy",
            "pandas",
            "requests",
            "flask",
            "fastapi",
            "pydantic",
            "openai",
            "anthropic",
            "google",
            "psutil",
            "pyyaml",
            "aiohttp",
            "sqlalchemy",
            "alembic",
            "pytest",
            "black",
            "flake8",
        }

        return any(import_name.startswith(lib) for lib in external_libs)

    def find_orphaned_files(self):
        """Find files that are never imported"""
        print("🏝️  Finding orphaned files...")

        for file_path in self.all_py_files:
            # Skip entry points - they're supposed to be standalone
            if file_path in self.entry_points:
                continue

            # Skip __init__.py files - they're package markers
            if file_path.name == "__init__.py":
                continue

            # If file is never imported by anything, it's orphaned
            if file_path not in self.file_imported_by:
                self.orphaned_files.add(file_path)

    def find_redundant_files(self):
        """Find groups of files that might be redundant"""
        print("🔄 Finding potentially redundant files...")

        # Group files by similar names/functions
        name_groups = defaultdict(list)

        for file_path in self.all_py_files:
            # Extract base functionality from filename
            name = file_path.stem.lower()

            # Remove common prefixes/suffixes
            name = re.sub(r"^(test_|demo_|sample_|old_|new_|backup_)", "", name)
            name = re.sub(r"(_test|_demo|_sample|_old|_new|_backup|_v\d+)$", "", name)

            # Group by core name
            if len(name) > 3:  # Avoid grouping very short names
                name_groups[name].append(file_path)

        # Find groups with multiple files
        for name, files in name_groups.items():
            if len(files) > 1:
                self.redundant_groups.append(
                    {
                        "name": name,
                        "files": [str(f.relative_to(self.project_root)) for f in files],
                        "count": len(files),
                    }
                )

    def analyze_aetherra_lyrixa_connection(self):
        """Analyze how well Aetherra and Lyrixa are connected"""
        print("🔗 Analyzing Aetherra-Lyrixa connectivity...")

        aetherra_files = {
            f
            for f in self.all_py_files
            if "Aetherra" in str(f) and "lyrixa" not in str(f)
        }
        lyrixa_files = {f for f in self.all_py_files if "lyrixa" in str(f)}

        # Find connections from Aetherra to Lyrixa
        aetherra_to_lyrixa = 0
        lyrixa_to_aetherra = 0

        for aetherra_file in aetherra_files:
            for imported_file in self.file_imports.get(aetherra_file, set()):
                if imported_file in lyrixa_files:
                    aetherra_to_lyrixa += 1

        for lyrixa_file in lyrixa_files:
            for imported_file in self.file_imports.get(lyrixa_file, set()):
                if imported_file in aetherra_files:
                    lyrixa_to_aetherra += 1

        return {
            "aetherra_files": len(aetherra_files),
            "lyrixa_files": len(lyrixa_files),
            "aetherra_to_lyrixa_imports": aetherra_to_lyrixa,
            "lyrixa_to_aetherra_imports": lyrixa_to_aetherra,
            "total_cross_imports": aetherra_to_lyrixa + lyrixa_to_aetherra,
        }

    def generate_comprehensive_report(self):
        """Generate comprehensive dependency analysis report"""
        print("\n" + "=" * 80)
        print("🧬 COMPREHENSIVE PYTHON DEPENDENCY ANALYSIS")
        print("=" * 80)

        # Run all analyses
        self.scan_all_python_files()
        self.analyze_imports()
        self.find_orphaned_files()
        self.find_redundant_files()
        connectivity = self.analyze_aetherra_lyrixa_connection()

        # Calculate statistics
        total_imports = sum(len(imports) for imports in self.file_imports.values())
        total_broken = sum(len(broken) for broken in self.broken_imports.values())

        # Generate report
        report = {
            "analysis_timestamp": str(self.project_root),
            "file_statistics": {
                "total_python_files": len(self.all_py_files),
                "entry_points": len(self.entry_points),
                "orphaned_files": len(self.orphaned_files),
                "files_with_broken_imports": len(
                    [f for f in self.broken_imports if self.broken_imports[f]]
                ),
                "total_import_statements": total_imports,
                "broken_import_statements": total_broken,
            },
            "connectivity": connectivity,
            "orphaned_files": [
                str(f.relative_to(self.project_root)) for f in self.orphaned_files
            ],
            "redundant_groups": self.redundant_groups,
            "broken_imports": {
                str(f.relative_to(self.project_root)): list(imports)
                for f, imports in self.broken_imports.items()
                if imports
            },
        }

        # Print summary
        print(f"\n📊 FILE STATISTICS:")
        print(f"   Total Python files: {len(self.all_py_files)}")
        print(f"   Entry points: {len(self.entry_points)}")
        print(f"   Orphaned files: {len(self.orphaned_files)}")
        print(f"   Redundant groups: {len(self.redundant_groups)}")
        print(
            f"   Files with broken imports: {len([f for f in self.broken_imports if self.broken_imports[f]])}"
        )

        print(f"\n🔗 CONNECTIVITY ANALYSIS:")
        print(f"   Aetherra files: {connectivity['aetherra_files']}")
        print(f"   Lyrixa files: {connectivity['lyrixa_files']}")
        print(
            f"   Aetherra→Lyrixa imports: {connectivity['aetherra_to_lyrixa_imports']}"
        )
        print(
            f"   Lyrixa→Aetherra imports: {connectivity['lyrixa_to_aetherra_imports']}"
        )
        print(f"   Total cross-imports: {connectivity['total_cross_imports']}")

        if connectivity["total_cross_imports"] < 10:
            print("   ⚠️  WARNING: Very few cross-imports detected!")
            print("   This suggests Aetherra and Lyrixa may not be well integrated.")

        print(f"\n🏝️  TOP ORPHANED FILES:")
        for i, orphan in enumerate(list(self.orphaned_files)[:10]):
            rel_path = orphan.relative_to(self.project_root)
            print(f"   {i + 1}. {rel_path}")
        if len(self.orphaned_files) > 10:
            print(f"   ... and {len(self.orphaned_files) - 10} more")

        print(f"\n🔄 TOP REDUNDANT GROUPS:")
        for i, group in enumerate(self.redundant_groups[:5]):
            print(f"   {i + 1}. '{group['name']}' ({group['count']} files):")
            for file in group["files"][:3]:
                print(f"      - {file}")
            if len(group["files"]) > 3:
                print(f"      ... and {len(group['files']) - 3} more")

        return report


def main():
    project_root = Path.cwd()
    analyzer = PythonDependencyAnalyzer(project_root)

    # Run comprehensive analysis
    report = analyzer.generate_comprehensive_report()

    # Save detailed report
    with open("python_dependency_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: python_dependency_analysis.json")

    # Generate actionable recommendations
    print(f"\n💡 RECOMMENDATIONS:")

    if report["file_statistics"]["orphaned_files"] > 100:
        print(
            f"   1. 🗑️  Consider moving {report['file_statistics']['orphaned_files']} orphaned files to Unused/"
        )

    if len(report["redundant_groups"]) > 10:
        print(
            f"   2. 🔄 Review {len(report['redundant_groups'])} redundant groups for consolidation"
        )

    if report["connectivity"]["total_cross_imports"] < 50:
        print(
            f"   3. 🔗 Improve Aetherra-Lyrixa integration (only {report['connectivity']['total_cross_imports']} cross-imports)"
        )

    if report["file_statistics"]["broken_import_statements"] > 0:
        print(
            f"   4. 🔧 Fix {report['file_statistics']['broken_import_statements']} broken import statements"
        )

    return report


if __name__ == "__main__":
    main()

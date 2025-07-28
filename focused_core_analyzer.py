#!/usr/bin/env python3
"""
Focused Aetherra/Lyrixa Analysis
Analyzes only the core Aetherra and Lyrixa directories, excluding packages and unused files.
"""

import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path


class FocusedAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.aetherra_dir = self.project_root / "Aetherra"
        self.lyrixa_dir = self.aetherra_dir / "lyrixa"

        # Only analyze core directories
        self.include_patterns = [
            r".*[\\/]Aetherra[\\/](?!.*[\\/]lyrixa[\\/]).*\.py$",  # Aetherra (not lyrixa)
            r".*[\\/]Aetherra[\\/]lyrixa[\\/].*\.py$",  # Lyrixa
        ]

        # Exclude these directories/patterns
        self.exclude_patterns = [
            r".*[\\/]Unused[\\/].*",
            r".*[\\/]unused.*[\\/].*",
            r".*[\\/]Lib[\\/].*",
            r".*[\\/]Scripts[\\/].*",
            r".*[\\/]share[\\/].*",
            r".*[\\/]__pycache__[\\/].*",
            r".*[\\/]\.venv[\\/].*",
            r".*[\\/]\.git[\\/].*",
            r".*[\\/]backup.*[\\/].*",
            r".*[\\/]archive[\\/].*",
            r".*[\\/]test_.*\.py$",
            r".*[\\/]demo_.*\.py$",
        ]

        self.core_files = set()
        self.imports = defaultdict(set)
        self.imported_by = defaultdict(set)
        self.broken_imports = defaultdict(set)
        self.orphaned = set()

    def should_include_file(self, file_path):
        """Check if file should be included in analysis"""
        file_str = str(file_path).replace("\\", "/")

        # Must match include pattern
        included = any(
            re.match(pattern, file_str, re.IGNORECASE)
            for pattern in self.include_patterns
        )
        if not included:
            return False

        # Must not match exclude pattern
        excluded = any(
            re.match(pattern, file_str, re.IGNORECASE)
            for pattern in self.exclude_patterns
        )
        if excluded:
            return False

        return True

    def scan_core_files(self):
        """Scan only core Aetherra and Lyrixa files"""
        print("🔍 Scanning core Aetherra/Lyrixa files...")

        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    if self.should_include_file(file_path):
                        self.core_files.add(file_path)

        print(f"   Found {len(self.core_files)} core Python files")

    def parse_imports(self, file_path):
        """Parse imports from a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

            return imports

        except Exception:
            return set()

    def resolve_import(self, import_name, current_file):
        """Resolve import to actual file in our core set"""
        if import_name.startswith("."):
            # Relative import
            base_dir = current_file.parent
            import_parts = import_name.lstrip(".").split(".")

            if import_parts == [""]:
                target = base_dir / "__init__.py"
            else:
                target_path = base_dir
                for part in import_parts:
                    target_path = target_path / part
                target = target_path.with_suffix(".py")
                if not target.exists():
                    target = target_path / "__init__.py"
        else:
            # Absolute import
            import_parts = import_name.split(".")

            # Try from Aetherra directory
            target_path = self.aetherra_dir
            for part in import_parts:
                target_path = target_path / part

            target = target_path.with_suffix(".py")
            if not target.exists():
                target = target_path / "__init__.py"

        return target if target.exists() and target in self.core_files else None

    def analyze_core_dependencies(self):
        """Analyze dependencies within core files"""
        print("🔗 Analyzing core dependencies...")

        for file_path in self.core_files:
            imports = self.parse_imports(file_path)

            for import_name in imports:
                resolved = self.resolve_import(import_name, file_path)

                if resolved:
                    self.imports[file_path].add(resolved)
                    self.imported_by[resolved].add(file_path)
                elif any(part in import_name for part in ["Aetherra", "lyrixa"]):
                    # This looks like it should be a core import but we can't resolve it
                    self.broken_imports[file_path].add(import_name)

    def find_core_orphans(self):
        """Find core files that are never imported"""
        print("🏝️  Finding core orphaned files...")

        for file_path in self.core_files:
            # Skip entry points and __init__.py files
            if file_path.name in [
                "__init__.py",
                "launcher.py",
                "main.py",
                "app.py",
            ] or any(
                pattern in file_path.name
                for pattern in ["launcher", "main", "demo", "test"]
            ):
                continue

            if file_path not in self.imported_by:
                self.orphaned.add(file_path)

    def categorize_files(self):
        """Categorize files by their location and purpose"""
        categories = {
            "aetherra_core": [],
            "aetherra_api": [],
            "aetherra_gui": [],
            "aetherra_memory": [],
            "aetherra_other": [],
            "lyrixa_core": [],
            "lyrixa_agents": [],
            "lyrixa_memory": [],
            "lyrixa_gui": [],
            "lyrixa_other": [],
        }

        for file_path in self.core_files:
            rel_path = str(file_path.relative_to(self.project_root))

            if "lyrixa" in rel_path:
                if "core" in rel_path:
                    categories["lyrixa_core"].append(rel_path)
                elif "agents" in rel_path:
                    categories["lyrixa_agents"].append(rel_path)
                elif "memory" in rel_path:
                    categories["lyrixa_memory"].append(rel_path)
                elif "gui" in rel_path:
                    categories["lyrixa_gui"].append(rel_path)
                else:
                    categories["lyrixa_other"].append(rel_path)
            else:
                if "core" in rel_path:
                    categories["aetherra_core"].append(rel_path)
                elif "api" in rel_path:
                    categories["aetherra_api"].append(rel_path)
                elif "gui" in rel_path or "ui" in rel_path:
                    categories["aetherra_gui"].append(rel_path)
                elif "memory" in rel_path:
                    categories["aetherra_memory"].append(rel_path)
                else:
                    categories["aetherra_other"].append(rel_path)

        return categories

    def generate_focused_report(self):
        """Generate focused analysis report"""
        print("\n" + "=" * 70)
        print("🎯 FOCUSED AETHERRA/LYRIXA ANALYSIS")
        print("=" * 70)

        self.scan_core_files()
        self.analyze_core_dependencies()
        self.find_core_orphans()
        categories = self.categorize_files()

        # Count connections
        aetherra_files = {f for f in self.core_files if "lyrixa" not in str(f)}
        lyrixa_files = {f for f in self.core_files if "lyrixa" in str(f)}

        aetherra_to_lyrixa = 0
        lyrixa_to_aetherra = 0

        for aetherra_file in aetherra_files:
            for imported_file in self.imports.get(aetherra_file, set()):
                if imported_file in lyrixa_files:
                    aetherra_to_lyrixa += 1

        for lyrixa_file in lyrixa_files:
            for imported_file in self.imports.get(lyrixa_file, set()):
                if imported_file in aetherra_files:
                    lyrixa_to_aetherra += 1

        report = {
            "analysis_type": "focused_core",
            "file_counts": {
                "total_core_files": len(self.core_files),
                "aetherra_files": len(aetherra_files),
                "lyrixa_files": len(lyrixa_files),
                "orphaned_files": len(self.orphaned),
                "files_with_broken_imports": len(
                    [f for f in self.broken_imports if self.broken_imports[f]]
                ),
            },
            "connectivity": {
                "aetherra_to_lyrixa": aetherra_to_lyrixa,
                "lyrixa_to_aetherra": lyrixa_to_aetherra,
                "total_cross_imports": aetherra_to_lyrixa + lyrixa_to_aetherra,
            },
            "categories": {k: len(v) for k, v in categories.items()},
            "orphaned_files": [
                str(f.relative_to(self.project_root)) for f in self.orphaned
            ],
            "broken_imports": {
                str(f.relative_to(self.project_root)): list(imports)
                for f, imports in self.broken_imports.items()
                if imports
            },
        }

        print("\n📊 CORE FILE STATISTICS:")
        print(f"   Total core files: {len(self.core_files)}")
        print(f"   Aetherra files: {len(aetherra_files)}")
        print(f"   Lyrixa files: {len(lyrixa_files)}")
        print(f"   Orphaned files: {len(self.orphaned)}")
        print(
            f"   Files with broken imports: {len([f for f in self.broken_imports if self.broken_imports[f]])}"
        )

        print("\n🔗 CORE CONNECTIVITY:")
        print(f"   Aetherra→Lyrixa imports: {aetherra_to_lyrixa}")
        print(f"   Lyrixa→Aetherra imports: {lyrixa_to_aetherra}")
        print(f"   Total cross-imports: {aetherra_to_lyrixa + lyrixa_to_aetherra}")

        if aetherra_to_lyrixa + lyrixa_to_aetherra < 20:
            print(
                "   ⚠️  WARNING: Very few cross-imports! Aetherra and Lyrixa may not be well integrated."
            )

        print("\n📁 COMPONENT BREAKDOWN:")
        for category, file_list in categories.items():
            count = len(file_list)
            if count > 0:
                category_name = category.replace("_", " ").title()
                print(f"   {category_name}: {count} files")

        print("\n🏝️  CORE ORPHANED FILES:")
        if self.orphaned:
            for i, orphan in enumerate(list(self.orphaned)[:15]):
                rel_path = orphan.relative_to(self.project_root)
                print(f"   {i + 1}. {rel_path}")
            if len(self.orphaned) > 15:
                print(f"   ... and {len(self.orphaned) - 15} more")
        else:
            print("   None found! (Good)")

        return report


def main():
    project_root = Path.cwd()
    analyzer = FocusedAnalyzer(project_root)

    report = analyzer.generate_focused_report()

    with open("focused_core_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n📄 Focused analysis saved to: focused_core_analysis.json")

    print("\n💡 ACTIONABLE RECOMMENDATIONS:")

    if report["file_counts"]["orphaned_files"] > 0:
        print(
            f"   1. 🗑️  Move {report['file_counts']['orphaned_files']} core orphaned files to Unused/"
        )

    if report["connectivity"]["total_cross_imports"] < 50:
        print(
            f"   2. 🔗 Improve Aetherra-Lyrixa integration (only {report['connectivity']['total_cross_imports']} cross-imports)"
        )

    if report["file_counts"]["files_with_broken_imports"] > 0:
        print(
            f"   3. 🔧 Fix broken imports in {report['file_counts']['files_with_broken_imports']} core files"
        )

    # Specific integration suggestions
    if report["connectivity"]["aetherra_to_lyrixa"] < 10:
        print("   4. 🔌 Aetherra needs better connections to Lyrixa")

    if report["connectivity"]["lyrixa_to_aetherra"] < 10:
        print("   5. 🔌 Lyrixa needs better connections to Aetherra")

    return report


if __name__ == "__main__":
    main()

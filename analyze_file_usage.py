#!/usr/bin/env python3
"""
File Usage Analysis Script
Analyzes Aetherra and Lyrixa directories to identify unused files.
"""

import ast
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


class FileUsageAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.aetherra_dir = self.project_root / "Aetherra"
        self.lyrixa_dir = self.aetherra_dir / "lyrixa"

        # Track file usage
        self.file_imports = defaultdict(set)  # file -> set of files that import it
        self.file_references = defaultdict(
            set
        )  # file -> set of files that reference it
        self.all_python_files = set()

        # Common patterns that indicate usage
        self.usage_patterns = [
            r"from\s+([.\w]+)\s+import",
            r"import\s+([.\w]+)",
            r'exec\(open\([\'"]([^"\']+)[\'"]',
            r'open\([\'"]([^"\']+)[\'"]',
            r'load\([\'"]([^"\']+)[\'"]',
            r'Path\([\'"]([^"\']+)[\'"]',
        ]

        # Patterns for non-Python file references
        self.file_ref_patterns = [
            r'[\'"]([^"\']*\.(?:json|yml|yaml|md|txt|csv|db|sql))[\'"]',
            r'[\'"]([^"\']*\.(?:html|css|js|jsx|ts|tsx))[\'"]',
        ]

    def scan_all_files(self):
        """Scan all Python files in the project"""
        print("🔍 Scanning all Python files...")

        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            if any(
                skip in root
                for skip in [".git", "__pycache__", ".venv", "node_modules", "Unused"]
            ):
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    self.all_python_files.add(file_path)

        print(f"Found {len(self.all_python_files)} Python files")

    def analyze_imports_and_references(self):
        """Analyze imports and references in all Python files"""
        print("🔍 Analyzing imports and references...")

        for file_path in self.all_python_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Find Python imports
                for pattern in self.usage_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Convert module path to file path
                        potential_files = self.module_to_file_paths(match, file_path)
                        for target_file in potential_files:
                            if target_file.exists():
                                self.file_imports[target_file].add(file_path)

                # Find file references
                for pattern in self.file_ref_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        referenced_file = self.resolve_file_reference(match, file_path)
                        if referenced_file and referenced_file.exists():
                            self.file_references[referenced_file].add(file_path)

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

    def module_to_file_paths(self, module_name, current_file):
        """Convert module name to possible file paths"""
        possible_files = []

        # Handle relative imports
        if module_name.startswith("."):
            base_dir = current_file.parent
            module_parts = module_name.strip(".").split(".")

            if module_parts == [""]:  # Just dots
                possible_files.append(base_dir / "__init__.py")
            else:
                for i in range(len(module_parts)):
                    partial_path = base_dir / "/".join(module_parts[: i + 1])
                    possible_files.append(partial_path.with_suffix(".py"))
                    possible_files.append(partial_path / "__init__.py")

        # Handle absolute imports
        else:
            module_parts = module_name.split(".")

            # Try from project root
            for i in range(len(module_parts)):
                partial_path = self.project_root / "/".join(module_parts[: i + 1])
                possible_files.append(partial_path.with_suffix(".py"))
                possible_files.append(partial_path / "__init__.py")

            # Try from Aetherra directory
            for i in range(len(module_parts)):
                partial_path = self.aetherra_dir / "/".join(module_parts[: i + 1])
                possible_files.append(partial_path.with_suffix(".py"))
                possible_files.append(partial_path / "__init__.py")

        return [Path(f) for f in possible_files]

    def resolve_file_reference(self, file_ref, current_file):
        """Resolve file reference to actual path"""
        if os.path.isabs(file_ref):
            return Path(file_ref)
        else:
            # Try relative to current file
            candidate = current_file.parent / file_ref
            if candidate.exists():
                return candidate

            # Try relative to project root
            candidate = self.project_root / file_ref
            if candidate.exists():
                return candidate

        return None

    def find_unused_files(self, directory):
        """Find unused files in a specific directory"""
        unused_files = []
        directory = Path(directory)

        print(f"\n🔍 Analyzing files in {directory}...")

        for root, dirs, files in os.walk(directory):
            # Skip __pycache__ and other system directories
            if "__pycache__" in root or ".git" in root:
                continue

            for file in files:
                file_path = Path(root) / file

                # Check if file is used
                is_used = False

                # Check imports
                if file_path in self.file_imports and self.file_imports[file_path]:
                    is_used = True

                # Check references
                if (
                    file_path in self.file_references
                    and self.file_references[file_path]
                ):
                    is_used = True

                # Special cases for certain file types
                if self.is_special_file(file_path):
                    is_used = True

                if not is_used:
                    unused_files.append(file_path)

        return unused_files

    def is_special_file(self, file_path):
        """Check if file should be considered as always used"""
        file_name = file_path.name.lower()

        # Configuration and important files
        special_files = [
            "__init__.py",
            "setup.py",
            "main.py",
            "app.py",
            "run.py",
            "launcher.py",
            "config.py",
            "settings.py",
            "requirements.txt",
            "pyproject.toml",
            "setup.cfg",
            "readme.md",
            "license",
            ".gitignore",
            "dockerfile",
            "docker-compose.yml",
        ]

        if file_name in special_files:
            return True

        # Files that end with certain patterns
        if (
            file_name.endswith("_main.py")
            or file_name.endswith("_launcher.py")
            or file_name.endswith("_server.py")
            or file_name.startswith("demo_")
            or file_name.startswith("test_")
        ):
            return True

        return False

    def generate_report(self):
        """Generate usage analysis report"""
        print("\n" + "=" * 60)
        print("📊 FILE USAGE ANALYSIS REPORT")
        print("=" * 60)

        # Analyze Lyrixa directory
        lyrixa_unused = self.find_unused_files(self.lyrixa_dir)

        # Analyze Aetherra directory (excluding lyrixa)
        aetherra_unused = []
        for root, dirs, files in os.walk(self.aetherra_dir):
            # Skip lyrixa directory as we analyzed it separately
            if "lyrixa" in root:
                continue
            if "__pycache__" in root or ".git" in root:
                continue

            for file in files:
                file_path = Path(root) / file

                is_used = False
                if file_path in self.file_imports and self.file_imports[file_path]:
                    is_used = True
                if (
                    file_path in self.file_references
                    and self.file_references[file_path]
                ):
                    is_used = True
                if self.is_special_file(file_path):
                    is_used = True

                if not is_used:
                    aetherra_unused.append(file_path)

        # Generate report
        report = {
            "analysis_timestamp": str(Path.cwd()),
            "total_python_files": len(self.all_python_files),
            "lyrixa_analysis": {
                "total_files": len(list(self.lyrixa_dir.rglob("*"))),
                "unused_files": [
                    str(f.relative_to(self.project_root)) for f in lyrixa_unused
                ],
                "unused_count": len(lyrixa_unused),
            },
            "aetherra_analysis": {
                "unused_files": [
                    str(f.relative_to(self.project_root)) for f in aetherra_unused
                ],
                "unused_count": len(aetherra_unused),
            },
        }

        # Print summary
        print(f"\n📁 LYRIXA DIRECTORY ANALYSIS:")
        print(f"   Unused files found: {len(lyrixa_unused)}")
        for f in lyrixa_unused[:10]:  # Show first 10
            print(f"   - {f.relative_to(self.project_root)}")
        if len(lyrixa_unused) > 10:
            print(f"   ... and {len(lyrixa_unused) - 10} more")

        print(f"\n📁 AETHERRA DIRECTORY ANALYSIS:")
        print(f"   Unused files found: {len(aetherra_unused)}")
        for f in aetherra_unused[:10]:  # Show first 10
            print(f"   - {f.relative_to(self.project_root)}")
        if len(aetherra_unused) > 10:
            print(f"   ... and {len(aetherra_unused) - 10} more")

        return report


def main():
    project_root = Path.cwd()
    analyzer = FileUsageAnalyzer(project_root)

    # Run analysis
    analyzer.scan_all_files()
    analyzer.analyze_imports_and_references()
    report = analyzer.generate_report()

    # Save report
    with open("file_usage_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: file_usage_analysis.json")

    return report


if __name__ == "__main__":
    main()

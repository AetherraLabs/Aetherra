#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Project Deep Analysis Tool
Comprehensive file analysis, duplicate detection, and documentation generator
"""

# Standard library imports
import ast
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class AetherraProjectAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.file_hashes = {}
        self.duplicate_groups = []
        self.file_inventory = {}
        self.directory_analysis = {}
        self.import_dependencies = defaultdict(set)

    def calculate_file_hash(self, filepath):
        """Calculate SHA256 hash of file content"""
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except (IOError, PermissionError):
            return None

    def analyze_python_file(self, filepath):
        """Analyze Python file for imports and basic info"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to find imports
            try:
                tree = ast.parse(content)
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)

                # Find classes and functions
                classes = [
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                ]
                functions = [
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)
                ]

                return {
                    "imports": imports,
                    "classes": classes,
                    "functions": functions,
                    "lines": len(content.split("\n")),
                    "docstring": ast.get_docstring(tree) if tree.body else None,
                }
            except SyntaxError:
                return {"error": "Syntax error in Python file"}

        except (IOError, UnicodeDecodeError):
            return {"error": "Could not read file"}

    def categorize_file(self, filepath):
        """Categorize file by type and purpose"""
        name = filepath.name.lower()

        # File type categories
        if name.endswith((".py",)):
            if "test" in name:
                return "test"
            elif "demo" in name:
                return "demo"
            elif "launcher" in name:
                return "launcher"
            elif name.startswith("__"):
                return "python_special"
            else:
                return "python_module"
        elif name.endswith((".md",)):
            return "documentation"
        elif name.endswith((".json",)):
            return "configuration"
        elif name.endswith((".db",)):
            return "database"
        elif name.endswith((".log",)):
            return "log"
        elif name.endswith((".yml", ".yaml")):
            return "configuration"
        elif name.endswith((".txt",)):
            return "text"
        else:
            return "other"

    def scan_directory(self, directory):
        """Scan a directory and analyze all files"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return

        analysis = {
            "path": str(dir_path),
            "files": [],
            "subdirectories": [],
            "file_counts": defaultdict(int),
            "total_files": 0,
            "purpose": self.infer_directory_purpose(dir_path),
        }

        try:
            for item in dir_path.iterdir():
                if item.is_file():
                    file_info = self.analyze_file(item)
                    analysis["files"].append(file_info)
                    analysis["file_counts"][file_info["category"]] += 1
                    analysis["total_files"] += 1
                elif item.is_dir() and not item.name.startswith("."):
                    analysis["subdirectories"].append(item.name)

        except PermissionError:
            analysis["error"] = "Permission denied"

        return analysis

    def analyze_file(self, filepath):
        """Comprehensive file analysis"""
        file_info = {
            "name": filepath.name,
            "path": str(filepath),
            "size": filepath.stat().st_size if filepath.exists() else 0,
            "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            if filepath.exists()
            else None,
            "category": self.categorize_file(filepath),
            "hash": self.calculate_file_hash(filepath),
        }

        # Additional analysis for Python files
        if filepath.suffix == ".py":
            file_info["python_analysis"] = self.analyze_python_file(filepath)

        # Store hash for duplicate detection
        if file_info["hash"]:
            if file_info["hash"] in self.file_hashes:
                self.file_hashes[file_info["hash"]].append(str(filepath))
            else:
                self.file_hashes[file_info["hash"]] = [str(filepath)]

        return file_info

    def infer_directory_purpose(self, dir_path):
        """Infer the purpose of a directory based on name and contents"""
        name = dir_path.name.lower()

        purpose_map = {
            "test": "Testing infrastructure and test files",
            "tests": "Testing infrastructure and test files",
            "doc": "Documentation files",
            "docs": "Documentation files",
            "docs-organized": "Organized documentation library",
            "config": "Configuration files",
            "data": "Data storage and databases",
            "db": "Database files",
            "gui": "Graphical user interface components",
            "api": "API definitions and handlers",
            "core": "Core system components",
            "plugin": "Plugin system components",
            "plugins": "Plugin system components",
            "utils": "Utility functions and helpers",
            "tools": "Development and maintenance tools",
            "scripts": "Automation and utility scripts",
            "bridge": "Integration and bridge components",
            "bridges": "Integration and bridge components",
            "interface": "Interface definitions and implementations",
            "lyrixa": "Lyrixa AI assistant system",
            "aetherra": "Aetherra OS core components",
            "memory": "Memory management and storage",
            "runtime": "Runtime components and services",
            "stdlib": "Standard library components",
            "web": "Web interface and components",
        }

        return purpose_map.get(name, f"Directory containing {name} related files")

    def find_duplicates(self):
        """Find files with identical content"""
        duplicates = []
        for file_hash, file_paths in self.file_hashes.items():
            if len(file_paths) > 1:
                duplicates.append(
                    {"hash": file_hash, "files": file_paths, "count": len(file_paths)}
                )
        return sorted(duplicates, key=lambda x: x["count"], reverse=True)

    def analyze_project(self):
        """Run comprehensive project analysis"""
        print("🔍 Starting comprehensive Aetherra project analysis...")

        # Scan all directories
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common excludes
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
            ]

            current_dir = Path(root)
            analysis = self.scan_directory(current_dir)
            if analysis:
                self.directory_analysis[str(current_dir)] = analysis

        # Find duplicates
        self.duplicate_groups = self.find_duplicates()

        print("✅ Analysis complete!")
        print(f"   📁 Directories analyzed: {len(self.directory_analysis)}")
        print(
            f"   📄 Total files processed: {sum(len(self.file_hashes.get(h, [])) for h in self.file_hashes)}"
        )
        print(f"   🔄 Duplicate groups found: {len(self.duplicate_groups)}")

        return {
            "directories": self.directory_analysis,
            "duplicates": self.duplicate_groups,
            "summary": self.generate_summary(),
        }

    def generate_summary(self):
        """Generate project summary statistics"""
        total_files = 0
        file_categories = defaultdict(int)

        for dir_analysis in self.directory_analysis.values():
            total_files += dir_analysis["total_files"]
            for category, count in dir_analysis["file_counts"].items():
                file_categories[category] += count

        return {
            "total_files": total_files,
            "total_directories": len(self.directory_analysis),
            "file_categories": dict(file_categories),
            "duplicate_files": sum(d["count"] - 1 for d in self.duplicate_groups),
        }

    def save_analysis(self, output_file="project_analysis.json"):
        """Save analysis results to JSON file"""
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "directories": self.directory_analysis,
            "duplicates": self.duplicate_groups,
            "summary": self.generate_summary(),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Analysis saved to {output_file}")


if __name__ == "__main__":
    # Run analysis on current directory
    analyzer = AetherraProjectAnalyzer(".")
    results = analyzer.analyze_project()
    analyzer.save_analysis("aetherra_project_analysis.json")

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Project Deep Analysis Tool
Comprehensive file analysis, duplicate detection, and documentation generator
"""

from __future__ import annotations

# Standard library imports
import ast
import hashlib
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from Aetherra.maintenance import require_allowed_report_destination


@dataclass(frozen=True)
class ProjectAnalysisWritePlan:
    file_path: Path
    data: dict


def _hash_value(value) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "maintenance" and capability in {
        "maintenance:cleanup",
        "fs:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _safe_relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def _guardian_preflight_analysis_write(
    *,
    project_root: Path,
    plan: ProjectAnalysisWritePlan,
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    summary = plan.data.get("summary", {})
    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.project_analysis_write",
            target="maintenance:project_analysis",
            purpose="Write generated project analysis JSON",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Planned project analysis JSON is written to disk",
            reversible=False,
            rollback_plan="delete generated analysis JSON or restore from version control",
            metadata={
                "project_root_hash": _hash_value(project_root.resolve()),
                "output_path_hash": _hash_value(
                    _safe_relative_path(plan.file_path, project_root)
                ),
                "directory_count": len(plan.data.get("directories", {})),
                "duplicate_group_count": len(plan.data.get("duplicates", [])),
                "total_files": summary.get("total_files", 0),
                "analysis_size_bytes": len(
                    json.dumps(plan.data, ensure_ascii=False, default=str)
                ),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


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
        except (OSError, PermissionError):
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
                    elif isinstance(node, ast.ImportFrom) and node.module:
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

        except (OSError, UnicodeDecodeError):
            return {"error": "Could not read file"}

    def categorize_file(self, filepath):
        """Categorize file by type and purpose"""
        name = filepath.name.lower()

        # File type categories
        if name.endswith((".py",)):
            if "test" in name:
                return "test"
            if "demo" in name:
                return "demo"
            if "launcher" in name:
                return "launcher"
            if name.startswith("__"):
                return "python_special"
            return "python_module"
        if name.endswith((".md",)):
            return "documentation"
        if name.endswith((".json",)):
            return "configuration"
        if name.endswith((".db",)):
            return "database"
        if name.endswith((".log",)):
            return "log"
        if name.endswith((".yml", ".yaml")):
            return "configuration"
        if name.endswith((".txt",)):
            return "text"
        return "other"

    def scan_directory(self, directory):
        """Scan a directory and analyze all files"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return None

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
        for root, dirs, _files in os.walk(self.project_root):
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

    def plan_analysis_write(
        self,
        output_file="artifacts/maintenance/aetherra_project_analysis.json",
    ):
        """Build a side-effect-free JSON write plan for analysis results."""
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = self.project_root / output_path

        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "directories": self.directory_analysis,
            "duplicates": self.duplicate_groups,
            "summary": self.generate_summary(),
        }
        return ProjectAnalysisWritePlan(file_path=output_path, data=analysis_data)

    def save_analysis(
        self,
        output_file="artifacts/maintenance/aetherra_project_analysis.json",
        *,
        plan=None,
    ):
        """Save analysis results to JSON file after Guardian approval."""
        write_plan = plan or self.plan_analysis_write(output_file)
        try:
            require_allowed_report_destination(write_plan.file_path, self.project_root)
        except ValueError as exc:
            print(f"Maintenance report path blocked: {exc}")
            return False

        decision = _guardian_preflight_analysis_write(
            project_root=self.project_root,
            plan=write_plan,
        )
        if not decision.allowed:
            print(f"Guardian denied project analysis write: {decision.reason}")
            return False

        write_plan.file_path.parent.mkdir(parents=True, exist_ok=True)
        write_plan.file_path.write_text(
            json.dumps(write_plan.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Analysis saved to {write_plan.file_path}")
        return True



if __name__ == "__main__":
    # Run analysis on current directory
    analyzer = AetherraProjectAnalyzer(".")
    analyzer.analyze_project()
    raise SystemExit(
        0 if analyzer.save_analysis() else 1
    )

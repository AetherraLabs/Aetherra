#!/usr/bin/env python3
"""
Comprehensive aetherra Workspace Analysis
Analyzes project structure, imports, dependencies, and configuration
"""

import ast
import importlib.util
import json
import os
import sys
from pathlib import Path


class WorkspaceAnalyzer:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.issues = []
        self.recommendations = []
        self.structure_analysis = {}
        self.import_analysis = {}
        self.dependency_analysis = {}

    def analyze_project_structure(self):
        """Analyze the overall project structure"""
        print("🔍 Analyzing project structure...")

        expected_dirs = {
            "core": "Core interpreter and runtime modules",
            "plugins": "Plugin system and extensions",
            "stdlib": "Standard library modules",
            "ui": "User interface components",
            ".vscode": "VS Code workspace configuration",
            "venv": "Python virtual environment (optional)",
        }

        expected_files = {
            "pyproject.toml": "Project configuration",
            "requirements.txt": "Python dependencies",
            "README.md": "Project documentation",
            ".gitignore": "Git ignore rules (optional)",
        }

        # Check directory structure
        for dir_name, description in expected_dirs.items():
            dir_path = self.workspace_path / dir_name
            if dir_path.exists():
                self.structure_analysis[dir_name] = {
                    "status": "found",
                    "description": description,
                    "files": list(f.name for f in dir_path.iterdir() if f.is_file()),
                }
            else:
                self.structure_analysis[dir_name] = {
                    "status": "missing",
                    "description": description,
                }
                if dir_name != "venv":  # venv is optional
                    self.issues.append(f"Missing directory: {dir_name}")

        # Check important files
        for file_name, description in expected_files.items():
            file_path = self.workspace_path / file_name
            if file_path.exists():
                self.structure_analysis[file_name] = {
                    "status": "found",
                    "description": description,
                    "size": file_path.stat().st_size,
                }
            else:
                self.structure_analysis[file_name] = {
                    "status": "missing",
                    "description": description,
                }
                if file_name != ".gitignore":  # .gitignore is optional
                    self.issues.append(f"Missing file: {file_name}")

    def analyze_python_imports(self):
        """Analyze Python imports across the project"""
        print("[DISC] Analyzing Python imports...")

        python_files = []
        for root, dirs, files in os.walk(self.workspace_path):
            # Skip venv and other irrelevant directories
            dirs[:] = [
                d for d in dirs if d not in {".git", "__pycache__", "venv", ".venv"}
            ]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        import_issues = []
        imports_found = set()

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST to find imports
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports_found.add(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            module = node.module or ""
                            for alias in node.names:
                                full_import = (
                                    f"{module}.{alias.name}" if module else alias.name
                                )
                                imports_found.add(full_import)
                except SyntaxError as e:
                    import_issues.append(
                        f"Syntax error in {py_file.relative_to(self.workspace_path)}: {e}"
                    )

            except Exception as e:
                import_issues.append(
                    f"Error reading {py_file.relative_to(self.workspace_path)}: {e}"
                )

        self.import_analysis = {
            "total_python_files": len(python_files),
            "unique_imports": sorted(list(imports_found)),
            "import_issues": import_issues,
        }

        self.issues.extend(import_issues)

    def analyze_dependencies(self):
        """Analyze project dependencies"""
        print("🔗 Analyzing dependencies...")

        # Check pyproject.toml
        pyproject_path = self.workspace_path / "pyproject.toml"
        requirements_path = self.workspace_path / "requirements.txt"

        pyproject_deps = []
        requirements_deps = []

        if pyproject_path.exists():
            try:
                import tomllib

                with open(pyproject_path, "rb") as f:
                    pyproject_data = tomllib.load(f)

                # Extract dependencies
                if (
                    "project" in pyproject_data
                    and "dependencies" in pyproject_data["project"]
                ):
                    pyproject_deps = pyproject_data["project"]["dependencies"]
                elif "tool" in pyproject_data and "poetry" in pyproject_data["tool"]:
                    poetry_deps = pyproject_data["tool"]["poetry"].get(
                        "dependencies", {}
                    )
                    pyproject_deps = [
                        f"{k}=={v}" if v != "*" else k
                        for k, v in poetry_deps.items()
                        if k != "python"
                    ]

            except Exception as e:
                self.issues.append(f"Error reading pyproject.toml: {e}")

        if requirements_path.exists():
            try:
                with open(requirements_path) as f:
                    requirements_deps = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
            except Exception as e:
                self.issues.append(f"Error reading requirements.txt: {e}")

        self.dependency_analysis = {
            "pyproject_dependencies": pyproject_deps,
            "requirements_dependencies": requirements_deps,
            "dependency_files_exist": {
                "pyproject.toml": pyproject_path.exists(),
                "requirements.txt": requirements_path.exists(),
            },
        }

    def check_vscode_configuration(self):
        """Check VS Code configuration"""
        print("⚙️ Analyzing VS Code configuration...")

        vscode_dir = self.workspace_path / ".vscode"
        if not vscode_dir.exists():
            self.issues.append("Missing .vscode directory")
            return

        important_files = {
            "settings.json": "Workspace settings",
            "extensions.json": "Recommended extensions",
            "launch.json": "Debug configurations (optional)",
            "tasks.json": "Build tasks (optional)",
        }

        vscode_analysis = {}
        for file_name, description in important_files.items():
            file_path = vscode_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = json.load(f)
                    vscode_analysis[file_name] = {
                        "status": "found",
                        "valid_json": True,
                        "content_keys": list(content.keys())
                        if isinstance(content, dict)
                        else [],
                    }
                except json.JSONDecodeError as e:
                    vscode_analysis[file_name] = {
                        "status": "found",
                        "valid_json": False,
                        "error": str(e),
                    }
                    self.issues.append(f"Invalid JSON in {file_name}: {e}")
            else:
                vscode_analysis[file_name] = {"status": "missing"}
                if file_name in ["settings.json"]:  # Only settings.json is critical
                    self.issues.append(f"Missing critical VS Code file: {file_name}")

        self.structure_analysis["vscode_config"] = vscode_analysis

    def check_module_integrity(self):
        """Check if all modules can be imported"""
        print("🔬 Testing module imports...")

        core_modules = [
            "core.interpreter",
            "core.memory",
            "core.functions",
            "core.agent",
            "core.debug_system",
        ]

        import_results = {}

        # Add workspace to Python path temporarily
        sys.path.insert(0, str(self.workspace_path))

        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
                import_results[module_name] = {"status": "success"}
            except ImportError as e:
                import_results[module_name] = {"status": "failed", "error": str(e)}
                self.issues.append(f"Cannot import {module_name}: {e}")
            except Exception as e:
                import_results[module_name] = {"status": "error", "error": str(e)}
                self.issues.append(f"Error importing {module_name}: {e}")

        # Remove workspace from Python path
        sys.path.remove(str(self.workspace_path))

        self.import_analysis["module_integrity"] = import_results

    def generate_recommendations(self):
        """Generate recommendations for improvements"""
        print("💡 Generating recommendations...")

        # Structure recommendations
        if (
            "venv" not in self.structure_analysis
            or self.structure_analysis["venv"]["status"] == "missing"
        ):
            self.recommendations.append(
                "Consider creating a virtual environment: python -m venv venv"
            )

        # Import recommendations
        if self.import_analysis.get("import_issues"):
            self.recommendations.append("Fix import issues to ensure code reliability")

        # Configuration recommendations
        if (
            ".gitignore" not in self.structure_analysis
            or self.structure_analysis[".gitignore"]["status"] == "missing"
        ):
            self.recommendations.append(
                "Add .gitignore file to exclude unnecessary files from version control"
            )

        # VS Code recommendations
        vscode_config = self.structure_analysis.get("vscode_config", {})
        if (
            "extensions.json" not in vscode_config
            or vscode_config["extensions.json"]["status"] == "missing"
        ):
            self.recommendations.append(
                "Add extensions.json to recommend essential VS Code extensions"
            )

        # Performance recommendations
        self.recommendations.extend(
            [
                "Consider using pre-commit hooks for code quality",
                "Set up automated testing with pytest",
                "Configure GitHub Actions for CI/CD",
                "Add type hints throughout the codebase for better IDE support",
            ]
        )

    def run_analysis(self):
        """Run complete workspace analysis"""
        print("🚀 Starting comprehensive workspace analysis...\n")

        self.analyze_project_structure()
        self.analyze_python_imports()
        self.analyze_dependencies()
        self.check_vscode_configuration()
        self.check_module_integrity()
        self.generate_recommendations()

        return {
            "structure": self.structure_analysis,
            "imports": self.import_analysis,
            "dependencies": self.dependency_analysis,
            "issues": self.issues,
            "recommendations": self.recommendations,
        }


def main():
    workspace_path = os.getcwd()
    analyzer = WorkspaceAnalyzer(workspace_path)
    results = analyzer.run_analysis()

    print("\n" + "=" * 60)
    print("📊 WORKSPACE ANALYSIS RESULTS")
    print("=" * 60)

    # Summary
    print(f"\n📁 Project: {Path(workspace_path).name}")
    print(f"📍 Location: {workspace_path}")

    # Issues
    if results["issues"]:
        print(f"\n[ERROR] ISSUES FOUND ({len(results['issues'])}):")
        for i, issue in enumerate(results["issues"], 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")

    # Structure summary
    print("\n📂 STRUCTURE SUMMARY:")
    structure = results["structure"]
    for item, info in structure.items():
        if isinstance(info, dict) and "status" in info:
            status_icon = "✅" if info["status"] == "found" else "[ERROR]"
            print(f"  {status_icon} {item}: {info['status']}")

    # Import summary
    print("\n[DISC] IMPORT SUMMARY:")
    imports = results["imports"]
    print(f"  • Python files: {imports.get('total_python_files', 0)}")
    print(f"  • Unique imports: {len(imports.get('unique_imports', []))}")

    if imports.get("module_integrity"):
        print("  • Core module tests:")
        for module, result in imports["module_integrity"].items():
            status_icon = "✅" if result["status"] == "success" else "[ERROR]"
            print(f"    {status_icon} {module}")

    # Recommendations
    if results["recommendations"]:
        print(f"\n💡 RECOMMENDATIONS ({len(results['recommendations'])}):")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")

    # Save detailed results
    results_file = Path(workspace_path) / "WORKSPACE_ANALYSIS_COMPLETE.md"
    with open(results_file, "w") as f:
        f.write("# aetherra Workspace Analysis Report\n\n")
        f.write(
            f"**Analysis Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        # Write detailed results
        f.write("## Issues Found\n\n")
        if results["issues"]:
            for i, issue in enumerate(results["issues"], 1):
                f.write(f"{i}. {issue}\n")
        else:
            f.write("✅ No critical issues found.\n")

        f.write("\n## Structure Analysis\n\n")
        for item, info in structure.items():
            if isinstance(info, dict):
                f.write(f"### {item}\n")
                f.write(f"- Status: {info.get('status', 'unknown')}\n")
                if "description" in info:
                    f.write(f"- Description: {info['description']}\n")
                f.write("\n")

        f.write("## Recommendations\n\n")
        for i, rec in enumerate(results["recommendations"], 1):
            f.write(f"{i}. {rec}\n")

    print(f"\n📄 Detailed report saved to: {results_file}")

    # Exit with appropriate code
    exit_code = 1 if results["issues"] else 0
    print(f"\n🎯 Analysis complete. Exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    main()

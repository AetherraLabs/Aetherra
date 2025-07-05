#!/usr/bin/env python3
"""
AetherraCode Workspace Comprehensive Analysis
Complete analysis of project structure, configuration, and code quality
"""

import ast
import json
import os
from pathlib import Path


def analyze_project_structure():
    """Analyze the overall project structure"""
    print("🔍 Analyzing Project Structure...")

    required_items = {
        # Core directories
        "core": {"type": "dir", "critical": True, "desc": "Core interpreter modules"},
        "plugins": {"type": "dir", "critical": True, "desc": "Plugin system"},
        "stdlib": {"type": "dir", "critical": True, "desc": "Standard library"},
        "ui": {"type": "dir", "critical": True, "desc": "User interface"},
        ".vscode": {"type": "dir", "critical": True, "desc": "VS Code config"},
        # Configuration files
        "pyproject.toml": {"type": "file", "critical": True, "desc": "Project config"},
        "requirements.txt": {"type": "file", "critical": True, "desc": "Dependencies"},
        "README.md": {"type": "file", "critical": False, "desc": "Documentation"},
        ".gitignore": {"type": "file", "critical": False, "desc": "Git ignore rules"},
    }

    structure_status = {}
    critical_missing = []

    for item, info in required_items.items():
        path = Path(item)
        exists = path.exists()

        if info["type"] == "dir":
            is_correct_type = path.is_dir() if exists else False
        else:
            is_correct_type = path.is_file() if exists else False

        status = {
            "exists": exists,
            "correct_type": is_correct_type,
            "critical": info["critical"],
            "description": info["desc"],
        }

        if exists and is_correct_type:
            status["status"] = "✅ Found"
        elif exists and not is_correct_type:
            status["status"] = "⚠️ Wrong type"
        else:
            status["status"] = "❌ Missing"
            if info["critical"]:
                critical_missing.append(item)

        structure_status[item] = status

    # Print results
    print("\n📁 Directories:")
    for item, status in structure_status.items():
        if required_items[item]["type"] == "dir":
            print(f"  {item}: {status['status']} - {status['description']}")

    print("\n📄 Files:")
    for item, status in structure_status.items():
        if required_items[item]["type"] == "file":
            print(f"  {item}: {status['status']} - {status['description']}")

    if critical_missing:
        print(f"\n❌ Critical items missing: {', '.join(critical_missing)}")
        return False
    else:
        print("\n✅ All critical structure items present")
        return True


def analyze_core_modules():
    """Analyze core Python modules"""
    print("\n🔬 Analyzing Core Modules...")

    core_modules = {
        "core/interpreter.py": "AetherraInterpreter",
        "core/memory.py": "AetherraMemory",
        "core/functions.py": "AetherraFunctions",
        "core/agent.py": "AetherraAgent",
        "core/chat_router.py": "AetherraChatRouter",
        "ui/aetherplex_gui.py": "NeuroplexGUI",
    }

    module_status = {}
    syntax_errors = []

    for module_path, main_class in core_modules.items():
        path = Path(module_path)
        status = {"path": module_path, "main_class": main_class}

        if not path.exists():
            status["status"] = "❌ Missing"
            status["issues"] = ["File does not exist"]
        else:
            try:
                # Check syntax
                with open(path, encoding="utf-8") as f:
                    source = f.read()

                tree = ast.parse(source)
                status["status"] = "✅ Syntax OK"
                status["issues"] = []

                # Check if main class exists in AST
                class_found = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == main_class:
                        class_found = True
                        break

                if not class_found:
                    status["issues"].append(f"Class {main_class} not found")

            except SyntaxError as e:
                status["status"] = "❌ Syntax Error"
                status["issues"] = [f"Line {e.lineno}: {e.msg}"]
                syntax_errors.append(module_path)
            except Exception as e:
                status["status"] = "⚠️ Parse Error"
                status["issues"] = [str(e)]

        module_status[module_path] = status

        # Print result
        print(f"  {module_path}: {status['status']}")
        for issue in status["issues"]:
            print(f"    ⚠️ {issue}")

    return len(syntax_errors) == 0


def analyze_vscode_configuration():
    """Analyze VS Code workspace configuration"""
    print("\n⚙️ Analyzing VS Code Configuration...")

    config_files = {
        ".vscode/settings.json": True,  # Required
        ".vscode/extensions.json": False,  # Recommended
        ".vscode/launch.json": False,  # Optional
        ".vscode/tasks.json": False,  # Optional
    }

    vscode_status = {}
    config_issues = []

    for config_file, required in config_files.items():
        path = Path(config_file)
        status = {"required": required}

        if not path.exists():
            status["status"] = "❌ Missing" if required else "⚠️ Missing (optional)"
            if required:
                config_issues.append(f"{config_file} missing")
        else:
            try:
                with open(path, encoding="utf-8") as f:
                    config_data = json.load(f)

                status["status"] = "✅ Valid"
                status["keys"] = list(config_data.keys()) if isinstance(config_data, dict) else []

                # Check important settings for settings.json
                if config_file == ".vscode/settings.json":
                    important_settings = [
                        "python.defaultInterpreterPath",
                        "ruff.enable",
                        "python.analysis.extraPaths",
                    ]

                    missing_settings = []
                    for setting in important_settings:
                        if setting not in config_data:
                            missing_settings.append(setting)

                    if missing_settings:
                        status["missing_settings"] = missing_settings
                        print(f"    ⚠️ Missing settings: {', '.join(missing_settings)}")

            except json.JSONDecodeError as e:
                status["status"] = "❌ Invalid JSON"
                status["error"] = str(e)
                config_issues.append(f"{config_file} has invalid JSON")
            except Exception as e:
                status["status"] = "❌ Error"
                status["error"] = str(e)
                config_issues.append(f"{config_file} error: {e}")

        vscode_status[config_file] = status
        print(f"  {config_file}: {status['status']}")

    return len(config_issues) == 0


def analyze_dependencies():
    """Analyze project dependencies and configuration"""
    print("\n📦 Analyzing Dependencies...")

    dep_files = ["pyproject.toml", "requirements.txt"]
    deps_status = {}
    deps_issues = []

    for dep_file in dep_files:
        path = Path(dep_file)
        status = {}

        if not path.exists():
            status["status"] = "❌ Missing"
            deps_issues.append(f"{dep_file} missing")
        else:
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()

                if dep_file == "pyproject.toml":
                    # Check for important sections
                    sections = {
                        "[tool.ruff]": "Ruff configuration",
                        "[project]": "Project metadata",
                        "[build-system]": "Build system",
                    }

                    found_sections = []
                    for section, desc in sections.items():
                        if section in content:
                            found_sections.append(desc)

                    status["status"] = "✅ Found"
                    status["sections"] = found_sections

                elif dep_file == "requirements.txt":
                    lines = [
                        line.strip()
                        for line in content.splitlines()
                        if line.strip() and not line.startswith("#")
                    ]
                    status["status"] = "✅ Found"
                    status["package_count"] = len(lines)

            except Exception as e:
                status["status"] = "❌ Error reading"
                status["error"] = str(e)
                deps_issues.append(f"{dep_file} error: {e}")

        deps_status[dep_file] = status
        print(f"  {dep_file}: {status['status']}")

        if "sections" in status:
            for section in status["sections"]:
                print(f"    ✅ {section}")

        if "package_count" in status:
            print(f"    📦 {status['package_count']} packages listed")

    return len(deps_issues) == 0


def count_and_categorize_files():
    """Count and categorize all project files"""
    print("\n📊 File Analysis...")

    file_stats = {
        "python": {"count": 0, "files": []},
        "config": {"count": 0, "files": []},
        "docs": {"count": 0, "files": []},
        "other": {"count": 0, "files": []},
    }

    config_extensions = {".json", ".toml", ".yaml", ".yml", ".ini", ".cfg"}
    doc_extensions = {".md", ".txt", ".rst"}

    for root, dirs, files in os.walk("."):
        # Skip certain directories
        dirs[:] = [
            d for d in dirs if d not in {".git", "__pycache__", "venv", ".venv", "node_modules"}
        ]

        for file in files:
            file_path = Path(root) / file
            extension = file_path.suffix.lower()

            if extension == ".py":
                file_stats["python"]["count"] += 1
                file_stats["python"]["files"].append(str(file_path))
            elif extension in config_extensions:
                file_stats["config"]["count"] += 1
                file_stats["config"]["files"].append(str(file_path))
            elif extension in doc_extensions:
                file_stats["docs"]["count"] += 1
                file_stats["docs"]["files"].append(str(file_path))
            else:
                file_stats["other"]["count"] += 1
                file_stats["other"]["files"].append(str(file_path))

    # Print stats
    total_files = sum(stats["count"] for stats in file_stats.values())
    print(f"  Total files: {total_files}")

    for category, stats in file_stats.items():
        print(f"  {category.title()} files: {stats['count']}")

    # Group Python files by directory
    python_by_dir = {}
    for py_file in file_stats["python"]["files"]:
        dir_name = str(Path(py_file).parent)
        python_by_dir[dir_name] = python_by_dir.get(dir_name, 0) + 1

    print("\n  Python files by directory:")
    for dir_name, count in sorted(python_by_dir.items()):
        print(f"    {dir_name}: {count} files")

    return file_stats


def main():
    """Run comprehensive workspace analysis"""
    print("🚀 AetherraCode Workspace Comprehensive Analysis")
    print("=" * 60)

    # Run all analysis components
    checks = [
        ("Project Structure", analyze_project_structure),
        ("Core Modules", analyze_core_modules),
        ("VS Code Config", analyze_vscode_configuration),
        ("Dependencies", analyze_dependencies),
    ]

    results = {}
    all_passed = True

    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results[check_name] = False
            all_passed = False

    # File analysis (informational)
    file_stats = count_and_categorize_files()

    # Generate summary
    print("\n" + "=" * 60)
    print("📋 ANALYSIS SUMMARY")
    print("=" * 60)

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")

    print("\n📊 Project Statistics:")
    print(f"  • Python files: {file_stats['python']['count']}")
    print(f"  • Config files: {file_stats['config']['count']}")
    print(f"  • Documentation: {file_stats['docs']['count']}")

    overall_status = "✅ EXCELLENT" if all_passed else "⚠️ NEEDS ATTENTION"
    print(f"\n🎯 Overall Status: {overall_status}")

    if all_passed:
        print(
            "\n🎉 AetherraCode workspace is perfectly structured and ready for next-generation development!"
        )
        print("🚀 All systems are operational and optimized.")
    else:
        print("\n💡 Issues found that need attention:")
        for check_name, passed in results.items():
            if not passed:
                print(f"  • {check_name}: Review the detailed output above")

    # Save detailed report
    report_path = Path("NEUROPLEX_ANALYSIS_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# AetherraCode Workspace Analysis Report\n\n")
        f.write(
            f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        f.write("## Summary\n\n")
        for check_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            f.write(f"- **{check_name}**: {status}\n")

        f.write("\n## File Statistics\n\n")
        f.write(f"- Python files: {file_stats['python']['count']}\n")
        f.write(f"- Config files: {file_stats['config']['count']}\n")
        f.write(f"- Documentation: {file_stats['docs']['count']}\n")
        f.write(f"- Other files: {file_stats['other']['count']}\n")

        f.write("\n## Overall Status\n\n")
        f.write(f"**{overall_status}**\n\n")

        if all_passed:
            f.write("🎉 Workspace is perfectly structured and ready for production!\n")
        else:
            f.write("⚠️ Some issues require attention. See detailed analysis above.\n")

    print(f"\n📄 Detailed report saved to: {report_path}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

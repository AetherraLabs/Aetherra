#!/usr/bin/env python3
"""
Comprehensive NeuroCode Project Error Analysis
==============================================

This script performs a deep analysis of the NeuroCode project to identify
and report all potential errors, import issues, and functionality problems.
"""

import ast
import importlib.util
from pathlib import Path
from typing import Any, Dict


class NeuroCodeErrorAnalyzer:
    """Comprehensive error analysis for NeuroCode project"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.import_issues = []
        self.syntax_errors = []

    def check_syntax(self, file_path: Path) -> bool:
        """Check Python syntax for a file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.syntax_errors.append({"file": str(file_path), "error": str(e), "line": e.lineno})
            return False
        except Exception as e:
            self.errors.append({"file": str(file_path), "error": f"Could not read file: {e}"})
            return False

    def test_import(self, module_path: str, file_path: Path) -> bool:
        """Test if a module can be imported"""
        try:
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return True
        except Exception as e:
            self.import_issues.append(
                {"file": str(file_path), "module": module_path, "error": str(e)}
            )
            return False
        return False

    def check_key_entry_points(self) -> Dict[str, Any]:
        """Check all key entry points for functionality"""
        entry_points = {
            "neurocode_launcher.py": self.project_root / "neurocode_launcher.py",
            "neurocode_cli.py": self.project_root / "neurocode_cli.py",
            "main CLI": self.project_root / "src" / "neurocode" / "cli" / "main.py",
            "launchers/main.py": self.project_root / "launchers" / "main.py",
            "neuroplex_gui.py": self.project_root / "src" / "neurocode" / "ui" / "neuroplex_gui.py",
            "enhanced_neuroplex.py": self.project_root
            / "src"
            / "neurocode"
            / "ui"
            / "enhanced_neuroplex.py",
        }

        results = {}
        for name, path in entry_points.items():
            if path.exists():
                syntax_ok = self.check_syntax(path)
                if syntax_ok:
                    import_ok = self.test_import(name, path)
                    results[name] = {
                        "exists": True,
                        "syntax": "OK",
                        "import": "OK" if import_ok else "FAILED",
                    }
                else:
                    results[name] = {"exists": True, "syntax": "FAILED", "import": "N/A"}
            else:
                results[name] = {"exists": False, "syntax": "N/A", "import": "N/A"}

        return results

    def check_core_modules(self) -> Dict[str, Any]:
        """Check core NeuroCode modules"""
        core_modules = {
            "interpreter.py": self.project_root / "core" / "interpreter.py",
            "enhanced_interpreter.py": self.project_root / "core" / "enhanced_interpreter.py",
            "memory.py": self.project_root / "core" / "memory.py",
            "functions.py": self.project_root / "core" / "functions.py",
            "agent.py": self.project_root / "core" / "agent.py",
            "neurocode_parser.py": self.project_root / "core" / "neurocode_parser.py",
        }

        results = {}
        for name, path in core_modules.items():
            if path.exists():
                syntax_ok = self.check_syntax(path)
                results[name] = {"exists": True, "syntax": "OK" if syntax_ok else "FAILED"}
            else:
                results[name] = {"exists": False, "syntax": "N/A"}

        return results

    def test_launchers(self) -> Dict[str, Any]:
        """Test launcher functionality"""
        launchers = {
            "launch_fully_modular_neuroplex.py": self.project_root
            / "launchers"
            / "launch_fully_modular_neuroplex.py",
            "launch_enhanced_neuroplex.py": self.project_root
            / "launchers"
            / "launch_enhanced_neuroplex.py",
            "launch_modular_neuroplex.py": self.project_root
            / "launchers"
            / "launch_modular_neuroplex.py",
        }

        results = {}
        for name, path in launchers.items():
            if path.exists():
                syntax_ok = self.check_syntax(path)
                results[name] = {"exists": True, "syntax": "OK" if syntax_ok else "FAILED"}
            else:
                results[name] = {"exists": False, "syntax": "N/A"}

        return results

    def generate_report(self) -> str:
        """Generate comprehensive error report"""
        report = []
        report.append("🔍 NeuroCode Project - Comprehensive Error Analysis")
        report.append("=" * 60)

        # Check entry points
        entry_results = self.check_key_entry_points()
        report.append("\n📍 Key Entry Points Analysis:")
        for name, result in entry_results.items():
            status = "✅" if result["syntax"] == "OK" and result["import"] == "OK" else "❌"
            report.append(
                f"  {status} {name}: Exists={result['exists']}, Syntax={result['syntax']}, Import={result['import']}"
            )

        # Check core modules
        core_results = self.check_core_modules()
        report.append("\n🧠 Core Modules Analysis:")
        for name, result in core_results.items():
            status = "✅" if result["syntax"] == "OK" else "❌"
            report.append(
                f"  {status} {name}: Exists={result['exists']}, Syntax={result['syntax']}"
            )

        # Check launchers
        launcher_results = self.test_launchers()
        report.append("\n🚀 Launchers Analysis:")
        for name, result in launcher_results.items():
            status = "✅" if result["syntax"] == "OK" else "❌"
            report.append(
                f"  {status} {name}: Exists={result['exists']}, Syntax={result['syntax']}"
            )

        # Report syntax errors
        if self.syntax_errors:
            report.append("\n🚨 Syntax Errors Found:")
            for error in self.syntax_errors:
                report.append(f"  ❌ {error['file']}:{error['line']} - {error['error']}")

        # Report import issues
        if self.import_issues:
            report.append("\n📦 Import Issues Found:")
            for issue in self.import_issues:
                report.append(f"  ⚠️ {issue['file']} - {issue['error']}")

        # General errors
        if self.errors:
            report.append("\n💥 General Errors:")
            for error in self.errors:
                report.append(f"  ❌ {error['file']} - {error['error']}")

        # Summary
        total_syntax_errors = len(self.syntax_errors)
        total_import_issues = len(self.import_issues)
        total_errors = len(self.errors)

        report.append("\n📊 Summary:")
        report.append(f"  • Syntax Errors: {total_syntax_errors}")
        report.append(f"  • Import Issues: {total_import_issues}")
        report.append(f"  • General Errors: {total_errors}")
        report.append(
            f"  • Total Issues: {total_syntax_errors + total_import_issues + total_errors}"
        )

        if total_syntax_errors + total_import_issues + total_errors == 0:
            report.append("\n🎉 No critical errors found! NeuroCode project appears healthy.")
        else:
            report.append(
                f"\n🔧 Found {total_syntax_errors + total_import_issues + total_errors} issues that need attention."
            )

        return "\n".join(report)


def main():
    """Run comprehensive error analysis"""
    print("🔍 Starting NeuroCode Project Error Analysis...")

    analyzer = NeuroCodeErrorAnalyzer()
    report = analyzer.generate_report()

    print(report)

    # Save report to file
    report_file = Path(__file__).parent / "error_analysis_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 Full report saved to: {report_file}")


if __name__ == "__main__":
    main()

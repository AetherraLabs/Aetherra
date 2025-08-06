#!/usr/bin/env python3
"""
🎯 AETHERRA ARCHITECTURAL COMPLIANCE CHECKER
Simple, focused validation of critical architectural patterns

Version: 1.0
Date: August 5, 2025
Purpose: Ensure Aetherra OS and Lyrixa maintain proper separation
"""

import os
import re
from pathlib import Path
from typing import Dict, List


class ArchitecturalChecker:
    """Simple checker for critical architectural compliance"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.aetherra_root = self.project_root / "Aetherra"
        self.lyrixa_root = self.aetherra_root / "lyrixa"

    def check_critical_violations(self) -> Dict[str, List[str]]:
        """Check for critical architectural violations"""
        violations = {
            "core_imports_interface": [],
            "gui_in_core": [],
            "engines_in_interface": [],
            "duplicates": [],
        }

        print("🔍 Checking critical architectural patterns...")

        # Check all Python files
        for py_file in self.aetherra_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Check for critical violations
                self._check_import_violations(py_file, content, violations)
                self._check_misplaced_components(py_file, content, violations)

            except Exception as e:
                print(f"⚠️  Could not read {py_file}: {e}")

        # Check for duplicate consciousness dashboards
        self._check_duplicate_dashboards(violations)

        return violations

    def _check_import_violations(self, file_path: Path, content: str, violations: Dict):
        """Check for improper import patterns"""
        is_in_lyrixa = self.lyrixa_root in file_path.parents

        # Aetherra core should NOT import from Lyrixa
        if not is_in_lyrixa and "from lyrixa" in content:
            violations["core_imports_interface"].append(str(file_path))

    def _check_misplaced_components(
        self, file_path: Path, content: str, violations: Dict
    ):
        """Check for components in wrong directories"""
        is_in_lyrixa = self.lyrixa_root in file_path.parents
        filename = file_path.name.lower()

        # Critical GUI components should be in Lyrixa
        gui_patterns = [
            r"class.*Window\(",
            r"class.*Panel\(",
            r"class.*Dashboard\(",
            r"from PySide6",
            r"from PyQt5",
            r"QWidget",
            r"QMainWindow",
        ]

        has_gui = any(re.search(pattern, content) for pattern in gui_patterns)

        if has_gui and not is_in_lyrixa and "gui" not in str(file_path):
            violations["gui_in_core"].append(str(file_path))

        # Core engines should NOT be in Lyrixa
        engine_patterns = [
            r"class.*Engine\(",
            r"class.*Core\(",
            r"class.*Brain\(",
            r"consciousness.*engine",
            r"quantum.*engine",
        ]

        has_engine = any(
            re.search(pattern, content, re.IGNORECASE) for pattern in engine_patterns
        )

        if has_engine and is_in_lyrixa:
            violations["engines_in_interface"].append(str(file_path))

    def _check_duplicate_dashboards(self, violations: Dict):
        """Check for duplicate consciousness dashboard files"""
        dashboard_files = [
            "evolution_monitoring_system.py",
            "quantum_temporal_interface.py",
            "meta_learning_control_panel.py",
        ]

        for dashboard in dashboard_files:
            gui_path = self.lyrixa_root / "gui" / dashboard
            consciousness_path = self.lyrixa_root / "gui" / "consciousness" / dashboard

            if gui_path.exists() and consciousness_path.exists():
                violations["duplicates"].append(f"Duplicate: {dashboard}")

    def generate_simple_report(self, violations: Dict) -> str:
        """Generate simple, actionable report"""
        report = []
        report.append("# 🎯 AETHERRA ARCHITECTURAL COMPLIANCE REPORT")
        report.append(
            f"**Generated**: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}"
        )
        report.append("")

        total_issues = sum(len(v) for v in violations.values())

        if total_issues == 0:
            report.append("✅ **STATUS**: ARCHITECTURE COMPLIANT")
            report.append("🎉 No critical architectural violations detected!")
            return "\n".join(report)

        report.append(f"❌ **STATUS**: {total_issues} CRITICAL VIOLATIONS DETECTED")
        report.append("")

        # Core imports interface violation
        if violations["core_imports_interface"]:
            report.append("## 🚨 CRITICAL: Core AI Imports Interface")
            report.append(
                "**Issue**: Aetherra core files importing from Lyrixa violates architecture"
            )
            report.append(
                "**Impact**: Creates circular dependencies and breaks separation"
            )
            report.append("")
            for file_path in violations["core_imports_interface"]:
                report.append(f"- ❌ `{file_path}`")
            report.append("")
            report.append("**Fix**: Remove all Lyrixa imports from core Aetherra files")
            report.append("")

        # GUI in core violation
        if violations["gui_in_core"]:
            report.append("## 🚨 CRITICAL: GUI Components in Core")
            report.append(
                "**Issue**: User interface components found in Aetherra core directories"
            )
            report.append("**Impact**: Mixes interface with core AI logic")
            report.append("")
            for file_path in violations["gui_in_core"]:
                report.append(f"- ❌ `{file_path}`")
            report.append("")
            report.append("**Fix**: Move GUI components to `Aetherra/lyrixa/gui/`")
            report.append("")

        # Engines in interface violation
        if violations["engines_in_interface"]:
            report.append("## 🚨 CRITICAL: Core Engines in Interface")
            report.append(
                "**Issue**: Core AI engines found in Lyrixa interface directories"
            )
            report.append("**Impact**: Core intelligence mixed with interface")
            report.append("")
            for file_path in violations["engines_in_interface"]:
                report.append(f"- ❌ `{file_path}`")
            report.append("")
            report.append(
                "**Fix**: Move core engines to appropriate Aetherra core directories"
            )
            report.append("")

        # Duplicate files
        if violations["duplicates"]:
            report.append("## 🚨 CRITICAL: Duplicate Files")
            report.append("**Issue**: Duplicate consciousness dashboard files detected")
            report.append("**Impact**: Confusion about which version is current")
            report.append("")
            for duplicate in violations["duplicates"]:
                report.append(f"- ❌ {duplicate}")
            report.append("")
            report.append(
                "**Fix**: Remove duplicate files, keep latest versions in `lyrixa/gui/`"
            )
            report.append("")

        # Quick fix guide
        report.append("## 🔧 QUICK FIX GUIDE")
        report.append("")
        report.append("### 🧠 **AETHERRA OS** (The Brain)")
        report.append(
            "- Contains: Consciousness engines, decision systems, learning algorithms"
        )
        report.append("- Location: `Aetherra/` (excluding `lyrixa/` subdirectory)")
        report.append("- Rule: Never imports from Lyrixa")
        report.append("")
        report.append("### 🎭 **LYRIXA** (The Interface)")
        report.append("- Contains: GUI components, dashboards, user interaction")
        report.append("- Location: `Aetherra/lyrixa/`")
        report.append("- Rule: Can import from Aetherra, provides interface to core AI")
        report.append("")

        return "\n".join(report)


def main():
    """Main function"""
    print("🎯 AETHERRA ARCHITECTURAL COMPLIANCE CHECKER")
    print("=" * 50)

    # Get project root
    project_root = os.getcwd()

    # Create checker
    checker = ArchitecturalChecker(project_root)

    # Check violations
    violations = checker.check_critical_violations()

    # Generate report
    report = checker.generate_simple_report(violations)

    # Save report
    report_path = Path(project_root) / "ARCHITECTURAL_COMPLIANCE_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📄 Report saved to: {report_path}")

    # Print summary
    total_issues = sum(len(v) for v in violations.values())
    if total_issues == 0:
        print("✅ Architecture compliance check PASSED!")
    else:
        print(f"❌ Found {total_issues} critical architectural violations")
        print("🔧 See report for detailed fixes")


if __name__ == "__main__":
    main()

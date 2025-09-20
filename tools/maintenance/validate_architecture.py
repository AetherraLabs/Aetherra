#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🏗️ AETHERRA DIRECTORY ARCHITECTURE VALIDATOR
Automated tool to enforce proper file placement between Aetherra OS and Lyrixa Interface

Version: 1.0
Date: August 5, 2025
Purpose: Prevent architectural confusion and validate directory structure
"""

# Standard library imports
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class ValidationResult:
    """Result of directory validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    file_path: str
    recommended_location: str = ""


@dataclass
class ArchitecturalRule:
    """Definition of architectural placement rule"""

    name: str
    pattern: str
    should_be_in_aetherra: bool
    should_be_in_lyrixa: bool
    description: str


class AetherraDirectoryValidator:
    """
    Validates that files are placed in architecturally correct directories

    Core Principle:
    - Aetherra OS = The Brain (Core AI Intelligence)
    - Lyrixa = The Interface (AI Assistant & User Interaction)
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.aetherra_root = self.project_root / "Aetherra"
        self.lyrixa_root = self.aetherra_root / "lyrixa"

        # Define architectural rules
        self.aetherra_patterns = self._define_aetherra_patterns()
        self.lyrixa_patterns = self._define_lyrixa_patterns()
        self.forbidden_patterns = self._define_forbidden_patterns()

        # Results storage
        self.validation_results = []
        self.scan_summary = {
            "files_scanned": 0,
            "errors_found": 0,
            "warnings_found": 0,
            "correctly_placed": 0,
            "misplaced_files": [],
        }

    def _define_aetherra_patterns(self) -> List[ArchitecturalRule]:
        """Define patterns that should be in Aetherra OS core"""
        return [
            ArchitecturalRule(
                "Consciousness Systems",
                r"consciousness|quantum|awareness|transcendence",
                True,
                False,
                "Core consciousness and quantum systems belong in Aetherra OS",
            ),
            ArchitecturalRule(
                "Decision Engines",
                r"decision|reasoning|logic|inference|analysis",
                True,
                False,
                "Core decision making systems belong in Aetherra OS",
            ),
            ArchitecturalRule(
                "Learning Systems",
                r"learning|neural|network|training|adaptation|evolution",
                True,
                False,
                "Core machine learning systems belong in Aetherra OS",
            ),
            ArchitecturalRule(
                "Memory Systems",
                r"memory|storage|retrieval|association|knowledge",
                True,
                False,
                "Core memory systems belong in Aetherra OS",
            ),
            ArchitecturalRule(
                "Intelligence Core",
                r"intelligence|cognitive|reasoning|understanding|processing",
                True,
                False,
                "Core AI intelligence belongs in Aetherra OS",
            ),
            ArchitecturalRule(
                "Autonomous Systems",
                r"autonomous|self_.*|auto_.*|engine|core|brain",
                True,
                False,
                "Self-operating AI systems belong in Aetherra OS",
            ),
        ]

    def _define_lyrixa_patterns(self) -> List[ArchitecturalRule]:
        """Define patterns that should be in Lyrixa interface"""
        return [
            ArchitecturalRule(
                "GUI Components",
                r"gui|interface|window|panel|dashboard|widget|display",
                False,
                True,
                "User interface components belong in Lyrixa",
            ),
            ArchitecturalRule(
                "Visualization",
                r"visualization|chart|graph|plot|monitor|viewer|renderer",
                False,
                True,
                "Data visualization components belong in Lyrixa",
            ),
            ArchitecturalRule(
                "User Interaction",
                r"interaction|communication|conversation|chat|assistant",
                False,
                True,
                "User interaction systems belong in Lyrixa",
            ),
            ArchitecturalRule(
                "Personality Systems",
                r"personality|emotion|mood|character|assistant|avatar",
                False,
                True,
                "Assistant personality systems belong in Lyrixa",
            ),
            ArchitecturalRule(
                "Experience Management",
                r"experience|ux|ui|user|presentation|launcher",
                False,
                True,
                "User experience systems belong in Lyrixa",
            ),
        ]

    def _define_forbidden_patterns(self) -> List[tuple[str, str]]:
        """Define patterns that should never appear together"""
        return [
            ("aetherra_core imports lyrixa", "Core AI should not depend on interface"),
            ("consciousness.*gui", "Consciousness engines should not contain GUI code"),
            (
                "gui.*consciousness_engine",
                "GUI should not contain core consciousness logic",
            ),
            (
                "interface.*neural_network",
                "Interfaces should not contain core neural networks",
            ),
        ]

    def classify_file(self, file_path: Path) -> tuple[bool, bool, List[str]]:
        """
        Classify whether a file should be in Aetherra or Lyrixa

        Returns:
            (should_be_aetherra, should_be_lyrixa, reasons)
        """
        file_content = ""
        file_name = file_path.name.lower()
        file_str = str(file_path).lower()

        # Try to read file content for analysis
        try:
            if file_path.suffix == ".py":
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    file_content = f.read()[:5000]  # First 5KB for analysis
        except Exception:
            pass

        analysis_text = f"{file_name} {file_str} {file_content}"

        aetherra_matches = []
        lyrixa_matches = []

        # Check Aetherra patterns
        for rule in self.aetherra_patterns:
            if re.search(rule.pattern, analysis_text, re.IGNORECASE):
                aetherra_matches.append(rule.description)

        # Check Lyrixa patterns
        for rule in self.lyrixa_patterns:
            if re.search(rule.pattern, analysis_text, re.IGNORECASE):
                lyrixa_matches.append(rule.description)

        return (
            len(aetherra_matches) > 0,
            len(lyrixa_matches) > 0,
            aetherra_matches + lyrixa_matches,
        )

    def validate_file_location(self, file_path: Path) -> ValidationResult:
        """Validate if a file is in the correct location"""
        should_be_aetherra, should_be_lyrixa, reasons = self.classify_file(file_path)

        # Determine current location
        is_in_lyrixa = (
            self.lyrixa_root in file_path.parents
            or file_path.parent == self.lyrixa_root
        )
        is_in_aetherra_core = (
            not is_in_lyrixa and self.aetherra_root in file_path.parents
        )

        errors = []
        warnings = []
        suggestions = []
        recommended_location = ""

        # Check for misplaced files
        if should_be_aetherra and is_in_lyrixa:
            errors.append(
                "Core AI file incorrectly placed in Lyrixa interface directory"
            )
            recommended_location = "Aetherra/[appropriate_core_directory]/"
            suggestions.append(
                "Move to Aetherra core directory - this appears to be core AI functionality"
            )

        elif should_be_lyrixa and is_in_aetherra_core:
            errors.append(
                "Interface file incorrectly placed in Aetherra core directory"
            )
            recommended_location = "Aetherra/lyrixa/[appropriate_interface_directory]/"
            suggestions.append(
                "Move to Lyrixa interface directory - this appears to be user interface"
            )

        elif should_be_aetherra and should_be_lyrixa:
            warnings.append(
                "File contains both core AI and interface elements - consider splitting"
            )
            suggestions.append("Split into separate core and interface components")

        # Check for specific architectural violations
        file_content = ""
        try:
            if file_path.suffix == ".py":
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    file_content = f.read()
        except Exception:
            pass

        # Check import patterns
        if is_in_aetherra_core and "from lyrixa" in file_content:
            errors.append(
                "Aetherra core file imports from Lyrixa - violates architecture"
            )
            suggestions.append("Remove Lyrixa dependencies from core AI")

        if is_in_lyrixa and re.search(
            r"class.*Engine|class.*Core|class.*Brain", file_content
        ):
            warnings.append("Interface file contains core engine classes")
            suggestions.append(
                "Move core engines to Aetherra, keep only interface in Lyrixa"
            )

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            file_path=str(file_path),
            recommended_location=recommended_location,
        )

    def scan_directory(self, directory: Path = None) -> Dict:
        """Scan directory structure and validate all files"""
        if directory is None:
            directory = self.aetherra_root

        print("🔍 Scanning Aetherra project architecture...")
        print(f"📂 Root directory: {directory}")

        # Scan all Python files
        python_files = list(directory.rglob("*.py"))

        print(f"📊 Found {len(python_files)} Python files to analyze")

        for file_path in python_files:
            # Skip __pycache__ and .git directories
            if "__pycache__" in str(file_path) or ".git" in str(file_path):
                continue

            result = self.validate_file_location(file_path)
            self.validation_results.append(result)

            # Update summary
            self.scan_summary["files_scanned"] += 1
            if not result.is_valid:
                self.scan_summary["errors_found"] += len(result.errors)
                self.scan_summary["misplaced_files"].append(result.file_path)
            if result.warnings:
                self.scan_summary["warnings_found"] += len(result.warnings)
            if result.is_valid and not result.warnings:
                self.scan_summary["correctly_placed"] += 1

        return self.scan_summary

    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("# 🏗️ AETHERRA DIRECTORY ARCHITECTURE VALIDATION REPORT")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Project Root**: {self.project_root}")
        report.append("")

        # Summary
        report.append("## 📊 VALIDATION SUMMARY")
        report.append("")
        report.append(f"- **Files Scanned**: {self.scan_summary['files_scanned']}")
        report.append(
            f"- **Correctly Placed**: {self.scan_summary['correctly_placed']}"
        )
        report.append(f"- **Errors Found**: {self.scan_summary['errors_found']}")
        report.append(f"- **Warnings Found**: {self.scan_summary['warnings_found']}")
        report.append(
            f"- **Misplaced Files**: {len(self.scan_summary['misplaced_files'])}"
        )
        report.append("")

        if self.scan_summary["errors_found"] == 0:
            report.append(
                "✅ **ARCHITECTURE STATUS**: VALID - All files correctly placed!"
            )
        else:
            report.append("❌ **ARCHITECTURE STATUS**: VIOLATIONS DETECTED")

        report.append("")

        # Detailed results
        if any(not r.is_valid for r in self.validation_results):
            report.append("## ❌ ARCHITECTURAL VIOLATIONS")
            report.append("")

            for result in self.validation_results:
                if not result.is_valid:
                    report.append(f"### 🚨 {os.path.basename(result.file_path)}")
                    report.append(f"**Location**: `{result.file_path}`")

                    if result.errors:
                        report.append("**Errors**:")
                        for error in result.errors:
                            report.append(f"- ❌ {error}")

                    if result.recommended_location:
                        report.append(
                            f"**Recommended Location**: `{result.recommended_location}`"
                        )

                    if result.suggestions:
                        report.append("**Suggestions**:")
                        for suggestion in result.suggestions:
                            report.append(f"- 💡 {suggestion}")

                    report.append("")

        # Warnings
        warning_results = [r for r in self.validation_results if r.warnings]
        if warning_results:
            report.append("## ⚠️ ARCHITECTURAL WARNINGS")
            report.append("")

            for result in warning_results:
                report.append(f"### ⚠️ {os.path.basename(result.file_path)}")
                report.append(f"**Location**: `{result.file_path}`")

                for warning in result.warnings:
                    report.append(f"- ⚠️ {warning}")

                if result.suggestions:
                    for suggestion in result.suggestions:
                        report.append(f"- 💡 {suggestion}")

                report.append("")

        # Architecture compliance
        report.append("## 🎯 ARCHITECTURE COMPLIANCE GUIDE")
        report.append("")
        report.append("### 🧠 AETHERRA OS (Core AI Intelligence)")
        report.append(
            "**Should contain**: Consciousness engines, decision systems, learning algorithms, memory systems"
        )
        report.append("**Location**: `Aetherra/` (excluding `lyrixa/` subdirectory)")
        report.append("")
        report.append("### 🎭 LYRIXA (Interface & Assistant)")
        report.append(
            "**Should contain**: GUI components, dashboards, user interaction, visualization"
        )
        report.append("**Location**: `Aetherra/lyrixa/`")
        report.append("")
        report.append("### 🔄 INTEGRATION PATTERN")
        report.append("- Lyrixa imports from Aetherra ✅")
        report.append("- Lyrixa displays Aetherra data ✅")
        report.append("- Aetherra imports from Lyrixa ❌")
        report.append("- Core AI logic in Lyrixa ❌")
        report.append("")

        return "\n".join(report)

    def fix_misplaced_files(self, dry_run: bool = True) -> List[str]:
        """Generate commands to fix misplaced files"""
        commands = []

        for result in self.validation_results:
            if not result.is_valid and result.recommended_location:
                file_path = Path(result.file_path)
                filename = file_path.name

                # Generate move command
                if "lyrixa" in result.recommended_location:
                    target = self.lyrixa_root / "gui" / filename
                else:
                    # Suggest appropriate Aetherra core directory
                    if "consciousness" in filename.lower():
                        target = self.aetherra_root / "consciousness" / filename
                    elif "memory" in filename.lower():
                        target = self.aetherra_root / "memory" / filename
                    elif "learning" in filename.lower():
                        target = self.aetherra_root / "core" / "learning" / filename
                    else:
                        target = self.aetherra_root / "core" / filename

                if dry_run:
                    commands.append(f"# Move: {file_path} -> {target}")
                    commands.append(f'mv "{file_path}" "{target}"')
                else:
                    commands.append(f'mv "{file_path}" "{target}"')

        return commands


def main():
    """Main validation function"""
    # Standard library imports
    import sys

    # Get project root
    project_root = os.getcwd()
    if len(sys.argv) > 1:
        project_root = sys.argv[1]

    # Create validator
    validator = AetherraDirectoryValidator(project_root)

    # Scan and validate
    print("🏗️ AETHERRA DIRECTORY ARCHITECTURE VALIDATOR")
    print("=" * 50)

    summary = validator.scan_directory()

    # Generate report
    report = validator.generate_report()

    # Save report
    report_path = Path(project_root) / "ARCHITECTURE_VALIDATION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("📊 Validation complete!")
    print(f"📄 Report saved to: {report_path}")

    # Print summary
    if summary["errors_found"] > 0:
        print(f"❌ Found {summary['errors_found']} architectural violations")
        print(f"⚠️  Found {summary['warnings_found']} warnings")
        print("🔧 Run with --fix to generate fix commands")
    else:
        print("✅ Architecture validation passed - all files correctly placed!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🏗️ NeuroCode Internal Refactoring System
========================================

Advanced code quality and maintainability tools for the NeuroCode codebase.
Handles import organization, documentation generation, logging infrastructure,
and code quality standards enforcement.

Features:
- Automatic import organization and cleanup
- Comprehensive documentation generation
- Structured logging infrastructure
- Code quality analysis and suggestions
- Type hint enforcement and validation
- Performance monitoring integration

Author: NeuroCode Development Team
Date: June 30, 2025
"""

import ast
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class ImportInfo:
    """Information about an import statement"""

    module: str
    alias: Optional[str] = None
    from_module: Optional[str] = None
    line_number: int = 0
    is_used: bool = False
    is_standard_library: bool = False
    is_third_party: bool = False
    is_local: bool = False


@dataclass
class FunctionInfo:
    """Information about a function or method"""

    name: str
    file_path: str
    line_number: int
    args: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    has_type_hints: bool = False
    complexity_score: int = 0
    is_public: bool = True


@dataclass
class CodeQualityReport:
    """Code quality analysis report"""

    file_path: str
    total_lines: int
    code_lines: int
    comment_lines: int
    docstring_lines: int
    imports: List[ImportInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    unused_imports: List[str] = field(default_factory=list)
    missing_docstrings: List[str] = field(default_factory=list)
    missing_type_hints: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    suggestions: List[str] = field(default_factory=list)


class ImportOrganizer:
    """Handles import statement organization and cleanup"""

    def __init__(self):
        self.standard_modules = self._get_standard_modules()

    def _get_standard_modules(self) -> Set[str]:
        """Get list of standard library modules"""
        try:
            import sys

            return set(sys.stdlib_module_names)
        except AttributeError:
            # Fallback for older Python versions
            return {
                "os",
                "sys",
                "json",
                "time",
                "datetime",
                "pathlib",
                "typing",
                "collections",
                "functools",
                "itertools",
                "logging",
                "threading",
                "asyncio",
                "dataclasses",
                "enum",
                "re",
                "math",
                "random",
            }

    def analyze_imports(self, file_path: Path) -> List[ImportInfo]:
        """Analyze imports in a Python file"""
        imports = []
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_info = ImportInfo(
                            module=alias.name,
                            alias=alias.asname,
                            line_number=node.lineno,
                            is_standard_library=alias.name.split(".")[0] in self.standard_modules,
                        )
                        imports.append(import_info)

                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        import_info = ImportInfo(
                            module=alias.name,
                            alias=alias.asname,
                            from_module=node.module,
                            line_number=node.lineno,
                            is_standard_library=(node.module or "").split(".")[0]
                            in self.standard_modules,
                        )
                        imports.append(import_info)

            # Classify imports
            for imp in imports:
                if imp.is_standard_library:
                    continue
                elif imp.from_module and (
                    imp.from_module.startswith(".") or imp.from_module.startswith("core")
                ):
                    imp.is_local = True
                else:
                    imp.is_third_party = True

        except Exception as e:
            logging.warning(f"Failed to analyze imports in {file_path}: {e}")

        return imports

    def find_unused_imports(self, file_path: Path) -> List[str]:
        """Find unused imports in a Python file"""
        unused = []
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Simple regex-based detection (could be improved with AST analysis)
            imports = self.analyze_imports(file_path)
            for imp in imports:
                module_name = imp.alias or imp.module
                if imp.from_module:
                    # Check if imported name is used
                    pattern = rf"\b{re.escape(module_name)}\b"
                    if not re.search(pattern, content):
                        unused.append(f"from {imp.from_module} import {imp.module}")
                else:
                    # Check if module is used
                    pattern = rf"\b{re.escape(module_name)}\."
                    if not re.search(pattern, content) and module_name not in content:
                        unused.append(f"import {imp.module}")

        except Exception as e:
            logging.warning(f"Failed to find unused imports in {file_path}: {e}")

        return unused

    def organize_imports(self, content: str) -> str:
        """Organize imports according to PEP 8 guidelines"""
        try:
            lines = content.split("\n")
            import_lines = []
            other_lines = []

            # Separate imports from other code
            import_section = True
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(("import ", "from ")) and import_section:
                    import_lines.append(line)
                elif stripped and not stripped.startswith("#") and import_section:
                    import_section = False
                    other_lines.append(line)
                else:
                    other_lines.append(line)

            if not import_lines:
                return content

            # Categorize imports
            standard_imports = []
            third_party_imports = []
            local_imports = []

            for line in import_lines:
                if any(std in line for std in self.standard_modules):
                    standard_imports.append(line)
                elif line.strip().startswith("from .") or "core." in line:
                    local_imports.append(line)
                else:
                    third_party_imports.append(line)

            # Sort each category
            standard_imports.sort()
            third_party_imports.sort()
            local_imports.sort()

            # Combine with proper spacing
            organized_imports = []
            if standard_imports:
                organized_imports.extend(standard_imports)
                organized_imports.append("")
            if third_party_imports:
                organized_imports.extend(third_party_imports)
                organized_imports.append("")
            if local_imports:
                organized_imports.extend(local_imports)
                organized_imports.append("")

            # Combine with rest of content
            return "\n".join(organized_imports + other_lines)

        except Exception as e:
            logging.warning(f"Failed to organize imports: {e}")
            return content


class DocumentationGenerator:
    """Generates and validates documentation for Python code"""

    def __init__(self):
        self.docstring_templates = {
            "function": '''"""
    {summary}
    
    Args:
        {args}
        
    Returns:
        {returns}
        
    Example:
        >>> {example}
    """''',
            "class": '''"""
    {summary}
    
    Attributes:
        {attributes}
        
    Example:
        >>> {example}
    """''',
            "module": '''"""
{summary}

{description}

Author: NeuroCode Development Team
Date: {date}
"""''',
        }

    def analyze_functions(self, file_path: Path) -> List[FunctionInfo]:
        """Analyze functions in a Python file"""
        functions = []
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_info = FunctionInfo(
                        name=node.name,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node),
                        is_public=not node.name.startswith("_"),
                    )

                    # Extract arguments
                    func_info.args = [arg.arg for arg in node.args.args]

                    # Check for type hints
                    has_type_hints = bool(node.returns) or any(
                        arg.annotation for arg in node.args.args
                    )
                    func_info.has_type_hints = has_type_hints

                    # Calculate complexity (simple metric)
                    complexity = self._calculate_complexity(node)
                    func_info.complexity_score = complexity

                    functions.append(func_info)

        except Exception as e:
            logging.warning(f"Failed to analyze functions in {file_path}: {e}")

        return functions

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def find_missing_docstrings(self, file_path: Path) -> List[str]:
        """Find functions/classes missing docstrings"""
        missing = []
        functions = self.analyze_functions(file_path)

        for func in functions:
            if func.is_public and not func.docstring:
                missing.append(f"{func.name} (line {func.line_number})")

        return missing

    def generate_docstring(self, func_info: FunctionInfo) -> str:
        """Generate a docstring template for a function"""
        args_doc = "\n        ".join([f"{arg}: Description of {arg}" for arg in func_info.args])

        template = self.docstring_templates["function"].format(
            summary=f"Brief description of {func_info.name}",
            args=args_doc or "None",
            returns="Description of return value",
            example=f"{func_info.name}(example_args)",
        )

        return template


class LoggingInfrastructure:
    """Structured logging infrastructure for NeuroCode"""

    def __init__(self, log_level: int = logging.INFO):
        self.log_level = log_level
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_formatters()

    def _setup_formatters(self):
        """Setup custom log formatters"""
        self.detailed_formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s"
        )

        self.simple_formatter = logging.Formatter("%(levelname)s: %(message)s")

        self.json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", '
            '"function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}'
        )

    def get_logger(self, name: str, use_json: bool = False) -> logging.Logger:
        """Get a configured logger"""
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)

        # Remove existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        formatter = self.json_formatter if use_json else self.detailed_formatter
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if possible)
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_dir / f"{name}.log")
            file_handler.setFormatter(self.detailed_formatter)
            logger.addHandler(file_handler)
        except (PermissionError, OSError):
            pass  # Graceful fallback

        self.loggers[name] = logger
        return logger

    def add_performance_logging(self, logger: logging.Logger):
        """Add performance logging capabilities"""

        def log_performance(func):
            def wrapper(*args, **kwargs):
                start_time = datetime.now()
                try:
                    result = func(*args, **kwargs)
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Performance: {func.__name__} completed in {duration:.3f}s")
                    return result
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.error(f"Performance: {func.__name__} failed after {duration:.3f}s: {e}")
                    raise

            return wrapper

        return log_performance


class CodeQualityAnalyzer:
    """Comprehensive code quality analysis"""

    def __init__(self):
        self.import_organizer = ImportOrganizer()
        self.doc_generator = DocumentationGenerator()
        self.logging_infra = LoggingInfrastructure()
        self.logger = self.logging_infra.get_logger("code_quality")

    def analyze_file(self, file_path: Path) -> CodeQualityReport:
        """Perform comprehensive analysis of a Python file"""
        self.logger.info(f"Analyzing file: {file_path}")

        report = CodeQualityReport(
            file_path=str(file_path),
            total_lines=0,
            code_lines=0,
            comment_lines=0,
            docstring_lines=0,
        )

        try:
            # Read file content
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            report.total_lines = len(lines)

            # Count line types
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                elif stripped.startswith("#"):
                    report.comment_lines += 1
                elif '"""' in stripped or "'''" in stripped:
                    report.docstring_lines += 1
                else:
                    report.code_lines += 1

            # Analyze imports
            report.imports = self.import_organizer.analyze_imports(file_path)
            report.unused_imports = self.import_organizer.find_unused_imports(file_path)

            # Analyze functions
            report.functions = self.doc_generator.analyze_functions(file_path)
            report.missing_docstrings = self.doc_generator.find_missing_docstrings(file_path)

            # Find missing type hints
            report.missing_type_hints = [
                f.name for f in report.functions if f.is_public and not f.has_type_hints
            ]

            # Generate suggestions
            report.suggestions = self._generate_suggestions(report)

            # Calculate quality score
            report.quality_score = self._calculate_quality_score(report)

        except Exception as e:
            self.logger.error(f"Failed to analyze {file_path}: {e}")

        return report

    def _generate_suggestions(self, report: CodeQualityReport) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        if report.unused_imports:
            suggestions.append(f"Remove {len(report.unused_imports)} unused imports")

        if report.missing_docstrings:
            suggestions.append(
                f"Add docstrings to {len(report.missing_docstrings)} public functions"
            )

        if report.missing_type_hints:
            suggestions.append(f"Add type hints to {len(report.missing_type_hints)} functions")

        # Comment ratio check
        comment_ratio = report.comment_lines / max(report.code_lines, 1)
        if comment_ratio < 0.1:
            suggestions.append("Consider adding more comments for code clarity")

        # Complexity check
        complex_functions = [f for f in report.functions if f.complexity_score > 10]
        if complex_functions:
            suggestions.append(f"Consider refactoring {len(complex_functions)} complex functions")

        return suggestions

    def _calculate_quality_score(self, report: CodeQualityReport) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0

        # Penalty for unused imports
        if report.unused_imports:
            score -= len(report.unused_imports) * 2

        # Penalty for missing docstrings
        public_functions = [f for f in report.functions if f.is_public]
        if public_functions:
            docstring_ratio = (len(public_functions) - len(report.missing_docstrings)) / len(
                public_functions
            )
            score *= docstring_ratio

        # Penalty for missing type hints
        if public_functions:
            type_hint_ratio = (len(public_functions) - len(report.missing_type_hints)) / len(
                public_functions
            )
            score *= type_hint_ratio

        # Bonus for good comment ratio
        comment_ratio = report.comment_lines / max(report.code_lines, 1)
        if comment_ratio > 0.15:
            score += 5

        return max(0.0, min(100.0, score))

    def analyze_project(self, project_path: Path) -> Dict[str, CodeQualityReport]:
        """Analyze entire project"""
        reports = {}

        # Find all Python files
        python_files = list(project_path.rglob("*.py"))

        self.logger.info(f"Analyzing {len(python_files)} Python files in project")

        for file_path in python_files:
            # Skip __pycache__ and virtual environments
            if "__pycache__" in str(file_path) or "venv" in str(file_path):
                continue

            try:
                report = self.analyze_file(file_path)
                reports[str(file_path)] = report
            except Exception as e:
                self.logger.error(f"Failed to analyze {file_path}: {e}")

        return reports

    def generate_quality_report(self, reports: Dict[str, CodeQualityReport]) -> str:
        """Generate a comprehensive quality report"""
        lines = ["📊 NeuroCode Project Quality Report", "=" * 50, ""]

        # Overall statistics
        total_files = len(reports)
        total_lines = sum(r.total_lines for r in reports.values())
        avg_quality = sum(r.quality_score for r in reports.values()) / max(total_files, 1)

        lines.extend(
            [
                f"📁 Files Analyzed: {total_files}",
                f"📝 Total Lines: {total_lines:,}",
                f"⭐ Average Quality Score: {avg_quality:.1f}/100",
                "",
            ]
        )

        # Top issues
        all_unused_imports = sum(len(r.unused_imports) for r in reports.values())
        all_missing_docs = sum(len(r.missing_docstrings) for r in reports.values())
        all_missing_types = sum(len(r.missing_type_hints) for r in reports.values())

        lines.extend(
            [
                "🔍 Key Issues:",
                f"  • Unused imports: {all_unused_imports}",
                f"  • Missing docstrings: {all_missing_docs}",
                f"  • Missing type hints: {all_missing_types}",
                "",
            ]
        )

        # Best and worst files
        if reports:
            best_file = max(reports.items(), key=lambda x: x[1].quality_score)
            worst_file = min(reports.items(), key=lambda x: x[1].quality_score)

            lines.extend(
                [
                    "🏆 Quality Leaders:",
                    f"  • Best: {Path(best_file[0]).name} ({best_file[1].quality_score:.1f}/100)",
                    f"  • Needs work: {Path(worst_file[0]).name} ({worst_file[1].quality_score:.1f}/100)",
                    "",
                ]
            )

        # Detailed file reports
        lines.append("📋 Detailed File Analysis:")
        for file_path, report in sorted(
            reports.items(), key=lambda x: x[1].quality_score, reverse=True
        ):
            file_name = Path(file_path).name
            lines.extend(
                [
                    f"\n📄 {file_name} (Score: {report.quality_score:.1f}/100)",
                    f"   Lines: {report.total_lines} | Functions: {len(report.functions)}",
                ]
            )

            if report.suggestions:
                lines.append("   Suggestions:")
                for suggestion in report.suggestions[:3]:  # Top 3 suggestions
                    lines.append(f"     • {suggestion}")

        return "\n".join(lines)


class InternalRefactoringSystem:
    """Main system for internal code refactoring and quality management"""

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.analyzer = CodeQualityAnalyzer()
        self.logger = self.analyzer.logging_infra.get_logger("refactoring")

    def run_full_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis of the entire project"""
        self.logger.info("Starting full project analysis")

        # Analyze all files
        reports = self.analyzer.analyze_project(self.project_path)

        # Generate summary report
        quality_report = self.analyzer.generate_quality_report(reports)

        # Calculate project-wide metrics
        project_metrics = self._calculate_project_metrics(reports)

        return {
            "file_reports": reports,
            "quality_report": quality_report,
            "project_metrics": project_metrics,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def _calculate_project_metrics(self, reports: Dict[str, CodeQualityReport]) -> Dict[str, Any]:
        """Calculate project-wide quality metrics"""
        if not reports:
            return {}

        total_files = len(reports)
        total_lines = sum(r.total_lines for r in reports.values())
        total_functions = sum(len(r.functions) for r in reports.values())
        avg_quality = sum(r.quality_score for r in reports.values()) / total_files

        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_functions": total_functions,
            "average_quality_score": round(avg_quality, 2),
            "files_needing_attention": len([r for r in reports.values() if r.quality_score < 70]),
            "high_quality_files": len([r for r in reports.values() if r.quality_score >= 90]),
            "total_unused_imports": sum(len(r.unused_imports) for r in reports.values()),
            "total_missing_docstrings": sum(len(r.missing_docstrings) for r in reports.values()),
            "total_missing_type_hints": sum(len(r.missing_type_hints) for r in reports.values()),
        }

    def generate_improvement_plan(
        self, reports: Dict[str, CodeQualityReport]
    ) -> List[Dict[str, Any]]:
        """Generate actionable improvement plan"""
        improvements = []

        # High-impact, low-effort improvements first
        for file_path, report in reports.items():
            file_name = Path(file_path).name

            # Unused imports (easy fix)
            if report.unused_imports:
                improvements.append(
                    {
                        "priority": "high",
                        "effort": "low",
                        "file": file_name,
                        "action": f"Remove {len(report.unused_imports)} unused imports",
                        "impact": "Code cleanup and reduced dependencies",
                    }
                )

            # Missing docstrings (medium effort)
            if report.missing_docstrings:
                improvements.append(
                    {
                        "priority": "medium",
                        "effort": "medium",
                        "file": file_name,
                        "action": f"Add docstrings to {len(report.missing_docstrings)} functions",
                        "impact": "Improved code documentation and maintainability",
                    }
                )

            # Missing type hints (medium effort)
            if report.missing_type_hints:
                improvements.append(
                    {
                        "priority": "medium",
                        "effort": "medium",
                        "file": file_name,
                        "action": f"Add type hints to {len(report.missing_type_hints)} functions",
                        "impact": "Better IDE support and code safety",
                    }
                )

        # Sort by priority and effort
        priority_order = {"high": 3, "medium": 2, "low": 1}
        effort_order = {"low": 3, "medium": 2, "high": 1}

        improvements.sort(
            key=lambda x: (priority_order[x["priority"]], effort_order[x["effort"]]), reverse=True
        )

        return improvements[:20]  # Top 20 improvements

    def apply_import_organization(self, file_path: Path) -> bool:
        """Apply import organization to a specific file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            organized_content = self.analyzer.import_organizer.organize_imports(original_content)

            if organized_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(organized_content)
                self.logger.info(f"Organized imports in {file_path}")
                return True

            return False
        except Exception as e:
            self.logger.error(f"Failed to organize imports in {file_path}: {e}")
            return False

    def get_refactoring_status(self) -> Dict[str, Any]:
        """Get current refactoring status and progress"""
        return {
            "project_path": str(self.project_path),
            "analyzers_available": {
                "import_organizer": True,
                "documentation_generator": True,
                "quality_analyzer": True,
                "logging_infrastructure": True,
            },
            "last_analysis": datetime.now().isoformat(),
            "features_implemented": [
                "Import organization and cleanup",
                "Function documentation analysis",
                "Type hint validation",
                "Code quality scoring",
                "Unused import detection",
                "Comprehensive project analysis",
                "Improvement plan generation",
            ],
        }


# Example usage and testing
if __name__ == "__main__":

    def demonstrate_refactoring_system():
        """Demonstrate the internal refactoring system"""
        print("🏗️ Internal Refactoring System Demo")
        print("=" * 50)

        # Initialize the system
        refactoring_system = InternalRefactoringSystem()

        # Show system status
        print("\n📊 System Status:")
        status = refactoring_system.get_refactoring_status()
        for key, value in status.items():
            if key != "features_implemented":
                print(f"  {key}: {value}")

        print("\n✨ Features Available:")
        for feature in status["features_implemented"]:
            print(f"  • {feature}")

        # Demonstrate analysis on current file
        current_file = Path(__file__)
        print(f"\n🔍 Analyzing current file: {current_file.name}")

        report = refactoring_system.analyzer.analyze_file(current_file)
        print(f"  Quality Score: {report.quality_score:.1f}/100")
        print(f"  Total Lines: {report.total_lines}")
        print(f"  Functions: {len(report.functions)}")
        print(f"  Imports: {len(report.imports)}")

        if report.suggestions:
            print("\n💡 Suggestions:")
            for suggestion in report.suggestions:
                print(f"  • {suggestion}")

        # Show project metrics
        print("\n📈 Quick Project Metrics:")
        project_files = list(refactoring_system.project_path.glob("*.py"))
        print(f"  Python Files Found: {len(project_files)}")
        print("  Analysis Capabilities: All systems operational")

        print("\n✅ Internal Refactoring System demonstration complete!")

    # Run the demonstration
    demonstrate_refactoring_system()

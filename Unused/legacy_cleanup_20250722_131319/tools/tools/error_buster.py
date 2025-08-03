#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERROR BUSTER DEVELOPER TOOL
============================

Advanced error detection and reporting system for workspace analysis.
Pinpoints errors with precision for Copilot agents to fix instantly.

Features:
- Multi-language error detection
- Static analysis integration
- Detailed error reporting
- IDE integration ready
- Copilot-friendly output
"""

import ast
import json
import os
import py_compile
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def safe_print(message: str) -> None:
    """Safe print function that handles Unicode encoding issues on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Remove Unicode characters for Windows console compatibility
        safe_message = message.encode("ascii", "ignore").decode("ascii")
        print(
            safe_message.replace("🔍", "[*]")
            .replace("📋", "[*]")
            .replace("[WARN]", "[!]")
            .replace("❌", "[X]")
            .replace("✅", "[OK]")
        )


@dataclass
class ErrorReport:
    """Structured error report"""

    file_path: str
    line_number: int
    column_number: int
    error_type: str
    severity: str  # critical, error, warning, info
    message: str
    rule_code: Optional[str] = None
    suggestion: Optional[str] = None
    context_lines: Optional[List[str]] = None
    tool: str = "error_buster"


@dataclass
class WorkspaceSummary:
    """Summary of workspace analysis"""

    total_files_scanned: int
    total_errors: int
    critical_errors: int
    errors: int
    warnings: int
    info_issues: int
    scan_duration: float
    timestamp: str
    tools_used: List[str]


class ErrorBuster:
    """
    Advanced Error Detection and Reporting System

    Scans workspace for errors across multiple file types and provides
    detailed reports for Copilot agents to act upon.
    """

    def __init__(
        self, workspace_path: str = ".", exclude_dirs: Optional[List[str]] = None
    ):
        self.workspace_path = Path(workspace_path).resolve()
        self.exclude_dirs = exclude_dirs or [
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            ".plugin_history",
            "backups",
            "archive",
        ]
        self.errors: List[ErrorReport] = []
        self.files_scanned = 0
        self.tools_available = self._check_available_tools()

        safe_print(f"🔍 Error Buster initialized for workspace: {self.workspace_path}")
        safe_print(f"📋 Available analysis tools: {', '.join(self.tools_available)}")

    def _check_available_tools(self) -> List[str]:
        """Check which analysis tools are available"""
        tools = []

        # Check for flake8
        try:
            subprocess.run(["flake8", "--version"], capture_output=True, check=True)
            tools.append("flake8")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Check for mypy
        try:
            subprocess.run(["mypy", "--version"], capture_output=True, check=True)
            tools.append("mypy")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Check for pylint
        try:
            subprocess.run(["pylint", "--version"], capture_output=True, check=True)
            tools.append("pylint")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Built-in tools always available
        tools.extend(["ast_parser", "syntax_checker", "import_analyzer"])

        return tools

    def scan_workspace(self) -> List[Path]:
        """Scan workspace for files to analyze"""
        print("📂 Scanning workspace for files...")

        files_to_check = []

        for root, dirs, files in os.walk(self.workspace_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = Path(root) / file

                # Check file extensions
                if self._should_analyze_file(file_path):
                    files_to_check.append(file_path)

        safe_print(f"📊 Found {len(files_to_check)} files to analyze")
        return files_to_check

    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if a file should be analyzed"""
        analyzable_extensions = {
            ".py",
            ".pyx",
            ".pyi",  # Python files
            ".json",
            ".jsonc",  # JSON files
            ".yaml",
            ".yml",  # YAML files
            ".toml",  # TOML files
            ".cfg",
            ".ini",  # Config files
            ".md",
            ".rst",  # Documentation
            ".js",
            ".ts",  # JavaScript/TypeScript
            ".html",
            ".htm",  # HTML files
            ".css",
            ".scss",  # CSS files
            ".xml",  # XML files
            ".txt",  # Text files
        }

        return file_path.suffix.lower() in analyzable_extensions

    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single file for errors"""
        try:
            self.files_scanned += 1

            if file_path.suffix == ".py":
                self._analyze_python_file(file_path)
            elif file_path.suffix in [".json", ".jsonc"]:
                self._analyze_json_file(file_path)
            elif file_path.suffix in [".yaml", ".yml"]:
                self._analyze_yaml_file(file_path)
            elif file_path.suffix == ".toml":
                self._analyze_toml_file(file_path)
            elif file_path.suffix in [".md", ".rst"]:
                self._analyze_markdown_file(file_path)
            else:
                self._analyze_generic_file(file_path)

        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "analysis_error",
                "error",
                f"Failed to analyze file: {e}",
                tool="error_buster",
            )

    def _analyze_python_file(self, file_path: Path) -> None:
        """Comprehensive Python file analysis"""
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 1. Syntax check using py_compile
            self._check_python_syntax(file_path, content)

            # 2. AST analysis
            self._analyze_python_ast(file_path, content)

            # 3. Import analysis
            self._analyze_python_imports(file_path, content)

            # 4. External tool analysis
            if "flake8" in self.tools_available:
                self._run_flake8(file_path)

            if "mypy" in self.tools_available:
                self._run_mypy(file_path)

            if "pylint" in self.tools_available:
                self._run_pylint(file_path)

        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "python_analysis_error",
                "error",
                f"Python analysis failed: {e}",
                tool="error_buster",
            )

    def _check_python_syntax(self, file_path: Path, content: str) -> None:
        """Check Python syntax using py_compile"""
        try:
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as e:
            # Parse error message to extract line number
            error_msg = str(e)
            line_match = re.search(r"line (\d+)", error_msg)
            line_num = int(line_match.group(1)) if line_match else 1

            self._add_error(
                file_path,
                line_num,
                0,
                "syntax_error",
                "critical",
                f"Syntax error: {error_msg}",
                tool="py_compile",
            )

    def _analyze_python_ast(self, file_path: Path, content: str) -> None:
        """Analyze Python AST for potential issues"""
        try:
            tree = ast.parse(content, filename=str(file_path))

            # Check for common issues
            for node in ast.walk(tree):
                # Check for undefined variables (simplified)
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id in ["undefined", "None"] and hasattr(node, "lineno"):
                        # This is a simplified check - in practice you'd want more sophisticated analysis
                        pass

                # Check for potential issues with function definitions
                if isinstance(node, ast.FunctionDef):
                    if not node.body:
                        self._add_error(
                            file_path,
                            node.lineno,
                            node.col_offset,
                            "empty_function",
                            "warning",
                            f"Function '{node.name}' has no body",
                            suggestion="Add 'pass' or implement the function",
                            tool="ast_analyzer",
                        )

                # Check for bare except clauses
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        self._add_error(
                            file_path,
                            node.lineno,
                            node.col_offset,
                            "bare_except",
                            "warning",
                            "Bare 'except:' clause found",
                            suggestion="Use 'except Exception:' instead",
                            tool="ast_analyzer",
                        )

        except SyntaxError as e:
            self._add_error(
                file_path,
                e.lineno or 1,
                e.offset or 0,
                "syntax_error",
                "critical",
                f"AST parsing failed: {e.msg}",
                tool="ast_analyzer",
            )
        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "ast_error",
                "error",
                f"AST analysis failed: {e}",
                tool="ast_analyzer",
            )

    def _analyze_python_imports(self, file_path: Path, content: str) -> None:
        """Analyze Python imports for issues"""
        try:
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()

                # Check for import issues
                if stripped.startswith(("import ", "from ")):
                    # Check for unused imports (simplified)
                    if "# noqa" not in line and "unused" in line.lower():
                        self._add_error(
                            file_path,
                            line_num,
                            0,
                            "unused_import",
                            "warning",
                            f"Potentially unused import: {stripped}",
                            suggestion="Remove if not used",
                            tool="import_analyzer",
                        )

                    # Check for relative imports outside packages
                    if stripped.startswith("from .") and not self._is_package_file(
                        file_path
                    ):
                        self._add_error(
                            file_path,
                            line_num,
                            0,
                            "relative_import",
                            "error",
                            "Relative import in non-package file",
                            suggestion="Use absolute import instead",
                            tool="import_analyzer",
                        )

        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "import_analysis_error",
                "error",
                f"Import analysis failed: {e}",
                tool="import_analyzer",
            )

    def _is_package_file(self, file_path: Path) -> bool:
        """Check if file is part of a Python package"""
        return (file_path.parent / "__init__.py").exists()

    def _run_flake8(self, file_path: Path) -> None:
        """Run flake8 on Python file"""
        try:
            result = subprocess.run(
                [
                    "flake8",
                    "--format=%(path)s:%(row)d:%(col)d:%(code)s:%(text)s",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        self._parse_flake8_output(line)

        except subprocess.TimeoutExpired:
            self._add_error(
                file_path,
                0,
                0,
                "flake8_timeout",
                "warning",
                "Flake8 analysis timed out",
                tool="flake8",
            )
        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "flake8_error",
                "warning",
                f"Flake8 analysis failed: {e}",
                tool="flake8",
            )

    def _parse_flake8_output(self, output_line: str) -> None:
        """Parse flake8 output line"""
        try:
            parts = output_line.split(":", 4)
            if len(parts) >= 5:
                file_path = Path(parts[0])
                line_num = int(parts[1])
                col_num = int(parts[2])
                rule_code = parts[3]
                message = parts[4]

                severity = "error" if rule_code.startswith("E") else "warning"

                self._add_error(
                    file_path,
                    line_num,
                    col_num,
                    "style_error",
                    severity,
                    message,
                    rule_code=rule_code,
                    tool="flake8",
                )
        except Exception:
            pass  # Skip malformed lines

    def _run_mypy(self, file_path: Path) -> None:
        """Run mypy on Python file"""
        try:
            result = subprocess.run(
                ["mypy", "--no-error-summary", str(file_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if line.strip() and ":" in line:
                        self._parse_mypy_output(line)

        except subprocess.TimeoutExpired:
            self._add_error(
                file_path,
                0,
                0,
                "mypy_timeout",
                "warning",
                "MyPy analysis timed out",
                tool="mypy",
            )
        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "mypy_error",
                "warning",
                f"MyPy analysis failed: {e}",
                tool="mypy",
            )

    def _parse_mypy_output(self, output_line: str) -> None:
        """Parse mypy output line"""
        try:
            # Format: file.py:line: error: message
            match = re.match(r"(.+):(\d+):\s*(error|warning|note):\s*(.+)", output_line)
            if match:
                file_path = Path(match.group(1))
                line_num = int(match.group(2))
                severity = match.group(3)
                message = match.group(4)

                self._add_error(
                    file_path,
                    line_num,
                    0,
                    "type_error",
                    "error" if severity == "error" else "warning",
                    message,
                    tool="mypy",
                )
        except Exception:
            pass  # Skip malformed lines

    def _run_pylint(self, file_path: Path) -> None:
        """Run pylint on Python file"""
        try:
            result = subprocess.run(
                ["pylint", "--output-format=json", str(file_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                    for issue in issues:
                        self._parse_pylint_output(issue)
                except json.JSONDecodeError:
                    pass  # Skip if JSON parsing fails

        except subprocess.TimeoutExpired:
            self._add_error(
                file_path,
                0,
                0,
                "pylint_timeout",
                "warning",
                "Pylint analysis timed out",
                tool="pylint",
            )
        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "pylint_error",
                "warning",
                f"Pylint analysis failed: {e}",
                tool="pylint",
            )

    def _parse_pylint_output(self, issue: Dict) -> None:
        """Parse pylint JSON output"""
        try:
            file_path = Path(issue["path"])
            line_num = issue["line"]
            col_num = issue.get("column", 0)
            message = issue["message"]
            rule_code = issue["message-id"]
            severity_map = {
                "error": "error",
                "warning": "warning",
                "refactor": "info",
                "convention": "info",
                "info": "info",
            }
            severity = severity_map.get(issue["type"], "warning")

            self._add_error(
                file_path,
                line_num,
                col_num,
                "code_quality",
                severity,
                message,
                rule_code=rule_code,
                tool="pylint",
            )
        except Exception:
            pass  # Skip malformed issues

    def _analyze_json_file(self, file_path: Path) -> None:
        """Analyze JSON file for syntax errors"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            self._add_error(
                file_path,
                e.lineno,
                e.colno,
                "json_syntax_error",
                "error",
                f"JSON syntax error: {e.msg}",
                suggestion="Fix JSON syntax",
                tool="json_validator",
            )
        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "json_error",
                "error",
                f"JSON analysis failed: {e}",
                tool="json_validator",
            )

    def _analyze_yaml_file(self, file_path: Path) -> None:
        """Analyze YAML file for syntax errors"""
        try:
            import yaml
        except ImportError:
            # YAML library not available, skip analysis
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                yaml.safe_load(f)
        except Exception as e:
            # Handle YAML parsing errors
            line_num = 1
            if (
                hasattr(e, "problem_mark")
                and e.problem_mark
                and hasattr(e.problem_mark, "line")
            ):
                line_num = e.problem_mark.line + 1

            self._add_error(
                file_path,
                line_num,
                0,
                "yaml_syntax_error",
                "error",
                f"YAML syntax error: {e}",
                suggestion="Fix YAML syntax",
                tool="yaml_validator",
            )

    def _analyze_toml_file(self, file_path: Path) -> None:
        """Analyze TOML file for syntax errors"""
        try:
            try:
                import tomllib  # Python 3.11+

                with open(file_path, "rb") as f:
                    tomllib.load(f)
            except ImportError:
                try:
                    import tomli  # Fallback for older Python versions

                    with open(file_path, "rb") as f:
                        tomli.load(f)
                except ImportError:
                    # Skip TOML validation if no library available
                    return
            except Exception as e:
                self._add_error(
                    file_path,
                    0,
                    0,
                    "toml_syntax_error",
                    "error",
                    f"TOML syntax error: {e}",
                    tool="toml_validator",
                )
        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "toml_syntax_error",
                "error",
                f"TOML syntax error: {e}",
                tool="toml_validator",
            )

    def _analyze_markdown_file(self, file_path: Path) -> None:
        """Analyze Markdown file for common issues"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                # Check for broken links (simplified)
                if "[" in line and "](" in line:
                    # Extract links
                    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
                    matches = re.finditer(link_pattern, line)

                    for match in matches:
                        link_url = match.group(2)
                        if link_url.startswith(("http://", "https://")):
                            # Could add URL validation here
                            pass
                        elif link_url.startswith("/") or not link_url.startswith("#"):
                            # Local file link
                            if not Path(file_path.parent / link_url).exists():
                                self._add_error(
                                    file_path,
                                    line_num,
                                    match.start(),
                                    "broken_link",
                                    "warning",
                                    f"Broken local link: {link_url}",
                                    suggestion="Fix or remove broken link",
                                    tool="markdown_analyzer",
                                )

        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "markdown_error",
                "warning",
                f"Markdown analysis failed: {e}",
                tool="markdown_analyzer",
            )

    def _analyze_generic_file(self, file_path: Path) -> None:
        """Basic analysis for generic files"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for common issues
            if not content.strip():
                self._add_error(
                    file_path,
                    1,
                    0,
                    "empty_file",
                    "info",
                    "File is empty",
                    tool="generic_analyzer",
                )

            # Check for very long lines
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                if len(line) > 500:  # Arbitrary threshold
                    self._add_error(
                        file_path,
                        line_num,
                        0,
                        "long_line",
                        "info",
                        f"Very long line ({len(line)} characters)",
                        suggestion="Consider breaking into multiple lines",
                        tool="generic_analyzer",
                    )

        except UnicodeDecodeError:
            self._add_error(
                file_path,
                0,
                0,
                "encoding_error",
                "warning",
                "File encoding issue - not valid UTF-8",
                suggestion="Check file encoding",
                tool="generic_analyzer",
            )
        except Exception as e:
            self._add_error(
                file_path,
                0,
                0,
                "generic_error",
                "warning",
                f"Generic analysis failed: {e}",
                tool="generic_analyzer",
            )

    def _add_error(
        self,
        file_path: Path,
        line_num: int,
        col_num: int,
        error_type: str,
        severity: str,
        message: str,
        rule_code: Optional[str] = None,
        suggestion: Optional[str] = None,
        tool: str = "error_buster",
    ) -> None:
        """Add an error to the report"""
        # Get context lines if possible
        context_lines = self._get_context_lines(file_path, line_num)

        error = ErrorReport(
            file_path=str(file_path.relative_to(self.workspace_path)),
            line_number=line_num,
            column_number=col_num,
            error_type=error_type,
            severity=severity,
            message=message,
            rule_code=rule_code,
            suggestion=suggestion,
            context_lines=context_lines,
            tool=tool,
        )

        self.errors.append(error)

    def _get_context_lines(
        self, file_path: Path, line_num: int, context: int = 3
    ) -> Optional[List[str]]:
        """Get context lines around an error"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            start = max(0, line_num - context - 1)
            end = min(len(lines), line_num + context)

            return [line.rstrip() for line in lines[start:end]]

        except Exception:
            return None

    def generate_report(self, output_format: str = "json") -> str:
        """Generate comprehensive error report"""
        # Calculate summary statistics
        severity_counts = {
            "critical": len([e for e in self.errors if e.severity == "critical"]),
            "error": len([e for e in self.errors if e.severity == "error"]),
            "warning": len([e for e in self.errors if e.severity == "warning"]),
            "info": len([e for e in self.errors if e.severity == "info"]),
        }

        summary = WorkspaceSummary(
            total_files_scanned=self.files_scanned,
            total_errors=len(self.errors),
            critical_errors=severity_counts["critical"],
            errors=severity_counts["error"],
            warnings=severity_counts["warning"],
            info_issues=severity_counts["info"],
            scan_duration=0.0,  # Will be set by caller
            timestamp=datetime.now().isoformat(),
            tools_used=self.tools_available,
        )

        if output_format == "json":
            return self._generate_json_report(summary)
        elif output_format == "markdown":
            return self._generate_markdown_report(summary)
        elif output_format == "copilot":
            return self._generate_copilot_report(summary)
        else:
            return self._generate_json_report(summary)

    def _generate_json_report(self, summary: WorkspaceSummary) -> str:
        """Generate JSON format report"""
        report = {
            "summary": asdict(summary),
            "errors": [asdict(error) for error in self.errors],
        }

        output_path = self.workspace_path / "error_buster_report.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(output_path)

    def _generate_markdown_report(self, summary: WorkspaceSummary) -> str:
        """Generate Markdown format report"""
        md_content = f"""# 🔍 Error Buster Report

**Generated:** {summary.timestamp}
**Workspace:** {self.workspace_path}

## 📊 Summary

- **Files Scanned:** {summary.total_files_scanned}
- **Total Issues:** {summary.total_errors}
- **Critical:** {summary.critical_errors}
- **Errors:** {summary.errors}
- **Warnings:** {summary.warnings}
- **Info:** {summary.info_issues}

**Tools Used:** {", ".join(summary.tools_used)}

## 🚨 Issues Found

"""

        # Group errors by severity
        for severity in ["critical", "error", "warning", "info"]:
            severity_errors = [e for e in self.errors if e.severity == severity]

            if severity_errors:
                md_content += (
                    f"\n### {severity.title()} Issues ({len(severity_errors)})\n\n"
                )

                for error in severity_errors:
                    md_content += f"#### {error.file_path}:{error.line_number}\n\n"
                    md_content += f"**Type:** {error.error_type}  \n"
                    md_content += f"**Message:** {error.message}  \n"
                    md_content += f"**Tool:** {error.tool}  \n"

                    if error.rule_code:
                        md_content += f"**Rule:** {error.rule_code}  \n"

                    if error.suggestion:
                        md_content += f"**Suggestion:** {error.suggestion}  \n"

                    md_content += "\n"

        output_path = self.workspace_path / "error_buster_report.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return str(output_path)

    def _generate_copilot_report(self, summary: WorkspaceSummary) -> str:
        """Generate Copilot-friendly report with actionable commands"""
        copilot_content = f"""# 🤖 Copilot Action Report

## Quick Stats
- {summary.total_errors} issues found across {summary.total_files_scanned} files
- {summary.critical_errors} critical, {summary.errors} errors, {summary.warnings} warnings

## Priority Actions

"""

        # Sort errors by severity and file
        priority_errors = sorted(
            [e for e in self.errors if e.severity in ["critical", "error"]],
            key=lambda x: (x.severity == "error", x.file_path, x.line_number),
        )

        for error in priority_errors[:20]:  # Top 20 priority issues
            copilot_content += f"""### Fix: {error.file_path}:{error.line_number}

**Problem:** {error.message}
**Type:** {error.error_type} ({error.severity})
**Tool:** {error.tool}

```
File: {error.file_path}
Line: {error.line_number}
Column: {error.column_number}
```

"""
            if error.suggestion:
                copilot_content += f"**Suggested Fix:** {error.suggestion}\n\n"

            if error.context_lines:
                copilot_content += "**Context:**\n```\n"
                for i, line in enumerate(error.context_lines):
                    line_num = error.line_number - len(error.context_lines) // 2 + i
                    marker = ">>> " if line_num == error.line_number else "    "
                    copilot_content += f"{marker}{line_num:4d}: {line}\n"
                copilot_content += "```\n\n"

            copilot_content += "---\n\n"

        output_path = self.workspace_path / "copilot_action_report.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(copilot_content)

        return str(output_path)

    def run_analysis(
        self, output_formats: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Run complete workspace analysis"""
        if output_formats is None:
            output_formats = ["json", "copilot"]

        start_time = datetime.now()

        print("🚀 Starting Error Buster analysis...")

        # Scan and analyze files
        files = self.scan_workspace()

        for file_path in files:
            try:
                self.analyze_file(file_path)
                if self.files_scanned % 50 == 0:
                    safe_print(f"   📋 Analyzed {self.files_scanned} files...")
            except KeyboardInterrupt:
                print("\n[WARN] Analysis interrupted by user")
                break
            except Exception as e:
                safe_print(f"   ❌ Error analyzing {file_path}: {e}")

        # Calculate scan duration
        scan_duration = (datetime.now() - start_time).total_seconds()

        print("\n✅ Analysis complete!")
        safe_print(
            f"📊 Scanned {self.files_scanned} files in {scan_duration:.2f} seconds"
        )
        safe_print(f"🔍 Found {len(self.errors)} issues")

        # Generate reports
        report_paths = {}
        for fmt in output_formats:
            try:
                path = self.generate_report(fmt)
                report_paths[fmt] = path
                safe_print(f"📄 {fmt.upper()} report: {path}")
            except Exception as e:
                safe_print(f"❌ Failed to generate {fmt} report: {e}")

        return report_paths


def main():
    """Command-line interface for Error Buster"""
    import argparse

    parser = argparse.ArgumentParser(description="Error Buster Developer Tool")
    parser.add_argument(
        "--workspace", "-w", default=".", help="Workspace directory to analyze"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "markdown", "copilot"],
        action="append",
        help="Output format(s)",
    )
    parser.add_argument(
        "--exclude", "-e", action="append", help="Directories to exclude"
    )

    args = parser.parse_args()

    # Initialize Error Buster
    error_buster = ErrorBuster(workspace_path=args.workspace, exclude_dirs=args.exclude)

    # Run analysis
    output_formats = args.format or ["json", "copilot"]
    report_paths = error_buster.run_analysis(output_formats)

    print("\n🎉 Error Buster analysis complete!")
    print("📋 Generated reports:")
    for fmt, path in report_paths.items():
        safe_print(f"   - {fmt.upper()}: {path}")


if __name__ == "__main__":
    main()

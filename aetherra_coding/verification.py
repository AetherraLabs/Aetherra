"""Verification engine for generated Python code.

This module provides layered validation intended for the code generation
pipeline:
  1) Syntax validation (AST parse)
  2) Import validation (import resolution)
  3) Style validation (basic static checks)
  4) Type validation (optional mypy invocation)
  5) Logic validation (dangerous/broad patterns)
"""

from __future__ import annotations

import ast
import importlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VerificationIssue:
    """Single verification finding."""

    category: str
    message: str
    severity: str = "error"
    line: int | None = None


@dataclass
class VerificationResult:
    """Aggregate verification result."""

    passed: bool
    syntax_ok: bool
    imports_ok: bool
    style_ok: bool
    types_ok: bool
    logic_ok: bool
    issues: list[VerificationIssue] = field(default_factory=list)

    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


class VerificationEngine:
    """Layered validator for Python source content."""

    def __init__(self, max_line_length: int = 100) -> None:
        self.max_line_length = max_line_length

    def verify_code(self, code: str, run_mypy: bool = False) -> VerificationResult:
        """Verify source code text using all available validators."""
        issues: list[VerificationIssue] = []

        syntax_ok = self._validate_syntax(code, issues)
        imports_ok = self._validate_imports(code, issues) if syntax_ok else False
        style_ok = self._validate_style(code, issues)
        types_ok = (
            self._validate_types(code, issues, run_mypy=run_mypy)
            if syntax_ok
            else False
        )
        logic_ok = self._validate_logic(code, issues) if syntax_ok else False

        passed = (
            syntax_ok
            and imports_ok
            and style_ok
            and types_ok
            and logic_ok
            and all(i.severity != "error" for i in issues)
        )

        return VerificationResult(
            passed=passed,
            syntax_ok=syntax_ok,
            imports_ok=imports_ok,
            style_ok=style_ok,
            types_ok=types_ok,
            logic_ok=logic_ok,
            issues=issues,
        )

    def verify_file(
        self, file_path: str | Path, run_mypy: bool = False
    ) -> VerificationResult:
        """Read and verify a Python file."""
        path = Path(file_path)
        try:
            code = path.read_text(encoding="utf-8")
        except Exception as exc:
            return VerificationResult(
                passed=False,
                syntax_ok=False,
                imports_ok=False,
                style_ok=False,
                types_ok=False,
                logic_ok=False,
                issues=[VerificationIssue("file", f"Failed to read file: {exc}")],
            )
        return self.verify_code(code, run_mypy=run_mypy)

    def _validate_syntax(self, code: str, issues: list[VerificationIssue]) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError as exc:
            issues.append(
                VerificationIssue(
                    category="syntax",
                    message=str(exc),
                    severity="error",
                    line=getattr(exc, "lineno", None),
                )
            )
            return False

    def _validate_imports(self, code: str, issues: list[VerificationIssue]) -> bool:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False

        ok = True
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if not self._can_import(mod):
                        ok = False
                        issues.append(
                            VerificationIssue(
                                category="import",
                                message=f"Cannot resolve import '{mod}'",
                                severity="error",
                                line=getattr(node, "lineno", None),
                            )
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    # Relative imports are context-dependent; don't fail hard.
                    issues.append(
                        VerificationIssue(
                            category="import",
                            message="Relative import skipped for standalone verification",
                            severity="warning",
                            line=getattr(node, "lineno", None),
                        )
                    )
                    continue
                mod = (node.module or "").split(".")[0]
                if mod and not self._can_import(mod):
                    ok = False
                    issues.append(
                        VerificationIssue(
                            category="import",
                            message=f"Cannot resolve import-from '{node.module}'",
                            severity="error",
                            line=getattr(node, "lineno", None),
                        )
                    )
        return ok

    def _validate_style(self, code: str, issues: list[VerificationIssue]) -> bool:
        ok = True
        for idx, line in enumerate(code.splitlines(), start=1):
            if len(line) > self.max_line_length:
                ok = False
                issues.append(
                    VerificationIssue(
                        category="style",
                        message=f"Line exceeds {self.max_line_length} characters",
                        severity="error",
                        line=idx,
                    )
                )
            if line.endswith(" "):
                ok = False
                issues.append(
                    VerificationIssue(
                        category="style",
                        message="Trailing whitespace",
                        severity="error",
                        line=idx,
                    )
                )
            if "\t" in line:
                ok = False
                issues.append(
                    VerificationIssue(
                        category="style",
                        message="Tab indentation found; use spaces",
                        severity="error",
                        line=idx,
                    )
                )
        return ok

    def _validate_types(
        self, code: str, issues: list[VerificationIssue], run_mypy: bool
    ) -> bool:
        if not run_mypy:
            return True
        if shutil.which("mypy") is None:
            issues.append(
                VerificationIssue(
                    category="types",
                    message="mypy not installed; type validation skipped",
                    severity="warning",
                )
            )
            return True

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "_verify_tmp.py"
            p.write_text(code, encoding="utf-8")
            proc = subprocess.run(
                ["mypy", str(p), "--hide-error-context", "--no-error-summary"],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                for raw in (proc.stdout or "").splitlines():
                    issues.append(
                        VerificationIssue(
                            category="types",
                            message=raw.strip() or "mypy type error",
                            severity="error",
                        )
                    )
                return False
        return True

    def _validate_logic(self, code: str, issues: list[VerificationIssue]) -> bool:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False

        ok = True
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"eval", "exec"}:
                    ok = False
                    issues.append(
                        VerificationIssue(
                            category="logic",
                            message=f"Dangerous call '{node.func.id}' is not allowed",
                            severity="error",
                            line=getattr(node, "lineno", None),
                        )
                    )
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    if handler.type is None:
                        issues.append(
                            VerificationIssue(
                                category="logic",
                                message="Bare except detected",
                                severity="warning",
                                line=getattr(handler, "lineno", None),
                            )
                        )
                    elif (
                        isinstance(handler.type, ast.Name)
                        and handler.type.id == "Exception"
                    ):
                        issues.append(
                            VerificationIssue(
                                category="logic",
                                message="Broad except Exception detected",
                                severity="warning",
                                line=getattr(handler, "lineno", None),
                            )
                        )
        return ok

    @staticmethod
    def _can_import(module_name: str) -> bool:
        try:
            importlib.import_module(module_name)
            return True
        except Exception:
            return False


def verify_code(
    code: str, run_mypy: bool = False, max_line_length: int = 100
) -> VerificationResult:
    """Convenience function for one-shot verification."""
    engine = VerificationEngine(max_line_length=max_line_length)
    return engine.verify_code(code, run_mypy=run_mypy)

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Aetherra Labs and Contributors

"""Generate a Phase 1.1 stub inventory JSON for production planning."""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import logging
import os
import re
import tokenize
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "STUB_INVENTORY.json"

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist-packages",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

TOKEN_PATTERNS = {
    "todo": re.compile(r"\bTODO\b", re.IGNORECASE),
    "fixme": re.compile(r"\bFIXME\b", re.IGNORECASE),
    "placeholder": re.compile(r"\bplaceholder\b", re.IGNORECASE),
    "stub": re.compile(r"\bstub\b", re.IGNORECASE),
}

HIGH_IMPACT_PATH_HINTS = (
    "aetherra_core/kernel",
    "aetherra_core/engine",
    "aetherra_core/memory",
    "aetherra_core/orchestration",
    "aetherra_core/agents",
    "consciousness",
)


@dataclass
class StubEntry:
    file: Path
    function: str
    line_start: int
    line_end: int
    reason: str
    severity: str


@dataclass(frozen=True)
class StubInventoryWritePlan:
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


def _guardian_preflight_stub_inventory(
    *,
    project_root: Path,
    plan: StubInventoryWritePlan,
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    summary = plan.data.get("summary", {})
    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.stub_inventory_write",
            target="maintenance:stub_inventory",
            purpose="Write generated stub inventory JSON",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Planned stub inventory JSON is written to disk",
            reversible=True,
            rollback_plan="delete generated stub inventory or restore from version control",
            metadata={
                "project_root_hash": _hash_value(project_root.resolve()),
                "output_path_hash": _hash_value(
                    _safe_relative_path(plan.file_path, project_root)
                ),
                "total_stubs": summary.get("total_stubs", 0),
                "severity_counts": summary.get("by_severity", {}),
                "module_count": len(summary.get("by_module", {})),
                "inventory_size_bytes": len(
                    json.dumps(plan.data, ensure_ascii=False, default=str)
                ),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def write_stub_inventory(
    *,
    project_root: Path = PROJECT_ROOT,
    plan: StubInventoryWritePlan,
) -> bool:
    decision = _guardian_preflight_stub_inventory(project_root=project_root, plan=plan)
    if not decision.allowed:
        print(f"Guardian denied stub inventory write: {decision.reason}")
        return False

    plan.file_path.parent.mkdir(parents=True, exist_ok=True)
    plan.file_path.write_text(
        json.dumps(plan.data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return True


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if should_skip(path):
            continue
        yield path


def path_to_module(path: Path) -> str:
    rel = path.relative_to(PROJECT_ROOT)
    return ".".join(rel.with_suffix("").parts)


def classify_severity(path: Path, reason: str) -> str:
    path_str = path.as_posix().lower()
    high_impact = any(hint in path_str for hint in HIGH_IMPACT_PATH_HINTS)

    if "NotImplementedError" in reason:
        return "critical" if high_impact else "high"
    if "pass-only" in reason:
        return "critical" if high_impact else "medium"
    if "placeholder" in reason or "stub" in reason:
        return "high" if high_impact else "medium"
    if "TODO" in reason or "FIXME" in reason:
        return "high" if high_impact else "medium"
    return "low"


def detect_text_markers(path: Path, source: str) -> list[StubEntry]:
    entries: list[StubEntry] = []
    string_lines: set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type != tokenize.STRING:
                continue
            start_line = tok.start[0]
            end_line = tok.end[0]
            for line_no in range(start_line, end_line + 1):
                string_lines.add(line_no)
    except Exception as exc:
        logger.debug("Tokenization failed for %s: %s", path, exc)

    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        if idx in string_lines:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        for token, pattern in TOKEN_PATTERNS.items():
            if pattern.search(line):
                reason = f"{token.upper()} marker"
                severity = classify_severity(path, reason)
                entries.append(
                    StubEntry(
                        file=path,
                        function="<module>",
                        line_start=idx,
                        line_end=idx,
                        reason=reason,
                        severity=severity,
                    )
                )
                break
    return entries


def is_pass_only(body: list[ast.stmt]) -> bool:
    if not body:
        return False

    statements = body
    if statements and isinstance(statements[0], ast.Expr):
        first_value = getattr(statements[0], "value", None)
        if isinstance(first_value, ast.Constant) and isinstance(first_value.value, str):
            statements = statements[1:]

    return len(statements) == 1 and isinstance(statements[0], ast.Pass)


def line_end(node: ast.AST) -> int:
    return getattr(node, "end_lineno", getattr(node, "lineno", 0))


def has_decorator(node: ast.AST, names: set[str]) -> bool:
    decorators = getattr(node, "decorator_list", [])
    for decorator in decorators:
        if isinstance(decorator, ast.Name) and decorator.id in names:
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr in names:
            return True
    return False


def is_exception_class(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id.endswith("Error"):
            return True
        if isinstance(base, ast.Attribute) and base.attr.endswith("Error"):
            return True
    return False


def detect_ast_stubs(path: Path, tree: ast.AST) -> list[StubEntry]:
    entries: list[StubEntry] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if is_pass_only(node.body) and not has_decorator(node, {"abstractmethod"}):
                reason = "pass-only implementation"
                severity = classify_severity(path, reason)
                entries.append(
                    StubEntry(
                        file=path,
                        function=node.name,
                        line_start=node.lineno,
                        line_end=line_end(node),
                        reason=reason,
                        severity=severity,
                    )
                )
            for inner in ast.walk(node):
                if isinstance(inner, ast.Raise) and isinstance(inner.exc, ast.Call):
                    fn = inner.exc.func
                    if isinstance(fn, ast.Name) and fn.id == "NotImplementedError":
                        reason = "raises NotImplementedError"
                        severity = classify_severity(path, reason)
                        entries.append(
                            StubEntry(
                                file=path,
                                function=node.name,
                                line_start=inner.lineno,
                                line_end=line_end(inner),
                                reason=reason,
                                severity=severity,
                            )
                        )

        if isinstance(node, ast.ClassDef) and is_pass_only(node.body):
            if is_exception_class(node):
                continue
            reason = "pass-only class"
            severity = classify_severity(path, reason)
            entries.append(
                StubEntry(
                    file=path,
                    function=node.name,
                    line_start=node.lineno,
                    line_end=line_end(node),
                    reason=reason,
                    severity=severity,
                )
            )

    return entries


def collect_import_index(py_files: list[Path]) -> dict[str, int]:
    imports = defaultdict(set)
    for path in py_files:
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except Exception as exc:
            logger.debug("Failed to parse imports for %s: %s", path, exc)
            continue

        importer = path_to_module(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.name].add(importer)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports[node.module].add(importer)

    return {name: len(users) for name, users in imports.items()}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON path (default: docs/STUB_INVENTORY.json)",
    )
    parser.add_argument(
        "--include-tools",
        action="store_true",
        help="Include stubs from tools/ in the inventory.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include stubs from tests/ in the inventory.",
    )
    return parser


def main(
    output_path: Path = DEFAULT_OUTPUT,
    include_tools: bool = False,
    include_tests: bool = False,
) -> int:
    py_files = list(iter_python_files(PROJECT_ROOT / "Aetherra"))
    if include_tools:
        py_files.extend(iter_python_files(PROJECT_ROOT / "tools"))
    if include_tests:
        py_files.extend(iter_python_files(PROJECT_ROOT / "tests"))

    # De-duplicate in case of overlap from repeated roots.
    py_files = sorted(set(py_files))

    import_index = collect_import_index(py_files)

    all_entries: list[StubEntry] = []
    for path in py_files:
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except SyntaxError:
            continue
        except Exception as exc:
            logger.debug("Failed to analyze %s: %s", path, exc)
            continue

        all_entries.extend(detect_ast_stubs(path, tree))
        all_entries.extend(detect_text_markers(path, source))

    by_severity = Counter(entry.severity for entry in all_entries)
    by_module = Counter(path_to_module(entry.file) for entry in all_entries)

    stubs = []
    for i, entry in enumerate(
        sorted(all_entries, key=lambda e: (str(e.file), e.line_start)), start=1
    ):
        module = path_to_module(entry.file)
        stubs.append(
            {
                "id": f"STUB_{i:04d}",
                "file": str(entry.file.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "function": entry.function,
                "severity": entry.severity,
                "reason": entry.reason,
                "lines": f"{entry.line_start}-{entry.line_end}",
                "blocking_count": import_index.get(module, 0),
            }
        )

    summary = {
        "total_stubs": len(stubs),
        "by_severity": {
            "critical": by_severity.get("critical", 0),
            "high": by_severity.get("high", 0),
            "medium": by_severity.get("medium", 0),
            "low": by_severity.get("low", 0),
        },
        "by_module": dict(by_module.most_common(50)),
    }

    output_data = {
        "summary": summary,
        "stubs": stubs,
        "generated_at": datetime.now(UTC).isoformat(),
        "generator": "tools/maintenance/generate_stub_inventory.py",
    }
    plan = StubInventoryWritePlan(file_path=output_path, data=output_data)

    if not write_stub_inventory(project_root=PROJECT_ROOT, plan=plan):
        return 1

    print(f"Wrote {len(stubs)} stubs to {output_path}")
    return 0


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    raise SystemExit(
        main(
            output_path=args.output,
            include_tools=args.include_tools,
            include_tests=args.include_tests,
        )
    )

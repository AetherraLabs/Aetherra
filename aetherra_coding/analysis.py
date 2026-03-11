"""Production-oriented analysis module for code generation safety.

Provides:
  - Dependency graph construction from Python imports
  - Dependents / transitive dependents lookup
  - Multi-factor impact scoring for proposed changes
  - Backward-compatible `analyze_patch` helper
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ImpactReport:
    touched_files: list[Path]
    suggested_tests: list[str]
    risk_level: str  # low|medium|high


@dataclass
class RiskProfile:
    file: Path
    changed_lines: int
    direct_dependents: list[Path]
    transitive_dependents: list[Path]
    affected_count: int
    score: float
    risk_level: str
    suggested_tests: list[str] = field(default_factory=list)
    factors: dict[str, float] = field(default_factory=dict)


class DependencyGraphBuilder:
    """Build and query an import dependency graph for Python source files."""

    def __init__(self) -> None:
        self.graph: dict[Path, set[Path]] = {}
        self.reverse_graph: dict[Path, set[Path]] = {}
        self.project_root: Path | None = None

    def build_graph(self, project_root: str | Path) -> dict[Path, set[Path]]:
        root = Path(project_root).resolve()
        self.project_root = root
        self.graph.clear()
        self.reverse_graph.clear()

        py_files = [
            p
            for p in root.rglob("*.py")
            if not any(part.startswith(".") for part in p.parts)
            and "__pycache__" not in p.parts
            and ".venv" not in p.parts
            and "dist-packages" not in p.parts
        ]

        module_map = self._module_map(py_files, root)

        for py_file in py_files:
            rel_file = py_file.relative_to(root)
            self.graph.setdefault(rel_file, set())
            imports = self._extract_imports(py_file)
            for imp in imports:
                target = module_map.get(imp)
                if target is not None and target != rel_file:
                    self.graph[rel_file].add(target)
                    self.reverse_graph.setdefault(target, set()).add(rel_file)
                    self.reverse_graph.setdefault(rel_file, set())

        return self.graph

    def find_dependents(self, filepath: str | Path) -> list[Path]:
        target = self._normalize(filepath)
        dependents = sorted(self.reverse_graph.get(target, set()))
        return dependents

    def find_transitive_dependents(self, filepath: str | Path) -> list[Path]:
        target = self._normalize(filepath)
        seen: set[Path] = set()
        queue: list[Path] = list(self.reverse_graph.get(target, set()))
        while queue:
            cur = queue.pop(0)
            if cur in seen:
                continue
            seen.add(cur)
            queue.extend(self.reverse_graph.get(cur, set()))
        return sorted(seen)

    def detect_cycles(self) -> list[list[Path]]:
        cycles: list[list[Path]] = []
        visiting: set[Path] = set()
        visited: set[Path] = set()
        stack: list[Path] = []

        def dfs(node: Path) -> None:
            if node in visiting:
                if node in stack:
                    idx = stack.index(node)
                    cycles.append(stack[idx:] + [node])
                return
            if node in visited:
                return

            visiting.add(node)
            stack.append(node)
            for nei in self.graph.get(node, set()):
                dfs(nei)
            stack.pop()
            visiting.remove(node)
            visited.add(node)

        for node in list(self.graph.keys()):
            dfs(node)

        return cycles

    def _module_map(self, files: list[Path], root: Path) -> dict[str, Path]:
        mapping: dict[str, Path] = {}
        for p in files:
            rel = p.relative_to(root)
            mod = ".".join(rel.with_suffix("").parts)
            mapping[mod] = rel
            mapping[mod.split(".")[-1]] = rel
        return mapping

    @staticmethod
    def _extract_imports(file_path: Path) -> set[str]:
        try:
            src = file_path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except Exception:
            return set()

        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        return imports

    def _normalize(self, filepath: str | Path) -> Path:
        p = Path(filepath)
        if self.project_root and p.is_absolute():
            try:
                return p.relative_to(self.project_root)
            except Exception:
                return p
        return p


class ImpactAnalyzer:
    """Multi-factor impact analysis built on dependency graph data."""

    def __init__(self, graph_builder: DependencyGraphBuilder | None = None) -> None:
        self.graph_builder = graph_builder or DependencyGraphBuilder()

    def analyze_change(
        self,
        file: str | Path,
        changes: str,
        project_root: str | Path,
    ) -> RiskProfile:
        self.graph_builder.build_graph(project_root)
        target = self.graph_builder._normalize(file)

        direct = self.graph_builder.find_dependents(target)
        transitive = self.graph_builder.find_transitive_dependents(target)
        changed_lines = self._count_changed_lines(changes)

        factors = {
            "affected_factor": min(1.0, len(transitive) / 20.0),
            "magnitude_factor": min(1.0, changed_lines / 200.0),
            "api_change_factor": self._api_change_factor(changes),
            "test_factor": self._test_factor(target),
        }

        score = self._score_factors(factors)
        if score >= 70:
            risk_level = "high"
        elif score >= 35:
            risk_level = "medium"
        else:
            risk_level = "low"

        suggested_tests = self._suggest_tests(target, transitive)

        return RiskProfile(
            file=Path(target),
            changed_lines=changed_lines,
            direct_dependents=direct,
            transitive_dependents=transitive,
            affected_count=len(transitive),
            score=score,
            risk_level=risk_level,
            suggested_tests=suggested_tests,
            factors=factors,
        )

    @staticmethod
    def _count_changed_lines(changes: str) -> int:
        return sum(
            1
            for l in changes.splitlines()
            if (l.startswith("+") and not l.startswith("+++"))
            or (l.startswith("-") and not l.startswith("---"))
        )

    @staticmethod
    def _api_change_factor(changes: str) -> float:
        lowered = changes.lower()
        tokens = ["def ", "class ", "public", "@api", "route(", "endpoint"]
        hits = sum(1 for t in tokens if t in lowered)
        return min(1.0, hits / 3.0)

    @staticmethod
    def _test_factor(target: Path) -> float:
        s = str(target).replace("\\", "/")
        if "/tests/" in f"/{s}/" or s.startswith("tests/"):
            return 0.0
        return 0.4

    @staticmethod
    def _score_factors(factors: dict[str, float]) -> float:
        # Weighted score out of 100
        return (
            factors["affected_factor"] * 35.0
            + factors["magnitude_factor"] * 30.0
            + factors["api_change_factor"] * 25.0
            + factors["test_factor"] * 10.0
        )

    @staticmethod
    def _suggest_tests(target: Path, transitive: list[Path]) -> list[str]:
        candidates: list[str] = []
        all_paths = [target] + transitive
        for p in all_paths:
            s = str(p).replace("\\", "/")
            stem = Path(s).stem
            if s.startswith("tests/"):
                candidates.append(s)
            else:
                candidates.append(f"tests/unit/test_{stem}.py")
        # Deduplicate preserving order
        seen: set[str] = set()
        out: list[str] = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return out[:20]


def analyze_patch(diff_text: str) -> ImpactReport:
    """Backward-compatible helper for quick patch-level risk estimation."""
    touched: list[Path] = []
    for line in diff_text.splitlines():
        if line.startswith("*** Update File:") or line.startswith("*** Add File:"):
            p = Path(line.split(":", 1)[1].strip())
            touched.append(p)

    risk = "low"
    if len(touched) > 5:
        risk = "medium"
    if len(touched) > 12:
        risk = "high"

    suggested_tests: list[str] = []
    for p in touched[:10]:
        stem = p.stem
        suggested_tests.append(f"tests/unit/test_{stem}.py")

    return ImpactReport(
        touched_files=touched,
        suggested_tests=suggested_tests,
        risk_level=risk,
    )

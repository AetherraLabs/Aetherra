"""Lyrixa Code Orchestrator (Phase 0 skeleton)

Responsible for coordinating plan -> generate -> apply_patch -> verify -> commit.
This initial implementation is intentionally minimal and synchronous.

Contracts (stable for internal callers):
    plan(intent: str, scope: list[str] | None) -> PlanResult
    generate(step_index: int, dry_run: bool = True) -> PatchResult
    apply_patch(diff_text: str, dry_run: bool = False) -> PatchResult
    verify(run_spec_tests_gate: bool = True, run_quality_gates: bool = True) -> VerifyResult
    commit(message: str, sign: bool = False) -> CommitResult

Autonomy modes (env or param): assist | co-drive | autopilot
Behavior (Phase 0):
    assist   : never auto-apply patches; only preview
    co-drive : auto-apply patches classified 'low' risk (placeholder heuristic)
    autopilot: apply all patches after verify passes and create git commit

Risk heuristic (placeholder): patch line count <= 50 => low.

Note: Further phases will delegate to specialization agents & analysis modules.
"""

from __future__ import annotations

# Standard library imports
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Local imports
from . import audit, ops_engine, safety


# -------- Result dataclasses ---------
@dataclass
class PlanStep:
    description: str
    target_files: list[str] = field(default_factory=list)
    tests_required: bool = True


@dataclass
class PlanResult:
    intent: str
    steps: list[PlanStep]
    created_at: float


@dataclass
class PatchResult:
    applied: bool
    dry_run: bool
    diff: str
    rollback_token: str | None = None
    summary: str | None = None
    diagnostics: list[str] = field(default_factory=list)
    risk_level: str | None = None
    changed_lines: int | None = None


@dataclass
class VerifyResult:
    passed: bool
    spec_tests_gate: bool
    quality_gates: bool
    aether_risk: bool
    format_lint: bool | None
    diagnostics: list[str] = field(default_factory=list)


@dataclass
class CommitResult:
    committed: bool
    sha: str | None
    message: str
    diagnostics: list[str] = field(default_factory=list)


@dataclass
class ParsedIntent:
    """Structured representation of a natural-language coding intent."""

    raw_intent: str
    intent_type: str
    target_name: str
    entities: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    complexity: str = "medium"


@dataclass
class CodeGenStep:
    """Single code-generation step in a structured plan."""

    name: str
    description: str
    output_type: str = "code"


@dataclass
class CodeGenerationPlan:
    """Plan generated from a parsed intent."""

    parsed_intent: ParsedIntent
    steps: list[CodeGenStep]
    estimated_effort: str
    target_file: str
    test_file: str


@dataclass
class GeneratedCode:
    """Output of the code generation workflow."""

    source_code: str
    test_code: str
    docs: str


class IntentParser:
    """Pattern-based parser that extracts entities and constraints from intent text."""

    _FUNC_PATTERNS = [
        re.compile(r"\bfunction\s+(?:to\s+)?([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE),
        re.compile(r"\bmethod\s+(?:to\s+)?([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE),
    ]
    _CLASS_PATTERNS = [
        re.compile(r"\bclass\s+([A-Z][a-zA-Z0-9_]*)", re.IGNORECASE),
        re.compile(r"\bbuild\s+(?:a\s+)?class\s+([A-Z][a-zA-Z0-9_]*)", re.IGNORECASE),
    ]

    def parse(self, intent: str) -> ParsedIntent:
        text = (intent or "").strip()
        lowered = text.lower()

        intent_type = "module"
        target_name = "generated_artifact"
        entities: list[str] = []
        requirements: list[str] = []
        constraints: list[str] = []
        dependencies: list[str] = []

        for pat in self._FUNC_PATTERNS:
            m = pat.search(text)
            if m:
                intent_type = "function"
                target_name = m.group(1)
                entities.append("function")
                break

        if intent_type == "module":
            for pat in self._CLASS_PATTERNS:
                m = pat.search(text)
                if m:
                    intent_type = "class"
                    target_name = m.group(1)
                    entities.append("class")
                    break

        if "recursive" in lowered:
            constraints.append("recursive")
            requirements.append("base case")
        if "async" in lowered:
            constraints.append("async")
        if "error handling" in lowered or "handle errors" in lowered:
            requirements.append("error handling")
        if "docstring" in lowered or "document" in lowered:
            requirements.append("docstring")
        if "test" in lowered:
            requirements.append("tests")

        if "flask" in lowered:
            dependencies.append("flask")
        if "fastapi" in lowered:
            dependencies.append("fastapi")
        if "pandas" in lowered:
            dependencies.append("pandas")

        if any(k in lowered for k in ["simple", "small", "quick"]):
            complexity = "low"
        elif any(k in lowered for k in ["enterprise", "distributed", "scalable", "complex"]):
            complexity = "high"
        else:
            complexity = "medium"

        if intent_type == "module" and "api" in lowered:
            entities.append("api")
            target_name = "api_module"

        return ParsedIntent(
            raw_intent=text,
            intent_type=intent_type,
            target_name=target_name,
            entities=entities,
            requirements=requirements,
            constraints=constraints,
            dependencies=dependencies,
            complexity=complexity,
        )


class PlanGenerator:
    """Generates structured build plans from ParsedIntent objects."""

    def generate(
        self, parsed_intent: ParsedIntent, scope: list[str] | None = None
    ) -> CodeGenerationPlan:
        target_file = scope[0] if scope else f"generated/{parsed_intent.target_name}.py"
        test_file = self._derive_test_file(target_file)

        steps = [
            CodeGenStep("skeleton", "Generate code skeleton", "code"),
            CodeGenStep("logic", "Add business logic", "code"),
            CodeGenStep("errors", "Add error handling", "code"),
            CodeGenStep("docs", "Add documentation", "docs"),
            CodeGenStep("tests", "Generate unit tests", "tests"),
        ]

        if parsed_intent.complexity == "low":
            effort = "1-2h"
        elif parsed_intent.complexity == "high":
            effort = "6-10h"
        else:
            effort = "3-5h"

        return CodeGenerationPlan(
            parsed_intent=parsed_intent,
            steps=steps,
            estimated_effort=effort,
            target_file=target_file,
            test_file=test_file,
        )

    @staticmethod
    def _derive_test_file(target_file: str) -> str:
        p = Path(target_file)
        stem = p.stem or "generated"
        return str(Path("tests") / "unit" / f"test_{stem}.py")


class CodeGenerationWorkflow:
    """Step-based workflow that generates runnable source code and tests."""

    def execute(self, plan: CodeGenerationPlan) -> GeneratedCode:
        code = self._generate_skeleton(plan.parsed_intent)
        code = self._add_logic(code, plan.parsed_intent)
        code = self._add_error_handling(code)
        docs = self._generate_docs(plan.parsed_intent)
        tests = self._generate_tests(plan.parsed_intent)
        return GeneratedCode(source_code=code, test_code=tests, docs=docs)

    def _generate_skeleton(self, parsed: ParsedIntent) -> str:
        if parsed.intent_type == "class":
            class_name = parsed.target_name[:1].upper() + parsed.target_name[1:]
            return (
                f"class {class_name}:\n"
                f"    \"\"\"Auto-generated class for intent: {parsed.raw_intent}\"\"\"\n"
                "\n"
                "    def __init__(self):\n"
                "        self._ready = True\n"
            )
        fn = parsed.target_name
        if "async" in parsed.constraints:
            return (
                f"async def {fn}(value):\n"
                f"    \"\"\"Auto-generated function for intent: {parsed.raw_intent}\"\"\"\n"
                "    return value\n"
            )
        return (
            f"def {fn}(value):\n"
            f"    \"\"\"Auto-generated function for intent: {parsed.raw_intent}\"\"\"\n"
            "    return value\n"
        )

    def _add_logic(self, skeleton: str, parsed: ParsedIntent) -> str:
        code = skeleton
        if parsed.intent_type == "function" and "factorial" in parsed.target_name.lower():
            code = code.replace(
                "    return value\n",
                "    if value < 0:\n"
                "        raise ValueError('value must be >= 0')\n"
                "    if value <= 1:\n"
                "        return 1\n"
                "    return value * factorial(value - 1)\n",
            )
        return code

    def _add_error_handling(self, code: str) -> str:
        if "raise ValueError" in code:
            return code
        if "def " in code and "return value" in code:
            return code.replace(
                "    return value\n",
                "    if value is None:\n"
                "        raise ValueError('value is required')\n"
                "    return value\n",
            )
        return code

    def _generate_docs(self, parsed: ParsedIntent) -> str:
        return (
            f"Intent type: {parsed.intent_type}\n"
            f"Target: {parsed.target_name}\n"
            f"Requirements: {', '.join(parsed.requirements) if parsed.requirements else 'none'}\n"
            f"Constraints: {', '.join(parsed.constraints) if parsed.constraints else 'none'}\n"
            f"Dependencies: {', '.join(parsed.dependencies) if parsed.dependencies else 'none'}\n"
        )

    def _generate_tests(self, parsed: ParsedIntent) -> str:
        fn = parsed.target_name
        if parsed.intent_type == "class":
            class_name = parsed.target_name[:1].upper() + parsed.target_name[1:]
            return (
                f"from generated.{parsed.target_name.lower()} import {class_name}\n\n"
                "def test_class_initializes():\n"
                f"    obj = {class_name}()\n"
                "    assert obj._ready is True\n"
            )
        return (
            f"from generated.{fn} import {fn}\n\n"
            f"def test_{fn}_basic():\n"
            f"    assert {fn}(1) == 1\n"
        )


# ------------- Orchestrator ----------------
class CodeOrchestrator:
    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root).resolve()
        self._plan: PlanResult | None = None
        self._parsed_intent: ParsedIntent | None = None
        self._codegen_plan: CodeGenerationPlan | None = None
        self.mode = os.getenv("AETHERRA_MODE", "assist")
        self._rollback_store = self.repo_root / ".aetherra" / "rollback"
        self._rollback_store.mkdir(parents=True, exist_ok=True)
        self.intent_parser = IntentParser()
        self.plan_generator = PlanGenerator()
        self.codegen_workflow = CodeGenerationWorkflow()

    # ---- Public API ----
    def plan(self, intent: str, scope: list[str] | None = None) -> PlanResult:
        self._parsed_intent = self.intent_parser.parse(intent)
        self._codegen_plan = self.plan_generator.generate(self._parsed_intent, scope)

        steps: list[PlanStep] = []
        for s in self._codegen_plan.steps:
            steps.append(
                PlanStep(
                    description=f"{s.name}: {s.description}",
                    target_files=[self._codegen_plan.target_file],
                )
            )
        self._plan = PlanResult(intent=intent, steps=steps, created_at=time.time())
        audit.record_event(
            "plan",
            {
                "intent": intent,
                "intent_type": self._parsed_intent.intent_type,
                "target": self._parsed_intent.target_name,
                "steps": [s.description for s in steps],
            },
        )
        return self._plan

    def generate(self, step_index: int, dry_run: bool = True) -> PatchResult:
        if not self._plan:
            raise RuntimeError("No active plan; call plan() first")
        if step_index < 0 or step_index >= len(self._plan.steps):
            raise IndexError("step_index out of range")
        step = self._plan.steps[step_index]
        if not self._codegen_plan or not self._parsed_intent:
            raise RuntimeError("No structured generation plan available")

        generated = self.codegen_workflow.execute(self._codegen_plan)
        target = Path(self._codegen_plan.target_file)
        if target.exists():
            diff = ops_engine.build_comment_insertion_diff(
                target,
                (
                    f"Generated update for intent: {self._plan.intent}; "
                    f"step={step.description}; effort={self._codegen_plan.estimated_effort}"
                ),
            )
        else:
            diff = ops_engine.build_new_file_diff(target, generated.source_code + "\n")
        summary = f"Proposed patch touching {target}"
        audit.record_event("generate", {"step": step_index, "target": str(target)})
        lvl, changed = ops_engine.classify_risk(diff)
        return PatchResult(
            applied=False,
            dry_run=dry_run,
            diff=diff,
            summary=summary,
            risk_level=lvl,
            changed_lines=changed,
        )

    def apply_patch(
        self, diff_text: str, dry_run: bool = False, colorize: bool = True
    ) -> PatchResult:
        raw = ops_engine.apply_unified_diff(
            diff_text, repo_root=self.repo_root, dry_run=dry_run
        )
        audit.record_event("apply_patch", {"dry_run": dry_run, "applied": raw.applied})
        # Autonomy mode could auto-stage
        if raw.applied and not dry_run and self.mode in {"co-drive", "autopilot"}:
            self._git_add_from_diff(diff_text)
        if raw.applied and raw.rollback_token:
            self._persist_rollback_snapshot(raw.rollback_token, raw.originals)
        # Use detailed risk classification for richer diagnostics
        risk_level, changed, added, removed = ops_engine.classify_risk_detailed(
            raw.diff
        )
        colored_diff = self._colorize_diff(raw.diff) if colorize else raw.diff
        pr = PatchResult(
            applied=raw.applied,
            dry_run=raw.dry_run,
            diff=colored_diff,
            rollback_token=raw.rollback_token,
            summary=(
                f"Applied patch ({len(raw.diagnostics)} diag, risk={risk_level}, +{added}/-{removed}, changed={changed})"
                if raw.applied
                else f"Dry run (risk={risk_level}, +{added}/-{removed}, changed={changed})"
            ),
            diagnostics=raw.diagnostics,
            risk_level=risk_level,
            changed_lines=changed,
        )
        return pr

    def verify(
        self,
        run_spec_tests_gate: bool = True,
        run_quality_gates: bool = True,
        strict_aether: bool = True,
        run_format_lint: bool = True,
    ) -> VerifyResult:
        """Run verification gates.

        Parameters:
            run_spec_tests_gate: execute spec → tests gate script.
            run_quality_gates: execute quality gates (tests + coverage etc.).
            strict_aether: enforce strict .aether script signature / risk rules.
            run_format_lint: run format/lint aggregator first (can be disabled via CLI flag or env).
        """
        diagnostics: list[str] = []

        # ---- Optional format/lint stage (run early so auto-fixes are included) ----
        format_lint_enabled_env = os.getenv("AETHERRA_FORMAT_LINT", "1") == "1"
        format_lint_ran = run_format_lint and format_lint_enabled_env
        format_lint_ok = True
        if format_lint_ran:
            fmt_tool = self.repo_root / "tools" / "format_lint.py"
            if fmt_tool.exists():
                format_lint_ok = self._run_tool(
                    ["python", str(fmt_tool)], diagnostics, label="format_lint"
                )
            else:
                diagnostics.append(
                    "[format_lint] missing script tools/format_lint.py (skipped)"
                )
                format_lint_ran = False  # treat as skipped

        # ---- Spec → Tests Gate ----
        spec_ok = True
        if run_spec_tests_gate:
            spec_ok = self._run_tool(
                ["python", "tools/spec_tests_gate.py"],
                diagnostics,
                label="spec_tests_gate",
            )

        # ---- Quality Gates ----
        quality_ok = True
        if run_quality_gates:
            quality_ok = self._run_tool(
                ["python", "tools/quality_gates.py"], diagnostics, label="quality_gates"
            )

        # ---- Aether risk / signature verifier ----
        aether_ok = safety.run_aether_risk_verifier(
            strict=strict_aether, diagnostics=diagnostics
        )

        passed = (
            spec_ok
            and quality_ok
            and aether_ok
            and (format_lint_ok if format_lint_ran else True)
        )

        audit.record_event(
            "verify",
            {
                "passed": passed,
                "spec": spec_ok,
                "quality": quality_ok,
                "format_lint": (format_lint_ok if format_lint_ran else None),
                "aether": aether_ok,
            },
        )

        return VerifyResult(
            passed=passed,
            spec_tests_gate=spec_ok,
            quality_gates=quality_ok,
            aether_risk=aether_ok,
            format_lint=(format_lint_ok if format_lint_ran else None),
            diagnostics=diagnostics,
        )

    def commit(self, message: str, sign: bool = False) -> CommitResult:
        diagnostics: list[str] = []
        sha = None
        code, out = self._run_git(["git", "commit", "-m", message], capture=True)
        diagnostics.append(out)
        committed = code == 0
        if committed:
            sha = self._git_rev_parse()
            audit.record_event("commit", {"message": message, "sha": sha})
        return CommitResult(
            committed=committed, sha=sha, message=message, diagnostics=diagnostics
        )

    # ---- New Phase 1 API additions ----
    def revert(self, token: str) -> PatchResult:
        """Revert files using stored snapshot (restores or deletes new files)."""
        snapshot_path = self._rollback_store / f"{token}.json"
        if not snapshot_path.exists():
            return PatchResult(
                applied=False,
                dry_run=False,
                diff="",
                rollback_token=None,
                summary="Token not found",
                diagnostics=[f"No snapshot for token {token}"],
            )
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        diagnostics: list[str] = []
        restored = deleted = 0
        for file_path, meta in data.items():
            p = self.repo_root / file_path
            existed = meta.get("existed", True)
            content = meta.get("content", "")
            try:
                if existed:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(content, encoding="utf-8")
                    diagnostics.append(f"Restored {file_path}")
                    restored += 1
                else:
                    if p.exists():
                        p.unlink()
                        diagnostics.append(f"Deleted new file {file_path}")
                        deleted += 1
            except Exception as e:  # pragma: no cover
                diagnostics.append(f"Failed revert {file_path}: {e}")
        audit.record_event(
            "revert", {"token": token, "restored": restored, "deleted": deleted}
        )
        summary = f"Reverted: restored={restored} deleted={deleted}"
        return PatchResult(
            applied=True,
            dry_run=False,
            diff="",
            rollback_token=None,
            summary=summary,
            diagnostics=diagnostics,
        )

    def scaffold_plugin(self, name: str) -> PatchResult:
        """Create minimal plugin scaffold (manifest + runtime stub + test)."""
        plugin_dir = self.repo_root / "plugins" / name
        runtime_py = plugin_dir / f"{name}.py"
        test_py = self.repo_root / "tests" / "plugins" / f"test_{name}.py"
        manifest = plugin_dir / "plugin.json"
        files_created: dict[str, str] = {}
        if plugin_dir.exists():
            return PatchResult(
                applied=False,
                dry_run=False,
                diff="",
                summary="Plugin already exists",
                diagnostics=[f"Directory {plugin_dir} exists"],
            )
        plugin_dir.mkdir(parents=True, exist_ok=True)
        (self.repo_root / "tests" / "plugins").mkdir(parents=True, exist_ok=True)
        class_name = f"{name.title().replace('_', '')}Plugin"
        runtime_content = (
            '"""Minimal Lyrixa Plugin Runtime Stub\n\nGenerated by aetherra_code scaffold.\n"""\n'
            f"class {class_name}:\n    def run(self):\n        return 'ok'\n"
        )
        test_content = (
            "import importlib\n\n"
            "def test_plugin_scaffold():\n"
            f"    mod = importlib.import_module('plugins.{name}.{name}')\n"
            f"    cls = getattr(mod, '{class_name}')\n"
            "    assert cls().run() == 'ok'\n"
        )
        manifest_content = json.dumps(
            {
                "name": name,
                "version": "0.0.0",
                "description": "Scaffolded plugin",
                "entry": f"plugins.{name}.{name}:{class_name}",
                "phase": 1,
            },
            indent=2,
        )
        runtime_py.write_text(runtime_content, encoding="utf-8")
        test_py.write_text(test_content, encoding="utf-8")
        manifest.write_text(manifest_content + "\n", encoding="utf-8")
        files_created[str(runtime_py.relative_to(self.repo_root))] = runtime_content
        files_created[str(test_py.relative_to(self.repo_root))] = test_content
        files_created[str(manifest.relative_to(self.repo_root))] = manifest_content
        token = f"scaffold-{int(time.time())}"
        snapshot = {
            k: {"content": v, "existed": False} for k, v in files_created.items()
        }
        self._persist_rollback_snapshot(token, snapshot)
        audit.record_event("plugin_scaffold", {"name": name, "token": token})
        diff_summary = "\n".join(files_created.keys())
        # Update central registered plugins index for auto-registration
        try:
            registry_dir = self.repo_root / "Aetherra" / "plugins" / "core"
            registry_dir.mkdir(parents=True, exist_ok=True)
            registry_file = registry_dir / "registered_plugins.json"
            if registry_file.exists():
                try:
                    reg_data = json.loads(registry_file.read_text(encoding="utf-8"))
                except Exception:
                    reg_data = {"plugins": []}
            else:
                reg_data = {"plugins": []}
            if name not in reg_data.get("plugins", []):
                reg_data.setdefault("plugins", []).append(name)
                registry_file.write_text(
                    json.dumps(reg_data, indent=2), encoding="utf-8"
                )
        except Exception:  # pragma: no cover
            pass
        return PatchResult(
            applied=True,
            dry_run=False,
            diff=diff_summary,
            rollback_token=token,
            summary=f"Created plugin {name}",
            diagnostics=[f"Created {len(files_created)} files"],
        )

    # ---- Helpers ----
    def _run_tool(self, cmd: list[str], diagnostics: list[str], label: str) -> bool:
        try:
            p = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            out, _ = p.communicate()
            diagnostics.append(f"[{label}]\n" + out)
            return p.returncode == 0
        except FileNotFoundError:
            diagnostics.append(f"[{label}] tool missing: {' '.join(cmd)}")
            return False

    def _run_git(self, cmd: list[str], capture: bool = False) -> tuple[int, str]:
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.STDOUT if capture else None,
            text=True,
        )
        out = ""
        if capture:
            out, _ = p.communicate()
        else:
            p.wait()
        return p.returncode, out

    def _git_rev_parse(self) -> str | None:
        code, out = self._run_git(["git", "rev-parse", "--short", "HEAD"], capture=True)
        if code == 0:
            return out.strip()
        return None

    def _git_add_from_diff(self, diff_text: str) -> None:
        paths: set[Path] = set()
        for line in diff_text.splitlines():
            if line.startswith("*** Update File:"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    path = parts[1].strip()
                    paths.add(Path(path))
            if line.startswith("*** Add File:"):
                path = line.split(":", 1)[1].strip()
                paths.add(Path(path))
        if paths:
            self._run_git(["git", "add", *[str(p) for p in paths]])

    def _persist_rollback_snapshot(
        self, token: str, originals: dict[str, dict]
    ) -> None:
        try:
            snap_path = self._rollback_store / f"{token}.json"
            snap_path.write_text(
                json.dumps(originals, ensure_ascii=False), encoding="utf-8"
            )
        except Exception:  # pragma: no cover
            pass

    def _colorize_diff(self, diff_text: str) -> str:
        if os.getenv("NO_COLOR", "0") == "1":
            return diff_text
        GREEN = "\x1b[32m"
        RED = "\x1b[31m"
        CYAN = "\x1b[36m"
        RESET = "\x1b[0m"
        out_lines: list[str] = []
        for line in diff_text.splitlines():
            if (
                line.startswith("@@")
                or line.startswith("+++")
                or line.startswith("---")
            ):
                out_lines.append(CYAN + line + RESET)
            elif line.startswith("+") and not line.startswith("+++ "):
                out_lines.append(GREEN + line + RESET)
            elif line.startswith("-") and not line.startswith("--- "):
                out_lines.append(RED + line + RESET)
            else:
                out_lines.append(line)
        return "\n".join(out_lines)


# End of orchestrator skeleton

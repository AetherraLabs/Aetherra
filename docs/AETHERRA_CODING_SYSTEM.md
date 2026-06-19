# Aetherra Coding System (Lyrixa Code Studio)

This document defines the autonomous coding system for Aetherra OS that enables Lyrixa to plan, write, modify, test, secure, and ship code across the entire stack, including .aether scripts and Aetherra plugins. It functions like a full IDE (akin to VS Code) with an AI-native autonomy layer.

## Objectives

- First-class, AI-native software development for general, advanced, and .aether code
- Autonomous end-to-end flow: plan → code → test → secure → sign → ship
- Safe-by-default with verifiable changes, audit trails, and least-privilege execution
- Extensible: plugin scaffolding, language support, toolchain adapters
- Headless and GUI: works from CLI, web, or Lyrixa GUI

## Guardian enforcement

Guardian protects Coding System paths that can mutate files, execute code, or materialize generated code:

- `CoreToolsPlugin` filesystem operations declare Guardian intents before write, append, directory creation, delete, copy, move, archive, extract, JSON, or CSV mutation.
- `PluginGeneratorPlugin.save_plugin_to_disk` declares `coding.plugin_generator_save` before creating generated plugin scaffold directories or writing scaffold files.
- Script execution and self-improvement/optimization apply paths are guarded through their owning systems before code execution or repository mutation.
- Strict capability mode blocks explicit external callers without the required filesystem, code-modification, plugin-creation, or execution capabilities.
- Denied plugin scaffold saves raise `PermissionError` before output directories or files are created.
- Audit metadata records file counts, file names, template IDs, and hashes of plugin/output identifiers without storing raw plugin names, descriptions, generated code, or output paths.

Remaining Guardian scope:

- Keep future natural compiler output, additional code generators, test-fix automation, refactor assistants, direct write helpers, and autonomous patch applicators behind Guardian before enabling them.

## Core Capabilities

1. IDE-grade experience

- Editor model (virtual and file-backed), explorer, problems, outline
- Command Palette and Quick Actions (e.g., “Add unit test for X”)
- Integrated terminal, source control, search/replace, refactor, rename
- Debug hooks (runner adapters per language)

1. Autonomy modes

- Assist: propose patches; user accepts/edits
- Co-drive: auto-apply small/safe changes; prompt for risky edits
- Autopilot: fully autonomous plan→PR with policy & guardrails

1. Multi-language support

- Python, TypeScript/JS, Markdown, JSON/YAML, HTML/CSS, Shell
- Aether Script (.aether): syntax/LSP, signing, static risk checks, execution
- Extensible to other languages via adapters

1. Plugin authoring

- Scaffold Aetherra plugins (runtime + manifest + tests + signing)
- Live reload in dev mode; sandboxed execution; permission requests

1. Continuous verification

- Build/lint/test before commit; fast smoke on save (opt-in)
- Security scanning (keys/memory/files/network) + .aether risk analysis
- Signature workflows for scripts/plugins with strict/lenient modes

## System Architecture

- Lyrixa Code Orchestrator
  - Plans work, assigns subtasks to specialized agents (coder, refactorer, tester, security, doc, reviewer)
  - Uses Multi-AI routing with fallback for codegen/analysis
  - Maintains project context graph (files, tests, deps, APIs)

- Code Operations Engine
  - File graph service (read/patch/create/delete/move/rename)
  - Patch composer (minimal, reversible diffs)
  - Refactor engine (rename symbols, extract methods, organize imports)
  - Formatters/Linters integration (black/isort/ruff, eslint/prettier, mdformat)

- Analysis & Safety
  - Impact analyzer (blast radius, dependency impact, test selection)
  - Security pipeline (AetherraSecuritySystem + SecurityAgent hooks)
  - .aether static risk: tools/verify_aether_scripts.py (strict mode available)

- Tooling & Runtimes
  - Test runners: pytest, node test, custom harness
  - Builders: Python (none/pyproject), TS (tsc/vite/next), docs (mkdocs/markdown)
  - Debug adapters (language-specific)

- Persistence & Audit
  - Change log, decision trace, prompts (sanitized), run artifacts, test results
  - Git integration: branches/commits/PRs; signed artifacts where applicable

## Autonomy Flow (Contract)

High-level autonomous loop:

1. Understand Intent

- Inputs: natural language goal, optional constraints, target scope
- Output: task spec (objective, acceptance tests, risk class)

1. Plan

- Generate step plan (files to touch, tests to add/update, checks)
- Estimate risk and choose autonomy mode per step

1. Retrieve Context

- Build context graph: code symbols, tests, configs, APIs, docs

1. Generate & Patch

- Propose patch → verify → apply minimal diff
- Keep patches atomic; one concern per commit in co-drive/autopilot

1. Build & Test

- Run fast checks; re-plan on failure (max N retries)

1. Secure & Sign

- Run security checks (.aether risk, keys/memory/files/network)
- Sign scripts/plugins when required and policy allows

1. Review & Ship

### Spec → Tests Gate (mandatory)

Before any patch is applied, Lyrixa MUST write or refresh acceptance tests that embody the intent/spec just captured. This introduces an explicit “Spec → Tests” step between Plan and Generate & Patch:

- Inputs: task spec (objective, acceptance criteria)
- Outputs: test deltas (new tests or updates), minimally runnable
- Enforcement: autonomy loop blocks patch application until tests exist; red tests are allowed to drive implementation, but tests must be present.

Tooling: Command Palette action “Generate unit/acceptance tests for current intent” and automatic scaffolds for common suites (pytest, Playwright, API checks). The default tasks include “Verify Claims (Capabilities Tests)”.

- Create branch/PR (autopilot), attach report; or apply locally (assist/co-drive)

### Minimal API Surface (Programmatic)

- code.plan
  - Input: intent, scope, constraints
  - Output: plan steps, files, risks

- code.generate
  - Input: plan step, context slice
  - Output: candidate patch, confidence, tests suggestions

- code.applyPatch
  - Input: target file(s), unified diff or operations
  - Output: result (applied, conflicts, rollback token)

- code.verify
  - Input: checks to run (build, lint, tests, security, .aether)
  - Output: PASS/FAIL with diagnostics

- code.commit
  - Input: message, sign? (optional), branch policy
  - Output: commit SHA / PR URL

- plugin.scaffold
  - Input: name, kind, permissions, description
  - Output: directory with manifest, code, tests, signing hooks

- aether.compile/run/sign/verify
  - Inputs vary; includes strict verification flag
  - Output: execution/logs or verification report

Example I/O (illustrative JSON):

```json
{
  "op": "code.applyPatch",
  "file": "Aetherra/plugins/example/__init__.py",
  "diff": "*** Begin Patch\n*** Update File: ...\n...\n*** End Patch"
}
```

## Editor Experience (Like VS Code)

- Panels
  - Explorer, Search, Source Control, Run & Debug, Extensions
  - Problems/Diagnostics and Output terminals

- Command Palette
  - “Generate unit tests for selection”
  - “Refactor: Extract function”
  - “Fix lints in staged files”
  - “Create Aetherra Plugin”
  - “Create .aether Script from Task” (one‑click): generates a timestamped `.aether` file using a standard template that includes meta, policy (profile=test, retries, timeouts), and a starter workflow scaffold. Backed by `tools/create_aether_from_task.py` and available as a task.
  - “Spec → Tests Gate”: checks staged/working changes to ensure tests are present for code edits (`tools/spec_tests_gate.py`).
  - “Quality Gates (Tests + Coverage No-Drop)”: runs tests with coverage and enforces coverage no-drop (`tools/quality_gates.py`).

- Code Actions
  - Quick Fixes (missing import, add types, docstrings)
  - Refactorings (rename symbol, move file/module)
  - Generate stubs (tests, README, config, scaffolds)

### Custom templates for “Create .aether from Task”

The generator supports custom templates via an environment variable:

- Set `AETHERRA_TEMPLATE_DIR` to a directory that contains either `template.aether` or `default.aether`.
- Placeholders are replaced safely (no `.format` braces issues) using simple key substitution. Common placeholders include: `TASK_TITLE`, `TASK_DESCRIPTION`, and `DATE`.
- Strict vs. lenient requires: controlled by `AETHERRA_REQUIRE_STRICT` (when set, the generated template uses strict require semantics).

Example (PowerShell):

`$env:AETHERRA_TEMPLATE_DIR = "C:\\path\\to\\my_templates"; python tools/create_aether_from_task.py "Build ingestion pipeline"`

## .aether Language Support

- LSP-like services
  - Syntax highlighting, outline, hover docs, signature help
  - Go to definition (functions/macros), find references (script ops)

- Security & Signing
  - Static risk analyzer: tools/verify_aether_scripts.py (supports --strict, --max-findings-per-file)
  - Signing: tests/unit/test_aether_script_signing.py illustrates round-trip
  - Env flags: AETHERRA_SCRIPT_VERIFY_STRICT, AETHERRA_SIGNING_STRICT

- Execution & Integration
  - Runtime: `aether.py`, `aetherra_script_service.py`
  - Orchestrated execution via service registry or hub API
  - Supports v1.1 features: keyword args, meta/policy header, imports, concurrency, step-level controls

### Deterministic Profiles (test vs live)

- Profile selection via env or CLI:
  - Env: `AETHERRA_PROFILE=test` enables deterministic behavior (seed 0 for Python/numpy/torch when available), sets `AETHERRA_DETERMINISTIC=1`, and `PYTHONHASHSEED=0`.
  - CLI: `tools/os_smoke.py --profile test` and `tools/verify_aether_scripts.py --profile test` honor the same.
- Purpose: eliminate incidental nondeterminism in CI/smoke and static analysis ordering.
- Runtime cooperation: components should check `AETHERRA_DETERMINISTIC=1` to disable non-deterministic algorithms where possible.

### Transactions & Idempotency (execution semantics)

- Script-level controls (minimal v1.1 surface):
  - `begin transaction [name]` … `commit transaction` | `rollback transaction`
  - Statements inside a transaction are collected as ops and summarized; rollback discards the collection. Nested transactions are rejected.
  - Built-ins indicate `idempotent` in results when safe to retry (e.g., assignments, narrate); effectful future ops should set `idempotent=false`.
- Engine semantics:
  - The interpreter does not persist or externalize effects in this minimal implementation; future effectful ops should obey begin/commit/rollback boundaries.
  - Retries and budgets are governed by policy (see `policy` directive) and plugin runtime contracts.

### Trace & Narrate (observability)

- Trace emission: set `AETHERRA_TRACE=1` to include a `trace` array in the execution payload with per-line inputs and outputs, plus txn boundary events.
- Narration primitive: `narrate "..."` appends an idempotent trace/result entry without external side effects; ideal for story-like progress logs.
- Payload enrichment:
  - `result.trace`: list of { line, statement, result } plus txn events.
  - `result.transactions`: summarized transactions with collected ops.
  - `result.policy` and `result.requires`: surfaced for UIs and analyzers.

### Aether Script v1.1 — Tightened Spec (superset of 1.0)

Reference: see `Aether_Script_Language_System.md` for the current spec and `Aether_Script_Language_Specification.md` for the retained legacy v1.0 reference.

#### Updated EBNF (selected)

Top-level and blocks (additions only):

```ebnf
script          ::= (meta_block | policy_block | require_block | statement | comment | blank_line)+

meta_block      ::= "meta:" INDENT meta_kv+ DEDENT
meta_kv         ::= identifier ":" expression NEWLINE

policy_block    ::= "policy:" INDENT policy_kv+ DEDENT
policy_kv       ::= identifier ":" expression NEWLINE
                  (* e.g., budget, risk_threshold, timeout_default, concurrency_limit *)

require_block   ::= "require:" INDENT require_item+ DEDENT
require_item    ::= ("plugin" | "module") identifier [version_spec] [signature_spec] NEWLINE
version_spec    ::= "version" "=" string_literal
signature_spec  ::= "signature" "=" string_literal

statement       ::= goal_stmt | memory_stmt | assignment | function_call
                  | conditional | workflow_block | loop_block | parallel_block

parallel_block  ::= "parallel:" INDENT (statement | await_stmt)+ DEDENT
await_stmt      ::= "await" expression NEWLINE
spawn_call      ::= "spawn" "(" function_call ")"

workflow_block  ::= "workflow:" INDENT workflow_body DEDENT
workflow_body   ::= (assignment | list_of_steps)+
list_of_steps   ::= "-" ( step_call | step_object ) NEWLINE

step_call       ::= identifier "(" [arguments] ")" [ step_options ]
step_object     ::= "step:" identifier NEWLINE step_options_block

step_options    ::= ( "retry" "=" number_literal
                    | "timeout" "=" string_literal
                    | "requires" "=" list_literal
                    | "produces" "=" string_literal
                    | "on_error" "=" string_literal )*

step_options_block ::= INDENT step_option_line+ DEDENT
step_option_line   ::= ("retry" | "timeout" | "requires" | "produces" | "on_error") ":" expression NEWLINE

conditional     ::= "if" expression ":" block [ "else:" block ] [ on_error_block ]
on_error_block  ::= "on_error:" INDENT statement+ DEDENT

assignment      ::= identifier ":" expression

expression      ::= string_literal | number_literal | bool_literal | null_literal
                  | function_call | identifier | list_literal | dict_literal

function_call   ::= identifier "(" [arguments] ")"

arguments       ::= [positional_args] [ ("," kwarg)* ]
positional_args ::= expression ("," expression)*
kwarg           ::= identifier "=" expression

block           ::= INDENT statement+ DEDENT
```

#### Tokens & Primitives (extended)

- bool_literal: `true` | `false`
- null_literal: `null`
- time literals are strings (e.g., "30s", "2m"); interpretable per policy

#### Truthiness & Error Model

- Truthy: non-empty strings/lists/dicts, non-zero numbers, `true`
- Falsy: empty strings/lists/dicts, `0`, `false`, `null`
- Error taxonomy (raised by runtime or functions): `Error`, `TimeoutError`, `PermissionError`, `ValidationError`
- `on_error` blocks run when a statement inside their guarded region throws; `on_error` may `escalate_to(...)`, `retry(...)`, or `store(...)`

#### Side-Effects & Purity

- Functions are tagged in the runtime registry as `pure` or `effectful`
- The engine may reorder or parallelize `pure` calls; `effectful` calls are serialized or isolated to preserve determinism
- Functions may declare `idempotent` to enable safe retries under failures

#### Concurrency Primitives

- `parallel:` block runs contained statements concurrently; shared memory writes follow last-writer-wins unless `merge()` is specified
- `spawn(func(...))` returns a task handle; `await handle` waits for a specific handle; `await all(handles)` waits for many
- Merge rules: `merge(a,b, policy="prefer_newer"|"prefer_older"|"custom")`

#### Modules & Imports (require)

- `require:` supports plugins/modules with version pins and signature constraints for reproducibility
- Example require items:

```aether
require:
  plugin anomaly_detector version="^1.4" signature="ed25519:abc..."
  module analytics_core version="2.3.1"
```

##### Require semantics (semver + strict)

- Semver supported in `version="..."`:
  - Exact: `"1.2.3"` matches only 1.2.3
  - Caret: `"^1.2"` matches >=1.2.0 and <2.0.0
  - Tilde: `"~1.2.3"` matches >=1.2.3 and <1.3.0
  - Wildcard: `"*"` matches any version
- Strict mode: set `AETHERRA_REQUIRE_STRICT=1` to make unmet requirements abort execution.

Inline examples:

```aether
# Require a plugin with a semver range and an optional signature hint
require plugin anomaly_detector version="^1.4" signature="ed25519:abc..."

# Require a Python module with a tilde range
require module analytics_core version="~2.3.1"
```

Execution payload exposure (what the service returns to callers):

```json
{
  "success": true,
  "result": {
    "results": [
      { "type": "policy_set", "policy": { "max_executions": 2 } },
      { "type": "require", "kind": "module", "name": "analytics_core", "ok": true }
    ],
    "policy": { "max_executions": 2 },
    "requires": [
      { "type": "require", "kind": "module", "name": "analytics_core", "version": "~2.3.1", "ok": true }
    ]
  }
}
```

#### Script Header (meta & policy)

- `meta:` is standardized at the top of file; recommended keys: `version`, `author`, `capabilities`, `budget`, `risk_threshold`, `signature`
- `policy:` declares execution defaults: `timeout_default`, `concurrency_limit`, `retry_default`, `allow_network`, etc.

#### Workflow Step Controls

- Each step can specify: `retry`, `timeout`, `requires` (capabilities or preconditions), `produces` (artifact name), `on_error` (continue|abort|fallback)
- Object-style steps allow multi-line options for readability

#### Examples

Header, imports, and policy:

```aether
meta:
  version: "1.1"
  author: "Aetherra Labs"
  capabilities: ["memory", "plugins", "network"]
  budget: "$0.50"
  risk_threshold: 0.2

policy:
  timeout_default: "60s"
  concurrency_limit: 4
  retry_default: 1

require:
  plugin anomaly_detector version="^1.4" signature="ed25519:abc..."
  module analytics_core version="2.3.1"

goal: "Daily maintenance and anomaly reporting"
```

Keyword args, purity, on_error, and workflow controls:

```aether
memory: load_logs(tag="system", days=1)
summary: summarize(memory)

if detect_anomalies(summary):
  reflect_on(summary)
else:
  store(summary, tag="daily")

workflow:
  steps:
    - parse_input(file="design.json") timeout="30s" retry=2 on_error="continue"
    - step: generate_assets
      timeout: "45s"
      requires: ["gpu"]
      on_error: "abort"
    - assemble_scene()
    - export_game(format="rbxmx") produces: "game_artifact"
```

Concurrency (parallel, spawn/await):

```aether
parallel:
  summary: summarize(memory)
  anomalies: detect_anomalies(summary)
  await all([summary, anomalies])

t1: spawn(run_plugin("indexer", target="src"))
t2: spawn(run_plugin("security_scan", scope="repo"))
await t1
await t2
```

## Plugin Development Workflow

- Scaffold
  - Create plugin skeleton with manifest, permissions, code, tests
  - Choose security level (Verified/Trusted/Standard/Experimental)

- Develop
  - Code in isolated sandbox; explicit capability declarations
  - Live reload / hot swap in dev

- Verify & Sign
  - Run security checks, unit tests; sign manifest if policy requires
  - Register with hub (strict/non-strict/signed modes supported by tests)

## Safety, Security, Guardrails

- Permissions & Sandboxing
  - Plugins run with declared capabilities; denied by default
  - File/Network/Process access mediated by policy

- Secrets & Memory Safety
  - API keys via secure vaults; rotation; leak detection
  - Memory/report redaction; sensitive artifact scrubbing

- Change Controls
  - Dry-run preview, diff summaries, automatic rollback tokens
  - Autopilot gated by policy thresholds (risk, coverage, ownership)

- Audit & Telemetry (opt-in)
  - Full activity trail; anonymized metrics when enabled

## Quality Gates (Default)

- Build: no syntax/type errors
- Lint: clean or auto-fixed
- Tests: required suites green (fast path on changed areas)
- Coverage: overall coverage must not drop vs. last baseline; configurable minimum via MIN_COVERAGE. Enforced by `tools/quality_gates.py` (added task: “Quality Gates (Tests + Coverage No-Drop)”).
- Security: no critical findings; .aether risk below threshold
- Docs: updated when public API changes

### Persistence & Audit (Model/Cost Ledger)

Runs persist audit records for reproducibility: model, seed/profile, token counts, cost, sanitized prompts, and script content. Controlled by env flags:

- AETHERRA_AUDIT=0 to disable (default enabled)
- AETHERRA_AUDIT_PATH to choose output (default `audit/aetherra_runs.jsonl`)

The `.jsonl` ledger is appended per run and can be consumed by dashboards. Trace and transactions, when enabled, are also referenced in each record.

## Example Workflows

1. “Create a plugin to expose a memory summary API”

- plan → scaffold plugin → implement handler → tests → verify & sign → register

1. “Add unit tests for Aether Script signing”

- locate module + tests skeleton → generate tests → run pytest → fix → commit

1. “Refactor memory engine to extract QFAC adapter”

- symbol graph → refactor plan → apply patches → run QFAC tests → commit

1. “Author .aether for nightly maintenance”

- open template → author operations → sign → verify via static analyzer → schedule

## Configuration

- Policies: autonomy levels, signing requirements, test gates
- Per-language settings: formatters, linters, runners
- Env flags leveraged:
  - AETHERRA_SCRIPT_VERIFY_STRICT, AETHERRA_SIGNING_STRICT
  - AETHERRA_PLUGINS_ENABLED, AETHERRA_PLUGINS_CLEANUP_REPORT
  - AETHERRA_QUIET (headless), AETHERRA_SAFE_MODE

## Integration Points in Repo (today)

- Agents & Orchestration: `Aetherra/aetherra_core/agents/collaboration.py`, `plugins/agent_components/agent_orchestrator.py`
- Security: `Aetherra/aetherra_core/system/security_system.py`, `lyrixa/agents/security_agent.py`
- .aether: `aether.py`, `aetherra_script_service.py`, `tools/verify_aether_scripts.py`, tests
- Hub/Registry: `aetherra_hub/compat.py`, `aetherra_service_registry.py`

## Roadmap (phased)

- Phase 1: Core code ops + test/lint/build + .aether LSP + plugin scaffold
- Phase 2: Full refactor graph, semantic code search, PR autopilot
- Phase 3: Live pair-programming UI in Lyrixa; multi-agent co-edit
- Phase 4: Advanced debugging & runtime patching; design-time telemetry
- Phase 5: Marketplace for community extensions; trust levels and reviews

---

This specification makes Lyrixa a fully autonomous, IDE-grade developer that can write general code, advanced systems, .aether scripts, and Aetherra plugins safely and repeatably with enterprise guardrails.

## Lyrixa Interaction Modes & Triggers

To operate like a full IDE while remaining autonomous, Lyrixa supports multiple interaction modes:

- On-demand Insert: user requests a change; Lyrixa previews and inserts code at the cursor/target file
- Co-drive Editing: Lyrixa continuously proposes fixes and refactors as you navigate files
- Self-Writing Sessions: Lyrixa executes the Autonomy Flow end-to-end without user input
- Hands-free Autopilot: runs plans, applies patches, verifies gates, and prepares PRs/commits

Triggers and UX hooks:

- Command Palette actions (e.g., “Create Aetherra Plugin”, “Generate tests for selection”)
- Quick Actions and inline Code Actions (fix imports, add types, extract function)
- Task-oriented prompts (natural language goals mapped to code.plan/code.generate)
- Optional voice or hotkey triggers that invoke the same programmatic API

All modes respect Safety, Security, and Quality Gates. Autopilot engages only when policy allows and risk thresholds are met.

## Python → .aether Migration Roadmap

Goal: Gradually rewrite Python subsystems into `.aether` for AI-native, declarative, and auditable operation.

- Phase A: Define canonical standard library bindings for core functions (memory, plugins, telemetry, security)
- Phase B: Wrap critical Python flows in `.aether` orchestration scripts (goal → steps → artifacts)
- Phase C: Implement pure/effectful function registries and migrate effectful edges first
- Phase D: Introduce `require:` versioned modules for formerly-Python packages; enable signature checks
- Phase E: Replace imperative Python maintenance jobs with `.aether` workflows (with policy + budgets)
- Phase F: Deprecate direct Python entrypoints in favor of `.aether` launchers through the service registry

Success criteria:

- 80% of operational flows expressible as `.aether` workflows with tests
- Concurrency (`parallel`, `spawn/await`) used in ≥50% of suitable workflows
- Security and signing enforced by default on distributed `.aether`

## Engine Updates Required (to support v1.1)

- Parser/Interpreter
  - Extend tokenizer for `true|false|null` and kwarg syntax
  - Implement `meta:`, `policy:`, and `require:` blocks
  - Add `on_error` blocks and error taxonomy mapping
  - Add `parallel:` block, `spawn()` and `await` semantics
  - Step-level options in `workflow:` (retry/timeout/requires/produces/on_error)

- Runtime Semantics
  - Function registry: `pure|effectful|idempotent` flags; scheduler respects determinism
  - Merge policies for shared memory; last-writer-wins and `merge()` custom hooks
  - Policy enforcement (timeouts, concurrency_limit, retry_default, budgets)
  - Import/require resolver with version pins and signature verification

- Tooling & DX
  - LSP: signature help for kwargs; diagnostics for policy/require/meta blocks
  - Static analyzer: truthiness, effectful/pure misuse, policy violations
  - Tests: golden parsing, concurrency execution, step options, error handling

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

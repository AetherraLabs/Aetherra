# Aetherra Coding System Roadmap (Lyrixa Code Studio)

Status: Phase 1 (Safe Edit Loop) – COMPLETE (Foundations + Safe Edit Loop features delivered; transitioning to Phase 2 initiation)
Owner: Lyrixa / Aetherra Engineering
Source Spec: `docs/AETHERRA_CODING_SYSTEM.md`
Ledger: `audit/aetherra_runs.jsonl` (coding ops)
Last Updated: 2025-09-07

## Vision

Deliver an AI‑native, autonomous, IDE‑grade environment that can plan → code → test → secure → sign → ship across Python, JS/TS, Markdown, JSON/YAML, and `.aether` scripts, with progressive autonomy modes (Assist, Co‑drive, Autopilot) and enterprise guardrails (Spec→Tests Gate, Quality Gates, Security & Audit).

## Phasing Overview

| Phase | Codename              | Core Outcomes                                                                                                                   | Exit Criteria                                                                                                             |
| ----- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 0     | Foundations           | Public API + CLI + patch engine + gates wiring                                                                                  | `aetherra_code` plan/generate/apply/verify/commit works locally; audit ledger writes; Spec→Tests & Quality Gates enforced |
| 1     | Safe Edit Loop        | Formatting/Lint integration, richer patch composer, test & build pipeline cohesion, `.aether` risk gating; plugin scaffold stub | `aetherra_code verify` fully enforces gates; minimal plugin scaffold command present                                      |
| 2     | Orchestrated Autonomy | Orchestrator context graph, agent routing (coder/tester/security/doc), autonomy policies; branch/PR autopilot                   | Autopilot opens draft PR with plan, patches, audit bundle                                                                 |
| 3     | Lyrixa IDE Panels     | Explorer/Search/Problems/Source Control/Command Palette parity with CLI                                                         | Lyrixa UI can drive identical operations; live diagnostics refresh                                                        |
| 4     | Refactor & Semantics  | Refactor graph, semantic code search, advanced rename/extract, risk scoring                                                     | Refactors atomic & reversible; semantic search feeds planning                                                             |
| 5     | Debug & Runtime Patch | Language debug adapters, hot patch w/ rollback tokens                                                                           | Live debug + safe runtime patch preview -> apply -> revert                                                                |
| 6     | Marketplace & Signing | Plugin scaffold→test→sign pipeline; trust metadata & marketplace prep                                                           | Signed plugins w/ trust levels; publish metadata manifest                                                                 |

## Detailed Phase Breakdown

### Phase 0 (Foundations) – COMPLETE

Delivered:

- Package `aetherra_coding/` with orchestrator, ops engine (MVP), safety/audit/analysis stubs
- CLI `cli/aetherra_code.py` (plan, generate, apply, verify, commit)
- Spec→Tests & Quality Gates integration
- `.aether` risk verifier hook + audit JSONL ledger

Rolled Forward (absorbed / completed early in Phase 1):

- Colorized diff + rollback execution (DELIVERED)
- Plugin scaffold skeleton command (DELIVERED)
- Initial unit tests for patch engine & orchestrator (BASIC CASES DELIVERED – extend for edge risk scenarios Phase 1)

### Phase 1 (Safe Edit Loop) – COMPLETE

Focus: robust, deterministic editing & verification.

Key Work Items (Original Scope):

1. Patch Composer v2: multi‑file diffs, hunk classification, risk scoring (low/medium/high)
2. Formatters/Linters: black, isort, ruff (Python); prettier/eslint (JS/TS); mdformat (Markdown) – auto-fix pre‑commit in co‑drive/autopilot
3. Test Selection (stub): touch list → candidate test filter (impact analyzer) – optimize verification cycle
4. Coverage delta embed in verify output + gating reasons surfaced to UI layer
5. Plugin Scaffold Command: `aetherra_code plugin scaffold --name NAME` producing manifest + runtime + tests + signing placeholder
6. Rollback Tokens: store pre‑patch snapshots (content hash), implement `aetherra_code revert --token <id>`
7. Enhanced Diagnostics: diff summary (files, +lines, -lines), risk classification

Progress (final as of 2025-09-08):

- ✅ Colorized diff + risk classification + per-file added/removed counts integrated into snapshots
- ✅ Rollback snapshot store (content + existence + line delta) – revert command operational
- ✅ Plugin scaffold + registry discovery + manifest validation & warning diagnostics
- ✅ Format/Lint pipeline: black (strict mode), isort integration, ruff config migrated to new `[tool.ruff.lint]` layout
- ✅ Gate wiring: format/lint stage incorporated into verify pipeline with `--no-format` flag and strict mode env toggle
- ✅ Encoding / parsing stability remediation (BOM removal, UTF‑16→UTF‑8 conversion, malformed f-string corrections)
- ✅ Intentional side‑effect import strategy (inline `# noqa: F401` on curated availability imports)
- ✅ Risk classification thresholds applied to diff summary output
- ✅ Bulk unused import removals (ruff near-clean; residual rare intentional imports documented with noqa)
- ✅ Coverage delta capture + gating reasons schema implemented (file snapshots + JSON report with schema_version)
- ✅ Test selection stub (confidence, fallback, gating integration)
- ✅ Patch Composer v2 groundwork (multi-file hunk classification hooks; risk scoring extended) – full semantic inputs deferred to Phase 4

Exit Criteria (achieved):

- All gates (format/lint + tests + coverage no-drop) green under normal run (PR description + structured reasons validated)
- Plugin scaffold created, verified (signing placeholder stub committed)
- Revert command functional (rollback token tests pass; audit ledger entries present)
- Coverage delta + gating reasons emitted (snapshot + gating report JSON, schema_version=1)
- Test selection stub producing candidate set with confidence gating

### Phase 2 (Orchestrated Autonomy)

Focus: intelligence & policy-driven execution.

Key Work Items:

1. Context Graph Builder: map symbols → tests → docs → config (caching layer)
2. Agent Routing: coder/refactor/test/security/doc/reviewer agents invoked via existing agent fabric
3. Autonomy Policies: risk thresholds, test coverage guard, ownership checks before auto‑apply
4. Branch Strategy: `autopilot` mode creates feature branch (`feat/<slug>`) and stages atomic commits
5. Draft PR Automation: generate PR description (intent, plan, diffs summary, risk, coverage diff, security report excerpt)
6. Adaptive Retries: on test fail, re‑plan limited to failing scope (max N attempts)

Exit Criteria:

- Autopilot run from intent to draft PR with audit bundle and passing gates.

### Phase 3 (Lyrixa IDE Panels)

Focus: full UI parity & developer ergonomics.

Work Items:

- Panels: Explorer, Search, Problems, Source Control, Run & Debug, Extensions
- Command Palette Actions mapped to minimal API
- Live Diagnostics Stream: push on verify steps (lint, tests, security)
- Inline Code Actions: fix imports, add types, generate tests for selection
- Diff Preview Panel: colorized patch + accept/skip granular hunks

Exit Criteria:

- All CLI operations driveable via Lyrixa UI without regressions.

### Phase 4 (Refactor & Semantic Layer)

Work Items:

- Refactor Graph: cross‑file symbol usage map, rename/extract w/ preview
- Semantic Search: embedding-based retrieval for planning context
- Risk Model: complexity + churn + dependency depth -> autonomy gating

Exit Criteria:

- 90% rename/extract operations pass idempotence tests; semantic search reduces prompt context size ≥30% (baseline).

### Phase 5 (Debug & Runtime Patching)

Work Items:

- Python & JS debug adapters (attach + launch)
- Hot Patch Mechanism: apply in-memory diff, verify, persist on confirm
- Runtime Safety: patch sandbox + quick rollback

Exit Criteria:

- Hot patch round trip (<5s) with at least one test verifying live change.

### Phase 6 (Marketplace & Signing)

Work Items:

- Plugin Signing Workflow: strict vs lenient; signature metadata embedded
- Trust Metadata Schema (verified/trusted/experimental)
- Marketplace Manifest (index JSON) + publish task
- Security Scoring: integrate risk reports into plugin listing

Exit Criteria:

- Signed plugin install round trip; marketplace index generated & verified.

## Cross-Cutting Concerns

| Concern                 | Strategy                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------- |
| Audit & Reproducibility | Append JSONL per operation; deterministic profile via `AETHERRA_PROFILE=test`       |
| Security                | `.aether` strict risk, memory & key leak scanning, plugin capability enforcement    |
| Performance             | Incremental context graph caching, selective test runs, parallel lint/test (future) |
| Observability           | Structured diagnostics for each gate; optional trace emission                       |
| Governance              | Ownership checks (OWNERSHIP.md) before autopilot commits (Phase 2)                  |

## Metrics & Success Indicators

- Mean time: intent → passing verify (target < 3 min for small edits, Phase 2)
- Autopilot acceptance (merged without manual diff edits) ≥ 60% by Phase 4
- Coverage no-drop failures < 5% of runs after Phase 1
- Refactor safety (post‑rename CI green on first attempt) ≥ 90% by Phase 4
- Plugin scaffold to signed publish median time < 10 min (Phase 6)

## Open Risks / Mitigations

| Risk                                  | Mitigation                                                            |
| ------------------------------------- | --------------------------------------------------------------------- |
| Patch misapplication in complex diffs | Integrate robust diff library & three-way merge Phase 1.5             |
| Test selection false negatives        | Always run full suite fallback if selective run passes too quickly    |
| Autopilot overreach                   | Multi-factor gate: risk score + coverage + ownership + security clean |
| Marketplace trust dilution            | Mandatory signing + risk scoring + provenance metadata                |

## Current TODO Snapshot (Rolling)

Completed (recent):

- [x] Color diff & revert command (CLI flags, integrated with risk output)
- [x] Plugin scaffold command (runtime, test, manifest, auto-registration)
- [x] Risk classification (low/medium/high + added/removed counts)
- [x] Plugin registry validation warnings & `plugin list` CLI
- [x] Rollback snapshot enriched (added/removed counts per file)
- [x] Ruff configuration migration to new lint sections
- [x] Format/lint gate (black + isort + ruff) with strict mode toggle
- [x] Encoding normalization (BOM removal, UTF‑16 file conversion) & parse error fixes
- [x] Side-effect import hygiene pattern established (targeted `noqa: F401`)
- [x] Basic unit tests for diff apply & revert paths

Transition Queue to Phase 2 (migrated from Phase 1 backlog):

- [ ] Patch Composer v2 semantic enrichment (diff AST cues, churn weighting)
- [ ] ADR: patch composer diff strategy v2
- [ ] ADR: autonomy risk model v1
- [ ] Branch/PR autopilot implementation
- [ ] Context graph prototype (symbols ↔ tests ↔ docs map)
- [ ] Semantic search index scaffold
- [ ] Remaining ruff edge ignores audit (convert to targeted noqa or remove)

## Governance & Process Additions

### Architecture Decision Records (ADRs)

- Store in `docs/adr/ADR-XXXX-short-title.md` (sequential, 4 digits).
- Required for: diff/merge strategy upgrade, autonomy risk model v1, semantic index design, marketplace trust schema, rollback mechanism.
- Template fields: Context, Decision, Status (Proposed/Accepted/Deprecated), Consequences, Linked Phase & Issues.

### Definition of Ready / Done (Per Phase)

| Phase | Ready Checklist (excerpt)                        | Done Checklist (excerpt)                                                     |
| ----- | ------------------------------------------------ | ---------------------------------------------------------------------------- |
| 1     | ADR for patch composer, test selection draft     | Unit tests ≥80% ops_engine lines; rollback tested; docs updated              |
| 2     | Autonomy policy doc draft; ownership map         | Draft PR autopilot working; risk scoring ADR accepted; audit fields complete |
| 3     | UI component inventory; accessibility audit plan | Keyboard map published; a11y checklist pass; parity test suite green         |

### RACI / Ownership

| Area                     | R              | A           | C               | I               |
| ------------------------ | -------------- | ----------- | --------------- | --------------- |
| Autopilot policy changes | Coding Lead    | CTO         | Security Lead   | All devs        |
| Risk thresholds          | Security Lead  | CTO         | Coding Lead     | Audit consumers |
| Marketplace listings     | Plugin Steward | CTO         | Security, Legal | Community       |
| Semantic index pipeline  | ML Engineer    | Coding Lead | DevEx           | Security        |

## Security & Supply Chain Enhancements

- SBOM & Provenance: extend existing `tools/generate_sbom.py`; sign artifact with detached signature (Phase 1.5).
- Dependency Policy: allowlist + denylist YAML (`config/dependencies_policy.yml`), monthly bump task; vulnerability scan must pass before merge.
- Threat Model (STRIDE) matrix: add `docs/security/THREAT_MODEL_CODING_SYSTEM.md`; include attack surfaces: diff ingestion, hot patch, plugin install, PR automation.
- Red-Team Test Seeds: create `tests/security/red_team/` with simulated malicious diff (oversized patch, path traversal) & plugin signature spoof.
- Revocation & Quarantine: implement `tools/marketplace_revoke.py` to blacklist plugin IDs & revert last safe commit in autopilot branch.

## Reliability & Operations

- Error Budgets: P90 intent→verify < 3m (Phase 2), P95 autopilot PR success ≥60% (Phase 4).
- Disaster Recovery: audit ledger backup task (`tools/backup_audit.py`) nightly; redact PII tokens via hashing.
- Canary Autopilot: shadow mode flag `AETHERRA_AUTOPILOT_CANARY=1` produces draft PR without write; compare outcomes.

## CI/CD & Environment Strategy

- Matrix: py{3.11,3.12,3.13} + Windows/Linux; Node LTS for JS adapters.
- Selective Tests v1: impact analyzer returns candidate set; always run full suite if <25 tests selected or selection logic fails.
- Pre-commit: enforce black/isort/ruff, prettier, secrets scan (trufflehog or custom), license header check.
- Cache: pip + node modules keyed by lock hash; semantic index embedding cache warmed in nightly workflow.

## DevEx & Lyrixa IDE Enhancements

- .aether LSP reference: hover (meta/policy/require), diagnostics (risk hints), code actions (add missing require, add retry/timeouts).
- Accessibility: contrast ≥4.5:1, focus ring for all interactive elements, ARIA roles for panels.
- Keyboard Map: publish `docs/shortcuts/LYRIXA_IDE_SHORTCUTS.md` (VS Code parity where sensible).
- Telemetry (opt-in): event schema (command_invoked, gate_failed, patch_applied, revert_performed) with hashed repo ID.

## Intelligence & Data Layer

- Semantic Index Pipeline: background worker builds embeddings for code/tests/docs; invalidation via git diff heuristic + mtime.
- Prompt/Template Versioning: store template hash + semantic diff in audit entries; rollback if regression score drops.
- Evaluation Suite: `tests/eval/` with fixed scenarios (rename, test-gen, doc-sync) returning structured metrics.

## Marketplace & Policy

- Trust Levels: experimental (default), standard (tests+signing), trusted (manual review), verified (security audit + usage threshold).
- License Compliance: enforce SPDX detection before publishing; block AGPL if policy disallows.
- Revocation Flow: signed revocation list file distributed; client refuses load if signature invalid or plugin revoked.

## Policies & Profiles

| Profile | Flags                                        | Write Permissions         | Guardrail Strictness                                                  |
| ------- | -------------------------------------------- | ------------------------- | --------------------------------------------------------------------- |
| test    | `AETHERRA_PROFILE=test`, deterministic seeds | None (dry-run only)       | Highest (strict risk, full gates)                                     |
| staging | `AETHERRA_PROFILE=staging`                   | Feature branches          | Medium (allow selective tests)                                        |
| prod    | `AETHERRA_PROFILE=prod`                      | Protected branches via PR | High security, selective tests allowed only if confidence > threshold |

## Rollback Cookbook

1. Bad Diff Applied: use stored rollback token -> `aetherra_code revert --token <id>` (Phase 1) then re-run verify.
2. Gate Failure After Merge: create hotfix branch, revert commit (`git revert <sha>`), open PR with failure diagnostics attached.
3. Compromised Plugin: run revoke tool; quarantine by disabling in registry & triggering autopilot branch revert to last passing commit.

## Metrics Baselines (Initial)

| Metric                   | Baseline           | Target Phase 2 | Target Phase 4 |
| ------------------------ | ------------------ | -------------- | -------------- |
| Coverage %               | 17.0               | ≥25            | ≥45            |
| Intent→Verify P90        | N/A (not measured) | <3m            | <2m            |
| Autopilot PR Success     | 0%                 | 40%            | ≥60%           |
| Refactor Safety (rename) | N/A                | 70%            | ≥90%           |
| Patch Revert Use Rate    | N/A                | Tracked        | <5% of patches |

## Release Train

- Cadence: minor phase increments every 2 weeks; patch releases ad-hoc for security/fix.
- Changelog Format: `CHANGELOG.md` keep/cut pattern (Added, Changed, Fixed, Security, Deprecated, Removed).
- Release Criteria: all gates pass, no open critical security findings, ADRs merged, metrics table updated.

## Additional Action Items

- [ ] Create ADR directory + template.
- [ ] Implement revoke & quarantine tooling.
- [ ] Add evaluation suite harness.
- [ ] Add semantic index incremental builder.
- [ ] Publish accessibility / keyboard shortcuts doc.
- [ ] Implement audit ledger backup + redaction.
- [ ] Extend unit test coverage for rollback edge cases (binary-like diffs, permission errors)
- [ ] Add coverage delta calculation & persistence layer
- [ ] Introduce lightweight provenance hash for each patch bundle (prep for signing)

## Latest Delta (2025-09-08)

Progress Since 2025-09-07:

- Refactored hub `/metrics` endpoint (`prometheus_metrics`) into scoped inner emitters – reduced cyclomatic complexity without changing metric names/labels.
- Sanitized plugin registration error response (generic client error, internal detailed logging retained).
- Sanitized web interface message relay endpoint to suppress internal engine error strings; emits generic failure while logging full stack.
- Consolidated outward error messaging pattern (generic: "An internal error occurred." / domain-specific variants) while preserving internal `logger.error(..., exc_info=True)`.
- Verified no syntax/runtime regressions post-refactor (module import check pass).
- Implemented per-file coverage snapshot system with retention + orphan pruning.
- Added structured gating reasons (COVERAGE_DROP, FILE_COVERAGE_DROP, TEST_SELECTION) and schema_version=1 field.
- Added future flags placeholder (branch/statement enforcement) in gate report.
- Integrated PR description generator (env toggled) summarizing gates, reasons, deltas.
- Implemented test selection heuristic stub (confidence, fallback logic) integrated into gates.

Decisions / Adjustments:

- Defer extracting metrics emitters into separate module until Phase 4 (Refactor & Semantic Layer) to avoid premature public surface changes.
- Adopt inner-helper pattern for large Flask route metrics to keep closure access to runtime state and minimize signature churn.
- Formalize error response contract: never expose raw exception text across hub/web API boundaries (Phase 1 security hardening extension).
- Lock Phase 1 scope; remaining semantic & autonomy features explicitly advanced to Phase 2.

Phase 1 Wrap‑Up (No Remaining Targets): All originally defined completion criteria met. Preparatory flags (`future`) and schema versioning enable forward-compatible evolution in Phase 2.

New / Updated Risks (carried into Phase 2 backlog):

| Risk                            | Update                                                             | Mitigation                                                             |
| ------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| Metrics refactor drift          | Future externalization could alter ordering consumed by dashboards | Snapshot scrape + contract note before Phase 4 refactor                |
| Coverage delta accuracy         | Line coverage only; branch metrics deferred                        | Add branch instrumentation prototype behind feature flag               |
| Test selection false confidence | Heuristic simplistic; may miss edge dependencies                   | Keep confidence gating + fallback full run; enhance with graph Phase 2 |

Planned ADR Queue (to draft):

- ADR-0001: Coverage Delta Data Model & Storage
- ADR-0002: Test Selection Heuristic v1 (Touch / Symbol Inversion Hybrid)
- ADR-0003: Gating Reasons Schema & UI Contract
- ADR-0004: Metrics Refactor Externalization Strategy (defer until Phase 4 window)

Design Notes (In Progress):

Coverage Delta (v1):
- Collect `coverage.json` artifact before & after run (or single post run plus cached baseline hash for changed files).
- Compute per-file: lines_covered_before, lines_covered_after, delta, percent_change.
- Gate failure if any tracked file loses covered lines (>0 delta negative) unless explicitly waived via allowlist.
- Persist structure under `audit/coverage_delta/<timestamp>.json` and embed summary in ledger entry.

Gating Reasons Emission:
- Provide ordered list; UI can render severity badges.
- Codes examples: `FORMAT_NON_COMPLIANT`, `TEST_FAILURE`, `COVERAGE_DROP`, `SEC_POLICY_VIOLATION`.
- Machine-consumable for future autonomy policy evaluation.

Test Selection Stub:
- Inputs: touched file paths, crude symbol extraction (regex of `def|class`), historical test file map (simple JSON cache updated nightly).
- Output: candidate_tests (list), confidence_score (0-1), reason (string), fallback (bool).
- If fallback true OR confidence <0.8 => run full suite.

---

## Latest Delta (2025-09-07)

"Safe Edit Loop" early slice landed: formatting/lint gate operational (black/isort/ruff), diff risk metrics + colorized preview, rollback snapshots enriched (content + line deltas), plugin scaffold & manifest validation shipped, encoding robustness pass completed, and ruff configuration migrated. Remaining near-term focus: finish unused import purge, introduce coverage delta + gating rationale, and stand up test selection stub ahead of Patch Composer v2.

## Adoption Guide

1. Use Assist mode for exploratory changes (`AETHERRA_MODE=assist`).
2. Enforce Spec→Tests early: write tests before implementation patch.
3. Transition to Co‑drive once patch composer v2 lands.
4. Enable Autopilot only after ownership + risk policy configuration.

## References

- Coding System Spec: `docs/AETHERRA_CODING_SYSTEM.md`
- Security System: `docs/AETHERRA_SECURITY_SYSTEM.md`
- Plugin System: `docs/AETHERRA_PLUGIN_SYSTEM.md`
- Memory System: `docs/AETHERRA_MEMORY_SYSTEM.md`

---

Prepared for iteration launch. Update this roadmap at each phase boundary with delta notes and metrics.

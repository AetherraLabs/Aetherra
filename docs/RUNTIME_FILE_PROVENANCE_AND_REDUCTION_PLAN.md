# Aetherra Runtime File Provenance and Safe Reduction Plan

**Status:** proposed baseline and audit contract — no deletion authorized.  
**Initial inventory source:** `main@64d5d5ccecbf2c445eac80902aad537e34d30ebf` (2026-11-27). **Superseded for execution:** PR #380 merged as `b72952bab04527073de50550f94cfef9e0c81da1` and current main is `a47e199b6903e4c6d277272e2434b055b6773fba`. Recompute all tree counts and reachability on the execution-time HEAD; initial counts remain historical only.  
**Owner:** Aetherra architecture, runtime, release, Security/Guardian and subsystem maintainers.  
**Parallel work:** the separate runtime fake-evidence plan in PR #384, now-merged Temporal PR #380, existing bug register, and legacy UI cleanup must retain their own acceptance and branches.

## Objective

Answer, for **every tracked file**: *Why does it belong here? Which supported Aetherra behavior, runtime entrypoint, build, test, governance rule or retained history requires it? What breaks if it disappears?* Then reduce the active source tree only after reversible, evidence-bound changes.

**Do not infer "unused" from "not imported".** A module may be loaded dynamically, read as a file, used by CLI/build/CI, required by tests, signed, referenced as a schema/config, fetched as a model asset, or intentionally held as future research. Conversely a module that imports successfully may do nothing useful and must still be reviewed for behavioral necessity.

### Baseline — one GitHub tree, not runtime execution

Complete Git tree (not truncated): **2,044 tracked files**, comprising **1,446 Python, 353 Markdown, 69 JSON, 41 YML, 28 HTML, 22 Aether Script, 16 PowerShell and other extensions**. Directory distributions include `Aetherra/` 725, `tests/` 586, `docs/` 301, `tools/` 197, `aetherra_hub/` 60. Within `Aetherra/`: `aetherra_core/` 238, `lyrixa/` 100, `consciousness/` 99, `plugins/` 74. There are 25 root-level Python files. This is a tracked-file inventory, **not a dead-code percentage**.

Existing work: `docs/REPOSITORY_CLEANUP_PLAN.md`, `docs/ROOT_SCRIPT_WORKFLOW_TRIAGE.md`, `docs/UI_REBUILD_AND_CLEANUP_PLAN.md` and `docs/UI_MIGRATION_MAP.md`. These are historical disposition inputs, **not proof of current runtime reachability**. Their dated inventories, paths and readiness claims must be checked against the current tree. **Do not rerun the root cleanup scripts or rewrite Git history as a shortcut.**

## Audit axes and file classification

Every file receives an immutable path and hash at the audited revision, one primary category, an owner, observed/declared consumers, profile-specific reachability, and evidence.

| Decision | Meaning | Action |
| --- | --- | --- |
| CORE-RUNTIME | Needed for supported normal Aetherra boot, memory/chat, Guardian/Security, lifecycle, Hub and canonical Observatory | Keep; document ownership |
| OPTIONAL-RUNTIME | Reachable only after an explicitly approved feature/mode, plugin or experiment is enabled | Keep if governed, bounded, reviewed and used; otherwise evaluate |
| COMPATIBILITY | Backward-compatible entrypoint/import alias, API contract or path still used by callers | Keep until migrated and dual-path checks pass |
| CONFIG/RESOURCE | Non-Python policy/schema/signature/manifest/asset required at runtime | Keep; record exact loading path and integrity |
| BUILD/RELEASE | CLI packaging, source dist, release signing, dependencies, workflow, tools | Keep where required by verifiable build/release |
| TEST/QUALITY | Fixtures, mocks, acceptance suites, test helpers, lint/static gates | Keep if serving an active contract; consolidate only under test review |
| DOC/GOVERNANCE | Canonical contracts, evidence, runbooks, legal/security, contributor navigation | Keep with retention policy |
| RESEARCH/PROTOTYPE | Experiment not part of supported runtime; no authority to act | Preserve separately or classify deferred with provenance |
| LEGACY/ARCHIVE | Historical superseded implementation, referenced only for reproducibility/provenance | Archive/tag first, remove from active tree only with approval |
| GENERATED/ARTIFACT | Re-creatable cache, database, report, runtime output mistakenly tracked | Verify reproduction + consumers; remove from tracking non-destructively |
| UNKNOWN | Missing data, dynamic consumer, ambiguous ownership or unresolved references | **Protected: cannot delete** |

These classifications are orthogonal to **mock/fake/simulated** behavior; PR #384 governs truthful values and evidence, this plan governs file ownership and necessity.

## The critical difference between two graphs

**Technical reachability:** which exact source files enter or are read during a profile's launch, usage, shutdown, build, and test.

**Behavioral necessity:** which subsystem feature/contracts require them to make the system genuinely Aetherra. A compatibility alias can be reachable but no longer product-critical; dormant Memory helpers may be essential for a deferred feature. Keep the distinction visible.

### Root set: support profiles, not "import all modules"

At minimum capture independently:

1. **Primary normal launcher:** `aetherra_os_launcher.py`, along with `aetherra_os.py` and `main.py` compatibility paths. Include complete start, health, bounded observation, orderly stop and restart.
2. **Conversations and continuity:** Hub -> Engine -> actual SQLite Memory -> local semantic recall -> Lyrixa; competing facts, unknowns, restart, local profile isolation, actual authorization. No live-model provider required for deterministic offline tracing; separately verify a permitted real-provider path if needed.
3. **Cognitive Observatory:** `Aetherra/runtime_ui/`, `aetherra_hub/blueprints/runtime_ui.py`, `Aetherra/lyrixa/gui/` React/Vite source, static dist generation, API/event subscriptions and failure states. Dist is a generated artifact, not a source file.
4. **Governed runtime:** Security, Guardian, Homeostasis, Maintenance, Kernel, registry, Self-Improvement proposal-only, optional Self-Incorporation under its explicit flag, Aether Script validation, signed audit. Exercise both enabled and disabled paths; **do not trigger live mutation or unapproved autonomy**.
5. **Memory and Consciousness optional paths:** QFAC/STORM, observer, owned checkpoint persistence/recovery. Temporal PR #380 **was unmerged at the original baseline but is now merged into main**. Its normal-launch temporal observation, existing-Memory history ownership, restart restoration, audit and inspector paths must be protected as supported opt-in runtime paths in the new baseline. Do not equate disabled-by-default with unused.
6. **Public CLI and entrypoints:** `aether.py`, `pyproject.toml` project scripts `aetherra` and `lyrixa`, operators' supported smoke and diagnostics, `setup.py`, packaging and Windows source-runtime entrypoints.
7. **Plugins, agents and scripts:** plugin manifests, filesystem scans, plugin registration, script `.aether` signature verification, approval contracts, dynamically resolved imports and entry-point scripts. Do not remove only because a plugin is disabled in the baseline.
8. **Release and developer profiles:** source distribution, wheel, signed release/manifest, CI workflows, docs consistency, source and data files in tests, import-map policy, dependency locks and license validation.
9. **Research and legacy:** separate, clearly labeled inventories, not part of the core boot metric. A historical code path may be preserved outside the active tree without pretending it is supported.

Profile matrix records platform (Windows verified vs Linux CI), Python version, environment/flags (redacted), requirements/model revision, authority, start/stop trigger, and negative cases. Capture at least disabled/observe/full supervised modes with effective configuration, plus opt-in feature paths; do not assume a mode is safe because its name says so.

### Observed technical core (evidence from current source, not exhaustive closure)

- `aetherra_os.py` calls `aetherra_os_launcher.AetherraOSLauncher`. `main.py` delegates to `aetherra_os.main`; the root `aether.py` is the Aether Script and CLI path.
- `aetherra_os_launcher.py` orchestrates root service registry, Kernel, Memory, plugin manager, Engine and Hub. Self-Incorporation registration/activation is conditional; QFAC has profile-dependent early stub logic. Presence in code does **not** prove activation.
- `Aetherra/plugins/core/plugin_registry.py` discovers plugins by scanning manifests from filesystem locations; static AST import reachability misses this.
- Hub blueprints and the Observatory frontend consume routes and static resources; do not prune runtime UI files just because Python never imports the generated `dist` output.
- `MANIFEST.in` includes the `Aetherra` package but excludes many root files; `pyproject.toml` declares console scripts and dependency extras. Packaging graph differs from source-run graph and must be compared explicitly.
- `docs/import_map.md` enforces canonical imports and provides migration constraints. Import aliases are not automatically unnecessary.

## Evidence capture toolchain: build first, delete later

**Static graph** (owned standard-library tool, suggested `tools/maintenance/runtime_file_audit.py`):
- Enumerate `git ls-files -z`; reject missing/modified source state unless explicitly permitted; record revision and SHA-256.
- Parse Python AST for `import`, `from ... import`, local relative imports, and constant-string calls to `importlib.import_module` and `__import__`; resolve local modules and record ambiguity/import package `__init__`.
- Record raw non-code file references in `Path`, `open`, config URLs, manifest entrypoints, template names, subprocess invocations, package-data, CI/packaging manifests, Aether Script files, plugin search roots, UI paths and signed resource patterns. These are **reference candidates**, not definitive consumers.
- Build incoming/outgoing edge sets with types `static_import`, `dynamic_literal`, `package_entrypoint`, `resource_reference`, `plugin_discovery`, `build_input`, `ci_input`, `documentation`. Distinguish unresolved/external from local; never treat a test-only edge as proof of normal runtime.
- Output sorted, bounded JSON/CSV/DOT and a human-readable summary of **all 2,044 files**, including protected unknowns, suspected orphans and evidence per claim. No delete/apply functionality.

**Runtime trace** (separate, opt-in, isolated):
- Capture loaded module `__file__` paths, Python import events, file opens and package resource access in **real subprocesses** through a guarded audit/profiler wrapper. Include child processes only with explicit launch ownership and closure; note native-library, browser, virtual-resource, and delayed-load limits.
- Require actual start -> conversation -> observable status -> feature selection -> stop/restart tests and record phase/timestamp/profile. Exclude personal content/secrets; normalize canonical paths inside the checkout.
- Include real file opens and reads, not just Python imports; record static JS/CSS build and asset references separately. Emit no fake healthy metric.
- Compare runtime trace with static graph, packaging build and tests. A missing runtime edge is **not** automatically an unused file.

**Coverage and confidence:**
- `required_proven`: observed under an accepted profile or build/CI contract.
- `required_declared`: dynamic feature or documented operator contract without sampled invocation.
- `unobserved_review`: no sampled use, but static or policy reference exists.
- `orphan_candidate`: no resolved edges, no dynamic/resource references after review, no test/release/legal/history requirement.
- `safe_to_archive` requires maintainer review plus successful removals in a reversible branch, not just a low graph degree.

Produce artifacts **outside the repository** by default; commit only compact sanitized manifest and summary when accepted, never massive generated imports, local paths, raw user data or secrets.

## Ordered cleanup waves and required gates

### Wave 0 — Freeze scope and capture baseline

- Include merged PR #380 (Temporal) in the current baseline; coordinate separate PR #384 (runtime mock cleanup), any active development worktrees and issue register. Never change their working directories, worktrees or unpublished files.
- Record clean checkout, exact head, public launch/test/CI profiles, signed scripts, approvals and baseline outcomes with real passes/skips/failures. Preserve current unknown-cause issues.
- Define canonical Aetherra identity and minimum usable system contract: governed boot, accurate status, actual persistent memory/retrieval, chat/Engine interface, shutdown/restart, safe Observatory, stable Security/Guardian, and truthful optional disabled state. **Do not declare the other documented systems obsolete solely because they are not required on the first frame.**
- Acceptance: reviewed source of truth and run list, baseline reproducible, no accidental broad cleanup authorization.

### Wave 1 — Machine-readable file inventory (no deletion)

- Implement and run static graph and resource graph at a pinned revision.
- Run profile-specific live file-use traces on isolated synthetic data with enforcing Guardian and Security.
- Compile `runtime-file-register.json` or similar, with one record per tracked file, evidence links and proposed disposition. Analyze root modules, duplicate namespaces and deprecated shims separately.
- Review all unknown/ambiguous imports, plugin scans, `.aether` signatures and `lyrixa`/Observatory asset chains.
- Acceptance: every tracked file accounted for; critical and unknown dynamic edges identified; no deletion list without reviewer.

### Wave 2 — Cheap source reduction only where proof is strong

- Start with generated/reproducible artifacts or duplicated **non-authoritative** reports still tracked; check if they are actually in current tree before proposing removals.
- Update `.gitignore`, packaging excludes or artifact destinations only where necessary. Do not rewrite Git history, force-push branches or remove historical failure receipts.
- Perform each change in small exact-path PRs with an inverse move plan, boot, packaging and targeted tests.

### Wave 3 — Legacy UI and duplicate runtime adapters

- Map every old UI/launcher/adapter to canonical owner and all import/CLI/test callers. Preserve `Aetherra/lyrixa/gui` React as the current Observatory frontend and `Aetherra/runtime_ui` canonical state contract.
- Migrate consumers and tests to the canonical implementation, with temporary compatibility shims where required. Only after zero known consumers under all supported profiles may the legacy path be archived/removed.
- Avoid a mass move that breaks Python package identity, Windows paths, QFAC signing or launcher readiness.

### Wave 4 — Optional subsystem and research separation

- Deliberately separate optional active features from unused future research. Audit Quantum, STORM/QFAC, alternate Memory variants, legacy self-improvement/trainer, simulated experiments, old dashboards, duplicated agent orchestration and plugin examples.
- A module with no normal-launch usage can still be owned research or a future milestone. Label and relocate behind explicit flags only after acceptance, rather than silently deleting work.
- This wave coordinates with PR #384's fake-data remediation; file curation and behavior replacement are separate changes.

### Wave 5 — Enforce single source of truth

- Document one canonical implementation and service owner per capability, plus supported adapters and extension points. Check duplicated `memory`, `agent`, `core`, `plugin` and interface namespaces for competing authorities. Duplicate names do not automatically imply duplicate functionality.
- Trim redundant import chains, circular imports, incompatible aliasing and dead registrations with regression proofs. Ensure the 20 documented system contracts still have honest owners.
- Add a CI drift check: new tracked executable files require a registered owner/category and known runtime/test/research purpose. Keep optional resources and plugin discoverability rules explicit.
- Verify fresh Windows alpha install, full launcher+conversation+restart, Observatory, Guardian/Security, signed Aether Script, packaging, offline CI and focused optional subsystem tests. Keep unsupported outcomes visible and readiness unchanged.

## Exact removal acceptance contract

No path may be removed unless its proposed change includes:
1. Source revision, existing Git blob or SHA-256, file owner and current disposition.
2. Zero **unresolved** use by active entrypoints, optional feature loading, scripts, package resources, import aliases, tests, workflows, tooling or legal/licensing references.
3. A documented replacement or explicit historical archive/recovery pointer.
4. Updated references, commands, import paths, doc links, manifest entries and signed resources.
5. A reversible exact-path change with comparison tests before and after, including full alpha launcher and packaging when relevant.
6. Maintainer approval and verification receipts; failed CI results stay visible and are not waived by unrelated reruns.

Use `git rm` only on reviewed exact paths after validation, never a broad `find ... -delete`, wildcard prune or destructive `git filter-repo` on the shared history. Do not silently change established service policy, risk acceptance, or release status.

## Files and areas to investigate early (not removal recommendations)

| Area | Reason for review |
| --- | --- |
| Root 25 Python files | Multiple command surfaces and daemon/compatibility entrypoints require a supported-entrypoint matrix |
| `Aetherra/aetherra_core/` (238) | Complex engine/memory/orchestration hierarchy; inspect duplicate responsibility and dynamic adapters |
| `Aetherra/lyrixa/` (100) | Persona internals, plugin UI, canonical React frontend and retired UI compatibility mixed |
| `Aetherra/consciousness/` (99) | Current observer + older experimental models with optional imports; Temporal PR #380 merged; validate new runtime history files |
| `Aetherra/plugins/` and `plugins/` | Manifest discovery and signed script loading are invisible to naive import tools |
| `Aetherra/memory/`, `Aetherra/aetherra_core/memory/`, `Aetherra/core/` | Multiple Memory namespaces; distinguish true store, adapters, legacy engines and research |
| `tools/` (197) | Many may be CLI/CI/smoke/generator dependencies, not runtime; trim by workflow evidence |
| `docs/` (301) | Separate current authority documents, immutable evidence, old reference and reports; avoid deleting provenance |
| `tests/` (586) | Active regression and safety coverage; old fixtures must be reviewed by contract, not "unused at runtime" |
| Root `MANIFEST.in` vs `pyproject.toml` | Source-run imports and wheel/sdist consumers can disagree; audit before module moves |

## Required Codex handoff (first execution, **no cleanup writes**)

> On a clean isolated checkout of `AetherraLabs/Aetherra` at a freshly fetched and pinned execution-time main SHA (which must include merged PR #380), implement a standard-library read-only **file provenance auditor** under `tools/maintenance`. Produce a complete JSON/CSV register with every `git ls-files` path, its Git/current hash, type, ownership candidate, static Python imports, dynamic-literal imports, resource and build references, test/CI relevance, entrypoint roots and unresolved edges. In a separate bounded supervised-alpha harness, observe actual imported modules, file reads and loaded services across normal boot, memory recall, Hub/Observatory and stop/restart. Use isolated synthetic data and existing strict policies. Provide exact execution commands, evidence hashes, missed-edge caveats, and candidate dispositions; **do not remove or move a single runtime file**. Propose the first narrowly scoped cleanup PRs only after comparison with packaging, tests, plugin manifests and maintainers' reviewed acceptance gates.

**Success is a smaller, comprehensible Aetherra that still demonstrably behaves as Aetherra—not the smallest possible file count.**

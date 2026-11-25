# Aetherra Master Roadmap

Updated: 2026-11-24

This is the single source of truth for Aetherra roadmap planning.

It consolidates the previous root, beta, production, memory, plugin,
consciousness, coding, quantum, living, and build-order roadmaps. Older roadmap
files were treated as historical inputs, not authoritative status records.

## Roadmap Rule

A roadmap item is complete only when it has:

- A current implementation path or system document.
- Clear authority boundaries.
- Safety limits appropriate to the system.
- Focused verification, tests, or an executable validation command.
- Documentation that explains what is complete and what is still limited.

Claims from older roadmaps that could not be verified by current docs, code, or
validation are not carried forward as complete.

## Current Project State

Personal continuity milestone (2026-11-19): the existing full-launcher
Hub/Engine/Memory path now supports bounded personal-fact recall across a process
restart. Competing facts, unknown attributes and isolated directories are covered
offline and in scoped OpenAI gpt-4o runs, including varied paraphrases and
missing-fact/separate-profile checks.
See `docs/PERSONAL_CONTINUITY.md` for exact commands, evidence and limitations.
Account isolation and broader memory/runtime redesign remain outside this scope.

Aetherra's existing supervised internal-alpha boundary covers the verified
Windows source-runtime profile. The current objective is bounded internal
testing with governance, observation and signing controls enforced. The
checkpoint verification qualification below does not expand that boundary.

C1 and C2a are merged through PRs #354 and #353 and released as
`v0.5.0-beta.13` (`949312c3`). Hosted main CI and production/release signing
passed. The command-task diagnostic correction passes local regressions and the
full suite; review/publication and hosted follow-up CI remain pending. The
original stop-receipt failure is retained and its slow operation is unproven. See the
[current decision](ALPHA_READINESS_DECISION.md#checkpoint-stop-follow-up).
Historical browser/live-model results retain their original source scope;
fresh Python installation, current browser/live-model checks and physical
keyboard shutdown remain unverified. The earlier supervised GO is not expanded.
C2b automatic selection, periodic saves and retention remain deferred. Pending
TemporalConsciousnessEngine work stays separate; checkpoints confer no
autonomous action authority or unattended readiness.

Authoritative identity and system references:

- `docs/WHO_IS_AETHERRA.md`
- `docs/ACTIVE_SYSTEMS.md`
- `docs/BUILD_ORDER.md`
- `docs/SYSTEM_INDEX.md`
- `docs/ALPHA_READINESS_CHECKLIST.md`
- `docs/ALPHA_OPERATOR_RUNBOOK.md`
- `docs/ALPHA_READINESS_DECISION.md`

## Verified Foundation Status

The following status reflects the current architecture documents and the
verification run on 2026-07-16.

| Area | Correct Current Status | Verification |
| --- | --- | --- |
| Security | Functional complete | System docs, Integration Validation, safety tests |
| Guardian | Functional complete | System docs, Integration Validation, safety tests |
| Homeostasis | Functional foundation complete | System docs, Integration Validation |
| Self-Improvement | Functional foundation complete | System docs, proposal-only authority boundary |
| Maintenance | Functional foundation complete | System docs, Integration Validation |
| Self-Incorporation | Functional foundation complete | System docs, scope-lock and rollback fail-closed tests |
| Memory | Functional foundation complete | System docs; deeper memory roadmap claims are not all alpha-verified |
| Kernel | Functional foundation complete | Alpha boot validation |
| Agent System | Functional foundation complete | System docs and boot/import validation |
| Aether Script | Functional foundation complete | Integration Validation runtime gate |
| Integration Validation | Functional foundation complete | `python -m Aetherra.integration_validation` |
| Runtime UI | Functional foundation complete | Runtime UI build and focused tests |
| Lyrixa | Functional foundation complete | System docs; Lyrixa is persona/interface, not a separate intelligence |
| Hub | Functional foundation complete | Alpha boot validation readiness contract |
| Engine | Functional complete | Engine system contract and focused hardening tests |
| Artificial Intelligence | Functional foundation complete | System docs and boot/import validation |
| Consciousness | Functional foundation complete | System docs; older transcendence claims are historical/unverified |
| Coding | Functional foundation complete | System docs; governed proposal/verification posture |
| Chat | Functional foundation complete | System docs and Hub readiness surface |
| AI Trainer | Functional foundation complete | System docs; alpha trainer limitations remain |

## Verification Evidence

Last verified locally on 2026-07-16:

```powershell
python tools\alpha_boot_validation.py
python -m Aetherra.integration_validation
python tools\verify_docs_consistency.py
python tools\ci_verify_no_website_artifacts.py
git diff --check
```

Results:

- Alpha boot validation passed: 4 checks.
- Integration Validation passed: 5 checks.
- Docs consistency passed: 0 missing documented endpoints/env vars.
- Website artifact guard passed.
- Whitespace check passed.

Runtime UI verification:

```powershell
Push-Location Aetherra\lyrixa\gui
npm.cmd run build
Pop-Location
python -m pytest -q -o addopts= --basetemp .pytest_tmp_runtime_ui `
  tests\unit\test_runtime_ui_api.py `
  tests\unit\test_runtime_ui_contract.py `
  tests\unit\test_runtime_ui_manifest.py `
  tests\unit\test_runtime_ui_observatory.py `
  tests\unit\test_runtime_ui_payload.py `
  tests\unit\test_runtime_ui_query.py `
  tests\unit\test_runtime_ui_scene.py `
  tests\unit\test_runtime_ui_snapshot.py
```

Results:

- Runtime UI build passed.
- Runtime UI focused tests passed: 37 tests.
- Build warnings remain: large JS chunk and stale Browserslist/baseline data.

Safety-focused tests:

```powershell
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_validation `
  tests\unit\test_integration_validation.py `
  tests\unit\test_selfinc_integration_guardian.py
```

Results:

- 18 tests passed.

## Corrected Build Sequence

| Order | Milestone | Target State | Current Status |
| --- | --- | --- | --- |
| 1 | Security | Functional complete | Complete |
| 2 | Guardian | Functional complete | Complete |
| 3 | Homeostasis | Functional foundation complete | Complete |
| 4 | Self-Improvement | Functional foundation complete | Complete |
| 5 | Maintenance | Umbrella lifecycle foundation | Complete |
| 6 | Self-Incorporation | Functional foundation complete | Complete |
| 7 | Memory | Functional foundation complete | Complete |
| 8 | Consciousness | Functional foundation complete | Complete |
| 9 | Agent System | Functional foundation complete | Complete |
| 10 | Aether Script | Runtime validation foundation | Complete |
| 11 | Integration Validation | Cross-system validation foundation | Complete |
| 12 | Runtime UI | Cognitive Observatory foundation | Complete |
| 13 | Kernel | Runtime readiness foundation | Complete |
| 14 | Hub | API readiness foundation | Complete |
| 15 | Lyrixa | Guided interaction foundation | Complete |
| 16 | Engine | Functional cognitive coordinator | Complete |
| 17 | Artificial Intelligence | Engine readiness foundation | Complete |
| 18 | Chat | Transport readiness foundation | Complete |
| 19 | Coding | Proposal and verification foundation | Complete |
| 20 | AI Trainer | Training readiness foundation | Complete |
| 21 | Internal Alpha | Safe internal alpha gate | Active |
| 22 | Beta Hardening | CI/security/stability maturity | Planned |
| 23 | Production Readiness | Operational maturity and release discipline | Planned |

## Current Priority: Internal Alpha

The current roadmap milestone is supervised internal alpha on the verified
Windows source-runtime profile.

Primary gate:

- `docs/ALPHA_READINESS_CHECKLIST.md`

Current alpha status (2026-11-22):

- PR #327 merged as `a0e8857c`; clean released main is `f55d48a9`,
  signed `v0.5.0-beta.6`. The approved-key signature and artifact hashes verify.
- The Windows/Python 3.13 source-runtime profile installs in a fresh venv with
  no inherited system packages. All 168 installed distributions audit with
  zero findings/skips; dependency and exact-lock checks pass.
- Default suite: **3,136 passed / 40 skipped**, plus five passing subtests, exit 0.
  Clean main: 87 focused regressions, boot/integration/import/hygiene, three
  gpt-4o turns without fallback, and clean shutdown pass. Browser source is
  unchanged from the verified fresh-install stop/reconnect check.
- All 12 main validation workflows and Release pass. Required production signing,
  Guardian/Security enforcement and the fixed quality baseline remain intact.
- **GO for supervised internal alpha on this documented profile.** Stage 21 stays
  active for bounded operation. Unattended/production use and unverified graphs
  remain NO-GO. Beta Hardening and Production Readiness remain Planned.

Current alpha boundaries:

The first Stage 21 supervised exercise on PR #328 main (`ff359b02`) completed
600 + 300 steady-state seconds across restart. Sixteen gpt-4o turns had no
fallback; varied recall, unknown detail, identity and browser reconnection pass.
It exposed incorrect acknowledgments of newly supplied facts; the prompt repair
integrated through PR #347. The cold recall took 63.603 seconds total and
interrupted status polling before the second window. Preserve that historical
limitation. The Phase A candidate now verifies concurrent observation, actual-core
readiness and effective disabled/observation modes through a full-CLI restart smoke;
see [current evidence and limits](ALPHA_READINESS_DECISION.md#phase-a-core-integration-candidate).
After review/integration, Phase B addresses the bounded observation/maintenance
loop. This does not advance Beta or enable autonomous authority.
See [the exercise evidence](evidence/supervised_alpha_2026-11-22.json).

| Gate | Status | Next expectation |
| --- | --- | --- |
| Identity and foundations | Preserved | Retain entity/persona and authority boundaries |
| Desktop installation | Verified | Keep optional/wheel/platform exclusions explicit |
| Runtime, continuity and browser | Pass | Preserve strict observation and truthful readiness |
| Integrated main | Accepted | Use the verified source revision and runbook |
| Signing | Enforced and verified | Require the approved key and production policy on every release |
| Broader modes | Unverified | Gather separate evidence before extending GO |

## Beta Hardening Roadmap

Beta begins only after internal alpha readiness is accepted.

| Workstream | Objective | Success Signal |
| --- | --- | --- |
| Stability and quality gates | Reduce flaky or non-deterministic behavior | Green checks across repeated runs |
| Security and trust | Harden signing, sandbox, audit, scan, and approval surfaces | No active safety bypasses; code scanning triaged |
| Observability | Improve health and runtime state visibility | No unexplained unknowns in health/readiness surfaces |
| Runtime UI | Mature Cognitive Observatory without unsafe control surfaces | UI remains read-only or Guardian-mediated |
| Plugins | Keep safe extension primitives, not unchecked autonomy | Exemplar plugins documented and governed |
| Memory | Make memory health and graph state inspectable | Stable memory consistency checks |
| Federation prep | Define trust and handshake model before implementation | Threat model draft |
| Developer experience | Make first-run and contribution paths reliable | Setup/runbook validated by a fresh clone |

## Production Readiness Roadmap

Production readiness is not the current milestone.

Before production can be considered, Aetherra needs:

- Reproducible release process.
- Stable CI and security gates.
- Operational runbooks.
- Disaster recovery and rollback playbooks.
- Performance and load profiles.
- Long-running runtime stability validation.
- Clear support and security disclosure process.
- No active source path depending on generated local runtime state.

## Consolidated Domain Backlog

### Security and Guardian

Keep:

- Capability checks.
- Sandbox policy.
- Signing and verification.
- Audit and ledger integrity.
- Guardian allow, deny, approval, and containment decisions.

Next:

- Continue triaging GitHub Advanced Security findings.
- Expand approval workflow tests for risky execution paths.
- Keep performance policies from making Guardian a bottleneck.

### Runtime UI

Keep:

- Cognitive Observatory direction.
- Read-only foundation posture.
- Runtime UI bootstrap API contract.

Next:

- Reduce bundle size or split chunks if warnings become quality-gate blockers.
- Update Browserslist/baseline data during dependency maintenance.
- Add live browser smoke once the alpha runtime path is stable.

### Memory and QFAC

Keep:

- Memory as functional foundation complete.
- QFAC/quantum ideas as forward-looking tracks.

Corrected status:

- Older memory roadmaps claim many advanced phases complete. The current
  verified status is foundation complete, not full cognitive memory maturity.

Next:

- Validate memory graph health.
- Add memory consistency and pressure checks.
- Reconcile QFAC claims with current tests and operator-visible behavior.

### Consciousness

Keep:

- Consciousness as an architectural system for perception, attention,
  appraisal, deliberation, action, and reflection.

Corrected status:

- Older "singularity", "cosmic consciousness", and "beyond transcendence"
  claims are historical narrative or experimental records. They are not current
  alpha readiness claims.

Next:

- Keep consciousness documentation grounded in observable runtime traces.
- Avoid claims that imply sentience, AGI, or unbounded autonomy.

### Plugins and Hub

Keep:

- Hub readiness contract.
- Plugin GUI surfaces.
- Safe plugin extension primitives.

Corrected status:

- Older plugin marketplace launch timelines are superseded.

Next:

- Document 1-2 minimal safe exemplar plugins.
- Keep plugin install/activation paths Guardian and Security mediated.

### Coding and Self-Modification

Keep:

- Self-Improvement proposes.
- Self-Incorporation executes only approved locked plans.
- Guardian decides.
- Security enforces.
- Homeostasis verifies.

Next:

- Expand verification around code proposal, dry-run, rollback, and audit.
- Do not allow closed-loop self-modification without explicit governance.

### Quantum

Keep:

- Simulator-first quantum bridge.
- Deterministic test/CI behavior.
- QFAC and quantum tracks as research and optimization paths.

Corrected status:

- Quantum-native and hardware-offload claims remain research/pilot work unless
  backed by current tests and operator-facing status.

Next:

- Keep Q0/Q1 as current baseline.
- Treat Q2+ as backlog unless implemented and verified.

## Roadmap Claims Audit

| Source Area | Old Claim Pattern | Corrected Current Interpretation |
| --- | --- | --- |
| Root `ROADMAP.md` | Beta 0.2/0.3/0.4 sequence | Superseded by alpha foundation and 0.5.0 planning |
| `PRODUCTION_ROADMAP.md` | Beta-to-production phase plan | Historical production plan; not current status authority |
| `docs/BETA_ROADMAP_0.5.0.md` | Community beta focus | Folded into Beta Hardening workstreams |
| `docs/BUILD_ORDER.md` | Active build order | Restored as the active build dashboard; keep synchronized with this roadmap |
| Memory roadmaps | Multiple advanced phases marked complete | Foundation complete; advanced claims require current verification |
| Plugin roadmaps | Registry and marketplace launch timelines | Superseded; safe plugin primitives remain backlog |
| Consciousness roadmaps | Phase 7/8 transcendence completion claims | Historical/experimental; not alpha readiness claims |
| Quantum roadmaps | Q0/Q1 existing, Q2+ implement/pilot/research | Q0/Q1 retained; Q2+ backlog unless verified |
| Living roadmap | 2025 dated active/planned epics | Superseded; useful ideas folded into domain backlog |
| AI chat enhancement plan | Chat roadmap items | Folded into Chat and Runtime UI backlog |

## Former Roadmap Inputs

The following files were consolidated into this Master Roadmap and should not
be recreated as separate roadmap sources:

- `.github/DISCUSSION_SEED_BETA_ROADMAP.md`
- `ROADMAP.md`
- `PRODUCTION_ROADMAP.md`
- `Aetherra/consciousness/ROADMAP.md`
- `Aetherra/consciousness/EXTENDED_ROADMAP.md`
- `docs/BETA_ROADMAP_0.5.0.md`
- `docs/ROADMAP_TRACKING.md`
- `docs/QFAC_ROADMAP.ipynb`
- `docs/aetherra_quantum_roadmap_v_1.md`
- `docs/roadmap/*`

## Maintenance Rule

When roadmap status changes:

1. Update this file.
2. Update `docs/BUILD_ORDER.md` if milestone order, status, or active focus
   changed.
3. Update `docs/ACTIVE_SYSTEMS.md` and `docs/SYSTEM_INDEX.md` only if system
   status changed.
4. Run the relevant verification commands.
5. Record limitations honestly.
6. Do not create additional roadmap files.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

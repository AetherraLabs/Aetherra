# Aetherra Documentation

Welcome to the Aetherra documentation surface. If you are new, start with the
Quick Start below. If you are returning, jump directly to the System Index or
operator guides.

## Quick Start

| Audience | Start Here | Why |
| --- | --- | --- |
| New Contributor | `INDEX.md` | Curated map of core documents |
| Operator / Maintainer | `SYSTEM_INDEX.md` | Status and maturity dashboard |
| Workflow Author | `Aether_Script_Operator_Guide.md` | How to write, sign, and verify `.aether` |
| Architect / Reviewer | `DOCS_ARCHITECTURE.md` | Structure and governance rules |
| Security Auditor | `THREAT_MODEL.md` and `AETHERRA_SECURITY_SYSTEM.md` | Current surface and planned controls |

## Core Entry Points

| Doc | Purpose |
| --- | --- |
| `INDEX.md` | Canonical index of active specs and guides |
| `SYSTEM_INDEX.md` | Implementation maturity and quick navigation |
| `AETHERRA_MASTER_MAP.md` | Operational repository map and cleanup authority |
| `AETHERRA_FILE_MANIFEST.json` | Per-file and per-directory tracked inventory |
| `MASTER_ROADMAP.md` | Consolidated project roadmap and roadmap claims audit |
| `Aether_Script_Language_System.md` | Formal language and execution semantics |
| `Aether_Script_Operator_Guide.md` | Practical usage from authoring to verification |
| `AETHERRA_MEMORY_SYSTEM.md` | Memory architecture, recall, QFAC, and quantum bridge |
| `RELEASE_PROCESS.md` | How releases are staged, gated, and verified |
| `COVERAGE_POLICY.md` | Coverage philosophy and no-drop gate |
| `GO_NO_GO_GATES.md` | Readiness criteria and gating model |
| `DOCS_ARCHITECTURE.md` | How docs are structured and validated |

## Historical Material

Historical reports and superseded notes belong under `docs/archive/` when they
have ongoing traceability value. Active planning is consolidated in
`MASTER_ROADMAP.md`; active system status is tracked in `ACTIVE_SYSTEMS.md` and
`SYSTEM_INDEX.md`.

## Validation

Run the docs architecture verifier locally:

```powershell
python tools/verify_docs_architecture.py --strict
```

It checks required files, classification coverage, and emits a JSON report at
`docs/docs_architecture_report.json`.

## Contributing To Docs

1. Use conventional commit prefix: `docs:`.
2. Touch only what you can validate or clearly flag as speculative.
3. Update `SYSTEM_INDEX.md` if maturity changes.
4. Keep sections concise; link instead of duplicating.
5. Run architecture and consistency verifiers.

## Design Intent

We deliberately avoid collapsing everything into a single flat docs site until
core system specs stabilize. The dual layer lets us iterate rapidly while
maintaining a clean authoritative surface.

See `DOCS_ARCHITECTURE.md` for deeper governance detail.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

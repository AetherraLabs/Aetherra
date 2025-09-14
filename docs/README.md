# Aetherra Documentation

Welcome to the Aetherra documentation surface. If you are new, start with the Quick Start below. If you are returning, jump directly to the System Index or Operator Guides.

## Quick Start

| Audience              | Start Here                                        | Why                                    |
| --------------------- | ------------------------------------------------- | -------------------------------------- |
| New Contributor       | `INDEX.md`                                        | Curated map of core documents          |
| Operator / Maintainer | `SYSTEM_INDEX.md`                                 | Status & maturity dashboard            |
| Workflow Author       | `Aether_Script_Operator_Guide.md`                 | How to write / sign / verify `.aether` |
| Architect / Reviewer  | `DOCS_ARCHITECTURE.md`                            | Structure & governance rules           |
| Security Auditor      | `THREAT_MODEL.md` & `AETHERRA_SECURITY_SYSTEM.md` | Current surface & planned controls     |

## Core Entry Points

| Doc                                 | Purpose                                                    |
| ----------------------------------- | ---------------------------------------------------------- |
| `INDEX.md`                          | Canonical index of active specs & guides                   |
| `SYSTEM_INDEX.md`                   | Implementation maturity + quick navigation                 |
| `Aetherr_Script_Language_System.md` | Formal language + execution semantics                      |
| `Aether_Script_Operator_Guide.md`   | Practical usage (authoring -> verification)                |
| `AETHERRA_MEMORY_SYSTEM.md`         | Memory architecture (layers, recall, QFAC, quantum bridge) |
| `RELEASE_PROCESS.md`                | How releases are staged, gated, and verified               |
| `COVERAGE_POLICY.md`                | Coverage philosophy (no-drop gate)                         |
| `GO_NO_GO_GATES.md`                 | Readiness criteria & gating model                          |
| `DOCS_ARCHITECTURE.md`              | How docs are structured & validated                        |

## Extended Library

Thematic / historical / roadmap material is organized under `../docs-organized/` and intentionally separated from the high‑signal active spec layer to reduce noise.

| Category            | Path                                                     | Contents                                    |
| ------------------- | -------------------------------------------------------- | ------------------------------------------- |
| Roadmaps            | `../docs-organized/roadmaps/`                            | Evolution & milestone plans                 |
| Reports             | `../docs-organized/reports/`                             | Completion + test / phase reports           |
| Manifestos & Vision | `../docs-organized/manifesto/`                           | Narrative, intent, philosophy               |
| Fixes & Cleanup     | `../docs-organized/fixes/`, `../docs-organized/cleanup/` | Technical & structural remediation notes    |
| Legacy              | `../docs-organized/legacy/`                              | Superseded material (kept for traceability) |

## Validation

Run the docs architecture verifier locally:

```
python tools/verify_docs_architecture.py --strict
```

It checks required files, classification coverage, and emits a JSON report at `docs/docs_architecture_report.json`.

## Contributing to Docs

1. Use conventional commit prefix: `docs:`
2. Touch only what you can validate or clearly flag speculative with 🔮
3. Update `SYSTEM_INDEX.md` if maturity changes
4. Keep sections concise; link instead of duplicating
5. Run architecture + consistency verifiers

## Design Intent

We deliberately avoid collapsing everything into a single flat docs site until stabilization of core system specs. The dual layer lets us iterate rapidly while maintaining a clean authoritative surface.

---
See `DOCS_ARCHITECTURE.md` for deeper governance detail.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

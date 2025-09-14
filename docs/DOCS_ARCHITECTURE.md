---
title: Aetherra Documentation Architecture
status: Draft v1
last_updated: 2025-09-14
---

# Aetherra Documentation Architecture

This document defines how project documentation is structured, categorized, validated, and evolved. It introduces a dual‑layer model:

1. Active System & Operational Docs (in `docs/`)
2. Organized Library / Historical & Thematic Collections (in `docs-organized/`)

The goal is to provide both: (a) a fast, authoritative surface for engineers and operators and (b) a deep library for research, audits, historical context, and narrative evolution.

## Guiding Principles

- Single authoritative entry points (no drift-prone duplications)
- Incremental consolidation: never break existing links abruptly
- Separation of “living specs” vs. “historical / narrative / completion reports”
- All system documents grounded in current code or clearly marked as planned (🔮)
- Machine-verifiable completeness (see `tools/verify_docs_architecture.py`)

## High-Level Topology

| Directory         | Purpose                                                            | Change Frequency | Indexed In                               |
| ----------------- | ------------------------------------------------------------------ | ---------------- | ---------------------------------------- |
| `docs/`           | Active specs, system docs, policies, operator guides               | High             | `docs/INDEX.md` & `docs/SYSTEM_INDEX.md` |
| `docs-organized/` | Curated thematic groupings (roadmaps, reports, manifestos, legacy) | Medium           | `docs/DOCS_ARCHITECTURE.md`              |
| `documentation/`  | Transitional pointer (kept for backwards compatibility)            | Low              | Root README                              |

## Core Entry Points

- `docs/README.md` – Quick start navigation
- `docs/INDEX.md` – Canonical list of system & operator documents
- `docs/SYSTEM_INDEX.md` – Status dashboard (implementation maturity)
- `docs/DOCS_ARCHITECTURE.md` – (This file) structure & governance

## Document Classes

| Class               | Description                          | Examples                                            | Validation                  |
| ------------------- | ------------------------------------ | --------------------------------------------------- | --------------------------- |
| System Specs        | Define core subsystems and contracts | `AETHERRA_MEMORY_SYSTEM.md`                         | Listed in `SYSTEM_INDEX.md` |
| Operator Guides     | How to run / operate / verify        | `Aether_Script_Operator_Guide.md`                   | Must link to tests or tasks |
| Policies & Process  | Release, coverage, security posture  | `RELEASE_PROCESS.md`, `COVERAGE_POLICY.md`          | Must declare scope          |
| Architecture Maps   | High-level diagrams & maps           | `aetherra_os_architecture_map_v_1.md`               | Optional                    |
| Roadmaps            | Evolutionary plans; time-sequenced   | `BETA_ROADMAP_0.5.0.md`                             | Mark date/version           |
| Reports             | Generated or curated audits          | `GO_NO_GO_GATES.md`                                 | Dated filename              |
| Research & Vision   | Narrative / exploratory              | `manifesto.md`, `CONSCIOUSNESS_UNIFIED_IDENTITY.md` | Mark non‑normative          |
| Historical / Legacy | Superseded or archived               | `docs-organized/legacy/`                            | Excluded from strict checks |

## Required Set (Baseline Completeness)

The following documents constitute the “minimum viable architecture surface” and are validated by the tooling:

- `INDEX.md`
- `SYSTEM_INDEX.md`
- `Aether_Script_Language_System.md`
- `AETHERRA_MEMORY_SYSTEM.md`
- `RELEASE_PROCESS.md`
- `THREAT_MODEL.md`
- `COVERAGE_POLICY.md`
- `GO_NO_GO_GATES.md`

If any are missing, `tools/verify_docs_architecture.py --strict` will exit non‑zero.

## Status Encoding

| Emoji | Meaning                 | Action                                    |
| ----- | ----------------------- | ----------------------------------------- |
| ✅     | Implemented & validated | Keep updated with code                    |
| 🚧     | Partial / in progress   | Identify missing sections                 |
| 🔮     | Planned / speculative   | Must not over‑claim; isolate future tense |

## File Naming Conventions

- Use UPPER_SNAKE_CASE for formal system specs (`AETHERRA_MEMORY_SYSTEM.md`).
- Use PascalCase or Title Case only for historical artifacts already named (do not rename retroactively unless necessary).
- Use `vX` or date suffixes for versioned diagrams / maps: `aetherra_os_architecture_map_v_1.md`.
- Use ISO dates in reports where appropriate: `PROJECT_STATUS_2025-08-11.md`.

## Link Stability Policy

Stable paths (must not rename without migration):

- `docs/INDEX.md`
- `docs/SYSTEM_INDEX.md`
- `docs/DOCS_ARCHITECTURE.md`
- Any file linked from root `README.md`

If a rename is required:
1. Create a stub file at old path pointing to the new location.
2. Update internal references (search & replace).
3. Run architecture verifier.

## Tooling & Automation

| Tool                                | Purpose                             |
| ----------------------------------- | ----------------------------------- |
| `tools/verify_docs_architecture.py` | Structural validation & report JSON |
| `tools/verify_docs_consistency.py`  | Env var & endpoint parity           |
| `tools/generate_file_index.py`      | Repository file index               |

Extend `verify_docs_architecture.py` before adding bespoke one-off checkers.

## Evolution Roadmap

| Phase | Focus                             | Outcome                         |
| ----- | --------------------------------- | ------------------------------- |
| 1     | Dual layer (current)              | Stability + organization ✅      |
| 2     | Consolidated navigation site      | Unified nav / _toc ✅ (planned)  |
| 3     | Generated architecture diagrams   | Auto‑updated visuals            |
| 4     | API & config reference extraction | Machine-derived spec complement |

## Contribution Workflow (Docs)

1. Add / modify doc
2. Ensure classification fits table above
3. Update `SYSTEM_INDEX.md` if system spec maturity changed
4. Run `python tools/verify_docs_architecture.py --strict` locally
5. Commit with scope `docs:` conventional prefix

## Anti-Patterns (Avoid)

- Duplicating whole sections between system docs
- Mixing speculative roadmap language into implemented spec sections
- Large unstructured dumps without classification
- Orphaned docs not reachable from at least one index

## Future Enhancements

- Introduce front-matter metadata for all specs (machine parsing)
- Tag maturity per section instead of whole-doc status
- Auto-link code symbols via static analysis

---
Maintainers: Documentation & Architecture Stewards (see `OWNERSHIP.md`)

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

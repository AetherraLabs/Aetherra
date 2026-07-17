---
title: Aetherra Documentation Architecture
status: Active
last_updated: 2026-07-17
---

# Aetherra Documentation Architecture

This document defines how project documentation is structured, categorized,
validated, and evolved.

Aetherra uses one active documentation surface:

1. Active system and operational docs in `docs/`.
2. Historical reports and superseded notes in `docs/archive/`.

The goal is to keep the repository's visible documentation surface clear while
retaining audit material only when it has ongoing traceability value.

## Guiding Principles

- Keep single authoritative entry points.
- Keep active docs grounded in current code or clearly marked as planned.
- Consolidate roadmaps into `MASTER_ROADMAP.md`.
- Prefer linking to duplicating.
- Move or remove stale historical material when it no longer supports audits,
  release context, or architecture decisions.
- Verify documentation with `tools/verify_docs_architecture.py`.

## Topology

| Directory | Purpose | Indexed In |
| --- | --- | --- |
| `docs/` | Active specs, policies, operator guides, maps, and retained archive material | `docs/INDEX.md`, `docs/SYSTEM_INDEX.md` |
| `docs/archive/` | Historical reports and superseded material retained for traceability | Referenced only when needed |
| `documentation/` | Transitional compatibility pointer | Root README |

## Core Entry Points

- `docs/README.md` - quick-start navigation
- `docs/INDEX.md` - canonical list of system and operator documents
- `docs/SYSTEM_INDEX.md` - implementation maturity dashboard
- `docs/AETHERRA_MASTER_MAP.md` - repository file/folder inventory
- `docs/MASTER_ROADMAP.md` - consolidated roadmap
- `docs/DOCS_ARCHITECTURE.md` - this governance file

## Document Classes

| Class | Description | Examples | Validation |
| --- | --- | --- | --- |
| System Specs | Define core subsystems and contracts | `AETHERRA_MEMORY_SYSTEM.md` | Listed in `SYSTEM_INDEX.md` |
| Operator Guides | How to run, operate, or verify | `Aether_Script_Operator_Guide.md` | Link to tests, commands, or gates |
| Policies & Process | Release, coverage, security posture | `RELEASE_PROCESS.md`, `COVERAGE_POLICY.md` | Declare scope |
| Architecture Maps | High-level diagrams and maps | `AETHERRA_MASTER_MAP.md` | Regenerated when applicable |
| Roadmaps | Evolutionary plans and build order | `MASTER_ROADMAP.md` | Single source of truth |
| Reports | Generated or curated audits | `GO_NO_GO_GATES.md`, `docs/archive/*` | Dated or clearly scoped |
| Historical / Legacy | Superseded or archived material | `docs/archive/` | Excluded from strict active-doc checks |

## Required Set

The following files form the minimum viable documentation surface and are
validated by `tools/verify_docs_architecture.py --strict`:

- `INDEX.md`
- `SYSTEM_INDEX.md`
- `Aether_Script_Language_System.md`
- `AETHERRA_MEMORY_SYSTEM.md`
- `RELEASE_PROCESS.md`
- `THREAT_MODEL.md`
- `COVERAGE_POLICY.md`
- `GO_NO_GO_GATES.md`

## Naming Rules

- Use `UPPER_SNAKE_CASE` for formal system specs.
- Use ISO dates for dated reports when appropriate.
- Avoid new roadmap files unless they are explicitly temporary and immediately
  consolidated into `MASTER_ROADMAP.md`.
- Do not create new legacy folders outside `docs/archive/`.

## Link Stability

Stable paths must not be renamed without a migration:

- `docs/INDEX.md`
- `docs/SYSTEM_INDEX.md`
- `docs/DOCS_ARCHITECTURE.md`
- `docs/AETHERRA_MASTER_MAP.md`
- Any file linked from root `README.md`

## Validation

Run:

```powershell
python tools/verify_docs_architecture.py --strict
python tools/verify_docs_consistency.py
```

When files are added, removed, or reclassified, regenerate the repository map:

```powershell
python tools/generate_master_map.py
python tools/generate_file_index.py --root . --output docs/FILE_INDEX.md
```

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Aetherra System Index

Last updated: 2025-08-28

This dashboard lists the core system documents, their purpose, and current implementation status across the Aetherra architecture.

Legend: ✅ implemented · 🚧 partial · 🔮 planned

## Foundational Documents

- Aetherra Manifesto — ./../Aetherra/docs/AETHERRA_MANIFESTO.md
- AI OS Manifesto — ./../Aetherra/docs/AI_OS_MANIFESTO.md
- Aetherra Labs Vision — ./../Aetherra/docs/aetherra_labs_vision.md

- Aether Script Language System — ./Aether_Script_Language_System.md
  - Purpose: Grammar, execution rules, policies, and signing/verification for `.aether`.
  - Status: 🚧 Partial

- Aetherra Kernel System — ./AETHERRA_KERNEL_SYSTEM.md
  - Purpose: This document describes the Aetherra Kernel: the core runtime loop, service registry, and launcher phases that bring the AI OS online and keep it healthy. It mirrors the structure of other system docs and is grounded in the current codebase and tasks.
  - Status: ✅ Implemented
  - Dependencies: required by all

- Aetherra Artificial Intelligence System — ./AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md
  - Purpose: This document describes the Aetherra Artificial Intelligence System: the core AI engine, its subsystems, contracts, observability, and extension points. It mirrors the structure of other system docs and is grounded in the current codebase.
  - Status: ✅ Implemented

- Aetherra Agent System — ./AETHERRA_AGENT_SYSTEM.md
  - Purpose: This document describes the Aetherra Agent System: the orchestrator and agent components responsible for coordinating specialized AI agents to execute tasks. It mirrors the structure of other system docs and reflects the current codebase.
  - Status: 🚧 Partial

- Aetherra Memory System — ./AETHERRA_MEMORY_SYSTEM.md
  - Purpose: Core/advanced memory layers, RAG-oriented recall, narratives, QFAC/quantum bridges, health/pulse.
  - Status: 🚧 Partial (Phase 2/4)
  - Dependencies: required by Lyrixa, AI System, Agents
  - Extension: DNA-inspired encoding & Living Memory Genome (see separate spec).

- Aetherra Security System — ./AETHERRA_SECURITY_SYSTEM.md
  - Purpose: This document describes the security measures implemented in Aetherra OS and Lyrixa today, how to configure them, and what’s planned next. It is grounded in the current codebase and tests to avoid over‑claiming.
  - Status: 🔮 Planned
  - Dependencies: hooks into Kernel and Memory

- Aetherra Coding System (Lyrixa Code Studio) — ./AETHERRA_CODING_SYSTEM.md
  - Purpose: AI-native coding orchestration (plan → code → test → secure → sign → ship), Spec → Tests gate, tooling.
  - Status: 🚧 Partial

- Aetherra AI Trainer System — ./AETHERRA_AI_TRAINER_SYSTEM.md
  - Purpose: Provide a reproducible training/evaluation pipeline for models and policies used by Aetherra (LLMs, adapters, classifiers, rerankers)
  - Status: 🔮 Planned

- Aetherra Lyrixa System — ./AETHERRA_LYRIXA_SYSTEM.md
  - Purpose: Define Lyrixa as the conversational and interface layer for Aetherra OS
  - Status: 🚧 Partial

- Aetherra Chat System — ./AETHERRA_CHAT_SYSTEM.md
  - Purpose: This document describes the Aetherra Chat System: a platform-level conversational service that provides message transport, streaming, safety middleware, and observability for multiple clients (Lyrixa UI/CLI, tools, and future apps).
  - Status: 🚧 Partial

---

Quick status: ✅ Implemented: 2 · 🚧 Partial: 6 · 🔮 Planned: 2

How to use

- Start here for system overviews and contracts; each doc links to files, APIs, and env flags.
- For a full repository file index, see ./FILE_INDEX.md.
- To verify behavior locally, use VS Code tasks under Test/Build (e.g., "Verify Aetherra OS (Headless Smoke)" and "Verify Claims").

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

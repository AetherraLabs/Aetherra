# Aetherra System Index

Last updated: 2026-06-20

This dashboard lists the core system documents, their purpose, and current
implementation status across the Aetherra architecture.

Status meanings:

- Functional complete: complete for the current architecture milestone.
- Functional foundation complete: working bounded foundation with documented
  safety limits and focused verification.
- Partial: implemented in part, but still requires refinement before alpha
  readiness.
- Planned: expected, but not yet implemented as an active foundation.

## Foundational Documents

- Aetherra Manifesto - ./../Aetherra/docs/AETHERRA_MANIFESTO.md
- AI OS Manifesto - ./../Aetherra/docs/AI_OS_MANIFESTO.md
- Aetherra Labs Vision - ./../Aetherra/docs/aetherra_labs_vision.md

## System Documents

- Aether Script Language System - ./Aether_Script_Language_System.md
  - Purpose: Grammar, execution rules, policies, and signing/verification for `.aether`.
  - Status: Functional foundation complete
  - Dependencies: Guardian, Security, Coding, Plugins, Runtime

- Aetherra Kernel System - ./AETHERRA_KERNEL_SYSTEM.md
  - Purpose: Core runtime loop, service registry, and launcher phases that bring the AI OS online and keep it healthy.
  - Status: Functional foundation complete
  - Dependencies: required by all systems

- Aetherra Artificial Intelligence System - ./AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md
  - Purpose: Core AI engine, subsystems, contracts, observability, and extension points.
  - Status: Functional foundation complete

- Aetherra Consciousness System - ./AETHERRA_CONSCIOUSNESS_SYSTEM.md
  - Purpose: Always-on awareness loop, qualia, attention, reflection, continuity, and governed autonomous action.
  - Status: Functional foundation complete
  - Dependencies: Guardian, Security, Memory, Homeostasis, Agents

- Aetherra Agent System - ./AETHERRA_AGENT_SYSTEM.md
  - Purpose: Orchestrator and agent components responsible for coordinating specialized AI agents.
  - Status: Functional foundation complete
  - Dependencies: Guardian, Security, Kernel, Hub, Memory

- Aetherra Memory System - ./AETHERRA_MEMORY_SYSTEM.md
  - Purpose: Core/advanced memory layers, RAG-oriented recall, narratives, QFAC/quantum bridges, health, and pulse.
  - Status: Functional foundation complete
  - Dependencies: Lyrixa, AI System, Agents

- Aetherra Security System - ./AETHERRA_SECURITY_SYSTEM.md
  - Purpose: Security controls, configuration, and verified protection surfaces for Aetherra OS and Lyrixa.
  - Status: Functional complete
  - Dependencies: Kernel, Memory, Hub, Plugins, Security policy consumers

- Aetherra Guardian System - ./AETHERRA_GUARDIAN_SYSTEM.md
  - Purpose: Central governance, safety, policy, approval, containment, and audit authority above Security.
  - Status: Functional complete
  - Dependencies: Security, Kernel, Plugins, Agents, Homeostasis, Self-Improvement

- Aetherra Homeostasis System - ./AETHERRA_HOMEOSTASIS_SYSTEM.md
  - Purpose: Stability observation, diagnosis, recommendation, controlled action, and verification.
  - Status: Functional foundation complete
  - Dependencies: Kernel, Memory, AI, Hub, Agents, Guardian, Security

- Aetherra Self-Improvement System - ./AETHERRA_SELF-IMPROVEMENT_SYSTEM.md
  - Purpose: Observation, hypothesis, simulation, and structured improvement proposals.
  - Status: Functional foundation complete
  - Dependencies: Homeostasis, Guardian, Security, Self-Incorporation, Maintenance

- Aetherra Maintenance System - ./AETHERRA_MAINTENANCE_SYSTEM.md
  - Purpose: Coordinates observe, diagnose, propose, review, apply, verify, and learn lifecycle.
  - Status: Functional foundation complete
  - Dependencies: Homeostasis, Self-Improvement, Guardian, Security, Self-Incorporation

- Aetherra Self-Incorporation System - ./AETHERRA_SELF-INCORPORATION_SYSTEM.md
  - Purpose: Controlled execution, staging, rollback, quarantine, and audit for approved system changes.
  - Status: Functional foundation complete
  - Dependencies: Self-Improvement, Guardian, Security, Homeostasis, Maintenance

- Aetherra Integration Validation System - ./AETHERRA_INTEGRATION_VALIDATION.md
  - Purpose: Non-destructive cross-system validation that proves foundation systems cooperate through current safety contracts.
  - Status: Functional foundation complete
  - Dependencies: Guardian, Security, Homeostasis, Maintenance, Self-Incorporation, Aether Script

- Aetherra Runtime UI System - ./AETHERRA_RUNTIME_UI_SYSTEM.md
  - Purpose: Cognitive Observatory and read-only operator state contract for rendering Aetherra as a living system.
  - Status: Functional foundation complete
  - Dependencies: Guardian, Security, Homeostasis, Maintenance, Aether Script, Integration Validation, Hub

- Aetherra Hub System - ./AETHERRA_HUB_API_REFERENCE.md
  - Purpose: HTTP, SSE, WebSocket, metrics, OpenAPI, health, and readiness integration boundary for Aetherra runtime systems and clients.
  - Status: Functional foundation complete
  - Dependencies: Guardian, Security, Kernel, Runtime UI, Maintenance

- Aetherra Coding System - ./AETHERRA_CODING_SYSTEM.md
  - Purpose: AI-native coding orchestration, testing, verification, security, signing, and governed change proposal.
  - Status: Functional foundation complete
  - Dependencies: Guardian, Security, Aether Script, Self-Incorporation, Homeostasis, Maintenance

- Aetherra Lyrixa System - ./AETHERRA_LYRIXA_SYSTEM.md
  - Purpose: Conversational and interface layer for Aetherra OS.
  - Status: Functional foundation complete

- Aetherra Chat System - ./AETHERRA_CHAT_SYSTEM.md
  - Purpose: Platform-level conversational service for message transport, streaming, safety middleware, and observability.
  - Status: Functional foundation complete

- Aetherra AI Trainer System - ./AETHERRA_AI_TRAINER_SYSTEM.md
  - Purpose: Reproducible training/evaluation pipeline for models and policies used by Aetherra.
  - Status: Planned

## Quick Status

- Functional complete: 2
- Functional foundation complete: 16
- Partial: 0
- Planned: 1

## How To Use

- Start here for system overviews and contracts.
- Use `docs/ACTIVE_SYSTEMS.md` for the current operational dashboard.
- Use `docs/BUILD_ORDER.md` for the active build sequence.
- Use `docs/UNDERSTANDING_RULE.md` before marking any system complete.
- For a full repository file index, see `docs/FILE_INDEX.md`.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

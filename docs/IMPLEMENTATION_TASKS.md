# Phase 1.2 Implementation Tasks

This task board translates Phase 2-5 roadmap work into atomic,
dependency-aware execution items grounded in current Week 1.1 findings:
`docs/STUB_INVENTORY.json` and `docs/architecture/DEPENDENCY_GRAPH.md`.

## Baseline

- Active stub count (source scope): `410`
- Primary hotspots: engine core, orchestration bridge, reflector-related paths, meta-cognition
- Priority objective: remove critical-path stub blockers before broad optimization work

## Phase 2a: Reflector Implementation

### 2a.1 Reflector Core (`Aetherra/aetherra_core/kernel/reflector.py`)

- [ ] T2A-R1 Define `ReflectionInsight` schema and typed fields.
- [ ] T2A-R2 Implement constructor config and state initialization.
- [ ] T2A-R3 Add file ingestion and safe parse boundary.
- [ ] T2A-R4 Implement class extraction with inheritance metadata.
- [ ] T2A-R5 Implement function extraction with async support.
- [ ] T2A-R6 Implement decorator extraction.
- [ ] T2A-R7 Implement import graph extraction per file.
- [ ] T2A-R8 Implement return/type annotation extraction.
- [ ] T2A-R9 Implement contradiction analysis over fragments.
- [ ] T2A-R10 Implement blind-spot detection heuristic.
- [ ] T2A-R11 Add actionable recommendation synthesis.
- [ ] T2A-R12 Add unit tests for nested classes and async functions.
- [ ] T2A-R13 Add unit tests for decorator and typing edge cases.
- [ ] T2A-R14 Add benchmark test (<100ms target, representative files).

### 2a.2 Plugin Reflector (`Aetherra/plugins/reflector.py`)

- [ ] T2A-P1 Define plugin feature analysis result model.
- [ ] T2A-P2 Add feature complexity scoring routine.
- [ ] T2A-P3 Add API stability signal calculation.
- [ ] T2A-P4 Add risk scoring for plugin features.
- [ ] T2A-P5 Add plugin-focused reflection test fixtures.
- [ ] T2A-P6 Add regression tests for reflector behavior outputs.

### 2a.3 Orchestration Bridge De-stubbing (`Aetherra/aetherra_core/orchestration/orchestration_bridge.py`)

- [ ] T2A-O1 Define task lifecycle states and transitions.
- [ ] T2A-O2 Implement dependency-aware task readiness checks.
- [ ] T2A-O3 Implement structured failure handling and retry policy.
- [ ] T2A-O4 Add deterministic queue ordering strategy.
- [ ] T2A-O5 Add orchestrator integration tests with multi-agent tasks.
- [ ] T2A-O6 Add timeout and cancellation tests.

## Phase 2b: Impact Analysis and Code Generation

- [ ] T2B-1 Create dependency graph builder module contract.
- [ ] T2B-2 Implement direct and transitive dependent traversal.
- [ ] T2B-3 Add circular dependency detector.
- [ ] T2B-4 Implement impact score factor model.
- [ ] T2B-5 Add risk profile serializer for gate consumption.
- [ ] T2B-6 Integrate impact analysis into code orchestration path.
- [ ] T2B-7 Add syntax/import/style/type verification chain.
- [ ] T2B-8 Implement dry-run patch simulation.
- [ ] T2B-9 Implement rollback plan and failure recovery.
- [ ] T2B-10 Add integration tests for end-to-end generation pipeline.

## Phase 3: Consciousness and Autonomy

- [ ] T3-1 Define decision object schema and confidence model.
- [ ] T3-2 Implement candidate action generation flow.
- [ ] T3-3 Implement confidence scoring and rationale capture.
- [ ] T3-4 Implement autonomy governor hard limits.
- [ ] T3-5 Implement approval-required path for high-risk actions.
- [ ] T3-6 Implement full audit event emission for decisions.
- [ ] T3-7 Add capability tests for blocked forbidden operations.
- [ ] T3-8 Add capability tests for valid autonomous actions.

## Phase 4: Memory and Learning

- [ ] T4-1 Implement semantic recall adapter contract.
- [ ] T4-2 Implement memory consolidation pass.
- [ ] T4-3 Implement episodic outcome recording.
- [ ] T4-4 Implement outcome-to-strategy learning loop.
- [ ] T4-5 Add drift/coherence metrics emission.
- [ ] T4-6 Add tests for consolidation and episodic retrieval.

## Phase 5: Validation and Release

- [ ] T5-1 Add end-to-end scenario tests for reflector to apply flow.
- [ ] T5-2 Add load tests for code generation and memory recall.
- [ ] T5-3 Run security scans and remediate high/critical findings.
- [ ] T5-4 Enforce strict signing and policy gates in release profile.
- [ ] T5-5 Validate coverage no-drop and gate sign-off artifacts.
- [ ] T5-6 Build release bundle and run smoke checks.

## Dependency Links

- `T2A-R4..T2A-R11` block `T2B-6` and `T2B-10`.
- `T2A-O1..T2A-O4` block `T3-4` and orchestration safety validation.
- `T2B-4..T2B-9` block `T3-5` risk-aware autonomy path.
- `T4-3..T4-4` depend on `T3-6` audit events.
- `T5-*` depends on all previous phases reaching minimum pass gates.

## Week 2 Exit Criteria

- Reflector and orchestration critical plans testable with concrete task ownership.
- Impact-analysis and verification pipeline tasks sequenced and dependency-mapped.
- Autonomy and memory tasks aligned to governance ADR decisions.
- At least first 12 Phase 2a tasks ready for active implementation.

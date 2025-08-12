# Engine Curation Proposal (Dry-Run Plan)

Purpose

- Consolidate engines, remove true duplicates, and place modules in the correct OS/Lyrixa/Consciousness areas without breaking runtime.
- No code moves were performed yet; this document is the reviewable plan.

Guardrails

- OS stays fully operational; GUI remains only in `Aetherra/lyrixa/launcher.py` and OS launcher.
- Consciousness engines are shared OS/UI and must not be removed.
- Lyrixa-specific components will not be used by OS.

Key Corrections vs Inspector

- Keep `Aetherra/aetherra_core/engine/aetherra_engine.py` (OS references: `aetherra_os_launcher.py`, `aetherra_os_web/server.py`). Action: KEEP.
- Treat `Aetherra/aetherra_core/engine/lyrixa_engine.py` as Lyrixa-only. Action: KEEP (Lyrixa), DEPRECATED for OS.

Proposed Actions by Area

OS Core – Keep

- Aetherra/aetherra_core/memory/aetherra_memory_engine.py (AetherraMemoryEngine)
- Aetherra/consciousness/quantum/quantum_consciousness_engine.py (QuantumConsciousnessEngine)
- beyond_transcendence_engine.py (BeyondTranscendenceEngine)
- cosmic_consciousness_engine.py (CosmicConsciousnessEngine) – Move to `Aetherra/consciousness/` for consistency
- Aetherra/aetherra_core/engine/aetherra_engine.py (AetherraEngine family)

Lyrixa – Keep or Deprecate in Place (no OS usage)

- Aetherra/aetherra_core/memory/memory_kernel.py – LyrixaMemoryEngine: KEEP (Lyrixa-only)
- Aetherra/aetherra_core/memory/fractal_replay_engine.py – KEEP-MOVE to Lyrixa
- Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/quantum_memory_engine.py – KEEP (canonical quantum memory engine)
- Aetherra/lyrixa/memory/lyrixa_memory_engine.py – DEPRECATE (duplicate of memory_kernel)
- Aetherra/lyrixa/memory/simple_memory_adapter.py – DEPRECATE (duplicate of memory_kernel)
- Aetherra/lyrixa/memory/quantum_memory_integration.py – DEPRECATE (duplicate of canonical quantum engine)

Duplicates/Legacy – Deprecate (Quarantine to `Aetherra/legacy/` after approval)

- Aetherra/aetherra_core/memory/quantum_memory_integration.py – duplicate of canonical quantum engine
- Aetherra/aetherra_core/memory/optimized_memory_engine.py – no runtime refs
- Aetherra/aetherra_core/memory/concept_clustering.py – no runtime refs
- Aetherra/aetherra_core/memory/fractal_mesh/timelines/reflective_timeline_engine.py – no runtime refs
- Aetherra/aetherra_core/engine/lyrixa_engine_mock.py – mock only
- Aetherra/aetherra_core/engine/prompt_engine.py – no runtime refs
- Aetherra/core/prompt_engine.py – duplicate of above
- Aetherra/aetherra_core/cognitive/reasoning_engine.py – duplicate of engine classes

Consciousness – Keep (Shared OS/UI) unless stated otherwise

- Aetherra/consciousness/quantum/consciousness_singularity_engine.py – keep (tests/docs)
- Aetherra/consciousness/quantum/multidimensional_state_engine.py – keep (tests/docs)
- Aetherra/consciousness/quantum/reality_synthesis_engine.py – keep (tests/docs)
- Aetherra/consciousness/quantum/temporal_consciousness_system.py – keep (tests/docs)
- Aetherra/consciousness/quantum/transcendence_consolidation_engine.py – keep (tests/docs)
- Aetherra/consciousness/quantum/quantum_decision_engine.py – DEPRECATE (no refs)
- Aetherra/consciousness/quantum/quantum_interference_patterns.py – DEPRECATE (no refs)
- Aetherra/consciousness/quantum/quantum_tunneling_logic.py – DEPRECATE (no refs)

Moves (Dry-Run; no changes yet)

- Move `cosmic_consciousness_engine.py` -> `Aetherra/consciousness/` (import path compat via relative shim if needed)
- Move Lyrixa data-flow engines under `Aetherra/lyrixa/` or mark them Lyrixa-only in current location:
  - `Aetherra/aetherra_core/memory/fractal_replay_engine.py`
  - `Aetherra/aetherra_core/memory/memory_kernel.py`

Optional Cleanup (Post-Approval)

- Add deprecation banners to files listed under Deprecate (without changing imports).
- Create shims for any moved modules to avoid breaking existing imports during a grace period.
- Re-run: engine inspector, usage matrix, and OS smoke boot.

Validation Plan

1) Apply moves/deprecations in a small, reviewable batch.
2) Run backend smoke boot (quiet) and UI checks:
   - Verify Aetherra UI task
   - Verify UI Standards task
3) Generate updated ENGINE_USAGE_MATRIX.md and ENGINE_INSPECTION_REPORT.md.

Notes

- Inspector suggested deprecating `aetherra_engine.py`, but OS actively imports it. Keeping for now.
- Consciousness engines are shared; treat as core.

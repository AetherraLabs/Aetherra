# Aetherra Quantum Layer: Overview

Roadmap Status: Active — see `docs/roadmap/aetherra_quantum_roadmap_v_1.md` (v1.0)

This document tracks the initial Quantum bridge, QRNG, and configuration.

- Components
  - QuantumBridge (simulator-first; provider pluggable later)
  - QRNG service (deterministic in test/simulator profile)

- Endpoints (Hub)
  - GET /api/quantum/status (alias: /quantum/status)
  - POST /api/quantum/run (alias: /quantum/run)

- Prometheus metrics
  - aetherra_quantum_mode{provider="..."}
  - aetherra_quantum_jobs_total
  - aetherra_quantum_shots_total
  - aetherra_quantum_queue_current
  - aetherra_quantum_cost_usd
  - aetherra_quantum_error_rate

- Environment variables
  - AETHERRA_QUANTUM_ENABLED (future use; enabling handled per-component)
  - AETHERRA_QUANTUM_MODE=simulator|provider
  - AETHERRA_QUANTUM_PROVIDER
  - AETHERRA_QUANTUM_MAX_SHOTS
  - AETHERRA_QUANTUM_BUDGET_USD
  - AETHERRA_QUANTUM_CACHE_TTL_SEC
  - AETHERRA_QUANTUM_DETERMINISTIC=1 (forces deterministic QRNG)

- Notes
  - Simulator is default; costs are 0 in simulator mode.
  - Deterministic behavior is automatic in test/ci profiles.

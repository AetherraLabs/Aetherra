# Memory subsystem (contributor guide)

This package contains the memory engines, adapters, and quantum-enhanced modules that
power Aetherra's memory system.

The current canonical implementation lives here (with optional quantum/reflector
layers for experimentation). See `QuantumEnhancedMemoryEngine/` for additional
research modules.

## Hashing and determinism policy

To maintain security and reproducibility across engines, we standardized hashing and seeding:

- Stable IDs: Use BLAKE2s with 16-byte digest for compact, strong, and fast IDs.
  - API: `hashlib.blake2s(data, digest_size=16).hexdigest()` produces 32 hex characters
  - Used for: memory IDs, record keys, cross-process stable identifiers

- Deterministic caches and seeds: Use SHA-256 over input data to derive cache keys
  and PRNG seeds.
  - API: `hashlib.sha256(data).hexdigest()` or
    `int.from_bytes(sha256(...).digest()[:8], 'big')` for seeds
  - Used for: content-derived cache keys, deterministic mock embeddings, reproducible scoring

Rationale:

- Security: Avoid weak hashes (MD5/SHA1). BLAKE2s provides strong properties with excellent performance and small output.
- Reproducibility: Deterministic outputs enable reliable tests and predictable behavior across runs/machines.

## Do and don't

Do:

- Use `blake2s(digest_size=16)` for IDs and persisted keys.
- Use `sha256` for cache keys and deterministic seeding of any pseudo-random behavior.
- Clearly document any non-deterministic paths and gate them behind explicit flags.

Avoid:

- Re-introducing `md5` or `sha1` for any purpose.
- Using time-based or OS-random seeds implicitly for core algorithms that must be reproducible.
- Mixing hashing strategies within the same ID space (stick to BLAKE2s-128 for IDs).

## Where this lives (quick map)

- `memory_core.py`: `_generate_memory_id` creates BLAKE2s-128 IDs.
- `compression_metrics.py`: cache keying and deterministic metric computation (SHA-256 for content keys).
- `concept_clustering.py`: deterministic mock embeddings seeded from SHA-256(text).
- `aetherra_memory_engine.py`: adapter/orchestration over the core, preserving determinism on public APIs.

Related research modules live under `quantum/`, `reflector/`, and `fractal_mesh/`.

## Quick verification

- Capabilities and smoke tests should remain green after changes touching hashing or seeding.
- If determinism is required, verify that repeated runs on identical input produce identical IDs, cache lookups, and embeddings.
- The docs consistency check (`tools/verify_docs_consistency.py`) runs in CI and should remain passing.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

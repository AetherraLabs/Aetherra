#!/usr/bin/env python3
"""QRNG service (simulated unless provider integrated).

Provides deterministic output in test/simulator modes.
"""

from __future__ import annotations

import os
import random
import secrets
from typing import Optional


def _deterministic_mode() -> bool:
    if os.environ.get("AETHERRA_QUANTUM_DETERMINISTIC", "0") == "1":
        return True
    prof = os.environ.get("AETHERRA_PROFILE", "").lower().strip()
    if prof in {"test", "ci"}:
        return True
    mode = os.environ.get("AETHERRA_QUANTUM_MODE", "simulator").lower().strip()
    return mode == "simulator"


def _rng(seed: Optional[int] = None) -> random.Random:
    r = random.Random()
    if _deterministic_mode():
        if seed is None:
            # Stable default seed in deterministic mode
            seed = 1337
        r.seed(int(seed))
    else:
        # Use system entropy to perturb the seed
        base = int.from_bytes(secrets.token_bytes(8), "big")
        r.seed(base ^ (int(seed) if seed is not None else 0))
    return r


def qrng_bytes(n: int, seed: Optional[int] = None) -> bytes:
    n = int(max(0, n))
    r = _rng(seed)
    # Build bytes deterministically via PRNG here (provider integration later)
    return bytes([r.randrange(0, 256) for _ in range(n)])


def qrng_int(a: int, b: int, seed: Optional[int] = None) -> int:
    if a > b:
        a, b = b, a
    r = _rng(seed)
    return int(r.randrange(a, b + 1))

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Quantum-inspired hashing utilities (SimHash-style).

Deterministic by default via QRNG seed rules. Useful for dedupe and quick
similarity hints.
"""

from __future__ import annotations

# Standard library imports
import hashlib
import math
from typing import Iterable, Optional

# Local imports
from .qrng_service import qrng_int


def _tokenize(text: str) -> Iterable[str]:
    if not text:
        return []
    # Simple, deterministic tokenization
    return [
        t
        for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
        if t
    ]


def _token_weight(token: str) -> float:
    # Deterministic weight per token (bounded)
    h = hashlib.sha256(token.encode("utf-8")).digest()
    # Map first 4 bytes to [0.5, 1.5)
    v = int.from_bytes(h[:4], "big") / (1 << 32)
    return 0.5 + v


def simhash_text(text: str, bits: int = 64, seed: Optional[int] = None) -> int:
    tokens = list(_tokenize(text))
    if not tokens:
        return 0
    # Build vector of length `bits`
    acc = [0.0] * bits
    # Global sign jitter from seed for extra stability across runs
    jitter = 1 if ((qrng_int(0, 1, seed=seed) % 2) == 0) else -1
    for tok in tokens:
        w = _token_weight(tok)
        # Deterministic per-token bit pattern using sha256
        h = hashlib.sha256(tok.encode("utf-8")).digest()
        # Expand into as many bits as needed by repeating digest
        idx = 0
        needed = bits
        buf = bytearray()
        while needed > 0:
            buf.extend(h)
            needed -= len(h) * 8
        # Accumulate signed weights
        for b in buf:
            for i in range(8):
                if idx >= bits:
                    break
                bit = (b >> i) & 1
                acc[idx] += (w if bit else -w) * jitter
                idx += 1
            if idx >= bits:
                break
    # Produce final hash
    out = 0
    for i, v in enumerate(acc):
        if v >= 0:
            out |= 1 << i
    return out


def hamming_distance(a: int, b: int) -> int:
    return int((a ^ b).bit_count())


def to_hex(x: int, bits: int = 64) -> str:
    width = math.ceil(bits / 4)
    return f"0x{x:0{width}x}"

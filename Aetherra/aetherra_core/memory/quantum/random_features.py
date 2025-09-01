#!/usr/bin/env python3
"""Random feature maps (simulator-first).

Provides a deterministic Gaussian random projection for simple RFF-like maps.
"""

from __future__ import annotations

import math
import random
from typing import Iterable, List, Optional, Sequence, Tuple

from .qrng_service import qrng_int


class RandomFeatureMap:
    def __init__(
        self, in_dim: int, out_dim: int = 128, seed: Optional[int] = None
    ) -> None:
        self.in_dim = int(in_dim)
        self.out_dim = int(out_dim)
        s = int(seed) if seed is not None else qrng_int(0, 2**31 - 1, seed=None)
        self._rng = random.Random(s)
        # Simple Gaussian matrix ~ N(0, 1/in_dim)
        scale = 1.0 / math.sqrt(max(1, self.in_dim))
        self.W: List[List[float]] = [
            [self._rng.gauss(0.0, 1.0) * scale for _ in range(self.in_dim)]
            for _ in range(self.out_dim)
        ]
        self.b: List[float] = [
            self._rng.uniform(0.0, 2 * math.pi) for _ in range(self.out_dim)
        ]

    def transform(self, vec: Sequence[float]) -> List[float]:
        x = list(vec)
        if len(x) != self.in_dim:
            raise ValueError(f"expected vec dim {self.in_dim}, got {len(x)}")
        out = []
        for i in range(self.out_dim):
            dot = 0.0
            Wi = self.W[i]
            for j, v in enumerate(x):
                dot += Wi[j] * float(v)
            # Cosine features
            out.append(math.cos(dot + self.b[i]))
        return out


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    num = 0.0
    da = 0.0
    db = 0.0
    for x, y in zip(a, b):
        fx = float(x)
        fy = float(y)
        num += fx * fy
        da += fx * fx
        db += fy * fy
    if da <= 0.0 or db <= 0.0:
        return 0.0
    return num / math.sqrt(da * db)

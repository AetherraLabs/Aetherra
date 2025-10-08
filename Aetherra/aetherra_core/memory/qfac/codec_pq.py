# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np


def simple_opq_fit(X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Very small OPQ-like: center and compute PCA rotation via SVD.
    Returns mean vector and rotation matrix.
    """
    mean = X.mean(axis=0, keepdims=True)
    Xc = X - mean
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    R = Vt
    return mean.squeeze(0), R


def simple_opq_apply(x: np.ndarray, mean: np.ndarray, R: np.ndarray) -> np.ndarray:
    return (x - mean) @ R.T


def pq_encode(vec: Sequence[float], codebooks: List[np.ndarray]) -> List[int]:
    """Encode by choosing nearest centroid in each subspace (toy)."""
    x = np.asarray(vec, dtype=np.float32)
    m = len(codebooks)
    codes: List[int] = []
    splits = np.array_split(x, m)
    for sub, C in zip(splits, codebooks, strict=True):
        d = ((C - sub) ** 2).sum(axis=1)
        codes.append(int(d.argmin()))
    return codes


def pq_decode(codes: Sequence[int], codebooks: List[np.ndarray]) -> np.ndarray:
    parts = []
    for c, C in zip(codes, codebooks, strict=True):
        parts.append(C[int(c)])
    return np.concatenate(parts, axis=0)

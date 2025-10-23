# SPDX-License-Identifier: GPL-3.0-or-later
"""TT/MPS-style compression shim for cost matrices.

PR-5 introduces an optional low-rank approximation step before OT. We expose a
tiny API that mimics a TT/MPS compressor while using a robust SVD-based
implementation underneath for portability and deterministic behavior.

The compressor is intentionally lightweight and dependency-free; it can be
swapped for a real TT/MPS backend in future work without changing callers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class TTApproxMeta:
    applied: bool
    rank_used: int
    shape: Tuple[int, int]
    method: str = "svd"
    err_fro: float | None = None


def approximate_cost_matrix(cost: np.ndarray, rank_cap: int) -> tuple[np.ndarray, TTApproxMeta]:
    """Return a low-rank approximation of the 2D cost matrix and metadata.

    Policy:
    - If rank_cap <= 0, or min(m, n) <= 1, return original with applied=False.
    - Uses thin SVD, keeps k=min(rank_cap, min(m, n)).
    - Ensures non-negativity by clamping tiny negative numerical noise to 0.
    - Computes optional Frobenius error for introspection (not used in tests).
    """
    cost = np.asarray(cost, dtype=float)
    m, n = cost.shape
    # Apply when rank_cap > 0 and matrix has at least one non-trivial dimension
    # Skip only for true scalars (1x1)
    if rank_cap <= 0 or (m == 1 and n == 1):
        return cost, TTApproxMeta(applied=False, rank_used=0, shape=(m, n), method="svd")

    k = int(max(1, min(rank_cap, min(m, n))))
    try:
        # Thin SVD
        U, S, Vt = np.linalg.svd(cost, full_matrices=False)
        U_k = U[:, :k]
        S_k = S[:k]
        Vt_k = Vt[:k, :]
        approx = (U_k * S_k) @ Vt_k
        # Clamp small negative values from numerical error
        approx = np.maximum(approx, 0.0)
        # Optional error metric
        err = float(np.linalg.norm(cost - approx, ord="fro"))
        meta = TTApproxMeta(applied=True, rank_used=k, shape=(m, n), method="svd", err_fro=err)
        return approx.astype(cost.dtype, copy=False), meta
    except Exception:
        # Fallback: no approximation
        return cost, TTApproxMeta(applied=False, rank_used=0, shape=(m, n), method="svd")

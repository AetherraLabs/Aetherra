# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Iterable

import numpy as np


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a).astype(float)
    b = np.asarray(b).astype(float)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def compute_sheaf_inconsistency(embeddings: Iterable[np.ndarray]) -> float:
    """Compute a simple sheaf inconsistency proxy from embeddings.

    Definition (PR-4 proxy): 1 - mean cosine similarity over all unique pairs.
    - For <=1 embedding, inconsistency = 0.0
    - Clamped to [0, +inf) (though typical range will be [0, 2])
    """
    embs = [np.asarray(e) for e in embeddings]
    n = len(embs)
    if n <= 1:
        return 0.0
    sims = []
    for i in range(n):
        for j in range(i + 1, n):
            sims.append(_cosine_similarity(embs[i], embs[j]))
    mean_sim = float(np.mean(sims)) if sims else 1.0
    inconsistency = max(0.0, 1.0 - mean_sim)
    return inconsistency


def _mst_total_length(dist_mat: np.ndarray) -> float:
    """Prim's algorithm for MST total length on a complete graph given a distance matrix.

    dist_mat is NxN with zeros on diagonal.
    """
    n = dist_mat.shape[0]
    if n <= 1:
        return 0.0
    visited = np.zeros(n, dtype=bool)
    visited[0] = True
    total = 0.0
    # For simplicity, maintain minimal edge to tree per node
    min_edge = dist_mat[0].copy()
    for _ in range(n - 1):
        # pick the smallest edge to an unvisited node
        min_edge[visited] = np.inf
        j = int(np.argmin(min_edge))
        w = float(min_edge[j])
        if not np.isfinite(w):
            break
        total += w
        visited[j] = True
        # update frontier
        min_edge = np.minimum(min_edge, dist_mat[j])
    return total


def compute_persistence_bonus(embeddings: Iterable[np.ndarray]) -> float:
    """Compute a simple persistence-based bonus in [0,1].

    Proxy: build pairwise Euclidean distance matrix, compute MST total length L.
    Normalize: L_norm = L / (n - 1) / (eps + mean(distances)) to keep scale-invariant.
    Map to [0,1]: bonus = 1 / (1 + L_norm). Tighter clusters -> smaller L -> higher bonus.
    """
    embs = [np.asarray(e).astype(float) for e in embeddings]
    n = len(embs)
    if n <= 1:
        return 1.0
    X = np.stack(embs, axis=0)
    # pairwise euclidean distances
    diffs = X[:, None, :] - X[None, :, :]
    dist = np.sqrt(np.sum(diffs * diffs, axis=-1))
    # zero diagonal ensured by computation
    L = _mst_total_length(dist)
    # mean of off-diagonal distances
    mask = ~np.eye(n, dtype=bool)
    mean_d = float(np.mean(dist[mask])) if np.any(mask) else float(np.mean(dist))
    eps = 1e-9
    L_norm = L / max(1.0, (n - 1)) / (eps + mean_d)
    bonus = 1.0 / (1.0 + L_norm)
    # clamp to [0,1]
    return float(min(1.0, max(0.0, bonus)))

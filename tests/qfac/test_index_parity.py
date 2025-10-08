# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import numpy as np

from Aetherra.aetherra_core.memory.qfac.index_ivf_pq import IVF_PQ_Index


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float((a @ b) / (na * nb))


def test_ivf_pq_index_parity_small_dataset():
    rng = np.random.RandomState(0)
    dim = 16
    n = 50
    x = rng.randn(n, dim).astype(np.float32)
    ids = [f"id{i}" for i in range(n)]
    q = x[0]

    # brute-force cosine top-k
    sims = np.array([_cosine(q, v) for v in x])
    top_brute_idx = np.argsort(-sims)[:10]
    top_brute_ids = [ids[i] for i in top_brute_idx]

    # our index
    index = IVF_PQ_Index(dim=dim, nlist=16, m=4, nbits=8)
    index.add_bulk(zip(ids, x, strict=True))
    top_index = index.search(q, k=10)
    top_index_ids = [i for i, _ in top_index]

    # Expect high overlap; allow approximate differences but at least 6/10
    overlap = len(set(top_brute_ids) & set(top_index_ids))
    assert overlap >= 6

# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any, Iterable, List, Sequence, Tuple

import numpy as np

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover - optional
    faiss = None


class IVF_PQ_Index:
    """IVF-PQ index with optional FAISS acceleration and NumPy fallback.

    - If FAISS is available, uses IndexIVFPQ for scalable ANN.
    - Otherwise, falls back to cosine-similarity over an in-memory matrix.
    """

    def __init__(self, dim: int, nlist: int = 64, m: int = 8, nbits: int = 8):
        self.dim = dim
        self.ids: List[str] = []
        self._vecs: List[np.ndarray] = []  # fallback store
        self._faiss_enabled: bool = faiss is not None
        self._faiss_index: Any = None
        self._faiss_trained: bool = False
        if self._faiss_enabled:
            try:
                quantizer = faiss.IndexFlatL2(dim)  # type: ignore[attr-defined]
                self._faiss_index = faiss.IndexIVFPQ(  # type: ignore[attr-defined]
                    quantizer, dim, nlist, m, nbits
                )
                # small default probe
                self._faiss_index.nprobe = min(8, nlist)
            except Exception:
                # Fall back if any construction error occurs
                self._faiss_enabled = False
                self._faiss_index = None

    def _as_np(self, v: Sequence[float]) -> np.ndarray:
        a = np.asarray(v, dtype=np.float32)
        if a.shape != (self.dim,):
            raise ValueError(f"vector has dim {a.shape}, expected {(self.dim,)}")
        return a

    def train(self, vectors: Iterable[Sequence[float]]):
        if not self._faiss_enabled or self._faiss_index is None:
            return  # no-op for fallback
        X = np.vstack([self._as_np(v) for v in vectors])
        if X.size == 0:
            return
        try:
            self._faiss_index.train(X)
            self._faiss_trained = True
        except Exception:
            # disable faiss path if training fails
            self._faiss_enabled = False
            self._faiss_index = None
            self._faiss_trained = False

    def add(self, vec: Sequence[float], id_: str):
        x = self._as_np(vec)
        self.ids.append(id_)
        if self._faiss_enabled and self._faiss_index is not None:
            try:
                # Attempt opportunistic train when enough data accumulates
                if (not self._faiss_trained) and (len(self.ids) >= 64):
                    self._faiss_index.train(np.expand_dims(x, 0))
                    self._faiss_trained = True
                self._faiss_index.add(np.expand_dims(x, 0))
                return
            except Exception:
                self._faiss_enabled = False
                self._faiss_index = None
                self._faiss_trained = False
        # fallback store
        self._vecs.append(x)

    def add_bulk(self, vecs: Iterable[Tuple[str, Sequence[float]]]):
        pairs = list(vecs)
        if not pairs:
            return
        if self._faiss_enabled and self._faiss_index is not None:
            try:
                X = np.vstack([self._as_np(v) for _, v in pairs])
                self.ids.extend([i for i, _ in pairs])
                if not self._faiss_trained:
                    self._faiss_index.train(X)
                    self._faiss_trained = True
                self._faiss_index.add(X)
                return
            except Exception:
                self._faiss_enabled = False
                self._faiss_index = None
                self._faiss_trained = False
        # fallback bulk
        for i, v in pairs:
            self.ids.append(i)
            self._vecs.append(self._as_np(v))

    def search(self, query: Sequence[float], k: int = 20) -> List[Tuple[str, float]]:
        q = self._as_np(query)
        k = min(k, len(self.ids))
        if k <= 0:
            return []
        if self._faiss_enabled and self._faiss_index is not None and self._faiss_trained:
            try:
                distances, indices = self._faiss_index.search(np.expand_dims(q, 0), k)
                out: List[Tuple[str, float]] = []
                for d, idx in zip(distances[0], indices[0], strict=True):
                    if idx == -1:
                        continue
                    sim = 1.0 / (1.0 + float(d))
                    out.append((self.ids[idx], sim))
                return out
            except Exception:
                # fallback on error
                pass
        # cosine similarity fallback
        if not self._vecs:
            return []
        Q = q / (np.linalg.norm(q) + 1e-8)
        M = np.vstack(self._vecs)
        M_norm = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-8)
        sims = M_norm @ Q
        top = np.argsort(-sims)[:k]
        return [(self.ids[i], float(sims[i])) for i in top]

# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import hashlib
from typing import List, Tuple

import numpy as np

from .models import FractalSignature, MemoryRecord


def _hash_motif(arr: np.ndarray) -> str:
    return hashlib.blake2s(arr.tobytes(), digest_size=8).hexdigest()


def compute_fractal_signature(record: MemoryRecord, k_per_scale: int = 4) -> FractalSignature:
    # Build a simple vector signal from embedding or content length
    if record.embedding is not None and len(record.embedding) > 0:
        sig = np.asarray(record.embedding, dtype=np.float32)
    else:
        # fallback: content length + ascii histogram proxy
        text = record.content if isinstance(record.content, str) else str(record.content)
        arr = np.frombuffer(text.encode("utf-8"), dtype=np.uint8)
        hist, _ = np.histogram(arr, bins=32, range=(0, 256))
        sig = hist.astype(np.float32)

    # Multi-scale via simple downsampled DWT-like differences
    scales = []
    coeffs: List[List[Tuple[int, float]]] = []
    motifs: List[str] = []
    cur = sig.copy()
    for s in range(1, 4):  # up to 3 scales
        scales.append(s)
        # simple high-pass difference
        hp = np.abs(cur[1:] - cur[:-1])
        if hp.size == 0:
            coeffs.append([])
            break
        top_idx = np.argsort(-hp)[:k_per_scale]
        coeffs.append([(int(i), float(hp[i])) for i in top_idx])
        motifs.append(_hash_motif(hp[top_idx]))
        # downsample for next scale
        cur = cur[::2] + 1e-6
        if cur.size < 2:
            break

    return FractalSignature(scales=scales, coeffs=coeffs, motifs=motifs)

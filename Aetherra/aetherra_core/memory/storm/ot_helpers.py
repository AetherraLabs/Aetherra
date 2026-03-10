import hashlib
from typing import List

import numpy as np


def _generate_mock_embedding(text: str, dim: int = 128) -> np.ndarray:
    """Generate a deterministic mock embedding for a string using SHA-256 seeding."""
    h = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big")
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, dim).astype(np.float32)


def _build_distance_matrix(X: List[np.ndarray], Y: List[np.ndarray]) -> np.ndarray:
    """Compute the pairwise Euclidean distance matrix between two sets of embeddings."""
    X_arr = np.stack(X)
    Y_arr = np.stack(Y)
    dists = np.linalg.norm(X_arr[:, None, :] - Y_arr[None, :, :], axis=-1)
    return dists

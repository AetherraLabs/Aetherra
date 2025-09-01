import math

import pytest

from Aetherra.aetherra_core.memory.quantum.random_features import (
    RandomFeatureMap,
    cosine_similarity,
)


def test_random_feature_map_shapes():
    fm = RandomFeatureMap(in_dim=4, out_dim=16, seed=123)
    x = [1, 0, 0, 0]
    y = [0, 1, 0, 0]
    fx = fm.transform(x)
    fy = fm.transform(y)
    assert len(fx) == 16
    assert len(fy) == 16
    # Cosine similarity bounded [-1, 1]
    s = cosine_similarity(fx, fy)
    assert -1.0 <= s <= 1.0

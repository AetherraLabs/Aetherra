# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import time

import numpy as np

from Aetherra.aetherra_core.memory.qfac import (
    Edge,
    MemoryRecord,
    ObserverState,
    qfac_rewrite_budgeted,
    qfac_search,
    qfac_store,
)
from Aetherra.aetherra_core.memory.qfac.api import _reset_qfac_state_for_tests


def _rand_vec(seed: int, dim: int = 32):
    return list(np.random.RandomState(seed).randn(dim).astype(np.float32))


def test_observer_bias_changes_order():
    _reset_qfac_state_for_tests()
    emb_a = _rand_vec(42)
    emb_b = _rand_vec(43)

    a = MemoryRecord(id="a", timestamp=int(time.time()), content="A", embedding=emb_a)
    b = MemoryRecord(id="b", timestamp=int(time.time()), content="B", embedding=emb_b)
    # Give B a supports edge so an observer who favors 'supports' might rank it higher
    b.causal_links = [Edge(to="a", type="supports", weight=1.0, confidence=1.0)]
    # Give A a causes edge so an observer who disfavors 'supports' might prefer A
    a.causal_links = [Edge(to="b", type="causes", weight=1.0, confidence=1.0)]

    qfac_store(a)
    qfac_store(b)

    # Observer 1 favors 'supports'
    obs1 = ObserverState(agent_id="o1", priors={"supports": 0.8}).materialize()
    view1 = qfac_search(emb_b, obs1, k=2)

    # Observer 2 disfavors 'supports'
    obs2 = ObserverState(agent_id="o2", priors={"supports": -0.8}).materialize()
    view2 = qfac_search(emb_b, obs2, k=2)

    assert [v["id"] for v in view1] != [v["id"] for v in view2]


def test_rewrite_budget_updates_last_rewrite():
    _reset_qfac_state_for_tests()
    emb = _rand_vec(5)
    r = MemoryRecord(id="r", timestamp=int(time.time()), content="R", embedding=emb)
    qfac_store(r)
    # Force old last_rewrite
    r.qfac_meta["last_rewrite"] = time.time() - 7200
    out = qfac_rewrite_budgeted(budget_ms=50)
    assert out["checked"] >= 1
    assert out["rewrites"] >= 1

# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import time

import numpy as np

from Aetherra.aetherra_core.memory.qfac import (
    MemoryRecord,
    ObserverState,
    qfac_search,
    qfac_store,
)


def test_store_and_search_observer_view():
    emb1 = list(np.random.RandomState(0).randn(32).astype(np.float32))
    emb2 = list(np.random.RandomState(1).randn(32).astype(np.float32))

    r1 = MemoryRecord(
        id="rec1",
        timestamp=int(time.time()),
        content="alpha",
        embedding=emb1,
    )
    r2 = MemoryRecord(
        id="rec2",
        timestamp=int(time.time()),
        content="beta",
        embedding=emb2,
    )

    qfac_store(r1)
    qfac_store(r2)

    obs = ObserverState(agent_id="tester", priors={"supports": 0.2}).materialize()
    view = qfac_search(emb1, obs, k=1)
    assert isinstance(view, list)
    assert len(view) == 1
    assert view[0]["id"] in ("rec1", "rec2")

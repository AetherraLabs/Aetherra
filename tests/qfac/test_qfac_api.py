# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from Aetherra.aetherra_core.memory.qfac import (
    qfac_rewrite_budgeted,
    qfac_search,
    qfac_store,
)


def test_qfac_store_and_search_text():
    rec1 = qfac_store("hello world")
    rec2 = qfac_store("auto models now supported")
    assert rec1.id != rec2.id

    results = qfac_search("hello", top_k=3)
    ids = [r.id for r, _ in results]
    assert rec1.id in ids


def test_qfac_vector_search_and_rewrite_stub():
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    r1 = qfac_store("vec1", embedding=v1)
    r2 = qfac_store("vec2", embedding=v2)

    res_v1 = qfac_search(v1, top_k=2)
    assert res_v1[0][0].id in {r1.id, r2.id}

    rewrites = qfac_rewrite_budgeted(budget_tokens=10)
    assert rewrites == 0

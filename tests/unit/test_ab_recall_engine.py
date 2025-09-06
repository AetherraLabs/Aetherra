# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import os

import pytest

from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine


@pytest.mark.asyncio
async def test_ab_forced_bucket_and_metrics(monkeypatch):
    # Force classical, then quantum; verify bucket in response and metrics tallies
    monkeypatch.setenv("AETHERRA_AB_RECALL_MODE", "abp")

    eng = AetherraEngine()
    await eng.initialize()
    await eng.start_conversation("abtest")

    # Force classical bucket
    monkeypatch.setenv("AETHERRA_AB_FORCE_BUCKET", "classical")
    r1 = await eng.process_message("hello world")
    assert r1.get("ab_bucket") == "classical"
    m = eng.get_session_metrics()
    assert int(m.get("ab_recall_total", 0)) == 1
    assert int(m.get("ab_recall_classical_total", 0)) == 1
    assert int(m.get("ab_recall_quantum_total", 0)) == 0
    assert int(m.get("ab_recall_latency_ms_count_classical", 0)) == 1

    # Force quantum bucket (may fall back internally, but bucket selection should be recorded)
    monkeypatch.setenv("AETHERRA_AB_FORCE_BUCKET", "quantum")
    r2 = await eng.process_message("how are you?")
    assert r2.get("ab_bucket") == "quantum"
    m = eng.get_session_metrics()
    assert int(m.get("ab_recall_total", 0)) == 2
    assert int(m.get("ab_recall_classical_total", 0)) == 1
    assert int(m.get("ab_recall_quantum_total", 0)) == 1
    # One latency recorded for each bucket
    assert int(m.get("ab_recall_latency_ms_count_classical", 0)) == 1
    assert int(m.get("ab_recall_latency_ms_count_quantum", 0)) == 1


def test_ab_percentage_extremes_det(monkeypatch):
    # In ABP mode, pct=0 => always classical; pct=100 => always quantum
    monkeypatch.setenv("AETHERRA_AB_RECALL_MODE", "abp")
    if "AETHERRA_AB_FORCE_BUCKET" in os.environ:
        monkeypatch.delenv("AETHERRA_AB_FORCE_BUCKET", raising=False)

    eng = AetherraEngine()
    # Stabilize internals for deterministic _choose_ab_bucket
    eng.session_id = "sess"
    eng._msg_counter = 0

    monkeypatch.setenv("AETHERRA_AB_RECALL_SEED", "7")

    # pct=0 -> classical
    monkeypatch.setenv("AETHERRA_AB_RECALL_PCT", "0")
    choices = [eng._choose_ab_bucket() for _ in range(5)]
    assert set(choices) == {"classical"}

    # Reset counter and try pct=100 -> quantum
    eng._msg_counter = 0
    monkeypatch.setenv("AETHERRA_AB_RECALL_PCT", "100")
    choices = [eng._choose_ab_bucket() for _ in range(5)]
    assert set(choices) == {"quantum"}

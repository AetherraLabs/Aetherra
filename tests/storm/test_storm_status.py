# SPDX-License-Identifier: GPL-3.0-or-later
"""Test STORM status fields per contract"""
import os

import pytest

from Aetherra.aetherra_core.memory.storm import StormConfig, StormEngine


def test_status_includes_enabled():
    """Status includes enabled field"""
    engine = StormEngine()
    status = engine.status()
    assert "enabled" in status
    assert isinstance(status["enabled"], bool)


def test_status_includes_backends():
    """Status includes backends availability map"""
    engine = StormEngine()
    status = engine.status()
    assert "backends" in status
    assert isinstance(status["backends"], dict)
    assert "pot" in status["backends"]
    assert "keops" in status["backends"]


def test_status_includes_selected_backend():
    """Status includes selected_backend field"""
    engine = StormEngine()
    status = engine.status()
    assert "selected_backend" in status
    assert status["selected_backend"] in ("pot", "keops")


def test_status_includes_exact_ot_active():
    """Status includes exact_ot_active flag"""
    engine = StormEngine()
    status = engine.status()
    assert "exact_ot_active" in status
    assert isinstance(status["exact_ot_active"], bool)


def test_status_includes_tt_rank_cap():
    """Status includes TT rank cap"""
    engine = StormEngine()
    status = engine.status()
    assert "tt_rank_cap" in status
    assert isinstance(status["tt_rank_cap"], int)


def test_status_includes_last_recall():
    """Status includes last_recall metadata"""
    engine = StormEngine()
    status = engine.status()
    assert "last_recall" in status
    assert isinstance(status["last_recall"], dict)


@pytest.mark.asyncio
async def test_last_recall_updates_after_recall():
    """last_recall field updates after recall operation"""
    engine = StormEngine()
    status_before = engine.status()
    assert not status_before["last_recall"]

    await engine.recall("test", limit=5)

    status_after = engine.status()
    assert "approximate" in status_after["last_recall"]
    assert "limit" in status_after["last_recall"]

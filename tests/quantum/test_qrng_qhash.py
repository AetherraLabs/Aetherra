import os

import pytest

from Aetherra.aetherra_core.memory.quantum.qhash import (
    hamming_distance,
    simhash_text,
    to_hex,
)
from Aetherra.aetherra_core.memory.quantum.qrng_service import qrng_bytes, qrng_int


def test_qrng_deterministic_in_test_profile(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    b1 = qrng_bytes(16)
    b2 = qrng_bytes(16)
    assert b1 == b2
    i1 = qrng_int(1, 100)
    i2 = qrng_int(1, 100)
    assert i1 == i2


def test_simhash_basic():
    a = simhash_text("hello world")
    b = simhash_text("hello world")
    c = simhash_text("goodbye world")
    assert a == b
    assert a != c
    # Distance sanity
    d_ab = hamming_distance(a, b)
    d_ac = hamming_distance(a, c)
    assert d_ab == 0
    assert d_ac > 0
    # Hex format
    hx = to_hex(a)
    assert hx.startswith("0x")

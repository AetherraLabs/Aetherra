"""Deterministic Profile Harness Test

Asserts core deterministic guarantees under AETHERRA_PROFILE=test (or CI).

Guarantees:
1. qrng_bytes returns identical output across repeated calls when profile=test.
2. qrng_int with same seed yields stable sequence.
3. Changing seed changes output (sanity).
4. Environment fallback: if AETHERRA_PROFILE missing but AETHERRA_QUANTUM_MODE=simulator,
   deterministic still holds.
"""

from __future__ import annotations

# Standard library imports
import os

# Aetherra imports
from Aetherra.aetherra_core.memory.quantum.qrng_service import qrng_bytes, qrng_int


def _reset_env(profile: str | None, mode: str | None = None):
    if profile is None:
        os.environ.pop("AETHERRA_PROFILE", None)
    else:
        os.environ["AETHERRA_PROFILE"] = profile
    if mode is None:
        os.environ.pop("AETHERRA_QUANTUM_MODE", None)
    else:
        os.environ["AETHERRA_QUANTUM_MODE"] = mode
    # Clear explicit deterministic override to test implicit behavior
    os.environ.pop("AETHERRA_QUANTUM_DETERMINISTIC", None)


def test_qrng_deterministic_under_test_profile():
    _reset_env("test")
    a = qrng_bytes(32)
    b = qrng_bytes(32)
    assert a == b, "qrng_bytes not stable in test profile"
    seq1 = [qrng_int(1, 100, seed=42) for _ in range(5)]
    seq2 = [qrng_int(1, 100, seed=42) for _ in range(5)]
    assert seq1 == seq2, "qrng_int sequence unstable with fixed seed in test profile"


def test_qrng_seed_variation_changes_output():
    _reset_env("test")
    a = qrng_bytes(16, seed=1)
    b = qrng_bytes(16, seed=2)
    assert a != b, "Different seeds produced identical byte sequences"


def test_qrng_simulator_mode_without_profile():
    _reset_env(None, mode="simulator")
    a = qrng_bytes(24)
    b = qrng_bytes(24)
    assert a == b, "Simulator mode didn't enforce deterministic output"

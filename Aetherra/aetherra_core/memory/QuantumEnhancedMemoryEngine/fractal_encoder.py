# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Compatibility shim for legacy quantum memory fractal encoder imports."""

from __future__ import annotations

from Aetherra.aetherra_core.memory.fractal_encoder import (
    fractal_compress,
    fractal_decompress,
)

__all__ = ["fractal_compress", "fractal_decompress"]

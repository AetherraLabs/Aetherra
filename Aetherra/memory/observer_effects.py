# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Compatibility shim for legacy ``memory.observer_effects`` imports."""

from __future__ import annotations

from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine.observer_effects import (
    ObserverEffectEngine,
)

__all__ = ["ObserverEffectEngine"]

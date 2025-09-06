# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
DEPRECATED SHIM MODULE
----------------------
This legacy path now re-exports the canonical QuantumEnhancedMemoryEngine to avoid
duplicate implementations. Prefer importing from:

    Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine.quantum_memory_engine

This shim will be removed in a future cleanup.
"""

from .QuantumEnhancedMemoryEngine.quantum_memory_engine import (
    QuantumEnhancedMemoryEngine,
)

__all__ = ["QuantumEnhancedMemoryEngine"]

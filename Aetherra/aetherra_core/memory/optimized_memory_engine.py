# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
DEPRECATED: OptimizedLyrixaMemoryEngine is now an adapter for QuantumEnhancedMemoryEngine.
All memory operations are delegated to the canonical engine.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Local imports
from .QuantumEnhancedMemoryEngine import QuantumEnhancedMemoryEngine


class OptimizedLyrixaMemoryEngine:
    def __init__(self, *args, **kwargs):
        self.engine = QuantumEnhancedMemoryEngine()

    def store(self, memory_entry: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        return self.engine.store(memory_entry, context)

    def retrieve(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.engine.retrieve(query, context)

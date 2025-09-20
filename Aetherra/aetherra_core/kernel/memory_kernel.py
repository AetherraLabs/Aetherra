# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lightweight compatibility shim for tests expecting a kernel-level memory engine.

Provides LyrixaMemoryEngine with a .fractal_mesh property backed by FractalMeshCore.
This keeps unit tests decoupled from the full AetherraMemoryEngineAdvanced.
"""

from __future__ import annotations

# Standard library imports
from typing import List, Optional

# Aetherra imports
from Aetherra.aetherra_core.memory.fractal_mesh import FractalMeshCore
from Aetherra.aetherra_core.memory.fractal_mesh.base import MemoryFragment


class LyrixaMemoryEngine:
    """
    Minimal engine exposing a FractalMeshCore instance for unit tests.

    - Ensures .fractal_mesh is initialized
    - Provides thin helpers that proxy to FractalMeshCore when present
    """

    def __init__(self, db_path: str = "fractal_memory.db") -> None:
        self.fractal_mesh = FractalMeshCore(db_path)

    # Optional convenience wrappers (not required by tests, but useful)
    def store_fragment(self, fragment: MemoryFragment) -> None:
        self.fractal_mesh.store_fragment(fragment)

    def retrieve_by_concept(
        self, concept: str, limit: int = 10
    ) -> List[MemoryFragment]:
        if hasattr(self.fractal_mesh, "retrieve_by_concept"):
            return self.fractal_mesh.retrieve_by_concept(concept, limit)
        return []

    def mutate_fragment(
        self, fragment: MemoryFragment, **kwargs
    ) -> Optional[MemoryFragment]:
        if hasattr(self.fractal_mesh, "mutate_fragment"):
            return self.fractal_mesh.mutate_fragment(fragment, **kwargs)
        return None

    def simulate_causal_branch(self, branch_id: str):
        if hasattr(self.fractal_mesh, "simulate_causal_branch"):
            return self.fractal_mesh.simulate_causal_branch(branch_id)
        return None

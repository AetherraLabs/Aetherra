# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Multidimensional Memory (7-layer) for Lyrixa Chat
=================================================

Implements a pragmatic 7-layer memory surface that integrates with the
existing persistent memory system. It provides:

- initialize(): connects to persistent memory
- store_multidimensional(payload): fans out writes across layers with tags
- evidence_for(query, limit): retrieves relevant evidence snippets

Layers (conceptual): working, episodic, semantic, procedural, declarative,
quantum, transcendent. Internally, writes route to the persistent memory with
typed metadata and tags so higher layers can build on top without blocking.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List


class MultidimensionalMemory:
    def __init__(self) -> None:
        self._pmem = None
        self._initialized = False
        # Map conceptual layers to memory_type/tags for persistent store
        self._layer_specs = [
            ("working", {"memory_type": "note", "tags": ["layer_working"]}),
            ("episodic", {"memory_type": "experience", "tags": ["layer_episodic"]}),
            ("semantic", {"memory_type": "fact", "tags": ["layer_semantic"]}),
            ("procedural", {"memory_type": "procedure", "tags": ["layer_procedural"]}),
            ("declarative", {"memory_type": "fact", "tags": ["layer_declarative"]}),
            ("quantum", {"memory_type": "quantum", "tags": ["layer_quantum"]}),
            (
                "transcendent",
                {"memory_type": "insight", "tags": ["layer_transcendent"]},
            ),
        ]

    async def initialize(self) -> bool:
        if self._initialized:
            return True
        try:
            # Import lazily to avoid heavy imports at module import time
            from aetherra_persistent_memory import (
                get_persistent_memory_system,  # type: ignore
            )

            self._pmem = await get_persistent_memory_system()
            self._initialized = True
            return True
        except Exception:
            self._pmem = None
            self._initialized = False
            return False

    async def store_multidimensional(self, interaction: Dict[str, Any]) -> None:
        """Store an interaction across the seven conceptual layers.

        interaction: { "text": str, "context": {...} }
        """
        if not self._initialized:
            await self.initialize()
        if not self._pmem:
            return

        text = str(interaction.get("text", "")).strip()
        ctx: Dict[str, Any] = dict(interaction.get("context") or {})

        # Fan-out writes concurrently with small importance variations
        tasks = []
        for i, (layer, spec) in enumerate(self._layer_specs):
            mtype = spec["memory_type"]
            base_tags = list(spec.get("tags", []))
            tags = base_tags + ["lyrixa", "chat", layer]
            importance = 0.5 + (i * 0.05)
            payload = {
                "layer": layer,
                "text": text,
                "context": ctx,
            }
            tasks.append(
                self._pmem.store(  # type: ignore[attr-defined]
                    content=payload,
                    context={"source": "lyrixa_chat", "layer": layer, **ctx},
                    memory_type=mtype,
                    importance=min(1.0, importance),
                    tags=tags,
                )
            )

        # Fire-and-wait to ensure durability; ignore individual failures
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            pass

    async def evidence_for(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Return small memory snippets relevant to the query for UI awareness."""
        if not self._initialized:
            await self.initialize()
        if not self._pmem:
            return []

        try:
            results = await self._pmem.retrieve(query, limit=limit)  # type: ignore[attr-defined]
        except Exception:
            results = []

        evidence: List[Dict[str, Any]] = []
        for r in results[:limit]:
            content = r.get("content", r)
            if isinstance(content, dict) and "text" in content:
                snippet = str(content.get("text", ""))[:280]
            else:
                snippet = str(content)[:280]
            evidence.append(
                {
                    "id": r.get("id"),
                    "memory_type": r.get("memory_type"),
                    "snippet": snippet,
                    "tags": r.get("tags", []),
                }
            )
        return evidence

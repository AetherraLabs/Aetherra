# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Quantum Enhanced Memory Engine
=============================

Quantum-enhanced memory processing for Aetherra OS.

Minimum quantum hardening (coherence/branch/observer):
- coherence_id (engine-level) and branch_id for entries
- observer_ids and observer drift lineage updates on reads
- entanglement graph and simple coherence score
- branch-aware retrieval and branch DAG audit helpers
"""

# Standard library imports
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class QuantumEnhancedMemoryEngine:
    """Quantum-enhanced memory processing engine"""

    def __init__(self):
        self.quantum_state = "coherent"
        # Engine-level coherence domain
        self.coherence_id: str = str(uuid.uuid4())
        # Branch management
        self.current_branch: str = "main"
        self.branch_parents: Dict[str, Optional[str]] = {"main": None}
        # Storage and topology
        self.memory_fragments: List[Dict[str, Any]] = []
        self.entanglement_map: Dict[Any, Set[Any]] = {}
        logger.info("[OK] QuantumEnhancedMemoryEngine initialized")

    def set_coherence_id(self, coherence_id: str) -> None:
        """Override the default coherence_id if needed."""
        self.coherence_id = coherence_id

    def fork_branch(self, new_branch_id: str, parent_branch_id: Optional[str] = None) -> str:
        """Create a new branch with an optional explicit parent (defaults to current)."""
        parent = parent_branch_id or self.current_branch
        if new_branch_id not in self.branch_parents:
            self.branch_parents[new_branch_id] = parent
        self.current_branch = new_branch_id
        return new_branch_id

    def checkout(self, branch_id: str) -> str:
        """Switch active branch (creates it as child of current if missing)."""
        if branch_id not in self.branch_parents:
            self.branch_parents[branch_id] = self.current_branch
        self.current_branch = branch_id
        return branch_id

    def link_entanglement(self, a_id: Any, b_id: Any) -> None:
        """Bidirectionally entangle two fragment ids."""
        self.entanglement_map.setdefault(a_id, set()).add(b_id)
        self.entanglement_map.setdefault(b_id, set()).add(a_id)

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def store(self, memory_entry: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        """Store memory entry with quantum enhancement"""
        try:
            context = context or {}
            branch_id = context.get("branch_id", memory_entry.get("branch_id", self.current_branch))
            # Ensure branch exists (create if needed, parent = current)
            if branch_id not in self.branch_parents:
                self.branch_parents[branch_id] = self.current_branch
            observer_ids: List[str] = list(
                {
                    *(context.get("observer_ids") or []),
                    *(memory_entry.get("observer_ids") or []),
                }
            )
            entry_id = memory_entry.get("id", len(self.memory_fragments))
            enhanced_entry = {
                "id": entry_id,
                "data": memory_entry,
                "quantum_enhanced": True,
                # legacy fields maintained for compatibility
                "coherence_level": 0.94,
                "entanglement_degree": 0.87,
                "timestamp": memory_entry.get("timestamp") or self._now(),
                # hardening metadata
                # Enforce engine coherence domain
                "coherence_id": self.coherence_id,
                "branch_id": branch_id,
                "observer_ids": observer_ids,
                "lineage": {
                    "observer_drift": [
                        {"observer_id": oid, "time": self._now(), "event": "write"}
                        for oid in observer_ids
                    ]
                },
                "entangled_with": sorted(list(self.entanglement_map.get(entry_id, set()))),
            }

            self.memory_fragments.append(enhanced_entry)
            return True

        except Exception as e:
            logger.error(f"[ERROR] Memory storage failed: {e}")
            return False

    def _fragment_matches(
        self, fragment: Dict[str, Any], query: str, branch_id: Optional[str]
    ) -> bool:
        # Branch filter first (if provided)
        if branch_id and fragment.get("branch_id") != branch_id:
            return False
        # Simple text containment over serialized data
        return query.lower() in str(fragment.get("data", "")).lower()

    def retrieve(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve memory with quantum enhancement"""
        try:
            context = context or {}
            branch_id = context.get("branch_id", self.current_branch)
            reader_ids: List[str] = list(context.get("observer_ids") or [])

            # Branch-aware simple retrieval
            for fragment in self.memory_fragments:
                if self._fragment_matches(fragment, query, branch_id):
                    # Update observer drift lineage and observer tag set
                    if reader_ids:
                        seen: Set[str] = set(fragment.get("observer_ids") or [])
                        new = False
                        for oid in reader_ids:
                            if oid not in seen:
                                seen.add(oid)
                                fragment.setdefault("lineage", {}).setdefault(
                                    "observer_drift", []
                                ).append(
                                    {
                                        "observer_id": oid,
                                        "time": self._now(),
                                        "event": "read",
                                    }
                                )
                                new = True
                        if new:
                            fragment["observer_ids"] = sorted(list(seen))
                    return fragment

            # Return empty result if nothing found
            return {
                "found": False,
                "query": query,
                "context": context,
                "quantum_enhanced": True,
            }

        except Exception as e:
            logger.error(f"[ERROR] Memory retrieval failed: {e}")
            return {"error": str(e)}

    def process_memory(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process memory through quantum enhancement"""
        try:
            # Quantum processing simulation
            enhanced_memory = {
                "original": memory_data,
                "quantum_enhanced": True,
                "coherence_level": 0.94,
                "entanglement_degree": 0.87,
            }

            return enhanced_memory

        except Exception as e:
            logger.error(f"[ERROR] Quantum memory processing failed: {e}")
            return memory_data

    # --- Audits and status ---
    def get_coherence_score(self) -> float:
        """Compute a simple coherence score [0..1] based on connectivity and drift.

        Heuristic:
        - Start from 1.0; penalize by observer drift ratio and sparse entanglement.
        - If no fragments: neutral 1.0
        """
        n = len(self.memory_fragments)
        if n == 0:
            return 1.0
        # Entanglement density
        edges = sum(len(v) for v in self.entanglement_map.values()) / 2.0
        max_edges = max(1, n * (n - 1) / 2.0)
        density = min(1.0, edges / max_edges)
        # Observer drift events per fragment
        drifts = 0
        for frag in self.memory_fragments:
            drifts += len(frag.get("lineage", {}).get("observer_drift", []))
        drift_ratio = min(1.0, drifts / max(1, n))
        # Combine: encourage density, discourage excessive drift
        score = 0.7 * density + 0.3 * (1.0 - drift_ratio * 0.1)
        return round(max(0.0, min(1.0, score)), 4)

    def audit_branch_dag(self) -> Dict[str, Any]:
        """Return a simple DAG of branches to parents."""
        edges: List[tuple[Optional[str], str]] = []
        for child, parent in self.branch_parents.items():
            if parent is not None:
                edges.append((parent, child))
        return {
            "branches": sorted(list(self.branch_parents.keys())),
            "root": "main",
            "edges": [{"parent": p, "child": c} for p, c in edges],
        }

    def get_status(self) -> Dict[str, Any]:
        """Get quantum engine status"""
        return {
            "state": self.quantum_state,
            "coherence_id": self.coherence_id,
            "branch": self.current_branch,
            "branches": len(self.branch_parents),
            "fragments": len(self.memory_fragments),
            "entanglement_nodes": len(self.entanglement_map),
            "coherence": self.get_coherence_score(),
        }

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""QuantumBridge (simulator-first)

Abstraction for running quantum recipes with a simulator backend by default,
pluggable provider backends later. Maintains lightweight metrics/state for Hub.
"""

from __future__ import annotations

import hashlib
import os
import random
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class QuantumRecipe:
    circuit: Dict[str, Any] | None
    shots: int = 100
    seed: Optional[int] = None
    noise: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QuantumResult:
    job_id: str
    ok: bool
    shots: int
    seed: int
    result: Dict[str, Any]
    provider: str
    mode: str


class QuantumBridge:
    def __init__(self) -> None:
        self.mode = os.environ.get("AETHERRA_QUANTUM_MODE", "simulator").strip().lower()
        self.provider = (
            os.environ.get("AETHERRA_QUANTUM_PROVIDER", "sim").strip() or "sim"
        )
        self.max_shots = int(
            os.environ.get("AETHERRA_QUANTUM_MAX_SHOTS", "20000") or 20000
        )
        self.cost_budget = float(
            os.environ.get("AETHERRA_QUANTUM_BUDGET_USD", "100") or 100.0
        )
        self.cache_ttl = int(
            os.environ.get("AETHERRA_QUANTUM_CACHE_TTL_SEC", "604800") or 604800
        )
        # metrics/state
        self._lock = threading.Lock()
        self.jobs_total = 0
        self.shots_total = 0
        self.queue_current = 0
        self.last_calibration_at = None  # ISO string
        self.cost_usd_accum = 0.0
        self.error_rate = 0.0  # placeholder

    # --- public API ---
    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "mode": self.mode,
                "provider": self.provider,
                "jobs_total": self.jobs_total,
                "shots_total": self.shots_total,
                "queue_current": self.queue_current,
                "last_calibration": self.last_calibration_at,
                "cost_usd": round(self.cost_usd_accum, 6),
                "error_rate": float(self.error_rate),
                "limits": {
                    "max_shots_per_day": self.max_shots,
                    "budget_usd_per_month": self.cost_budget,
                },
            }

    def run(self, recipe: QuantumRecipe) -> QuantumResult:
        # Enqueue (synthetic)
        with self._lock:
            self.queue_current += 1
        try:
            # Simulator-only behavior for now
            shots = int(max(1, recipe.shots))
            seed = (
                int(recipe.seed)
                if recipe.seed is not None
                else self._seed_from_recipe(recipe)
            )
            rnd = random.Random(seed)
            # Produce a toy result: a few pseudo measurement counts that sum to shots
            outcomes = ["00", "01", "10", "11"]
            weights = [rnd.random() for _ in outcomes]
            s = sum(weights) or 1.0
            probs = [w / s for w in weights]
            counts = {o: 0 for o in outcomes}
            for _ in range(shots):
                # multinomial sample
                r = rnd.random()
                acc = 0.0
                for o, p in zip(outcomes, probs):
                    acc += p
                    if r <= acc:
                        counts[o] += 1
                        break
            job_id = self._job_id(recipe, seed)
            # Update metrics
            with self._lock:
                self.jobs_total += 1
                self.shots_total += shots
                # trivial cost model: $0.000001 per shot in provider mode, 0 in simulator
                if self.mode != "simulator":
                    self.cost_usd_accum += 0.000001 * shots
            return QuantumResult(
                job_id=job_id,
                ok=True,
                shots=shots,
                seed=seed,
                result={"counts": counts, "probs": probs},
                provider=self.provider,
                mode=self.mode,
            )
        finally:
            with self._lock:
                self.queue_current = max(0, self.queue_current - 1)

    # --- helpers ---
    def _job_id(self, recipe: QuantumRecipe, seed: int) -> str:
        h = hashlib.sha256()
        h.update(str(seed).encode("utf-8"))
        h.update(str(recipe.shots).encode("utf-8"))
        if recipe.circuit:
            h.update(repr(sorted(recipe.circuit.items())).encode("utf-8"))
        return h.hexdigest()[:16]

    def _seed_from_recipe(self, recipe: QuantumRecipe) -> int:
        base = int(time.time())
        try:
            h = hashlib.sha256()
            if recipe.circuit:
                h.update(repr(sorted(recipe.circuit.items())).encode("utf-8"))
            if recipe.noise:
                h.update(repr(sorted(recipe.noise.items())).encode("utf-8"))
            h.update(str(recipe.shots).encode("utf-8"))
            return int(h.hexdigest()[:8], 16) ^ base
        except Exception:
            return base


_bridge_singleton: Optional[QuantumBridge] = None


def get_quantum_bridge() -> QuantumBridge:
    global _bridge_singleton
    if _bridge_singleton is None:
        _bridge_singleton = QuantumBridge()
    return _bridge_singleton

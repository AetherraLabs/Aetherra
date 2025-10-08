# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Dict

from .api import qfac_rewrite_budgeted


class FractalGC:
    """Background Fractal GC (self-healing + compaction) stub.

    Provides a run_once method to execute within a time budget. Integration with
    the host scheduler can periodically call this.
    """

    def __init__(self, budget_ms: int = 200):
        self.budget_ms = budget_ms

    def run_once(self, budget_ms: int | None = None) -> Dict[str, int]:
        return qfac_rewrite_budgeted(budget_ms=budget_ms or self.budget_ms)

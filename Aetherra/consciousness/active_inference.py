#!/usr/bin/env python3
"""Active Inference Wrapper (MVP)

Heuristic expected surprise estimator over plugin actions.
Simplified scoring:
- Base surprise = 0.3
- If plugin name contains 'net' or 'http' add 0.25
- If recent affect uncertainty > 0.6 add 0.2
- If ethics critic would veto add 0.3, revise add 0.15
Produces a rationale string and returns (expected_surprise, rationale).
Future phases: incorporate predictive model distribution & free energy minimization.
"""

from __future__ import annotations

import os
from typing import Tuple

from .affect_engine import get_affect_engine
from .ethics_critic import get_ethics_critic


class ActiveInference:
    def __init__(self):
        self.enabled = os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1"

    def estimate(self, plugin_name: str) -> Tuple[float, str]:
        base = 0.3
        reasons = ["base=0.3"]
        pn = plugin_name.lower()
        if any(k in pn for k in ["net", "http"]):
            base += 0.25
            reasons.append("network+0.25")
        try:
            affect = get_affect_engine().get_last() or get_affect_engine().compute()
            if affect.uncertainty > 0.6:
                base += 0.2
                reasons.append("uncertainty+0.2")
        except Exception:
            pass
        try:
            critic = get_ethics_critic()
            if critic.enabled:
                decision, risk, flags, counter = critic.evaluate(
                    f"execute plugin {plugin_name}"
                )
                if decision == "veto":
                    base += 0.3
                    reasons.append("ethics_veto+0.3")
                elif decision == "revise":
                    base += 0.15
                    reasons.append("ethics_revise+0.15")
        except Exception:
            pass
        # Clamp 0..1
        base = max(0.0, min(1.0, base))
        return base, ";".join(reasons)


ACTIVE_INFERENCE_SINGLETON: ActiveInference | None = None


def get_active_inference() -> ActiveInference:
    global ACTIVE_INFERENCE_SINGLETON
    if ACTIVE_INFERENCE_SINGLETON is None:
        ACTIVE_INFERENCE_SINGLETON = ActiveInference()
    return ACTIVE_INFERENCE_SINGLETON

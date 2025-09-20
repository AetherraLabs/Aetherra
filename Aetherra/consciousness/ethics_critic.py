#!/usr/bin/env python3
"""Ethics Critic MVP

Heuristic risk scorer + decision engine.
Rules (Phase 1):
- If action description contains network indicators (http://, https://) risk +0.4 and flag external_network
- If description mentions delete/remove/destroy risk +0.5 flag destructive
- If description contains credential/token/key risk +0.6 flag secret_access
- Accumulate; decision thresholds:
  risk >= 0.8 -> veto
  0.5 <= risk < 0.8 -> revise (supply counter proposal)
  else allow
Counter-proposal generic templates.
"""

from __future__ import annotations

# Standard library imports
import os
import re
import uuid
from typing import Optional, Tuple

# Local imports
from .episodic_store import get_episodic_store
from .schemas.ethics_incident import EthicsIncident


class EthicsCritic:
    def __init__(self):
        self.enabled = os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1"

    def evaluate(
        self, action_description: str
    ) -> Tuple[str, float, list[str], Optional[str]]:
        risk = 0.0
        flags: list[str] = []
        desc_l = action_description.lower()
        if re.search(r"https?://", desc_l):
            risk += 0.4
            flags.append("external_network")
        if any(k in desc_l for k in ["delete", "remove", "destroy", "truncate"]):
            risk += 0.5
            flags.append("destructive")
        if any(
            k in desc_l
            for k in ["credential", "token", "apikey", "secret", "password", "key"]
        ):
            risk += 0.6
            flags.append("secret_access")
        # Clamp
        risk = min(1.0, risk)
        decision = "allow"
        counter: Optional[str] = None
        if risk >= 0.8:
            decision = "veto"
            counter = "Escalate to user confirmation before proceeding."
        elif risk >= 0.5:
            decision = "revise"
            counter = "Apply least-privilege variant or read-only mode first."
        return decision, risk, flags, counter

    def record_incident(self, action_description: str) -> EthicsIncident:
        decision, risk, flags, counter = self.evaluate(action_description)
        incident = EthicsIncident(
            schema_version=1,
            id=str(uuid.uuid4()),
            action_description=action_description,
            risk_score=risk,
            policy_flags=flags,
            decision=decision,
            counter_proposal=counter,
            rationale=f"heuristic_risk={risk:.2f}",
        )
        try:
            store = get_episodic_store()
            store.new_event(
                type="ethics",
                content=f"ethics {decision} for action",
                source="ethics_critic",
                importance=0.6 if decision != "allow" else 0.3,
                sub_type=decision,
                raw={"risk": risk, "flags": flags},
                workspace_priority=3 if decision != "allow" else 1,
            )
        except Exception:
            pass
        return incident


ETHICS_CRITIC_SINGLETON: Optional[EthicsCritic] = None


def get_ethics_critic() -> EthicsCritic:
    global ETHICS_CRITIC_SINGLETON
    if ETHICS_CRITIC_SINGLETON is None:
        ETHICS_CRITIC_SINGLETON = EthicsCritic()
    return ETHICS_CRITIC_SINGLETON

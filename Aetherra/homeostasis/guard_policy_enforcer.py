from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Deque, Dict, Iterable, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency, we fall back to defaults
    yaml = None


@dataclass
class GuardPolicy:
    metric: str
    threshold: int | float
    window_sec: int
    breach_action: str


class GuardPolicyEnforcer:
    """Lightweight in-memory guard policy enforcer.

    Supports:
      - integration_velocity: max N accepted integrations per hour
      - actuator_frequency: max N actions per component per minute
      - rollback_cascade: max N rollbacks per hour

    Notes:
      - Uses in-memory counters/queues; suitable for single-process service instance.
      - Policy file path can be overridden via AETHERRA_GUARD_POLICY_PATH.
      - If YAML is not available or file missing, sensible defaults are used.
    """

    def __init__(self, policy_path: str | Path | None = None) -> None:
        env_policy_path = os.getenv("AETHERRA_GUARD_POLICY_PATH")
        if env_policy_path:
            self.policy_path = Path(env_policy_path)
        else:
            self.policy_path = Path(policy_path) if policy_path else None
        # Deques of timestamps (epoch seconds)
        self._accepted: Deque[float] = deque()
        self._rollbacks: Deque[float] = deque()
        # Per-component action timestamps within short window
        self._component_actions: Dict[str, Deque[float]] = defaultdict(deque)

        # Load or initialize policies
        self.policies: Dict[str, GuardPolicy] = self._load_policies()

    # ---------------- Policy loading -----------------
    def _load_policies(self) -> Dict[str, GuardPolicy]:
        defaults = {
            "integration_velocity": GuardPolicy(
                metric="integrations_per_hour",
                threshold=int(os.getenv("AETHERRA_GUARD_INTEGRATION_PER_HOUR", "5")),
                window_sec=3600,
                breach_action="alert_and_degrade",
            ),
            "actuator_frequency": GuardPolicy(
                metric="actuations_per_component_per_minute",
                threshold=int(os.getenv("AETHERRA_GUARD_ACTUATIONS_PER_COMPONENT_PER_MIN", "1")),
                window_sec=60,
                breach_action="trigger_maintenance",
            ),
            "rollback_cascade": GuardPolicy(
                metric="rollbacks_per_hour",
                threshold=int(os.getenv("AETHERRA_GUARD_ROLLBACKS_PER_HOUR", "3")),
                window_sec=3600,
                breach_action="auto_rollback",
            ),
        }

        if not self.policy_path or not self.policy_path.exists() or yaml is None:
            return defaults

        try:
            data = yaml.safe_load(self.policy_path.read_text(encoding="utf-8")) or {}
            slos = data.get("slos") or {}
            for key, pol in defaults.items():
                cfg = slos.get(key) or {}
                metric = str(cfg.get("metric", pol.metric))
                # Environment override takes precedence even when YAML present
                env_override = None
                if key == "integration_velocity":
                    env_override = os.getenv("AETHERRA_GUARD_INTEGRATION_PER_HOUR")
                elif key == "actuator_frequency":
                    env_override = os.getenv("AETHERRA_GUARD_ACTUATIONS_PER_COMPONENT_PER_MIN")
                elif key == "rollback_cascade":
                    env_override = os.getenv("AETHERRA_GUARD_ROLLBACKS_PER_HOUR")
                threshold = (
                    int(env_override) if env_override else cfg.get("threshold", pol.threshold)
                )
                # window can be specified explicitly, else derive from metric name
                window_sec = cfg.get("window_sec")
                if window_sec is None:
                    window_sec = 60 if "minute" in metric else 3600
                breach_action = str(cfg.get("breach_action", pol.breach_action))
                defaults[key] = GuardPolicy(metric, int(threshold), int(window_sec), breach_action)
            return defaults
        except Exception:
            return defaults

    # ----------------- Evaluation helpers -----------------
    @staticmethod
    def _now() -> float:
        return time.time()

    @staticmethod
    def _cleanup_window(q: Deque[float], window_sec: int, now_ts: float) -> None:
        cutoff = now_ts - window_sec
        while q and q[0] < cutoff:
            q.popleft()

    def _cleanup_components(self, window_sec: int, now_ts: float) -> None:
        cutoff = now_ts - window_sec
        for comp, dq in list(self._component_actions.items()):
            while dq and dq[0] < cutoff:
                dq.popleft()
            if not dq:
                self._component_actions.pop(comp, None)

    # ----------------- Public API -----------------
    def check_proposal(self, proposal: dict[str, Any]) -> Tuple[bool, list[str]]:
        """Check guard policies before executing a proposal.

        Returns (ok, violations)
        """
        now_ts = self._now()
        violations: list[str] = []

        # 1) Integration velocity
        g1 = self.policies.get("integration_velocity")
        if g1:
            self._cleanup_window(self._accepted, g1.window_sec, now_ts)
            if len(self._accepted) >= int(g1.threshold):
                violations.append("integration_velocity")

        # 2) Actuator frequency (if proposal provides a plan/actions)
        g2 = self.policies.get("actuator_frequency")
        if g2:
            actions = []
            params = proposal.get("params") or {}
            if isinstance(params.get("actions"), list):
                actions = params.get("actions") or []
            elif isinstance(params.get("integration_plan"), dict):
                actions = (params.get("integration_plan") or {}).get("actions") or []

            # Each action can optionally denote a target component (string or dict)
            self._cleanup_components(g2.window_sec, now_ts)
            for act in actions:
                comp = None
                if isinstance(act, dict):
                    comp = act.get("component") or act.get("target")
                elif isinstance(act, str):
                    comp = act
                if not comp:
                    continue
                dq = self._component_actions.setdefault(str(comp), deque())
                # If we've already hit the threshold for this component in window
                if len(dq) >= int(g2.threshold):
                    violations.append(f"actuator_frequency:{comp}")

        # 3) Rollback cascade - only applies to explicit "rollback" type proposals
        g3 = self.policies.get("rollback_cascade")
        if g3 and str(proposal.get("type") or "").lower() == "rollback":
            self._cleanup_window(self._rollbacks, g3.window_sec, now_ts)
            if len(self._rollbacks) >= int(g3.threshold):
                violations.append("rollback_cascade")

        return (len(violations) == 0, violations)

    def record_accept(self, proposal: dict[str, Any]) -> None:
        """Record acceptance to update velocity and component/action windows."""
        now_ts = self._now()
        # Integration acceptance
        self._accepted.append(now_ts)
        # Actuator component actions from plan
        params = proposal.get("params") or {}
        actions: Iterable[Any] = []
        if isinstance(params.get("actions"), list):
            actions = params.get("actions") or []
        elif isinstance(params.get("integration_plan"), dict):
            actions = (params.get("integration_plan") or {}).get("actions") or []
        for act in actions:
            comp = None
            if isinstance(act, dict):
                comp = act.get("component") or act.get("target")
            elif isinstance(act, str):
                comp = act
            if not comp:
                continue
            dq = self._component_actions.setdefault(str(comp), deque())
            dq.append(now_ts)

    def record_rollback(self) -> None:
        now_ts = self._now()
        self._rollbacks.append(now_ts)

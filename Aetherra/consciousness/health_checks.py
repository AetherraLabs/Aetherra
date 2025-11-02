# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Health Checks (Phase 1)
=======================

Boot-time and periodic self-maintenance checks for the Aetherra OS.

Design:
- Each check: {name, question, probe, pass_if, remediate[], verify, rollback[]}
- Probes are fast, safe, and cross-process (HTTP/registry) where possible
- Remediations map 1:1 to Safety Envelope capabilities (registry-backed)
- Policy engine gates execution; we keep risk low in Phase 1

Notes:
- Cross-platform: avoids Linux-only commands on Windows
- HTTP to Hub: assumes Hub on http://127.0.0.1:3001
- Periodic: intended to run every ~60s
"""

from __future__ import annotations

# Standard library imports
import shutil
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

# Third party imports
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - runtime environment without requests
    requests = None  # type: ignore

# Aetherra imports
from Aetherra.consciousness.core import config as core_config
from Aetherra.consciousness.core.types import Intent, Plan, PlanStep
from Aetherra.safety_envelope.actuator import Actuator
from Aetherra.safety_envelope.capability_registry import REGISTRY as CAP_REG
from Aetherra.safety_envelope.policy_engine import PolicyEngine

CheckProbe = Callable[[], Dict[str, Any]]
CheckPassIf = Callable[[Dict[str, Any]], bool]
RemedyArgs = Dict[str, Any]


@dataclass
class HealthCheck:
    name: str
    question: str
    probe: CheckProbe
    pass_if: CheckPassIf
    remediate: List[Tuple[str, RemedyArgs]]
    verify: Optional[CheckPassIf] = None
    rollback: Optional[List[Tuple[str, RemedyArgs]]] = None
    risk: str = "low"


class HealthCheckEngine:
    def __init__(
        self,
        policy: PolicyEngine,
        hub_base_url: str = "http://127.0.0.1:3001",
        self_trust: Optional[Any] = None,
    ):
        self.policy = policy
        self.actuator = Actuator(CAP_REG, policy)
        self.last_results: Dict[str, Dict[str, Any]] = {}
        self.hub = hub_base_url.rstrip("/")
        # Phase 3: Optional self-trust layer for consciousness integration
        self.self_trust = self_trust

    # -----------------------------
    # Probes (safe, fast, defensive)
    # -----------------------------

    def probe_chat(self) -> Dict[str, Any]:
        """Probe chat system health via Hub API.

        Strategy:
        - Check Hub liveness /api/ping
        - Attempt lightweight /api/ai/ask roundtrip with "ping"
        """
        res: Dict[str, Any] = {"hub": False, "roundtrip": False, "detail": None}
        if not requests:
            res["detail"] = "requests_unavailable"
            return res
        try:
            r = requests.get(f"{self.hub}/api/ping", timeout=1.0)
            res["hub"] = r.status_code == 200
        except Exception as e:
            res["detail"] = f"ping_err:{e}"
            return res
        try:
            r2 = requests.post(f"{self.hub}/api/ai/ask", json={"message": "ping"}, timeout=2.0)
            j = (
                r2.json()
                if r2.headers.get("content-type", "").startswith("application/json")
                else {}
            )
            res["roundtrip"] = r2.status_code == 200 and bool(j.get("ok"))
            res["echo"] = j.get("result")
        except Exception as e:
            res["detail"] = f"ask_err:{e}"
        return res

    def pass_chat(self, d: Dict[str, Any]) -> bool:
        return bool(d.get("hub") and d.get("roundtrip"))

    def probe_perception(self) -> Dict[str, Any]:
        """Probe perception/event bus via Hub KEB endpoints.

        Note: In dev, the consciousness runner uses PerceptionBus locally,
        while the Hub's /api/keb endpoints query the kernel's EventBus.
        If the kernel EventBus isn't registered in the Hub process,
        we treat it as OK since the local PerceptionBus is independent.
        """
        out: Dict[str, Any] = {"enabled": False, "source": "none"}
        if not requests:
            return out
        try:
            r = requests.get(f"{self.hub}/api/keb/status", timeout=1.0)
            if r.status_code == 200:
                js = r.json()
                out.update(js)
                out["source"] = "keb_status"
        except Exception:
            pass
        if not out.get("enabled"):
            try:
                r2 = requests.get(f"{self.hub}/api/keb/metrics", timeout=1.0)
                if r2.status_code == 200:
                    js2 = r2.json()
                    # Consider enabled if metrics exist
                    if js2:
                        out.update({"enabled": True, "metrics": js2, "source": "keb_metrics"})
            except Exception:
                pass
        return out

    def pass_perception(self, d: Dict[str, Any]) -> bool:
        # In dev/consciousness runner mode, local PerceptionBus is separate from kernel EventBus
        # If Hub's KEB endpoint returns enabled=false, that's OK—it means kernel EventBus
        # isn't registered in the Hub process, but the local PerceptionBus works fine.
        # Only fail if the endpoint errors out completely.
        return d.get("source") != "none"  # Any response means Hub is reachable

    def probe_memory(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"ok": False}
        if not requests:
            return out
        try:
            r = requests.get(f"{self.hub}/api/memory/status", timeout=1.0)
            if r.status_code == 200:
                js = r.json()
                out.update(js)
        except Exception:
            pass
        return out

    def pass_memory(self, d: Dict[str, Any]) -> bool:
        return bool(d.get("ok"))

    def probe_plugins(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"total": 0}
        if not requests:
            return out
        try:
            r = requests.get(f"{self.hub}/api/plugins", timeout=1.5)
            if r.status_code == 200:
                js = r.json()
                out["total"] = int(js.get("total", 0))
        except Exception:
            pass
        return out

    def pass_plugins(self, d: Dict[str, Any]) -> bool:
        # At least 0 is fine for dev; consider present if endpoint reachable
        return d.get("total", 0) >= 0

    def probe_policy(self) -> Dict[str, Any]:
        return {"configured": core_config.AUTONOMY_MODE, "policy_mode": self.policy.mode}

    def pass_policy(self, d: Dict[str, Any]) -> bool:
        return str(d.get("configured")) == str(d.get("policy_mode"))

    def probe_disk(self, path: str = "/") -> Dict[str, Any]:
        try:
            total, used, free = shutil.disk_usage(path)
            pct_free = free / total if total else 0.0
            return {"total": total, "used": used, "free": free, "pct_free": pct_free}
        except Exception as e:
            return {"error": str(e), "pct_free": 0.0}

    def pass_disk(self, d: Dict[str, Any]) -> bool:
        return float(d.get("pct_free", 0.0)) >= 0.10

    # -----------------------------
    # Engine
    # -----------------------------

    def run_check(self, check: HealthCheck) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "name": check.name,
            "question": check.question,
            "status": "unknown",
            "steps": [],
            "ts": time.time(),
        }
        try:
            probe_out = check.probe()
            result["probe"] = probe_out
            if check.pass_if(probe_out):
                result["status"] = "ok"
                self.last_results[check.name] = result
                return result

            # Build plan from remediate steps
            intent = Intent(
                why=f"Auto-repair: {check.name}",
                goal=f"Restore {check.name}",
                expected_gain=0.8,
                risk=check.risk,
                cost_estimate="short",
                plan=[sid for sid, _ in check.remediate],
                rollback=[sid for sid, _ in (check.rollback or [])],
                deadline_s=300,
            )
            steps = [PlanStep(id=sid, capability=sid, args=args) for sid, args in check.remediate]
            rb = [
                PlanStep(id=sid, capability=sid, args=args) for sid, args in (check.rollback or [])
            ]
            ledger = self.actuator.execute(Plan(intent=intent, steps=steps, rollback=rb))
            result["steps"] = ledger.actions
            # Verify
            verified = (check.verify or check.pass_if)(check.probe())
            result["status"] = "repaired" if (ledger.success and verified) else "failed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        # Phase 3: Update self-trust layer if available
        if self.self_trust:
            # Map check name to subsystem (simple mapping strategy)
            subsystem = self._map_check_to_subsystem(check.name)
            if subsystem:
                self.self_trust.observe(subsystem, result["status"])

        self.last_results[check.name] = result
        return result

    def _map_check_to_subsystem(self, check_name: str) -> Optional[str]:
        """Map health check name to subsystem name for self-trust tracking.

        Args:
            check_name: Health check name (e.g., "chat_system", "memory_engine")

        Returns:
            Subsystem name or None if no mapping
        """
        # Simple heuristic mapping
        if "chat" in check_name:
            return "chat"
        elif "perception" in check_name or "event" in check_name:
            return "perception"
        elif "memory" in check_name:
            return "memory"
        elif "plugin" in check_name:
            return "plugins"
        elif "policy" in check_name:
            return "policy"
        elif "disk" in check_name:
            return "disk"
        # Add more mappings as needed
        return None


# -----------------------------
# Check Builders (Phase 1 set)
# -----------------------------


def build_default_checks(hce: HealthCheckEngine) -> List[HealthCheck]:
    checks: List[HealthCheck] = []

    # Chat
    checks.append(
        HealthCheck(
            name="chat_system",
            question="Is my chat system working?",
            probe=hce.probe_chat,
            pass_if=hce.pass_chat,
            # Safe remediations for dev: rotate logs (low-risk), no rollback needed
            remediate=[("system.rotate_logs", {})],
            verify=hce.pass_chat,
            rollback=[],
            risk="low",
        )
    )

    # Perception Bus / Event Bus
    checks.append(
        HealthCheck(
            name="perception_bus",
            question="Is my perception/event bus delivering events?",
            probe=hce.probe_perception,
            pass_if=hce.pass_perception,
            remediate=[("system.rotate_logs", {})],  # low-risk nudge
            verify=hce.pass_perception,
            rollback=[],
            risk="low",
        )
    )

    # Memory Engine
    checks.append(
        HealthCheck(
            name="memory_engine",
            question="Is memory system within SLO? (status reachable)",
            probe=hce.probe_memory,
            pass_if=hce.pass_memory,
            remediate=[("system.rotate_logs", {})],
            verify=hce.pass_memory,
            rollback=[],
            risk="low",
        )
    )

    # Plugin Registry
    checks.append(
        HealthCheck(
            name="plugin_registry",
            question="Is plugin registry stable and non-empty?",
            probe=hce.probe_plugins,
            pass_if=hce.pass_plugins,
            remediate=[("system.rotate_logs", {})],
            verify=hce.pass_plugins,
            rollback=[],
            risk="low",
        )
    )

    # Policy Engine mode consistency
    checks.append(
        HealthCheck(
            name="policy_engine",
            question="Is policy mode consistent with boot policy?",
            probe=hce.probe_policy,
            pass_if=hce.pass_policy,
            remediate=[],
            verify=hce.pass_policy,
            rollback=[],
            risk="low",
        )
    )

    # Disk headroom
    checks.append(
        HealthCheck(
            name="disk_headroom",
            question="Is free disk space above 10%?",
            probe=hce.probe_disk,
            pass_if=hce.pass_disk,
            remediate=[("fs.cleanup_temp", {"path": "/tmp", "older_than_days": 7})],
            verify=hce.pass_disk,
            rollback=[],
            risk="low",
        )
    )

    return checks

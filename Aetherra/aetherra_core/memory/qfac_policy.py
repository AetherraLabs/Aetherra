#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
QFAC Policy: Centralized gating for hybrid/quantum modes

Purpose
 - Provide a single place to determine the effective QFAC mode
   (classical|hybrid|quantum) based on environment profile, validation,
   and coherence/drift health.

Environment knobs (all optional)
 - AETHERRA_PROFILE: prod|production|staging|test|dev
 - AETHERRA_QFAC_MODE: desired mode from operator (default classical)
 - AETHERRA_QFAC_POLICY: enforce|shadow|off
     * enforce (default in prod/staging): apply gating rules, may downgrade
     * shadow: evaluate but do not downgrade (reports would-deny)
     * off (default outside prod/staging): accept desired mode
 - AETHERRA_QFAC_VALIDATED: 1|true to declare validated quantum path present
 - AETHERRA_QFAC_BACKEND: simulator|qiskit|ionq|aws_braket|azure|custom
 - AETHERRA_QFAC_ALLOW_SIMULATOR_IN_PROD: 1 to allow simulator in prod
 - AETHERRA_QFAC_GATE_MIN: float (default 0.85)
 - AETHERRA_QFAC_HARD_MIN: float (default 0.75)
 - AETHERRA_QFAC_WINDOW_SIZE: int (for reporting only)
 - AETHERRA_QFAC_COHERENCE_EMA: float (optional runtime signal)
 - AETHERRA_QFAC_LAST_DRIFT_ALERT_EPOCH: float seconds since epoch (optional)
 - AETHERRA_QFAC_DRIFT_COOLDOWN_SEC: int seconds (default 300)

Inputs to resolve_mode
 - profile: str
 - desired_mode: str (classical|hybrid|quantum)
 - metrics: optional dict with keys {ema: float, last_drift_alert: epoch}

Outputs
 - dict with keys: mode, allowed, reason, policy, thresholds, metrics_used
"""

from __future__ import annotations

# Standard library imports
import os
import time
from typing import Any

PROD_PROFILES = {"prod", "production", "staging"}


class QFACPolicy:
    def __init__(self) -> None:
        # Thresholds and flags
        self.gate_min = float(os.getenv("AETHERRA_QFAC_GATE_MIN", "0.85"))
        self.hard_min = float(os.getenv("AETHERRA_QFAC_HARD_MIN", "0.75"))
        self.window_size = int(os.getenv("AETHERRA_QFAC_WINDOW_SIZE", "12"))
        self.drift_cooldown = int(os.getenv("AETHERRA_QFAC_DRIFT_COOLDOWN_SEC", "300"))

        # Backend/validation hints
        self.backend = (os.getenv("AETHERRA_QFAC_BACKEND") or "simulator").lower()
        self.validated_flag = os.getenv("AETHERRA_QFAC_VALIDATED", "").lower() in {
            "1",
            "true",
            "yes",
        }
        self.allow_simulator_in_prod = os.getenv(
            "AETHERRA_QFAC_ALLOW_SIMULATOR_IN_PROD", ""
        ).lower() in {"1", "true", "yes"}

    def _policy_mode(self, profile: str) -> str:
        pm = (os.getenv("AETHERRA_QFAC_POLICY") or "").lower()
        if not pm:
            return "enforce" if profile in PROD_PROFILES else "off"
        if pm not in {"enforce", "shadow", "off"}:
            return "enforce" if profile in PROD_PROFILES else "off"
        return pm

    def _collect_metrics(self, metrics: dict[str, Any] | None) -> dict[str, Any]:
        if metrics is None:
            # Allow env to provide minimal signals
            ema_str = os.getenv("AETHERRA_QFAC_COHERENCE_EMA")
            last_alert_str = os.getenv("AETHERRA_QFAC_LAST_DRIFT_ALERT_EPOCH")
            ema = float(ema_str) if ema_str else None
            last_alert = float(last_alert_str) if last_alert_str else None
            return {"ema": ema, "last_drift_alert": last_alert}
        # normalize keys
        ema = metrics.get("ema")
        last_alert = metrics.get("last_drift_alert")
        return {"ema": ema, "last_drift_alert": last_alert}

    def _has_validated_backend(self) -> bool:
        # Consider non-simulator backend or explicit validation flag as validated
        if self.validated_flag:
            return True
        return bool(self.backend and self.backend != "simulator")

    def resolve_mode(
        self,
        profile: str,
        desired_mode: str,
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        p = (profile or "").lower()
        dm = (desired_mode or "classical").lower()
        if dm not in {"classical", "hybrid", "quantum"}:
            dm = "classical"

        policy_mode = self._policy_mode(p)
        m = self._collect_metrics(metrics)
        now = time.time()

        # Always accept classical
        if dm == "classical":
            return {
                "mode": "classical",
                "allowed": True,
                "reason": "classical-always-allowed",
                "policy": policy_mode,
                "thresholds": self._thresholds_dict(),
                "metrics_used": m,
            }

        # Non-prod profiles: accept desired unless explicitly enforcing and thresholds fail
        if p not in PROD_PROFILES:
            if policy_mode == "off":
                return {
                    "mode": dm,
                    "allowed": True,
                    "reason": "non-prod-policy-off",
                    "policy": policy_mode,
                    "thresholds": self._thresholds_dict(),
                    "metrics_used": m,
                }
            # enforce/shadow in non-prod still respect health if provided
            would_deny, cause = self._would_deny_for_health(dm, m, now, prod=False)
            if policy_mode == "shadow":
                return {
                    "mode": dm,
                    "allowed": True,
                    "reason": f"shadow-would-deny:{cause}" if would_deny else "shadow-allow",
                    "policy": policy_mode,
                    "thresholds": self._thresholds_dict(),
                    "metrics_used": m,
                }
            if would_deny:
                return {
                    "mode": "classical",
                    "allowed": False,
                    "reason": cause,
                    "policy": policy_mode,
                    "thresholds": self._thresholds_dict(),
                    "metrics_used": m,
                }
            return {
                "mode": dm,
                "allowed": True,
                "reason": "non-prod-allow",
                "policy": policy_mode,
                "thresholds": self._thresholds_dict(),
                "metrics_used": m,
            }

        # Prod/staging: enforce by default
        would_deny, cause = self._would_deny_for_health(dm, m, now, prod=True)

        if policy_mode == "shadow":
            return {
                "mode": dm,
                "allowed": True,
                "reason": f"shadow-would-deny:{cause}" if would_deny else "shadow-allow",
                "policy": policy_mode,
                "thresholds": self._thresholds_dict(),
                "metrics_used": m,
            }

        if policy_mode == "off":
            # Operator override: accept desired
            return {
                "mode": dm,
                "allowed": True,
                "reason": "prod-policy-off-override",
                "policy": policy_mode,
                "thresholds": self._thresholds_dict(),
                "metrics_used": m,
            }

        # enforce
        if would_deny:
            return {
                "mode": "classical",
                "allowed": False,
                "reason": cause,
                "policy": policy_mode,
                "thresholds": self._thresholds_dict(),
                "metrics_used": m,
            }
        return {
            "mode": dm,
            "allowed": True,
            "reason": "prod-allow",
            "policy": policy_mode,
            "thresholds": self._thresholds_dict(),
            "metrics_used": m,
        }

    def _would_deny_for_health(
        self, desired_mode: str, metrics: dict[str, Any], now: float, prod: bool
    ) -> tuple[bool, str]:
        # Backend validation gate (only for hybrid/quantum)
        if (
            desired_mode in {"hybrid", "quantum"}
            and prod
            and not (self._has_validated_backend() or self.allow_simulator_in_prod)
        ):
            return True, "no-validated-backend"
        # Coherence/drift gates
        ema = metrics.get("ema")
        if ema is None:
            # In prod enforce presence of metric; outside prod allow if not provided
            if prod:
                return True, "missing-coherence-ema"
            else:
                return False, "no-metrics-non-prod"
        if ema < self.hard_min:
            return True, "ema-below-hard-min"
        if ema < self.gate_min:
            return True, "ema-below-gate-min"
        last_alert = metrics.get("last_drift_alert")
        if last_alert:
            try:
                age = max(0.0, now - float(last_alert))
                if age < self.drift_cooldown:
                    return True, "recent-drift-alert"
            except Exception:
                # Malformed alert timestamp -> deny in prod
                if prod:
                    return True, "invalid-drift-alert-ts"
        return False, "ok"

    def _thresholds_dict(self) -> dict[str, Any]:
        return {
            "gate_min": self.gate_min,
            "hard_min": self.hard_min,
            "window_size": self.window_size,
            "drift_cooldown_sec": self.drift_cooldown,
            "backend": self.backend,
            "validated_flag": self.validated_flag,
            "allow_sim_in_prod": self.allow_simulator_in_prod,
        }


__all__ = ["QFACPolicy", "PROD_PROFILES"]

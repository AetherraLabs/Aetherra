# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Self-Incorporation Security Layer

Provides security validation for autonomous code integration:
- Signature verification for code files
- Capability grant validation for integration plans
- Network policy compliance checks
- Policy drift detection
- Proposal authentication and authorization
- Rate limiting for proposal consumption

Author: Aetherra Security Team
Date: 2025-01-23
"""

# Standard library imports
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Aetherra imports
from Aetherra.security.capabilities import has_capability

logger = logging.getLogger(__name__)


@dataclass
class SecurityValidationResult:
    """Result of security validation."""

    approved: bool
    reason: str
    risk_score: float  # 0.0-1.0
    details: dict[str, Any]


@dataclass
class ProposalAuthResult:
    """Result of proposal authentication."""

    authenticated: bool
    authorized: bool
    sender: str | None
    reason: str


class SelfIncorporationSecurity:
    """
    Security layer for Self-Incorporation service.

    Provides:
    - Signature verification for code integration
    - Capability grant validation
    - Network policy compliance
    - Policy drift detection
    - Proposal authentication and rate limiting
    """

    def __init__(self, trust_mode: str = "standard"):
        """
        Initialize security layer.

        Args:
            trust_mode: "strict", "standard", or "permissive"
        """
        self.trust_mode = trust_mode
        self.strict_mode = self._is_strict_mode()

        # Rate limiting for proposals
        self._proposal_timestamps: dict[str, list[float]] = {}
        self._proposal_rate_limit = 10  # Max proposals per minute per sender
        self._proposal_window = 60.0  # 1 minute window

        logger.info(
            f"[SELFINC-SEC] Initialized with trust_mode={trust_mode}, strict={self.strict_mode}"
        )

    def _is_strict_mode(self) -> bool:
        """Check if strict security mode is enabled."""
        profile = os.getenv("AETHERRA_PROFILE", "").lower()
        strict_env = os.getenv("AETHERRA_NET_STRICT", "0")

        return profile in ("prod", "production") or strict_env == "1"

    async def verify_signature(self, file_path: Path) -> bool:
        """
        Verify code signature for a file.

        In strict mode: requires valid signature
        In standard/permissive mode: signature optional

        Args:
            file_path: Path to file to verify

        Returns:
            True if signature valid or not required, False if invalid
        """
        # Check if file has .sig companion
        sig_path = file_path.with_suffix(file_path.suffix + ".sig")

        if not sig_path.exists():
            if self.strict_mode:
                logger.warning(f"[SELFINC-SEC] No signature found for {file_path} (strict mode)")
                return False
            else:
                logger.debug(f"[SELFINC-SEC] No signature for {file_path} (permissive)")
                return True

        # Verify signature (simplified - production would use GPG/cryptography)
        try:
            sig_data = sig_path.read_text(encoding="utf-8").strip()
            file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()

            # Basic signature format: "sha256:<hash>"
            if sig_data.startswith("sha256:"):
                expected_hash = sig_data.split(":", 1)[1]
                if file_hash == expected_hash:
                    logger.debug(f"[SELFINC-SEC] Signature valid for {file_path}")
                    return True

            logger.warning(f"[SELFINC-SEC] Invalid signature for {file_path}")
            return False

        except Exception as e:
            logger.error(f"[SELFINC-SEC] Signature verification failed: {e}")
            return False

    async def check_capabilities(self, requester: str, required_caps: list[str]) -> bool:
        """
        Validate that integration has required capability grants.

        Args:
            requester: Identifier of requesting component
            required_caps: List of required capabilities

        Returns:
            True if all capabilities granted, False otherwise
        """
        if not required_caps:
            return True  # No capabilities required

        for cap in required_caps:
            if not has_capability(requester, cap):
                logger.warning(f"[SELFINC-SEC] Capability '{cap}' not granted to '{requester}'")
                return False

        logger.debug(f"[SELFINC-SEC] All capabilities granted for '{requester}'")
        return True

    async def check_network_policy(self, file_path: Path) -> bool:
        """
        Check if file complies with network access policies.

        Args:
            file_path: Path to file to check

        Returns:
            True if compliant, False otherwise
        """
        if not self.strict_mode:
            return True  # Permissive mode allows network access

        # Check if file contains network-related imports
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            dangerous_imports = [
                "import socket",
                "from socket",
                "import urllib",
                "from urllib",
                "import requests",
                "from requests",
                "import httpx",
                "from httpx",
            ]

            for imp in dangerous_imports:
                if imp in content:
                    logger.warning(f"[SELFINC-SEC] Network import detected: {imp} in {file_path}")

                    # Check if network capability granted
                    if not has_capability(str(file_path), "network:outbound"):
                        return False

            return True

        except Exception as e:
            logger.error(f"[SELFINC-SEC] Network policy check failed: {e}")
            return False

    async def detect_policy_drift(
        self, file_path: Path, current_risk: float
    ) -> SecurityValidationResult:
        """
        Detect if file's risk profile has changed significantly.

        Args:
            file_path: Path to file
            current_risk: Current risk score (0.0-1.0)

        Returns:
            SecurityValidationResult with drift assessment
        """
        # Load previous risk score from cache (simplified)
        cache_path = Path(".aetherra") / "security_cache" / f"{file_path.name}.risk"

        try:
            if cache_path.exists():
                prev_risk = float(cache_path.read_text(encoding="utf-8").strip())
                risk_delta = abs(current_risk - prev_risk)

                if risk_delta > 0.3:  # 30% drift threshold
                    return SecurityValidationResult(
                        approved=False,
                        reason="critical_policy_drift",
                        risk_score=current_risk,
                        details={"prev_risk": prev_risk, "delta": risk_delta},
                    )

            # Update cache
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(str(current_risk), encoding="utf-8")

            return SecurityValidationResult(
                approved=True,
                reason="no_drift",
                risk_score=current_risk,
                details={},
            )

        except Exception as e:
            logger.warning(f"[SELFINC-SEC] Policy drift detection failed: {e}")
            # Fail open in non-strict mode, fail closed in strict mode
            return SecurityValidationResult(
                approved=not self.strict_mode,
                reason="drift_check_failed",
                risk_score=current_risk,
                details={"error": str(e)},
            )

    async def authenticate_proposal(
        self, proposal: dict[str, Any], sender: str | None = None
    ) -> ProposalAuthResult:
        """
        Authenticate and authorize an improvement proposal.

        Args:
            proposal: Proposal data
            sender: Optional sender identifier

        Returns:
            ProposalAuthResult with authentication status
        """
        # Extract sender from proposal or use provided
        proposal_sender = sender or proposal.get("sender", "unknown")

        # Check if sender is authenticated
        if proposal_sender == "unknown":
            if self.strict_mode:
                return ProposalAuthResult(
                    authenticated=False,
                    authorized=False,
                    sender=proposal_sender,
                    reason="unknown_sender_in_strict_mode",
                )
            else:
                # Allow in permissive mode but log
                logger.warning(
                    "[SELFINC-SEC] Allowing proposal from unknown sender (permissive mode)"
                )
                proposal_sender = "anonymous"

        # Check rate limit
        if not self._check_rate_limit(proposal_sender):
            return ProposalAuthResult(
                authenticated=True,
                authorized=False,
                sender=proposal_sender,
                reason="rate_limit_exceeded",
            )

        # Check if sender is authorized for proposal type
        proposal_type = proposal.get("type", "unknown")
        required_cap = f"maintenance:proposal:{proposal_type}"

        if self.strict_mode and not has_capability(proposal_sender, required_cap):
            logger.warning(
                f"[SELFINC-SEC] Sender '{proposal_sender}' not authorized for '{proposal_type}'"
            )
            return ProposalAuthResult(
                authenticated=True,
                authorized=False,
                sender=proposal_sender,
                reason=f"missing_capability:{required_cap}",
            )

        return ProposalAuthResult(
            authenticated=True,
            authorized=True,
            sender=proposal_sender,
            reason="approved",
        )

    def _check_rate_limit(self, sender: str) -> bool:
        """
        Check if sender is within rate limit for proposals.

        Args:
            sender: Sender identifier

        Returns:
            True if within limit, False if exceeded
        """
        now = time.time()

        # Initialize sender's timestamp list if not exists
        if sender not in self._proposal_timestamps:
            self._proposal_timestamps[sender] = []

        # Remove timestamps outside the window
        timestamps = self._proposal_timestamps[sender]
        timestamps[:] = [ts for ts in timestamps if now - ts < self._proposal_window]

        # Check if rate limit exceeded
        if len(timestamps) >= self._proposal_rate_limit:
            logger.warning(
                f"[SELFINC-SEC] Rate limit exceeded for sender '{sender}': "
                f"{len(timestamps)} proposals in {self._proposal_window}s"
            )
            return False

        # Add current timestamp
        timestamps.append(now)
        return True

    async def validate_integration_security(
        self, file_path: Path, plan: dict[str, Any]
    ) -> SecurityValidationResult:
        """
        Comprehensive security validation for integration.

        Args:
            file_path: Path to file being integrated
            plan: Integration plan

        Returns:
            SecurityValidationResult with overall assessment
        """
        reasons = []
        risk_score = 0.0

        # 1. Signature verification
        if not await self.verify_signature(file_path):
            reasons.append("invalid_signature")
            risk_score += 0.4
            if self.strict_mode:
                return SecurityValidationResult(
                    approved=False,
                    reason="signature_verification_failed",
                    risk_score=1.0,
                    details={"reasons": reasons},
                )

        # 2. Capability grants
        required_caps = plan.get("required_capabilities", [])
        requester = str(file_path)

        if not await self.check_capabilities(requester, required_caps):
            reasons.append("missing_capabilities")
            risk_score += 0.3
            if self.strict_mode:
                return SecurityValidationResult(
                    approved=False,
                    reason="capabilities_not_granted",
                    risk_score=risk_score,
                    details={"reasons": reasons, "required_caps": required_caps},
                )

        # 3. Network policy
        if not await self.check_network_policy(file_path):
            reasons.append("network_policy_violation")
            risk_score += 0.3
            return SecurityValidationResult(
                approved=False,
                reason="network_policy_violation",
                risk_score=risk_score,
                details={"reasons": reasons},
            )

        # All checks passed
        return SecurityValidationResult(
            approved=True,
            reason="security_approved",
            risk_score=risk_score,
            details={"reasons": reasons},
        )

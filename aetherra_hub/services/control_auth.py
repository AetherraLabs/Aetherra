"""Authorization policy for privileged Hub control-plane operations."""

from __future__ import annotations

import hmac
import ipaddress
import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ControlAuthResult:
    """Result of a control-plane authorization decision."""

    allowed: bool
    status_code: int
    error: str | None = None


def _is_production_profile() -> bool:
    profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
    return profile in {"prod", "production"}


def _is_loopback(remote_addr: str | None) -> bool:
    if not remote_addr:
        return False
    try:
        return ipaddress.ip_address(remote_addr).is_loopback
    except ValueError:
        return remote_addr.strip().lower() == "localhost"


def provided_token(headers: Mapping[str, str]) -> str:
    """Extract a supported bearer or Aetherra token header."""
    authorization = (headers.get("Authorization") or "").strip()
    scheme, separator, credentials = authorization.partition(" ")
    if separator and scheme.lower() == "bearer":
        return credentials.strip()
    return (
        (headers.get("X-Aetherra-Control-Token") or "").strip()
        or (headers.get("X-Aetherra-Token") or "").strip()
    )


def authorize_control_request(
    headers: Mapping[str, str],
    remote_addr: str | None,
) -> ControlAuthResult:
    """Authorize a privileged Hub request.

    Production requires a configured control token. In non-production, a
    missing token permits loopback requests only. When a token is configured,
    every caller must provide it regardless of profile or source address.
    """

    expected = (os.getenv("AETHERRA_HUB_CONTROL_TOKEN") or "").strip()
    if not expected:
        if _is_production_profile():
            return ControlAuthResult(
                allowed=False,
                status_code=503,
                error="control_token_not_configured",
            )
        if _is_loopback(remote_addr):
            return ControlAuthResult(allowed=True, status_code=200)
        return ControlAuthResult(
            allowed=False,
            status_code=403,
            error="loopback_required",
        )

    return authorize_token_request(headers, expected)


def authorize_token_request(
    headers: Mapping[str, str],
    expected_token: str | None,
    *,
    missing_configuration_error: str = "token_not_configured",
    unauthorized_status: int = 401,
) -> ControlAuthResult:
    """Authorize a request against an explicitly configured service token."""
    expected = (expected_token or "").strip()
    if not expected:
        return ControlAuthResult(
            allowed=False,
            status_code=503,
            error=missing_configuration_error,
        )
    supplied = provided_token(headers)
    if not supplied or not hmac.compare_digest(supplied, expected):
        return ControlAuthResult(
            allowed=False,
            status_code=unauthorized_status,
            error="unauthorized",
        )
    return ControlAuthResult(allowed=True, status_code=200)


__all__ = [
    "ControlAuthResult",
    "authorize_control_request",
    "authorize_token_request",
    "provided_token",
]

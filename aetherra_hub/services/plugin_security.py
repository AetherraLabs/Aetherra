"""Focused plugin registration validation & redaction utilities.

Keeps implementation minimal; advanced signing / schema verification may be
layered later by integrating existing `services.plugins` logic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict

__all__ = [
    "PluginValidationError",
    "ValidationResult",
    "redact_text",
    "validate_and_register_plugin",
]


class PluginValidationError(ValueError):
    pass


_SECRET_PATTERNS = [
    re.compile(r"(sk-[A-Za-z0-9]{20,})"),
    re.compile(r"(?:apikey|api_key|token)\s*[:=]\s*['\"]?([A-Za-z0-9\-_]{16,})", re.I),
    re.compile(r"(?i)(password|secret)\s*[:=]\s*['\"][^'\"\n]{4,}['\"]"),
]


def redact_text(text: str) -> str:
    if not text:
        return text
    red = text
    for pat in _SECRET_PATTERNS:
        red = pat.sub("[REDACTED]", red)
    return red


_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]{1,63}$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z\-.]+)?$")


@dataclass(frozen=True)
class ValidationResult:
    registry_record: Dict[str, Any]


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise PluginValidationError(msg)


def _deny_html(text: str, field: str) -> None:
    if "<" in (text or "") or ">" in (text or ""):
        raise PluginValidationError(f"{field} must not contain HTML/markup")


def validate_and_register_plugin(
    payload: Dict[str, Any],
    *,
    require_signature: bool = False,
    max_description_len: int = 2000,
) -> ValidationResult:
    name = str(payload.get("name", "")).strip()
    version = str(payload.get("version", "")).strip()
    description = str(payload.get("description", "")).strip()
    category = str(payload.get("category", "utilities")).strip() or "utilities"
    display_name = (
        str(payload.get("display_name", name.title())).strip() or name.title()
    )

    _require(bool(name), "name is required")
    _require(_NAME_RE.match(name) is not None, "name must be [a-z0-9][a-z0-9_-]{1,63}")
    _require(bool(version), "version is required")
    _require(
        _SEMVER_RE.match(version) is not None, "version must be semver (e.g., 1.2.3)"
    )
    _require(bool(description), "description is required")
    _require(
        len(description) <= max_description_len,
        f"description too long (>{max_description_len})",
    )
    _deny_html(description, "description")
    _deny_html(display_name, "display_name")
    _deny_html(category, "category")

    if require_signature:
        sig = payload.get("signature")
        _require(bool(sig), "signature required by policy")

    allowed_extra = {"homepage", "repo", "author", "license"}
    extras = {k: v for k, v in payload.items() if k in allowed_extra}

    record: Dict[str, Any] = {
        "name": name,
        "version": version,
        "display_name": display_name,
        "description": description,
        "category": category or "utilities",
        "registered_at": payload.get("registered_at") or "",
        **extras,
    }
    return ValidationResult(registry_record=record)

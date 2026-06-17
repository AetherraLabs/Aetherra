"""Guardian policy bridge to the existing Aetherra Security System."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import IntentDeclaration, PolicyResult
from .paths import guardian_policy_file

CapabilityChecker = Callable[[str, str], bool]


@dataclass(frozen=True, slots=True)
class GuardianPolicy:
    """Parsed Guardian policy document."""

    version: int = 1
    default: str = "allow"
    allow: tuple[dict[str, Any], ...] = ()
    deny: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def load_guardian_policy(path: Path | str | None = None) -> GuardianPolicy:
    """Load Guardian policy from JSON.

    Supported shape:
    {
      "version": 1,
      "default": "allow" | "deny",
      "allow": [{"requester": "plugin:*", "action": "plugin.execute"}],
      "deny": [{"target": "Aetherra/security/*"}]
    }
    """

    policy_path = Path(path).expanduser().resolve() if path else guardian_policy_file()
    if not policy_path.exists():
        return GuardianPolicy()
    data = json.loads(policy_path.read_text(encoding="utf-8") or "{}")
    if not isinstance(data, dict):
        raise ValueError("Guardian policy must be a JSON object")
    default = str(data.get("default", "allow")).strip().lower()
    if default not in {"allow", "deny"}:
        raise ValueError("Guardian policy default must be 'allow' or 'deny'")
    return GuardianPolicy(
        version=int(data.get("version", 1)),
        default=default,
        allow=tuple(rule for rule in data.get("allow", []) if isinstance(rule, dict)),
        deny=tuple(rule for rule in data.get("deny", []) if isinstance(rule, dict)),
        metadata=dict(data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {}),
    )


def security_capability_checker(requester: str, capability: str) -> bool:
    """Check capabilities through the Security System policy layer."""

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def evaluate_guardian_policy(
    intent: IntentDeclaration,
    *,
    policy: GuardianPolicy | None = None,
) -> PolicyResult:
    """Evaluate explicit Guardian allow/deny rules for an intent."""

    try:
        resolved = policy or load_guardian_policy()
    except Exception as exc:
        return PolicyResult(
            allowed=False,
            reason="guardian_policy_load_failed",
            details={"error_type": type(exc).__name__, "error": str(exc)},
        )

    for rule in resolved.deny:
        if _rule_matches(rule, intent):
            return PolicyResult(
                allowed=False,
                reason="guardian_policy_denied",
                details={"rule": rule},
            )

    if resolved.allow:
        for rule in resolved.allow:
            if _rule_matches(rule, intent):
                return PolicyResult(
                    allowed=True,
                    reason="guardian_policy_allowed",
                    details={"rule": rule},
                )
        return PolicyResult(allowed=False, reason="guardian_policy_no_allow_match")

    if _requires_explicit_policy() or resolved.default == "deny":
        return PolicyResult(allowed=False, reason="guardian_policy_default_deny")

    return PolicyResult(allowed=True, reason="guardian_policy_default_allow")


def evaluate_capabilities(
    intent: IntentDeclaration,
    *,
    capability_checker: CapabilityChecker | None = None,
) -> PolicyResult:
    """Evaluate all requested capabilities through Security's capability policy."""

    checker = capability_checker or security_capability_checker
    missing: list[str] = []
    for capability in intent.capabilities:
        try:
            if not checker(intent.requester, capability):
                missing.append(capability)
        except Exception as exc:
            return PolicyResult(
                allowed=False,
                reason="capability_check_failed",
                missing_capabilities=(capability,),
                details={"error_type": type(exc).__name__, "error": str(exc)},
            )
    if missing:
        return PolicyResult(
            allowed=False,
            reason="missing_capability",
            missing_capabilities=tuple(missing),
        )
    return PolicyResult(allowed=True, reason="capabilities_allowed")


def _requires_explicit_policy() -> bool:
    return (os.getenv("AETHERRA_GUARDIAN_REQUIRE_POLICY", "0") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _rule_matches(rule: dict[str, Any], intent: IntentDeclaration) -> bool:
    fields = {
        "requester": intent.requester,
        "subsystem": intent.subsystem,
        "action": intent.action,
        "target": intent.target,
    }
    for key, actual in fields.items():
        expected = rule.get(key)
        if expected is not None and not _value_matches(expected, actual):
            return False
    expected_capabilities = rule.get("capabilities")
    if expected_capabilities is not None:
        expected_values = _as_string_list(expected_capabilities)
        if not expected_values:
            return False
        actual_caps = set(intent.capabilities)
        if not all(
            any(_value_matches(expected, actual) for actual in actual_caps)
            for expected in expected_values
        ):
            return False
    return True


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, str)]
    return []


def _value_matches(expected: Any, actual: str) -> bool:
    if isinstance(expected, list):
        return any(_value_matches(item, actual) for item in expected)
    if not isinstance(expected, str):
        return False
    if expected == "*":
        return True
    if expected.endswith("*"):
        return actual.startswith(expected[:-1])
    return expected == actual

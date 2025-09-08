# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Plugin Manifest Schema and Validator
============================================

Lightweight JSON-like schema and validator for plugin manifests.
Avoids external deps; validates types, required fields, enums, and ranges.

Fields (defaults in parentheses):
- name (required, str)
- version (required, str)
- description (str, "")
- author (str, "Unknown")
- entry_point (required, str)
- capabilities (list[str], [])
- dependencies (list[str], [])
- ui_components (list[str], [])
- permissions (list[str], []) allowed: filesystem, network, process, lyrixa_core
- data_classification (str, "public") in {public, internal, restricted, secret}
- deterministic (bool, False)
- side_effects (str, "none") in {none, filesystem, network, process, multiple}
- timeout_ms (int, 60000) >= 0
- retries (int, 0) >= 0
- min_confidence (float, 0.0) in [0,1]
- input_schema (dict, optional)
- output_schema (dict, optional)
- trust (dict, optional): { min_zone: "unsigned|lenient_signed|strict_signed" }
"""

from __future__ import annotations

from typing import Any, Dict, List

ALLOWED_PERMISSIONS = {"filesystem", "network", "process", "lyrixa_core"}
ALLOWED_CLASSIFICATIONS = {"public", "internal", "restricted", "secret"}
ALLOWED_SIDE_EFFECTS = {"none", "filesystem", "network", "process", "multiple"}
ALLOWED_TRUST_ZONES = {"unsigned", "lenient_signed", "strict_signed"}


def _is_str(v: Any) -> bool:
    return isinstance(v, str) and len(v.strip()) > 0


def _is_str_list(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def validate_manifest(
    manifest: Dict[str, Any],
) -> tuple[bool, List[str], Dict[str, Any]]:
    """
    Validate manifest and return (ok, errors, normalized_manifest).
    Does not mutate input. Provides defaults for missing optional fields.
    """
    errors: List[str] = []
    m = dict(manifest or {})

    # Required
    if not _is_str(m.get("name")):
        errors.append("name: required non-empty string")
    if not _is_str(m.get("version")):
        errors.append("version: required non-empty string")
    if not _is_str(m.get("entry_point")):
        errors.append("entry_point: required non-empty string")

    # Optionals with defaults
    if not isinstance(m.get("description", ""), str):
        errors.append("description: must be string")
    else:
        m.setdefault("description", "")

    if not isinstance(m.get("author", "Unknown"), str):
        errors.append("author: must be string")
    else:
        m.setdefault("author", "Unknown")

    if "capabilities" in m and not _is_str_list(m["capabilities"]):
        errors.append("capabilities: must be list of strings")
    else:
        m.setdefault("capabilities", [])

    if "dependencies" in m and not _is_str_list(m["dependencies"]):
        errors.append("dependencies: must be list of strings")
    else:
        m.setdefault("dependencies", [])

    if "ui_components" in m and not _is_str_list(m["ui_components"]):
        errors.append("ui_components: must be list of strings")
    else:
        m.setdefault("ui_components", [])

    # Permissions
    perms = m.get("permissions", [])
    if perms is None:
        perms = []
    if not isinstance(perms, list) or not all(isinstance(p, str) for p in perms):
        errors.append("permissions: must be list of strings")
    else:
        invalid = [p for p in perms if p not in ALLOWED_PERMISSIONS]
        if invalid:
            errors.append(f"permissions: invalid values {invalid}")
    m["permissions"] = perms

    # Classification
    cls = m.get("data_classification", "public")
    if not isinstance(cls, str) or cls not in ALLOWED_CLASSIFICATIONS:
        errors.append(f"data_classification: must be one of {sorted(ALLOWED_CLASSIFICATIONS)}")
    m["data_classification"] = cls if isinstance(cls, str) else "public"

    # Determinism & side effects
    det = m.get("deterministic", False)
    if not isinstance(det, bool):
        errors.append("deterministic: must be boolean")
    m["deterministic"] = bool(det)

    se = m.get("side_effects", "none")
    if not isinstance(se, str) or se not in ALLOWED_SIDE_EFFECTS:
        errors.append(f"side_effects: must be one of {sorted(ALLOWED_SIDE_EFFECTS)}")
    m["side_effects"] = se if isinstance(se, str) else "none"

    # Timeouts / retries
    to = m.get("timeout_ms", 60000)
    if not isinstance(to, int) or to < 0:
        errors.append("timeout_ms: must be non-negative integer")
    m["timeout_ms"] = int(to) if isinstance(to, int) else 60000

    rt = m.get("retries", 0)
    if not isinstance(rt, int) or rt < 0:
        errors.append("retries: must be non-negative integer")
    m["retries"] = int(rt) if isinstance(rt, int) else 0

    # Confidence
    mc = m.get("min_confidence", 0.0)
    if not isinstance(mc, (int, float)) or mc < 0 or mc > 1:
        errors.append("min_confidence: must be a number in [0,1]")
    m["min_confidence"] = float(mc) if isinstance(mc, (int, float)) else 0.0

    # I/O Schemas
    if "input_schema" in m and not isinstance(m["input_schema"], dict):
        errors.append("input_schema: must be an object if provided")
    if "output_schema" in m and not isinstance(m["output_schema"], dict):
        errors.append("output_schema: must be an object if provided")

    # Trust policy
    trust = m.get("trust")
    if trust is not None:
        if not isinstance(trust, dict):
            errors.append("trust: must be an object if provided")
        else:
            mz = trust.get("min_zone", "unsigned")
            if mz not in ALLOWED_TRUST_ZONES:
                errors.append(f"trust.min_zone: must be one of {sorted(ALLOWED_TRUST_ZONES)}")
            else:
                trust["min_zone"] = mz
    else:
        trust = {"min_zone": "unsigned"}
    m["trust"] = trust

    return (len(errors) == 0, errors, m)


def compute_trust_zone(strict: bool, signature_verified: bool) -> str:
    """Map hub signing strictness and signature verification to trust zone label."""
    if strict and signature_verified:
        return "strict_signed"
    if signature_verified:
        return "lenient_signed"
    return "unsigned"

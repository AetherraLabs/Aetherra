#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Replace legacy mojibake markers in the service registry with ASCII labels.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("[WARN]", "[WARN]"),
    ("[OK]", "[OK]"),
    ("[ERROR]", "[ERROR]"),
    ("[DISC]", "[DISC]"),
    ("[TOOL]", "[TOOL]"),
    ("[FAIL]", "[FAIL]"),
    ("ðŸ”Œ", "[PLUGIN]"),
    ("ðŸŽ™ï¸", "[VOICE]"),
    ("ðŸ”—", "[LINK]"),
)


@dataclass(frozen=True)
class ServiceRegistryUnicodePlan:
    file_path: Path
    content: str
    replacements: int


def _hash_value(value: object) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "maintenance" and capability in {
        "maintenance:cleanup",
        "fs:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_fix(plan: ServiceRegistryUnicodePlan):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.service_registry_unicode_fix",
            target="maintenance:service_registry_unicode",
            purpose="Replace legacy encoded service registry markers with ASCII labels",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Service registry marker text is normalized",
            reversible=False,
            rollback_plan="restore service registry file from version control or backup",
            metadata={
                "file_path_hash": _hash_value(plan.file_path),
                "replacement_count": int(plan.replacements),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def plan_unicode_service_registry_fix(
    file_path: str | Path = "aetherra_service_registry.py",
) -> ServiceRegistryUnicodePlan | None:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    updated_content = content
    replacement_count = 0

    for old, new in REPLACEMENTS:
        occurrences = updated_content.count(old)
        if occurrences:
            updated_content = updated_content.replace(old, new)
            replacement_count += occurrences

    if updated_content == content:
        return None

    return ServiceRegistryUnicodePlan(
        file_path=path,
        content=updated_content,
        replacements=replacement_count,
    )


def fix_unicode_service_registry(
    file_path: str | Path = "aetherra_service_registry.py",
) -> int:
    plan = plan_unicode_service_registry_fix(file_path)
    if plan is None:
        print("No service registry Unicode fixes needed.")
        return 0

    decision = _guardian_preflight_fix(plan)
    if not decision.allowed:
        print(f"Guardian denied service registry Unicode fix: {decision.reason}")
        return 1

    plan.file_path.write_text(plan.content, encoding="utf-8")
    print("Service registry Unicode markers replaced.")
    return 0


def main() -> int:
    return fix_unicode_service_registry()


if __name__ == "__main__":
    raise SystemExit(main())

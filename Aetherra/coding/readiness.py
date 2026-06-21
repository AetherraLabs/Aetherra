"""Read-only readiness contract for the Aetherra Coding System."""

from __future__ import annotations

from pathlib import Path
from typing import Any

CODING_READINESS_CONTRACT_VERSION = "1.0"


REQUIRED_PATHS: dict[str, str] = {
    "system_document": "docs/AETHERRA_CODING_SYSTEM.md",
    "guardian_document": "docs/AETHERRA_GUARDIAN_SYSTEM.md",
    "security_document": "docs/AETHERRA_SECURITY_SYSTEM.md",
    "self_incorporation_document": "docs/AETHERRA_SELF-INCORPORATION_SYSTEM.md",
    "aether_script_verifier": "tools/verify_aether_scripts.py",
    "spec_tests_gate": "tools/spec_tests_gate.py",
    "quality_gates": "tools/quality_gates.py",
    "script_signing": "Aetherra/security/script_signing.py",
    "plugin_signing": "Aetherra/security/plugin_signing.py",
    "self_incorporation_blueprint": "aetherra_hub/blueprints/self_incorporation.py",
}

OPTIONAL_PATHS: dict[str, str] = {
    "coding_tests": "tests/coding",
    "aether_script_tests": "tests/unit/test_aether_script_guardian.py",
    "self_incorporation_tests": "tests/unit/test_selfinc_integration_guardian.py",
}


def assess_coding_readiness(project_root: Path | str | None = None) -> dict[str, Any]:
    """Assess whether Coding can safely operate as a governed foundation.

    This function never inspects or executes untrusted source code. It only
    checks for the repository-level contracts that make AI-assisted coding safe
    enough to expose as a read-only status surface.
    """

    root = _resolve_project_root(project_root)
    required = _path_checks(root, REQUIRED_PATHS)
    optional = _path_checks(root, OPTIONAL_PATHS)

    missing_required = [
        name for name, check in required.items() if check["available"] is False
    ]
    proposal_only = True
    direct_mutation_allowed = False
    guardian_required_for_mutation = True
    self_incorporation_required_for_apply = True

    if missing_required:
        readiness = "blocked"
    else:
        readiness = "ready"

    safe_for_assist = readiness == "ready"
    safe_for_autonomous_apply = False
    reasons = [f"missing_required:{name}" for name in missing_required] or ["ready"]

    return {
        "ok": readiness == "ready",
        "system": "coding",
        "contract_version": CODING_READINESS_CONTRACT_VERSION,
        "readiness": readiness,
        "safe_for_assist": safe_for_assist,
        "safe_for_autonomous_apply": safe_for_autonomous_apply,
        "reasons": reasons,
        "checks": {
            "proposal_only_default": proposal_only,
            "direct_mutation_allowed": direct_mutation_allowed,
            "guardian_required_for_mutation": guardian_required_for_mutation,
            "self_incorporation_required_for_apply": self_incorporation_required_for_apply,
            "required_paths": required,
            "optional_paths": optional,
            "verification_tools": [
                "tools/spec_tests_gate.py",
                "tools/quality_gates.py",
                "tools/verify_aether_scripts.py",
                "pytest",
                "ruff",
            ],
        },
        "authority": {
            "owns": [
                "coding intent analysis",
                "implementation planning",
                "test and verification planning",
                "candidate patch proposal",
                "code review readiness reporting",
                "script and plugin signing workflow coordination",
            ],
            "does_not_own": [
                "direct repository mutation",
                "privileged code execution",
                "Guardian approval decisions",
                "Security capability enforcement",
                "Self-Incorporation application and rollback",
                "Kernel scheduling",
                "release publishing authority",
            ],
            "mutation_path": [
                "Coding proposal",
                "Guardian review",
                "Security enforcement",
                "Self-Incorporation staged apply",
                "Homeostasis verification",
                "Maintenance record",
            ],
        },
        "failure_modes": {
            "missing_contract": "block autonomous coding readiness and report the missing prerequisite",
            "verification_failure": "do not apply; return diagnostics for user or Self-Improvement review",
            "guardian_denial": "terminate proposal without mutation",
            "security_block": "terminate execution path and preserve audit trail",
            "apply_failure": "Self-Incorporation owns rollback and quarantine",
        },
    }


def build_coding_status_payload(
    project_root: Path | str | None = None,
) -> dict[str, Any]:
    """Build the public Coding status payload without applying changes."""

    return {
        "ok": True,
        "read_only": True,
        "readiness": assess_coding_readiness(project_root),
    }


def _resolve_project_root(project_root: Path | str | None) -> Path:
    if project_root is not None:
        return Path(project_root).resolve()
    return Path(__file__).resolve().parents[2]


def _path_checks(root: Path, paths: dict[str, str]) -> dict[str, dict[str, Any]]:
    checks: dict[str, dict[str, Any]] = {}
    for name, relative_path in paths.items():
        path = root / relative_path
        checks[name] = {
            "path": relative_path,
            "available": path.exists(),
            "kind": "directory" if path.is_dir() else "file",
        }
    return checks

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
from __future__ import annotations

import argparse
import json
import os
from collections.abc import Iterable
from pathlib import Path

"""
Policy Bootstrap CLI
====================

Generate starter policy files under the Aetherra policy directory.

Defaults are safe for production:
- capabilities.json: no grants (deny-by-default)
- net_policy.json: allow localhost/127.0.0.1/.aetherra.dev, empty deny list
- selfinc.json: default incorporation rules (auto-integrate low-risk types; review for plugins/agents/workflows)

Override policy home by setting env AETHERRA_POLICY_HOME for use in CI/tests.

Usage examples:
    python -m Aetherra.cli.policy_bootstrap --all
    python -m Aetherra.cli.policy_bootstrap --capabilities --force
    python -m Aetherra.cli.policy_bootstrap --network --allow api.example.com .corp.example
    python -m Aetherra.cli.policy_bootstrap --selfinc
"""


def _policy_home() -> Path:
    override = os.getenv("AETHERRA_POLICY_HOME", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(os.path.expanduser("~/.aetherra")).resolve() / "policy"


def _write_json(path: Path, data: dict, force: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return False
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True


def bootstrap_capabilities(target_dir: Path, force: bool = False) -> Path:
    """Create a minimal capabilities.json (deny-by-default unless explicitly granted).

    Includes a starter 'limits' section with conservative defaults for risky capabilities.
    """
    data = {
        "allow": {"core:webhook_manager": ["network:webhook"]},
        "limits": {
            # Outbound network actions should be fast and sparse by default
            "network:outbound": {"timeout_sec": 10, "max_concurrency": 1},
            "network:webhook": {"timeout_sec": 8, "max_concurrency": 1},
        },
    }
    path = target_dir / "capabilities.json"
    _write_json(path, data, force=force)
    return path


def bootstrap_net_policy(
    target_dir: Path, allow_extra: Iterable[str] | None = None, force: bool = False
) -> Path:
    allow = ["localhost", "127.0.0.1", ".aetherra.dev"]
    if allow_extra:
        for a in allow_extra:
            s = str(a or "").strip()
            if s:
                allow.append(s)
    data = {"allow_domains": allow, "deny_domains": []}
    path = target_dir / "net_policy.json"
    _write_json(path, data, force=force)
    return path


def bootstrap_selfinc_policy(target_dir: Path, force: bool = False) -> Path:
    """Create a default self-incorporation policy (selfinc.json).

    Mirrors defaults used by SelfIncorporationConfig._load_selfinc_policies so that
    operators have a tangible file to edit. Safe, conservative defaults.
    """
    data = {
        "version": "1.0",
        "auto_integrate": ["utility", "docs", "dataset"],
        "require_review": ["plugin", "agent", "workflow"],
        "quarantine": ["unknown"],
        # Capabilities considered unique (empty by default; multi-provider allowed)
        "unique_capabilities": [],
        "conflict_policy": "multi_provider_by_default",
        "trust_tiers": {
            "verified": {"auto_integrate": True, "elevated_permissions": True},
            "trusted": {"auto_integrate": True, "elevated_permissions": False},
            "standard": {"auto_integrate": False, "elevated_permissions": False},
            "experimental": {"auto_integrate": False, "elevated_permissions": False},
            "quarantined": {"auto_integrate": False, "elevated_permissions": False},
        },
    }
    path = target_dir / "selfinc.json"
    _write_json(path, data, force=force)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Aetherra policy files")
    parser.add_argument("--all", action="store_true", help="Generate all policies")
    parser.add_argument("--capabilities", action="store_true", help="Generate capabilities.json")
    parser.add_argument("--network", action="store_true", help="Generate net_policy.json")
    parser.add_argument("--selfinc", action="store_true", help="Generate selfinc.json")
    parser.add_argument(
        "--allow",
        nargs="*",
        default=[],
        help="Additional entries for allow_domains (network policy)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing policy files")
    args = parser.parse_args(argv)

    target = _policy_home()
    target.mkdir(parents=True, exist_ok=True)

    if not (args.all or args.capabilities or args.network or args.selfinc):
        # default to all if nothing specified
        args.all = True

    wrote_any = False
    outputs: list[str] = []
    if args.all or args.capabilities:
        p = bootstrap_capabilities(target, force=args.force)
        outputs.append(str(p))
        wrote_any = True
    if args.all or args.network:
        p = bootstrap_net_policy(target, allow_extra=args.allow, force=args.force)
        outputs.append(str(p))
        wrote_any = True
    if args.all or args.selfinc:
        p = bootstrap_selfinc_policy(target, force=args.force)
        outputs.append(str(p))
        wrote_any = True

    print("[OK] Policy files ready:")
    for o in outputs:
        print(f" - {o}")
    return 0 if wrote_any else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

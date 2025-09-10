# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Policy Bootstrap CLI
====================

Generate starter policy files under the Aetherra policy directory.

Defaults are safe for production:
- capabilities.json: no grants (deny-by-default)
- net_policy.json: allow localhost/127.0.0.1/.aetherra.dev, empty deny list

Override policy home by setting env AETHERRA_POLICY_HOME for use in CI/tests.

Usage examples:
  python -m Aetherra.cli.policy_bootstrap --all
  python -m Aetherra.cli.policy_bootstrap --capabilities --force
  python -m Aetherra.cli.policy_bootstrap --network --allow api.example.com .corp.example
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable


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
    """Create a minimal capabilities.json (deny-by-default unless explicitly granted)."""
    data = {"allow": {"core:webhook_manager": ["network:webhook"]}}
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Aetherra policy files")
    parser.add_argument("--all", action="store_true", help="Generate all policies")
    parser.add_argument("--capabilities", action="store_true", help="Generate capabilities.json")
    parser.add_argument("--network", action="store_true", help="Generate net_policy.json")
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

    if not (args.all or args.capabilities or args.network):
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

    print("[OK] Policy files ready:")
    for o in outputs:
        print(f" - {o}")
    return 0 if wrote_any else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

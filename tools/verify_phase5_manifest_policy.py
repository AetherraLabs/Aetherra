#!/usr/bin/env python3
"""Verify Phase 5 bundle manifest policy constraints.

Policy checks:
- Bundle summary JSON exists and includes release_manifest metadata.
- Release manifest generation step completed successfully.
- Optional: signature must be present (for production enforcement).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("expected top-level JSON object")
    return data


def verify_policy(summary_path: Path, require_signature: bool = False) -> tuple[bool, str]:
    if not summary_path.exists():
        return False, f"summary_missing: {summary_path}"

    try:
        payload = _load_json(summary_path)
    except Exception as exc:
        return False, f"summary_invalid_json: {type(exc).__name__}: {exc}"

    release_manifest = payload.get("release_manifest") or {}
    if not release_manifest:
        return False, "release_manifest_section_missing"

    if not bool(release_manifest.get("enabled", False)):
        return False, "release_manifest_disabled"

    step = release_manifest.get("step") or {}
    if not bool(step.get("ok", False)):
        return False, "release_manifest_step_failed"

    manifest_path = Path(str(release_manifest.get("path", "")).strip())
    if not manifest_path or not manifest_path.exists():
        return False, "release_manifest_file_missing"

    if require_signature:
        if not bool(release_manifest.get("signature_exists", False)):
            return False, "release_manifest_signature_missing"
        if not release_manifest.get("signature_sha256"):
            return False, "release_manifest_signature_hash_missing"

    return True, "ok"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Verify phase5 release manifest policy")
    p.add_argument("--summary", required=True, help="Path to phase5 bundle summary JSON")
    p.add_argument(
        "--require-signature",
        action="store_true",
        help="Fail unless release-manifest signature is present",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    ok, reason = verify_policy(
        summary_path=Path(args.summary),
        require_signature=bool(args.require_signature),
    )
    if ok:
        print("[PHASE5_POLICY][OK] release manifest policy satisfied")
        return 0
    print(f"[PHASE5_POLICY][FAIL] {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

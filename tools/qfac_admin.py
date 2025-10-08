#!/usr/bin/env python
"""
QFAC Admin CLI
 - Show retrieval parity counters and current retrieval policy config
 - Reset retrieval parity counters

Usage examples:
  python tools/qfac_admin.py --show
  python tools/qfac_admin.py --reset

Exit codes:
  0 on success; 1 on unexpected errors.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any, cast


@contextmanager
def _suppress_prints():
    import builtins as _bi

    _orig_print = _bi.print
    try:
        _bi.print = lambda *a, **k: None
        yield
    finally:
        _bi.print = _orig_print


def _load_qfac_instance():
    """Attempt to obtain a QFACMemorySystem instance.

    Strategy:
    - Import class and create a lightweight instance for inspection.
    - If creation fails, return None (callers must handle).
    """
    import os as _os

    # By default, run in safe mode to avoid background prints from live init.
    # Set AETHERRA_QFAC_ADMIN_ENABLE_LIVE=1 to opt-in to live instance.
    if _os.getenv("AETHERRA_QFAC_ADMIN_ENABLE_LIVE", "0") not in ("1", "true", "True"):
        return None
    try:
        # Suppress any initialization prints to keep output JSON-only, including
        # potential prints during module import.
        buf = io.StringIO()
        import time as _time

        with (
            contextlib.redirect_stdout(buf),
            contextlib.redirect_stderr(buf),
            _suppress_prints(),
        ):
            from Aetherra.aetherra_core.memory.qfac_integration import (
                QFACMemorySystem,
            )

            inst = QFACMemorySystem("_qfac_admin_probe")
            # Allow any immediate async prints to flush while still redirected
            _time.sleep(0.05)
            return inst
    except Exception:
        return None


def do_show() -> dict[str, Any]:
    inst = _load_qfac_instance()
    if inst is None:
        # Safe defaults if unavailable
        return {
            "available": False,
            "retrieval_policy": {"threshold": 0.0, "parity_enabled": 0},
            "parity_counters": {
                "total": 0,
                "top1_match": 0,
                "any_rank_mismatch": 0,
                "threshold_dropped": 0,
            },
            "parity_by_k": {"1": 0, "3": 0, "5": 0, "10": 0},
        }

    try:
        cfg = inst.get_retrieval_policy_config_snapshot()
    except Exception:
        cfg = {"threshold": 0.0, "parity_enabled": 0}

    try:
        parity = inst.get_retrieval_parity_metrics_snapshot()
    except Exception:
        parity = {
            "total": 0,
            "top1_match": 0,
            "any_rank_mismatch": 0,
            "threshold_dropped": 0,
        }

    # Optional per-k parity breakdown (top-k match counts); prefer dedicated snapshot if present
    parity_by_k: dict[str, int] = {"1": 0, "3": 0, "5": 0, "10": 0}
    try:
        preferred_keys = ("1", "3", "5", "10")
        if hasattr(inst, "get_retrieval_parity_by_k_snapshot"):
            pbk = inst.get_retrieval_parity_by_k_snapshot()
            if isinstance(pbk, dict):
                mpbk: Mapping[object, Any] = cast(Mapping[object, Any], pbk)
                for k in preferred_keys:
                    v = mpbk.get(int(k))
                    if v is None:
                        v = mpbk.get(k)
                    if isinstance(v, int | float):
                        parity_by_k[k] = int(v)
        elif isinstance(parity, dict):
            pbk2 = parity.get("parity_by_k")
            if isinstance(pbk2, dict):
                mpbk2: Mapping[object, Any] = cast(Mapping[object, Any], pbk2)
                for k in preferred_keys:
                    v = mpbk2.get(int(k))
                    if v is None:
                        v = mpbk2.get(k)
                    if isinstance(v, int | float):
                        parity_by_k[k] = int(v)
    except Exception as exc:
        # Keep defaults on any issues
        import logging as _log

        _log.debug("qfac_admin: parity_by_k extraction failed: %s", exc)

    return {
        "available": True,
        "retrieval_policy": cfg,
        "parity_counters": parity,
        "parity_by_k": parity_by_k,
    }


def do_reset() -> dict[str, Any]:
    inst = _load_qfac_instance()
    if inst is None:
        return {"ok": False, "reason": "qfac unavailable"}
    try:
        inst.reset_retrieval_parity_counters()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main(argv: list[str] | None = None) -> int:
    # Ensure quiet mode where supported by QFAC components
    import os

    os.environ.setdefault("AETHERRA_QUIET", "1")

    p = argparse.ArgumentParser(description="QFAC Admin CLI")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--show", action="store_true", help="Show policy and parity counters"
    )
    g.add_argument("--reset", action="store_true", help="Reset parity counters")

    args = p.parse_args(argv)
    # Suppress any noise emitted during execution by swapping process I/O
    noise = io.StringIO()
    real_stdout, real_stderr = sys.stdout, sys.stderr
    import time as _time

    try:
        sys.stdout = noise
        sys.stderr = noise
        with _suppress_prints():
            if args.show:
                data = do_show()
                out = json.dumps(data, indent=2)
            elif args.reset:
                res = do_reset()
                out = json.dumps(res, indent=2)
            else:
                out = json.dumps({"ok": False, "error": "no-op"})
            _time.sleep(0.05)
    finally:
        sys.stdout = real_stdout
        sys.stderr = real_stderr
    print(out)
    if args.reset:
        return 0 if res.get("ok") else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

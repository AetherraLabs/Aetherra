#!/usr/bin/env python3
"""Generate Self-Inc Production Readiness doc from metadata.

Usage:
  python tools/generate_selfinc_readiness_doc.py --meta metadata/selfinc_readiness.json --out docs/SELFINC_PRODUCTION_READINESS.md

Idempotent: overwrites output file.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from textwrap import dedent


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    col_widths = [
        max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)
    ]

    def fmt_row(cells: list[str]) -> str:
        return (
            "| "
            + " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(cells))
            + " |"
        )

    lines = [fmt_row(headers), fmt_row(["-" * w for w in col_widths])] + [
        fmt_row(r) for r in rows
    ]
    return "\n" + "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", default="metadata/selfinc_readiness.json")
    ap.add_argument("--out", default="docs/SELFINC_PRODUCTION_READINESS.md")
    args = ap.parse_args()

    meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))

    title = meta["title"]
    date = meta.get("date", datetime.utcnow().date().isoformat())
    status = meta.get("status", "Unknown")
    owner = meta.get("owner", "Unassigned")

    dim_rows = [
        [d["name"], d["outcome"], d["notes"]] for d in meta.get("dimensions", [])
    ]
    env_rows = [
        [e["var"], e["required"], e["purpose"], e["auto"]]
        for e in meta.get("env_matrix", [])
    ]
    api_rows = [
        [e["path"], e["method"], e["auth"], e["shape"]]
        for e in meta.get("api_endpoints", [])
    ]
    risk_rows = [
        [r["risk"], r["likelihood"], r["impact"], r["mitigation"]]
        for r in meta.get("risks", [])
    ]

    phase2_list = "\n".join(f"- {item}" for item in meta.get("phase2_items", []))

    doc = (
        dedent(f"""
    # {title}

    Date: {date}
    Status: {status}
    Owner: {owner}

    ---
    ## 1. Snapshot

    This document is generated from structured metadata (`{args.meta}`). Edit the JSON to update.

    ---
    ## 2. Validation Dimensions
    {render_table(["Dimension", "Outcome", "Notes"], dim_rows)}
    ---
    ## 3. Environment Variables
    {render_table(["Variable", "Required", "Purpose", "Auto-Remediation"], env_rows)}
    ---
    ## 4. HTTP API (Subset)
    {render_table(["Endpoint", "Method", "Auth", "Shape"], api_rows)}
    ---
    ## 5. Risk Register
    {render_table(["Risk", "Likelihood", "Impact", "Mitigation"], risk_rows)}
    ---
    ## 6. Phase 2 Items
    {phase2_list}

    ---
    Generated: {datetime.utcnow().isoformat()}Z
    """).strip()
        + "\n"
    )

    Path(args.out).write_text(doc, encoding="utf-8")
    print(f"[OK] Wrote {args.out} from {args.meta}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Safe ingest pipeline: Stage -> Validate -> Dedup -> Generate ingest script (.aether) -> Optionally run

import argparse
import hashlib
import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = WORKSPACE_ROOT / "docs" / "schemas" / "memory_item.schema.json"
AETHER_RUNNER = WORKSPACE_ROOT / "tools" / "run_aether_script.py"

RE_BLOCKED = re.compile(r"(ssn|social\s*security|credit\s*card|\b\d{16}\b)", re.I)


def load_schema() -> dict[str, Any]:
    if not SCHEMA_PATH.exists():
        return {}
    data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return dict(data) if isinstance(data, dict) else {}


def basic_validate(item: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    required = schema.get("required", [])
    for k in required:
        if k not in item:
            errs.append(f"missing:{k}")
    # minimal type checks
    if "confidence" in item:
        try:
            c = float(item["confidence"])
            if c < 0 or c > 1:
                errs.append("confidence_out_of_range")
        except Exception:
            errs.append("confidence_not_number")
    # Safety: simple PII/forbidden patterns
    blob = (item.get("title", "") + "\n" + item.get("body", "")).lower()
    if RE_BLOCKED.search(blob):
        errs.append("blocked_tokens")
    return errs


def compute_hash(item: dict[str, Any]) -> str:
    h = hashlib.sha256()
    h.update(
        (item.get("title", "") + "\n" + item.get("body", "")).encode(
            "utf-8", errors="ignore"
        )
    )
    return h.hexdigest()


def scan_folder(folder: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for p in folder.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix.lower() in (".json",):
            try:
                docs.extend(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                try:
                    obj = json.loads(p.read_text(encoding="utf-8"))
                    if isinstance(obj, dict):
                        docs.append(obj)
                except Exception as exc:
                    logging.debug("Skipping unreadable JSON file %s: %s", p, exc)
        elif p.suffix.lower() in (".md", ".txt"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            item = {
                "id": str(p),
                "type": "knowledge",
                "title": p.stem,
                "body": text[:10000],
                "tags": ["import"],
                "source": str(p),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "confidence": 0.7,
            }
            docs.append(item)
    return docs


def dedup_items(
    items: list[dict[str, Any]], threshold: float = 0.92
) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    out: list[dict[str, Any]] = []
    for it in items:
        h = compute_hash(it)
        if h in seen:
            # near-duplicate skip
            continue
        it["hash"] = h
        seen[h] = it
        out.append(it)
    return out


def generate_aether(items: list[dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Create a simple .aether that calls memory.ingest for each item
    lines = ["goal: Safe Ingest", "policy_set: default"]
    for it in items:
        # Compact JSON to embed
        payload = json.dumps(it, ensure_ascii=False)
        lines.append(f"memory.ingest: {payload}")
    content = "\n".join(lines) + "\n"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def run_aether(script_path: Path) -> int:
    if not AETHER_RUNNER.exists():
        print(
            "[WARN] tools/run_aether_script.py not found; cannot auto-run. Returning 0."
        )
        return 0
    proc = subprocess.run(
        [sys.executable, str(AETHER_RUNNER), str(script_path)], cwd=str(WORKSPACE_ROOT)
    )
    return proc.returncode


def main():
    p = argparse.ArgumentParser("Safe ingest pipeline")
    p.add_argument("folder", help="Folder to ingest from")
    p.add_argument(
        "--out",
        default=str(WORKSPACE_ROOT / "workflows" / "ingest_safe_generated.aether"),
    )
    p.add_argument(
        "--run", action="store_true", help="Run the generated .aether immediately"
    )
    p.add_argument(
        "--eval",
        action="store_true",
        help="After successful ingest, run learning evaluator",
    )
    p.add_argument(
        "--testset",
        default=str(WORKSPACE_ROOT / "tests" / "data" / "golden_learning_set.json"),
        help="Path to evaluator golden set",
    )
    args = p.parse_args()

    schema = load_schema()
    items = scan_folder(Path(args.folder))

    staged: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []

    for it in items:
        errs = basic_validate(it, schema)
        if errs:
            it["_errors"] = errs
            bad.append(it)
        else:
            staged.append(it)

    staged = dedup_items(staged)

    # Write staging report
    reports_dir = WORKSPACE_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "ingest_staging.json").write_text(
        json.dumps(
            {"staged": len(staged), "bad": len(bad)}, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )

    # Generate .aether and optionally run
    script_path = generate_aether(staged, Path(args.out))
    print(f"Generated: {script_path}")
    if args.run:
        code = run_aether(script_path)
        print(f"Runner exit code: {code}")
        # Post-eval: run KPIs when ingest succeeded
        if code == 0 and args.eval:
            eval_cmd = [
                sys.executable,
                str(WORKSPACE_ROOT / "tools" / "learning_evaluator.py"),
                args.testset,
            ]
            print("Running learning evaluator...")
            subprocess.run(eval_cmd, cwd=str(WORKSPACE_ROOT))


if __name__ == "__main__":
    main()

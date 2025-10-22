#!/usr/bin/env python3
# Daily teacher stub: extract Q&A pairs and summarize into knowledge notes.

import argparse
import json
import time
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def extract_pairs(_period: str = "last_24h") -> list[dict[str, Any]]:
    # Placeholder: pull from logs if available later
    return []


def summarize_pairs(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for i, p in enumerate(pairs):
        notes.append(
            {
                "id": f"note_{int(time.time())}_{i}",
                "type": "note",
                "title": p.get("q", "What I learned"),
                "body": p.get("a", ""),
                "tags": ["learned_today"],
                "source": "daily_teacher",
                "created_at": now,
                "confidence": 0.6,
            }
        )
    return notes


def main():
    p = argparse.ArgumentParser("Daily teacher stub")
    p.add_argument(
        "--output", default=str(WORKSPACE_ROOT / "staging" / "daily_teacher_notes.json")
    )
    args = p.parse_args()

    pairs = extract_pairs("last_24h")
    notes = summarize_pairs(pairs)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(notes)} notes to {out}")


if __name__ == "__main__":
    main()

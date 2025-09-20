# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Alerts CLI: view recent security alerts or follow the live alerts feed.

Usage examples (PowerShell):
  python -m Aetherra.cli.alerts --recent 30
  python -m Aetherra.cli.alerts --follow

By default, reads from ./.aetherra/security/alerts.jsonl in the current workspace.
You can override with --path.
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Iterable


def _iter_jsonl(path: Path) -> Iterable[dict]:
    if not path.exists():
        return
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def print_alert(alert: dict):
    ts = alert.get("timestamp")
    sev = alert.get("severity", "info").upper()
    msg = alert.get("alert") or alert
    print(f"[{sev}] {ts}: {msg}")


def tail_file(path: Path, sleep_sec: float = 1.0):
    # Simple polling tail; robust on Windows
    last_size = path.stat().st_size if path.exists() else 0
    try:
        while True:
            if path.exists():
                size = path.stat().st_size
                if size < last_size:
                    # rotated/truncated
                    last_size = 0
                if size > last_size:
                    try:
                        with path.open("r", encoding="utf-8") as f:
                            f.seek(last_size)
                            for line in f:
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    print_alert(json.loads(line))
                                except Exception:
                                    continue
                        last_size = size
                    except Exception:
                        pass
            time.sleep(sleep_sec)
    except KeyboardInterrupt:
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aetherra Alerts CLI")
    parser.add_argument(
        "--path",
        type=str,
        default=str(Path(".aetherra") / "security" / "alerts.jsonl"),
        help="Path to alerts.jsonl (default: ./.aetherra/security/alerts.jsonl)",
    )
    parser.add_argument("--recent", type=int, default=20, help="Show last N alerts")
    parser.add_argument(
        "--follow", action="store_true", help="Follow the alerts feed (tail)"
    )

    args = parser.parse_args(argv)
    path = Path(args.path)

    # Print recent alerts
    if path.exists():
        alerts = list(_iter_jsonl(path))
        for a in alerts[-args.recent :]:
            print_alert(a)
    else:
        print(f"No alerts file found at: {path}")

    # Follow if requested
    if args.follow:
        print(f"Following alerts: {path} (Ctrl+C to stop)")
        tail_file(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

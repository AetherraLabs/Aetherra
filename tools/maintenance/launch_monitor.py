#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra OS Monitor Launcher
---------------------------
Thin wrapper around aetherra_live_monitor for convenience.

Usage:
  python launch_monitor.py           # one-shot snapshot
  python launch_monitor.py --watch 5 # refresh every 5 seconds
"""

import argparse


def main(argv=None) -> int:
    from aetherra_live_monitor import monitor_aetherra_activity

    parser = argparse.ArgumentParser(description="Launch Aetherra OS Live Monitor")
    parser.add_argument(
        "--watch",
        "-w",
        type=int,
        default=0,
        help="Refresh every N seconds (0 = one-shot)",
    )
    args = parser.parse_args(argv)

    # Delegate to the real monitor
    monitor_aetherra_activity(args.watch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

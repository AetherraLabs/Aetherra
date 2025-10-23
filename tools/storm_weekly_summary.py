#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
STORM Shadow Mode Weekly Summary Generator

Analyzes STORM metrics trends over the week and generates a comprehensive
summary report for Phase 1 monitoring.

Usage:
    python tools/storm_weekly_summary.py              # This week's summary
    python tools/storm_weekly_summary.py --save       # Save to file
    python tools/storm_weekly_summary.py --readiness  # Check Phase 2 readiness
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Missing dependency: requests")
    print("Install with: pip install requests")
    sys.exit(1)


def generate_weekly_summary(hub_url: str = "http://localhost:3001") -> str:
    """Generate weekly monitoring summary"""

    report = []
    report.append("=" * 80)
    report.append("STORM SHADOW MODE - WEEKLY SUMMARY")
    report.append(f"Week ending: {datetime.now().strftime('%Y-%m-%d')}")
    report.append("=" * 80)
    report.append("")

    # Check Hub health
    try:
        r = requests.get(f"{hub_url}/health", timeout=5)
        hub_healthy = r.status_code == 200
    except requests.RequestException:
        hub_healthy = False

    report.append(f"Current Hub Status: {'✅ HEALTHY' if hub_healthy else '❌ DOWN'}")
    report.append("")

    if not hub_healthy:
        report.append("⚠️  Hub is not responding. Cannot generate summary.")
        return "\n".join(report)

    # Get metrics
    try:
        r = requests.get(f"{hub_url}/metrics", timeout=5)
        r.raise_for_status()
        metrics_text = r.text
    except requests.RequestException as e:
        report.append(f"❌ Failed to fetch metrics: {e}")
        return "\n".join(report)

    # Check for STORM metrics
    storm_lines = [
        line
        for line in metrics_text.split("\n")
        if "storm" in line.lower() and not line.startswith("#")
    ]

    if not storm_lines:
        report.append("⚠️  STORM METRICS NOT YET VISIBLE")
        report.append("")
        report.append("This is expected during the initial deployment period.")
        report.append("STORM metrics will appear once the system:")
        report.append("  1. Processes recall operations with storm_hybrid strategy")
        report.append("  2. Begins shadow mode comparisons")
        report.append("  3. Collects sufficient data for reporting")
        report.append("")
        report.append("RECOMMENDED ACTIONS:")
        report.append(
            "  • Ensure production traffic is using storm_hybrid recall strategy"
        )
        report.append("  • Monitor daily with: python tools/monitor_storm_shadow.py")
        report.append(
            "  • Check metrics endpoint: curl http://localhost:3001/metrics | grep storm"
        )
        report.append("")
        report.append(
            "Expected timeline: Metrics should appear within 24-48 hours of deployment"
        )
        return "\n".join(report)

    report.append(f"📊 STORM Metrics Active: {len(storm_lines)} data points")
    report.append("")

    # TODO: Once metrics are available, add trend analysis
    # - Daily agreement rate trend
    # - Error rate over time
    # - Latency percentiles
    # - Sheaf inconsistency trends

    report.append("WEEK SUMMARY:")
    report.append("-" * 80)
    report.append("(Summary will be populated once metrics are available)")
    report.append("")

    report.append("PHASE 2 READINESS CHECKLIST:")
    report.append("-" * 80)
    report.append("[ ] Shadow error rate < 1% (stable)")
    report.append("[ ] STORM latency p95 < 500ms (within threshold)")
    report.append("[ ] Agreement rate > 80% (STORM and baseline align)")
    report.append("[ ] No production impact (baseline serving correctly)")
    report.append("[ ] Metrics collecting properly (all 13 STORM series visible)")
    report.append("[ ] No security incidents (audit logs clean)")
    report.append("[ ] No user complaints (transparent operation)")
    report.append("")

    report.append("NEXT STEPS:")
    report.append("-" * 80)
    report.append("• Continue daily monitoring with monitor_storm_shadow.py")
    report.append("• Review metrics trends weekly")
    report.append("• After 2 weeks, evaluate Phase 2 readiness")
    report.append("• If criteria met: Proceed to Phase 2 (Hybrid Mode)")
    report.append("")

    report.append("=" * 80)

    return "\n".join(report)


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate STORM weekly summary")
    parser.add_argument(
        "--hub-url",
        default="http://localhost:3001",
        help="Hub server URL",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save summary to file (e.g., reports/week1_summary.md)",
    )
    parser.add_argument(
        "--readiness",
        action="store_true",
        help="Focus on Phase 2 readiness check",
    )

    args = parser.parse_args()

    summary = generate_weekly_summary(args.hub_url)

    print(summary)

    if args.save:
        output_path = Path(args.save)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary)
        print(f"\n📝 Summary saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

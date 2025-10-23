#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
STORM Shadow Mode Monitoring Tool

Monitors STORM shadow mode deployment metrics and generates health reports.
Use this daily during Phase 1 (2-week shadow period) to track:
- Agreement rates
- Error rates
- Latency performance
- Sheaf inconsistency

Usage:
    python tools/monitor_storm_shadow.py              # Daily report
    python tools/monitor_storm_shadow.py --detailed   # Detailed metrics
    python tools/monitor_storm_shadow.py --check      # Quick health check
    python tools/monitor_storm_shadow.py --alert      # Check alert thresholds
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("❌ Missing dependency: requests")
    print("Install with: pip install requests")
    sys.exit(1)


class STORMMonitor:
    """Monitor STORM shadow mode deployment"""

    def __init__(self, hub_url: str = "http://localhost:3001"):
        self.hub_url = hub_url
        self.metrics_url = f"{hub_url}/metrics"
        self.status_url = f"{hub_url}/api/memory/status"
        self.health_url = f"{hub_url}/health"

    def get_metrics(self) -> dict[str, Any]:
        """Fetch metrics from Hub"""
        try:
            r = requests.get(self.metrics_url, timeout=5)
            r.raise_for_status()
            return self._parse_prometheus_metrics(r.text)
        except requests.RequestException as e:
            print(f"❌ Failed to fetch metrics: {e}")
            return {}

    def get_status(self) -> dict[str, Any]:
        """Fetch STORM status from Hub"""
        try:
            r = requests.get(self.status_url, timeout=5)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"❌ Failed to fetch status: {e}")
            return {}

    def check_health(self) -> bool:
        """Check if Hub is healthy"""
        try:
            r = requests.get(self.health_url, timeout=5)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def _parse_prometheus_metrics(self, text: str) -> dict[str, Any]:
        """Parse Prometheus metrics format"""
        metrics = {}
        for line in text.split("\n"):
            if not line or line.startswith("#"):
                continue

            # Simple parser for metric_name{labels} value
            if "{" in line:
                # Has labels
                parts = line.split("{")
                name = parts[0]
                rest = parts[1].split("}")
                labels_str = rest[0]
                value_str = rest[1].strip()

                # Parse labels
                labels = {}
                for label_pair in labels_str.split(","):
                    if "=" in label_pair:
                        k, v = label_pair.split("=", 1)
                        labels[k.strip()] = v.strip().strip('"')

                # Store with labels
                if name not in metrics:
                    metrics[name] = []
                metrics[name].append({"labels": labels, "value": float(value_str)})
            else:
                # No labels
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    value = float(parts[1])
                    metrics[name] = value

        return metrics

    def calculate_agreement_rate(self, metrics: dict[str, Any]) -> float | None:
        """Calculate STORM shadow agreement rate"""
        comparisons = metrics.get("storm_shadow_comparisons_total", [])
        if isinstance(comparisons, list):
            agreed = 0
            disagreed = 0
            for metric in comparisons:
                labels = metric.get("labels", {})
                value = metric.get("value", 0)
                if labels.get("agreed") == "true":
                    agreed += value
                elif labels.get("agreed") == "false":
                    disagreed += value

            total = agreed + disagreed
            if total > 0:
                return agreed / total
        return None

    def get_error_rate(self, metrics: dict[str, Any]) -> float:
        """Get STORM shadow error count"""
        errors = metrics.get("storm_shadow_errors_total", 0)
        if isinstance(errors, list):
            return sum(m.get("value", 0) for m in errors)
        return float(errors)

    def get_recall_latency_p95(self, metrics: dict[str, Any]) -> float | None:
        """Get p95 recall latency"""
        latencies = metrics.get("storm_recall_latency_seconds", [])
        if isinstance(latencies, list):
            for metric in latencies:
                if metric.get("labels", {}).get("quantile") == "0.95":
                    return metric.get("value", 0) * 1000  # Convert to ms
        return None

    def get_sheaf_inconsistency(self, metrics: dict[str, Any]) -> float:
        """Get current sheaf inconsistency"""
        inconsistency = metrics.get("storm_sheaf_inconsistency", 0)
        if isinstance(inconsistency, list):
            return max(m.get("value", 0) for m in inconsistency)
        return float(inconsistency)

    def get_recalls_total(self, metrics: dict[str, Any]) -> int:
        """Get total STORM recalls"""
        recalls = metrics.get("storm_recalls_total", 0)
        if isinstance(recalls, list):
            return int(sum(m.get("value", 0) for m in recalls))
        return int(recalls)

    def generate_daily_report(self) -> str:
        """Generate daily monitoring report"""
        report = []
        report.append("=" * 70)
        report.append(
            f"STORM Shadow Mode Daily Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report.append("=" * 70)
        report.append("")

        # Check Hub health
        healthy = self.check_health()
        report.append(f"Hub Status: {'✅ HEALTHY' if healthy else '❌ DOWN'}")

        if not healthy:
            report.append("\n⚠️  Hub is not responding. Cannot collect metrics.")
            return "\n".join(report)

        report.append("")

        # Get metrics
        metrics = self.get_metrics()

        if not metrics:
            report.append("⚠️  No metrics available")
            return "\n".join(report)

        # Check for STORM metrics
        storm_metrics = [k for k in metrics.keys() if "storm" in k.lower()]
        if not storm_metrics:
            report.append("⚠️  STORM metrics not yet visible")
            report.append("This is expected during initial deployment.")
            report.append("Metrics will appear after STORM processes recalls.")
            return "\n".join(report)

        report.append(f"📊 STORM Metrics Found: {len(storm_metrics)} series\n")

        # Key Metrics
        report.append("KEY METRICS:")
        report.append("-" * 70)

        # Recalls
        recalls = self.get_recalls_total(metrics)
        report.append(f"Total STORM Recalls:        {recalls:>10,}")

        # Agreement rate
        agreement = self.calculate_agreement_rate(metrics)
        if agreement is not None:
            status = "✅" if agreement >= 0.8 else "⚠️" if agreement >= 0.7 else "❌"
            report.append(
                f"Shadow Agreement Rate:      {agreement:>10.1%} {status} (target: >80%)"
            )
        else:
            report.append("Shadow Agreement Rate:      N/A (no comparisons yet)")

        # Error rate
        errors = self.get_error_rate(metrics)
        error_rate = (errors / recalls * 100) if recalls > 0 else 0
        status = "✅" if error_rate < 1.0 else "❌"
        report.append(
            f"Shadow Error Count:         {int(errors):>10} {status} (target: <1%)"
        )
        if recalls > 0:
            report.append(f"Shadow Error Rate:          {error_rate:>10.2f}%")

        # Latency
        latency_p95 = self.get_recall_latency_p95(metrics)
        if latency_p95 is not None:
            status = "✅" if latency_p95 < 500 else "⚠️" if latency_p95 < 600 else "❌"
            report.append(
                f"Recall Latency (p95):       {latency_p95:>10.1f}ms {status} (target: <500ms)"
            )
        else:
            report.append("Recall Latency (p95):       N/A")

        # Sheaf inconsistency
        inconsistency = self.get_sheaf_inconsistency(metrics)
        status = "✅" if inconsistency < 0.3 else "⚠️" if inconsistency < 0.5 else "❌"
        report.append(
            f"Sheaf Inconsistency:        {inconsistency:>10.3f} {status} (target: <0.3)"
        )

        report.append("")

        # Success criteria check
        report.append("SUCCESS CRITERIA CHECK:")
        report.append("-" * 70)

        criteria_met = []
        criteria_failed = []

        if agreement is not None and agreement >= 0.8:
            criteria_met.append("✅ Agreement rate >80%")
        elif agreement is not None:
            criteria_failed.append(f"❌ Agreement rate {agreement:.1%} (need >80%)")
        else:
            criteria_met.append("⏳ Agreement rate (pending data)")

        if error_rate < 1.0:
            criteria_met.append("✅ Error rate <1%")
        else:
            criteria_failed.append(f"❌ Error rate {error_rate:.2f}% (need <1%)")

        if latency_p95 is not None and latency_p95 < 500:
            criteria_met.append("✅ Latency p95 <500ms")
        elif latency_p95 is not None:
            criteria_failed.append(f"❌ Latency p95 {latency_p95:.1f}ms (need <500ms)")
        else:
            criteria_met.append("⏳ Latency p95 (pending data)")

        if inconsistency < 0.3:
            criteria_met.append("✅ Sheaf inconsistency <0.3")
        else:
            criteria_failed.append(
                f"❌ Sheaf inconsistency {inconsistency:.3f} (need <0.3)"
            )

        for criterion in criteria_met:
            report.append(criterion)
        for criterion in criteria_failed:
            report.append(criterion)

        report.append("")

        # Overall status
        if len(criteria_failed) == 0:
            report.append("🎉 ALL SUCCESS CRITERIA MET - Ready for Phase 2")
        elif recalls < 100:
            report.append("⏳ Collecting data... (need more samples for validation)")
        else:
            report.append("⚠️  Some criteria not met - continue monitoring")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def check_alerts(self) -> list[str]:
        """Check if any alert thresholds are exceeded"""
        alerts = []

        if not self.check_health():
            alerts.append("🚨 CRITICAL: Hub is down")
            return alerts

        metrics = self.get_metrics()
        if not metrics:
            return alerts

        # Critical alerts
        error_rate_total = self.get_error_rate(metrics)
        recalls_total = self.get_recalls_total(metrics)
        if recalls_total > 0:
            error_rate = error_rate_total / recalls_total
            if error_rate > 0.01:
                alerts.append(
                    f"🚨 CRITICAL: Shadow error rate {error_rate:.1%} (threshold: 1%)"
                )

        inconsistency = self.get_sheaf_inconsistency(metrics)
        if inconsistency > 0.5:
            alerts.append(
                f"🚨 CRITICAL: Sheaf inconsistency {inconsistency:.3f} (threshold: 0.5)"
            )

        # Warning alerts
        agreement = self.calculate_agreement_rate(metrics)
        if agreement is not None and agreement < 0.7:
            alerts.append(
                f"⚠️  WARNING: Agreement rate {agreement:.1%} (threshold: 70%)"
            )

        latency_p95 = self.get_recall_latency_p95(metrics)
        if latency_p95 is not None and latency_p95 > 400:
            alerts.append(
                f"⚠️  WARNING: Latency p95 {latency_p95:.1f}ms (threshold: 400ms)"
            )

        return alerts


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Monitor STORM shadow mode deployment")
    parser.add_argument(
        "--hub-url",
        default="http://localhost:3001",
        help="Hub server URL (default: http://localhost:3001)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed metrics breakdown",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Quick health check only",
    )
    parser.add_argument(
        "--alert",
        action="store_true",
        help="Check alert thresholds only",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save report to file",
    )

    args = parser.parse_args()

    monitor = STORMMonitor(args.hub_url)

    # Quick health check
    if args.check:
        healthy = monitor.check_health()
        if healthy:
            print("✅ Hub is healthy")
            metrics = monitor.get_metrics()
            storm_metrics = [k for k in metrics.keys() if "storm" in k.lower()]
            if storm_metrics:
                print(f"📊 {len(storm_metrics)} STORM metrics visible")
            else:
                print("⚠️  STORM metrics not yet visible")
            return 0
        print("❌ Hub is down")
        return 1

    # Alert check
    if args.alert:
        alerts = monitor.check_alerts()
        if alerts:
            print("ACTIVE ALERTS:")
            print("-" * 70)
            for alert in alerts:
                print(alert)
            return 1
        print("✅ No alerts - all thresholds within limits")
        return 0

    # Generate report
    report = monitor.generate_daily_report()

    # Output
    if args.json:
        metrics = monitor.get_metrics()
        data = {
            "timestamp": datetime.now().isoformat(),
            "hub_healthy": monitor.check_health(),
            "metrics": metrics,
            "agreement_rate": monitor.calculate_agreement_rate(metrics),
            "error_rate": monitor.get_error_rate(metrics),
            "latency_p95_ms": monitor.get_recall_latency_p95(metrics),
            "sheaf_inconsistency": monitor.get_sheaf_inconsistency(metrics),
            "recalls_total": monitor.get_recalls_total(metrics),
        }
        print(json.dumps(data, indent=2))
    else:
        print(report)

    # Save to file
    if args.save:
        output_path = Path(args.save)
        output_path.write_text(report)
        print(f"\n📝 Report saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Report locally exposed metrics without making requests at import time."""

# Standard library imports
import sys

# Third party imports
import requests


def main() -> int:
    try:
        response = requests.get(
            "http://127.0.0.1:3001/metrics", timeout=5, allow_redirects=False
        )
    except requests.RequestException as exc:
        print(f"Metrics request failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    if response.status_code != 200:
        print(f"Metrics request failed: HTTP {response.status_code}", file=sys.stderr)
        return 1

    lines = [
        line
        for line in map(str.strip, response.text.splitlines())
        if line and not line.startswith("#")
    ]
    print(f"Total metrics: {len(lines)}\n")
    metrics_by_prefix: dict[str, int] = {}
    for line in lines:
        metric_name = line.split("{", 1)[0].split()[0]
        prefix = metric_name.split("_", 1)[0]
        metrics_by_prefix[prefix] = metrics_by_prefix.get(prefix, 0) + 1
    print("Metrics by prefix:")
    for prefix, count in sorted(metrics_by_prefix.items()):
        print(f"  {prefix:20s}: {count:3d} metrics")

    storm_metrics = [line for line in lines if "storm" in line.lower()]
    if storm_metrics:
        print(f"\nFound {len(storm_metrics)} STORM metrics:")
        for metric in storm_metrics[:10]:
            print(f"  {metric}")
    else:
        print("\nNo STORM metrics found")
    aetherra_metrics = [line for line in lines if line.startswith("aetherra_")]
    print(f"\nFound {len(aetherra_metrics)} aetherra_ metrics")
    if aetherra_metrics:
        print("First 10:")
        for metric in aetherra_metrics[:10]:
            print(f"  {metric}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Check what metrics are exposed"""

import requests

r = requests.get("http://localhost:3001/metrics")
lines = [l for l in r.text.split("\n") if l and not l.startswith("#")]

print(f"Total metrics: {len(lines)}\n")

# Group by prefix
metrics_by_prefix = {}
for line in lines:
    parts = line.split("{")
    if parts:
        metric_name = parts[0]
        prefix = metric_name.split("_")[0] if "_" in metric_name else metric_name
        if prefix not in metrics_by_prefix:
            metrics_by_prefix[prefix] = []
        metrics_by_prefix[prefix].append(metric_name)

print("Metrics by prefix:")
for prefix in sorted(metrics_by_prefix.keys()):
    count = len(metrics_by_prefix[prefix])
    print(f"  {prefix:20s}: {count:3d} metrics")

# Check for STORM metrics specifically
storm_metrics = [l for l in lines if "storm" in l.lower()]
if storm_metrics:
    print(f"\n🎯 Found {len(storm_metrics)} STORM metrics:")
    for m in storm_metrics[:10]:
        print(f"  {m}")
else:
    print("\n⚠️  No STORM metrics found")

# Check for aetherra metrics
aetherra_metrics = [l for l in lines if l.startswith("aetherra_")]
print(f"\n📊 Found {len(aetherra_metrics)} aetherra_ metrics")
if aetherra_metrics:
    print("First 10:")
    for m in aetherra_metrics[:10]:
        print(f"  {m}")

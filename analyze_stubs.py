import json
from collections import defaultdict
from pathlib import Path

with open("STUB_INVENTORY.json") as f:
    data = json.load(f)

stubs = data["stubs"]

# Group by type
by_type = defaultdict(int)
for stub in stubs:
    by_type[stub["type"]] += 1

# Group by directory (for core Aetherra files only)
by_dir = defaultdict(int)
for stub in stubs:
    if "dist" in stub["file"] or "archive" in stub["file"] or "demos" in stub["file"]:
        continue  # Skip bundled/archived code
    if "Aetherra" in stub["file"] or "aetherra_" in stub["file"].strip("/"):
        parent = str(Path(stub["file"]).parent)
        by_dir[parent] += 1

# Sort and display
print("📊 STUB INVENTORY SUMMARY")
print("=" * 60)
print(f"\n🎯 Total Stubs Found: {data['total']}")

print("\n📋 By Type:")
for stub_type in sorted(by_type.keys()):
    count = by_type[stub_type]
    pct = round(100 * count / data["total"], 1)
    print(f"   {stub_type:30s} : {count:4d} ({pct:5.1f}%)")

print("\n📁 Top Core Aetherra Modules (by stub count):")
for directory in sorted(by_dir.items(), key=lambda x: -x[1])[:15]:
    print(f"   {directory[0]:50s} : {directory[1]:3d}")

print("\n✅ Stub inventory saved to: STUB_INVENTORY.json")

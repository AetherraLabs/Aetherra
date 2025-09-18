#!/usr/bin/env python3
import csv
import subprocess
import sys

# Read CSV and extract all unique labels
labels = set()
with open("aetherra_selfinc_issues.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        label_list = row["labels"].strip()
        if label_list:
            for label in label_list.split(","):
                labels.add(label.strip())

# Define label colors and descriptions
label_config = {
    # Phase labels
    "phase:1": {
        "color": "0e8a16",
        "description": "Self-Incorporation Phase 1 - Core Infrastructure",
    },
    "phase:2": {
        "color": "fbca04",
        "description": "Self-Incorporation Phase 2 - Advanced Features",
    },
    "phase:3": {
        "color": "d73a49",
        "description": "Self-Incorporation Phase 3 - Learning & Autonomy",
    },
    # Area labels
    "area:kernel": {
        "color": "5319e7",
        "description": "Kernel loop and core OS integration",
    },
    "area:indexing": {
        "color": "0075ca",
        "description": "Code discovery and indexing systems",
    },
    "area:classifier": {
        "color": "7057ff",
        "description": "Heuristic and ML-based classification",
    },
    "area:security": {
        "color": "d73a49",
        "description": "Safety gates and security validation",
    },
    "area:planning": {
        "color": "a2eeef",
        "description": "Integration planning and dependency analysis",
    },
    "area:integration": {
        "color": "0e8a16",
        "description": "Component integration and registration",
    },
    "area:ethics": {
        "color": "f9d0c4",
        "description": "Ethics and audit logging systems",
    },
    "area:observability": {
        "color": "1d76db",
        "description": "Metrics, monitoring, and status APIs",
    },
    "area:testing": {
        "color": "c5def5",
        "description": "Test automation and validation",
    },
    "area:maintenance": {
        "color": "fef2c0",
        "description": "Background maintenance and optimization",
    },
    "area:ui": {"color": "e99695", "description": "User interface and visualization"},
    "area:apis": {"color": "bfd4f2", "description": "REST APIs and control interfaces"},
    "area:quality": {
        "color": "d4c5f9",
        "description": "Code quality and validation gates",
    },
    "area:policy": {
        "color": "f9c2ff",
        "description": "Policy configuration and autonomy controls",
    },
    "area:dx": {"color": "c2e0c6", "description": "Developer experience and tooling"},
    "area:docs": {"color": "0052cc", "description": "Documentation and guides"},
    # Type labels
    "type:feature": {"color": "a2eeef", "description": "New feature implementation"},
    "type:infra": {
        "color": "d876e3",
        "description": "Infrastructure and foundational work",
    },
    "type:test": {
        "color": "c5def5",
        "description": "Test implementation and validation",
    },
    "type:enhancement": {
        "color": "84b6eb",
        "description": "Enhancement to existing functionality",
    },
    "type:docs": {"color": "0052cc", "description": "Documentation work"},
}

# Create each label
for label in sorted(labels):
    config = label_config.get(
        label, {"color": "ededed", "description": f"Self-incorporation: {label}"}
    )

    cmd = [
        "gh",
        "api",
        "repos/AetherraLabs/Aetherra/labels",
        "--method",
        "POST",
        "--field",
        f"name={label}",
        "--field",
        f"color={config['color']}",
        "--field",
        f"description={config['description']}",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created label: {label}")
        else:
            if "already_exists" in result.stderr:
                print(f"ℹ️ Label already exists: {label}")
            else:
                print(f"❌ Failed to create label {label}: {result.stderr}")
    except Exception as e:
        print(f"❌ Error creating label {label}: {e}")

print(f"\n🏷️ Processed {len(labels)} labels")

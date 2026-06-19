#!/usr/bin/env python3
# Standard library imports
import csv
import os
import subprocess
import sys

CSV_PATH = os.getenv(
    "CSV_PATH",
    "docs/reports/selfinc/aetherra_selfinc_issues.csv",
)
REPO = os.getenv("REPO")  # e.g., AetherraLabs/Aetherra
ASSIGNEES = os.getenv("ASSIGNEES", "")  # comma-separated GitHub handles
MILESTONE_MAP = {}  # optional: {"Phase 1": "1", "Phase 2": "2"} if you prefer numeric IDs

if not REPO:
    print("ERROR: Please set REPO (e.g., export REPO=AetherraLabs/Aetherra)")
    sys.exit(1)


with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row["title"].strip()
        body = row["body"].strip()
        labels = row["labels"].strip()
        milestone = row.get("milestone", "").strip()

        label_args = []
        if labels:
            for lbl in [x.strip() for x in labels.split(",") if x.strip()]:
                label_args += ["--label", lbl]

        assignee_args = []
        if ASSIGNEES:
            for a in [x.strip() for x in ASSIGNEES.split(",") if x.strip()]:
                assignee_args += ["--assignee", a]

        milestone_arg = []
        if milestone:
            # If MILESTONE_MAP provided, translate; otherwise use title text
            ms = MILESTONE_MAP.get(milestone, milestone)
            milestone_arg = ["--milestone", ms]

        cmd = (
            ["gh", "issue", "create", "--repo", REPO, "--title", title, "--body", body]
            + label_args
            + assignee_args
            + milestone_arg
        )

        # Use subprocess directly to avoid shell escaping issues
        print(f"+ Creating issue: {title}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"Failed to create issue: {title}")
            sys.exit(result.returncode)

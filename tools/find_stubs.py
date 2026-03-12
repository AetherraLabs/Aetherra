#!/usr/bin/env python3
"""Find all stub/placeholder functions in the codebase."""

import json
import os
from collections import defaultdict


def find_stubs():
    stubs = []
    stub_keywords = [
        "pass  # stub",
        "raise NotImplementedError",
        "# TODO:",
        "# FIXME:",
        "return {}",
        "return []",
        "return None  # stub",
        "return False  # stub",
        "return True  # stub",
    ]

    skip_dirs = {
        ".git",
        ".venv",
        "node_modules",
        "dist-packages",
        "__pycache__",
        ".pytest_cache",
        "archive",
        "demos",
        "experiments",
    }

    for root, dirs, files in os.walk("."):
        # Filter out skip directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()

                        # Check for stub keywords
                        is_stub = False
                        for keyword in stub_keywords:
                            if keyword in line:
                                is_stub = True
                                break

                        if is_stub:
                            # Get context (function/class name)
                            context = "module"
                            for j in range(max(0, i - 10), i):
                                prev_line = lines[j].strip()
                                if prev_line.startswith("def ") or prev_line.startswith(
                                    "class "
                                ):
                                    context = (
                                        prev_line.split("(")[0]
                                        .replace("def ", "")
                                        .replace("class ", "")
                                    )
                                    break

                            stubs.append(
                                {
                                    "file": filepath.replace("\\", "/"),
                                    "line": i,
                                    "context": context,
                                    "code": stripped[:100],
                                }
                            )
            except Exception:
                pass

    return stubs


def main():
    print("🔍 Scanning for stubs and placeholders...")
    stubs = find_stubs()

    # Group by severity (return statements are lower priority than NotImplementedError)
    severity_counts = defaultdict(int)
    for stub in stubs:
        if "NotImplementedError" in stub["code"]:
            severity_counts["critical"] += 1
        elif "TODO" in stub["code"] or "FIXME" in stub["code"]:
            severity_counts["high"] += 1
        else:
            severity_counts["medium"] += 1

    # Summary
    print(f"\n📊 Found {len(stubs)} stub markers:")
    print(f"   🔴 Critical (NotImplementedError): {severity_counts['critical']}")
    print(f"   🟠 High (TODO/FIXME): {severity_counts['high']}")
    print(f"   🟡 Medium (return stubs): {severity_counts['medium']}")

    # Save to JSON
    output = {
        "total": len(stubs),
        "by_severity": dict(severity_counts),
        "stubs": sorted(stubs, key=lambda x: (x["file"], x["line"])),
    }

    with open("STUB_INVENTORY.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\n✅ Saved stub inventory to STUB_INVENTORY.json")

    # Print first 30 stubs
    print("\n📋 First 30 stubs:")
    for i, stub in enumerate(stubs[:30], 1):
        print(
            f"   {i:2d}. {stub['file']}:{stub['line']:4d} | {stub['context']:30s} | {stub['code'][:50]}"
        )

    if len(stubs) > 30:
        print(f"   ... and {len(stubs) - 30} more")


if __name__ == "__main__":
    main()

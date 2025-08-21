#!/usr/bin/env python3
"""
Self-Healing Demo
Uses the SelfRepairPlugin to detect issues, suggest fixes, and attempt auto-repair.
"""

from Aetherra.stdlib.selfrepair import SelfRepairPlugin

SAMPLE_BROKEN_CODE = """
 def add(a,b):
    return a+b

x=1
y=2
print(add(x,y))
"""


def main():
    plugin = SelfRepairPlugin()

    print("=== Detect Syntax Errors ===")
    errors = plugin.detect_syntax_errors(SAMPLE_BROKEN_CODE)
    print(errors)

    print("\n=== Suggest Improvements ===")
    suggestions = plugin.suggest_code_improvements(SAMPLE_BROKEN_CODE)
    print(suggestions)

    print("\n=== Auto Repair ===")
    repair = plugin.auto_fix_common_issues(SAMPLE_BROKEN_CODE)
    print(repair)

    print("\n=== Repair Report ===")
    report = plugin.generate_repair_report(
        "sample.py",
        issues=[
            {
                "type": e.get("type", "unknown"),
                "confidence": 70,
                "suggestion": e.get("suggestion", ""),
            }
            for e in errors
        ],
    )
    print(report)


if __name__ == "__main__":
    main()

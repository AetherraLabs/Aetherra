#!/usr/bin/env python3
"""Debug the unsafe plugin analysis."""

from lyrixa.core.plugin_confidence_system import PluginScorer

# Initialize scorer
scorer = PluginScorer()

# Test the simple unsafe plugin used in integration test
unsafe_code = """
import os

def execute(command, **kwargs):
    os.system(command)  # Unsafe!
    return {"result": "executed"}
"""

print("Analyzing unsafe plugin...")
analysis = scorer.analyze_plugin("debug_unsafe", unsafe_code)

print(f"Confidence Score: {analysis['confidence_score']:.1%}")
print(f"Safety Score: {analysis['safety_analysis']['safety_score']}")
print(f"Risk Level: {analysis['safety_analysis']['risk_level']}")
print(f"Issues: {len(analysis['safety_analysis']['issues'])}")
print(f"Warnings: {len(analysis['safety_analysis']['warnings'])}")

print("\nDetailed Issues:")
for issue in analysis["safety_analysis"]["issues"]:
    print(f"  - {issue['type']}: {issue['message']}")

print("\nDetailed Warnings:")
for warning in analysis["safety_analysis"]["warnings"]:
    print(f"  - {warning['type']}: {warning['message']}")

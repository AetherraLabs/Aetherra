#!/usr/bin/env python3
"""Test script for aetherra Plugin SDK"""

import os
import sys

# Add paths
sys.path.append("src")
sys.path.append("sdk/plugins")

# Import plugin API first
from core.plugin_api import PLUGIN_REGISTRY

print(f"Initial registry state: {PLUGIN_REGISTRY}")

# Import example plugin to trigger registration
try:
    import example

    print("✅ Example plugin imported successfully")
    print(f"Registry after import: {PLUGIN_REGISTRY}")
except Exception as e:
    print(f"❌ Example plugin import failed: {e}")
    import traceback

    traceback.print_exc()


def test_plugin_system():
    print("=== aetherra Plugin SDK Test ===")
    print()

    print(f"PLUGIN_REGISTRY contents: {list(PLUGIN_REGISTRY.keys())}")
    print()

    print("Registered plugins:")
    for name, funcs in PLUGIN_REGISTRY.items():
        print(f"  {name}: {len(funcs)} functions")
        for func_name, func_info in funcs.items():
            print(f"    - {func_name}: {func_info['description']}")
    print()

    # Test calling functions directly through registry
    if "example" in PLUGIN_REGISTRY:
        print("Testing example plugin functions:")

        # Test hello_world
        if "hello_world" in PLUGIN_REGISTRY["example"]:
            func = PLUGIN_REGISTRY["example"]["hello_world"]["function"]
            result = func("SDK Test")
            print(f"1. hello_world('SDK Test') -> {result}")

        # Test greet
        if "greet" in PLUGIN_REGISTRY["example"]:
            func = PLUGIN_REGISTRY["example"]["greet"]["function"]
            result = func("Developer")
            print(f"2. greet('Developer') -> {result}")

        # Test calculate
        if "calculate" in PLUGIN_REGISTRY["example"]:
            func = PLUGIN_REGISTRY["example"]["calculate"]["function"]
            result = func("5 + 7")
            print(f"3. calculate('5 + 7') -> {result}")

        # Test status
        if "status" in PLUGIN_REGISTRY["example"]:
            func = PLUGIN_REGISTRY["example"]["status"]["function"]
            result = func()
            print(f"4. status() -> {result}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_plugin_system()

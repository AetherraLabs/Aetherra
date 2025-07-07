#!/usr/bin/env python3
"""Test script for the updated script router"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Aetherra.runtime.script_router import ScriptRouter


def main():
    # Create dummy context
    dummy_context = {"memory": None, "plugins": None, "agents": None}

    # Initialize router
    router = ScriptRouter(context=dummy_context)

    # Test commands
    print("=== Testing Script Router ===")
    print()

    print("1. Listing available scripts:")
    result = router.handle_input("list scripts")
    print(result)
    print()

    print("2. Describing a script:")
    result = router.handle_input("describe reflect")
    print(result)
    print()

    print("3. Describing another script:")
    result = router.handle_input("describe bootstrap")
    print(result)
    print()

    print("=== Test Complete ===")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Plugin Discovery Test
====================
Test plugin discovery logic to understand validation issues.
"""

import os
import re
from pathlib import Path


def test_plugin_validation(file_path):
    """Test plugin file validation."""
    print(f"\n🧪 Testing: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Test patterns
        patterns = [
            ("class.*plugin", "Class with 'plugin' in name"),
            ("baseplugin", "BasePlugin inheritance"),
            ("lyrixaplugin", "LyrixaPlugin inheritance"),
            ("def execute", "Execute method"),
            ("def run", "Run method"),
        ]

        print("   Pattern checks:")
        has_plugin_class = False
        for pattern, description in patterns:
            if re.search(pattern, content.lower()):
                print(f"   ✅ {description}")
                has_plugin_class = True
            else:
                print(f"   ❌ {description}")

        print(f"   Has plugin class: {has_plugin_class}")

        # Test required fields
        required_patterns = ["name", "description", "input_schema", "output_schema"]
        print("\n   Required field checks:")
        for pattern in required_patterns:
            if pattern in content.lower():
                print(f"   ✅ {pattern}")
            else:
                print(f"   ❌ {pattern}")

        has_required_fields = all(
            pattern in content.lower() for pattern in required_patterns
        )
        print(f"   Has required fields: {has_required_fields}")

        # Look for class attributes specifically
        lines = content.split("\n")
        found_attributes = set()
        print("\n   Class attribute checks:")
        for line in lines:
            line = line.strip()
            for attr in required_patterns:
                if line.startswith(f"{attr} ="):
                    found_attributes.add(attr)
                    print(f"   ✅ Found attribute: {line[:50]}...")

        print(f"   Found attributes: {found_attributes}")
        print(f"   Valid plugin: {has_plugin_class and len(found_attributes) >= 4}")

    except Exception as e:
        print(f"   ⚠️ Error: {e}")


def main():
    """Test plugin validation."""
    print("🔍 PLUGIN DISCOVERY TEST")
    print("=" * 40)

    # Test a few problematic plugins
    test_files = [
        "lyrixa/plugins/assistant_trainer_plugin.py",
        "lyrixa/plugins/sample_plugin_1.py",
        "src/aetherra/plugins/math_plugin.py",
    ]

    for file_path in test_files:
        full_path = Path(file_path)
        if full_path.exists():
            test_plugin_validation(full_path)


if __name__ == "__main__":
    main()

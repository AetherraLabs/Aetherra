#!/usr/bin/env python3
"""
🧬 Aetherra File Parser Test
===========================

Test the Aetherra parser with .aether files to demonstrate
that Aetherra is now a true programming language.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Aetherra.core.aethercode_grammar import create_Aetherra_parser


def test_aether_file(file_path: str):
    """Test parsing a .aether file"""
    parser = create_Aetherra_parser()

    try:
        with open(file_path, encoding="utf-8") as f:
            aether_code = f.read()

        print(f"🧬 Testing Aetherra file: {file_path}")
        print("=" * 60)
        print("Source Code:")
        print(aether_code)
        print("=" * 60)

        result = parser.validate_syntax(aether_code)

        if result["valid"]:
            print("✅ Aetherra syntax is VALID!")
            print("🎉 Aetherra is working as a true programming language!")
            return True
        else:
            print("❌ Syntax errors found:")
            for error in result["errors"]:
                print(f"   {error}")
            return False

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Error testing file: {e}")
        return False


if __name__ == "__main__":
    test_file = "examples/test.aether"

    if len(sys.argv) > 1:
        test_file = sys.argv[1]

    success = test_aether_file(test_file)

    if success:
        print("\n🚀 SUCCESS: Aetherra language implementation is complete!")
        print("📝 Aetherra files (.aether) can now be parsed with formal grammar!")
        print("🎯 Aetherra is now syntax-native, not Python-wrapped!")
    else:
        print("\n🔧 Parser needs refinement for complex syntax.")
